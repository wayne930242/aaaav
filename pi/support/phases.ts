/**
 * The phase machine: each loop kind runs a fixed sequence of phases, and the book's evidence says which
 * phases are complete. Nothing here blocks; a phase entered while an earlier one is incomplete yields
 * one warning line that names what is missing and the `skip` escape. Phases regress by themselves when
 * evidence changes (a diff after verify, a spec edited back to proposed) and by `back` on request.
 */

import { existsSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, relative, resolve } from "node:path";
import {
	type Book,
	type Entry,
	type Kind,
	type Task,
	allFriction,
	anchorCommand,
	artifactOnDisk,
	currentKind,
	lastActIndex,
	lastIndex,
	retryWithoutFriction,
	specFolder,
} from "./book.ts";

export const SEQUENCES: Record<Kind, readonly string[]> = {
	quick: ["act", "check", "reflect", "close"],
	inline: ["anchor", "act", "verify", "reflect", "close"],
	reviewed: ["anchor", "act", "verify", "review", "reflect", "close"],
	durable: ["decide", "grill", "spec", "read", "approve", "design", "anchor", "act", "verify", "review", "reflect", "close"],
};

export type Status = { name: string; state: "done" | "skipped" | "missing"; note: string };

export type Phases = {
	kind: Kind | "undeclared";
	statuses: Status[];
	/** The last phase of the complete prefix, or `start`. */
	current: string;
	/** The first incomplete phase, `fix` when a check or review failed after the last change, else `close`. */
	next: string;
	missing: string;
	skipped: string[];
	backs: string[];
	/** Advisory hints that are not phases. */
	hints: string[];
};

export type Inputs = { entries: Entry[]; cwd: string; todos: Task[]; env?: NodeJS.ProcessEnv };

// --- paths ---------------------------------------------------------------------------------------

const EXEMPT_IN_PROJECT = ["scratch", "docs/specs"];
const EXEMPT_ROOTS = [tmpdir(), "/tmp", "/var/folders"];
const EXEMPT_EXTENSIONS = [".md", ".txt", ".html", ".htm"];

/** The real path of `path`, resolving symlinks such as /var → /private/var through its nearest existing parent. */
function real(path: string): string {
	if (existsSync(path)) return realpathSync(path);
	const parent = dirname(path);
	return parent === path ? path : join(real(parent), basename(path));
}

function within(root: string, target: string): boolean {
	const rel = relative(root, target);
	return rel === "" || (!rel.startsWith("..") && !isAbsolute(rel));
}

/** Scratch and spec folders in the project and temp files outside it; a project that lives in a temp dir is still counted. */
export function outsideWork(filePath: string, cwd: string): boolean {
	const root = real(cwd);
	const target = real(resolve(cwd, filePath));
	if (within(root, target)) return EXEMPT_IN_PROJECT.some((dir) => within(join(root, dir), target));
	return EXEMPT_ROOTS.some((tmp) => within(real(tmp), target));
}

/** Markdown, text, and HTML files and everything `outsideWork` names: an edit the anchor gate does not warn about. */
export function exempt(filePath: string, cwd: string): boolean {
	return EXEMPT_EXTENSIONS.includes(extname(filePath).toLowerCase()) || outsideWork(filePath, cwd);
}

// --- evidence ------------------------------------------------------------------------------------

type Ctx = Inputs & { seq: readonly string[]; folder?: string; lastAct: number };

const done = (name: string, note = ""): Status => ({ name, state: "done", note });
const missing = (name: string, note: string): Status => ({ name, state: "missing", note });

function same(a: string, b: string): boolean {
	const group = (name: string) => (name === "check" ? "verify" : name);
	return group(a) === group(b);
}

/** Entries before this index do not count for `name`: the latest `back` to this phase or an earlier one. */
function floor(entries: Entry[], seq: readonly string[], name: string): number {
	const at = seq.indexOf(name);
	let from = 0;
	entries.forEach((entry, index) => {
		if (entry.stage !== "back" || typeof entry.phase !== "string") return;
		const target = seq.findIndex((candidate) => same(candidate, entry.phase as string));
		if (target >= 0 && at >= target) from = index + 1;
	});
	return from;
}

function lastWhere(entries: Entry[], from: number, test: (entry: Entry) => boolean): number {
	for (let i = entries.length - 1; i >= from; i--) if (test(entries[i])) return i;
	return -1;
}

function skipEntry(entries: Entry[], from: number, name: string): Entry | undefined {
	const index = lastWhere(entries, from, (entry) => entry.stage === "skip" && typeof entry.phase === "string" && same(entry.phase, name));
	return index >= 0 ? entries[index] : undefined;
}

/** The latest recorded summary of an artifact since `from`; a loop that never wrote it falls back to the file on disk. */
function artifact(ctx: Ctx, name: string, from: number): Entry | undefined {
	const index = lastWhere(ctx.entries, from, (entry) => entry.stage === name && entry.auto === true);
	if (index >= 0) return ctx.entries[index];
	const wrote = ctx.entries.some((entry) => entry.stage === name && entry.auto === true);
	return from === 0 && !wrote && ctx.folder ? artifactOnDisk(ctx.folder, name, ctx.cwd) : undefined;
}

const total = (counts: unknown): number => Object.values((counts ?? {}) as Record<string, number>).reduce((sum, n) => sum + Number(n), 0);

/** The index of the first spec entry in the latest run of proposed-or-approved spec entries, -1 when there is no entry for it, or undefined when the spec is not proposed. */
function proposedSince(ctx: Ctx): number | undefined {
	let start: number | undefined;
	let seen = false;
	ctx.entries.forEach((entry, index) => {
		if (entry.stage !== "spec" || entry.auto !== true) return;
		seen = true;
		const live = entry.status === "proposed" || entry.status === "approved";
		if (!live) start = undefined;
		else if (start === undefined) start = index;
	});
	if (seen) return start;
	const disk = ctx.folder ? artifactOnDisk(ctx.folder, "spec", ctx.cwd) : undefined;
	return disk && (disk.status === "proposed" || disk.status === "approved") ? -1 : undefined;
}

function evaluate(name: string, ctx: Ctx): Status {
	const { entries } = ctx;
	const from = floor(entries, ctx.seq, name);
	const skip = skipEntry(entries, from, name);
	if (skip) return { name, state: "skipped", note: String(skip.reason ?? skip.skip ?? "") };
	switch (name) {
		case "decide": {
			const decision = artifact(ctx, "decision", from);
			return total(decision?.counts) > 0 ? done(name) : missing(name, ctx.folder ? `${ctx.folder}/decision.md with decision rows` : "decision.md with decision rows (no spec folder recorded)");
		}
		case "grill": {
			const decision = artifact(ctx, "decision", from);
			if (!decision || total(decision.counts) === 0) return missing(name, "decision rows to grill");
			const open = Number((decision.counts as Record<string, number>).open ?? 0);
			if (open > 0) return missing(name, `${open} open decision row${open === 1 ? "" : "s"}`);
			const first = entries.find((entry) => entry.stage === "decision" && entry.auto === true);
			return first && Number((first.counts as Record<string, number>).open ?? 0) === 0 ? { name, state: "skipped", note: "no open rows" } : done(name);
		}
		case "spec": {
			const spec = artifact(ctx, "spec", from);
			return spec?.status === "proposed" || spec?.status === "approved" ? done(name) : missing(name, "spec.md with Status: proposed");
		}
		case "read": {
			const start = proposedSince(ctx);
			if (start === undefined) return missing(name, "a proposed spec to read");
			const index = lastWhere(entries, Math.max(from, start + 1), (entry) => entry.stage === "goldfish" && entry.ok !== false);
			if (index >= 0) return done(name, String(entries[index].source ?? ""));
			const wrote = entries.some((entry) => entry.stage === "spec" && entry.auto === true);
			if (!wrote && from === 0 && artifact(ctx, "spec", 0)?.status === "approved") return done(name, "spec approved before this loop");
			return missing(name, "a fresh-context read of the spec (dispatch a subagent, or `anchorloop_stage fresh-read`)");
		}
		case "approve": {
			const spec = artifact(ctx, "spec", from);
			return spec?.status === "approved" && spec.approvedFrom === true ? done(name) : missing(name, `spec.md Status: approved with Approved from${spec?.status ? ` (now ${spec.status})` : ""}`);
		}
		case "design": {
			const design = artifact(ctx, "design", from);
			return design?.approach === true ? done(name) : missing(name, "design.md with its approach section filled");
		}
		case "anchor": {
			const index = lastWhere(entries, from, (entry) => entry.stage === "anchor");
			return index >= 0 ? done(name, String(entries[index].check ?? "")) : missing(name, "a `Reality anchor:` line, or `anchor` on the kind call");
		}
		case "act":
			return lastWhere(entries, from, (entry) => entry.stage === "edit") >= 0 ? done(name) : missing(name, "a change to the code");
		case "check":
		case "verify": {
			const index = lastWhere(entries, Math.max(from, ctx.lastAct + 1), (entry) => entry.stage === "verify" || entry.stage === "check");
			if (index < 0) {
				const command = anchorCommand(entries);
				return missing(name, command ? `a passing run of \`${command}\` after the last change` : "a verify declaration (the anchor is not a command)");
			}
			const entry = entries[index];
			if (entry.declared === true) return entry.result === "fail" ? missing(name, "the declared verify failed") : done(name, "declared");
			return entry.exit === 0 ? done(name) : missing(name, `the anchor exited ${entry.exit ?? "unknown"} after the last change`);
		}
		case "review": {
			const index = lastWhere(entries, Math.max(from, ctx.lastAct + 1), (entry) => entry.stage === "review");
			if (index < 0) return missing(name, "a review round after the last change with Blocking: P0=0 P1=0");
			const round = entries[index];
			if (round.blocking === false) return done(name);
			const rounds = entries.filter((entry) => entry.stage === "review");
			const stalled = rounds.length >= 2 && rounds.at(-1)?.blocking === true && rounds.at(-2)?.blocking === true;
			return missing(name, stalled ? "two consecutive review rounds still blocking: hand the trend to the user" : round.blocking === true ? "blocking review findings are open" : "the review verdict is unknown");
		}
		case "reflect": {
			const items = allFriction(entries, ctx.env);
			if (items.length === 0) return { name, state: "skipped", note: "no friction" };
			const open = items.filter((item) => !item.reflected).length;
			return open === 0 ? done(name) : missing(name, `${open} friction entr${open === 1 ? "y" : "ies"} without a reflect`);
		}
		default:
			return missing(name, name);
	}
}

/** The phase state of the loop kind recorded in the book. */
export function computePhases(book: Pick<Book, "entries">, inputs: Omit<Inputs, "entries">): Phases {
	const kind = currentKind(book.entries);
	const seq = SEQUENCES[kind ?? "inline"];
	const ctx: Ctx = { ...inputs, entries: book.entries, seq, folder: specFolder(book.entries, inputs.todos, inputs.cwd), lastAct: lastActIndex(book.entries) };
	const statuses = seq.filter((name) => name !== "close").map((name) => evaluate(name, ctx));
	let prefix = 0;
	while (prefix < statuses.length && statuses[prefix].state !== "missing") prefix++;
	const first = statuses[prefix];
	const reached = statuses.slice(0, prefix).filter((status) => status.state === "done").at(-1);
	let next = first ? first.name : "close";
	let note = first ? first.note : "";
	const last = ctx.lastAct;
	const verify = book.entries.map((entry, index) => ({ entry, index })).filter(({ entry, index }) => index > last && (entry.stage === "verify" || entry.stage === "check")).at(-1)?.entry;
	const review = book.entries.map((entry, index) => ({ entry, index })).filter(({ entry, index }) => index > last && entry.stage === "review").at(-1)?.entry;
	if ((next === "verify" || next === "check") && last >= 0 && verify && verify.exit !== 0 && verify.declared !== true) next = "fix";
	else if (next === "review" && last >= 0 && review?.blocking === true) next = "fix";
	if (next === "fix") note = first?.note ?? "";
	const skipped = statuses.filter((status) => status.state === "skipped" && status.note !== "no friction").map((status) => `${status.name} (${status.note})`);
	const backs = book.entries.filter((entry) => entry.stage === "back").map((entry) => `${entry.phase} (${entry.reason})`);
	const hints = retryWithoutFriction(book.entries) ? ["friction: a failed run was retried and passed, with no friction entry after it"] : [];
	return {
		kind: kind ?? "undeclared",
		statuses,
		current: reached?.name ?? "start",
		next,
		missing: note,
		skipped,
		backs,
		hints,
	};
}

/** The statuses of phases before `entering` that are incomplete. */
export function incompleteBefore(phases: Phases, entering: string): Status[] {
	const order = phases.statuses.map((status) => status.name);
	const at = entering === "close" ? order.length : order.findIndex((name) => same(name, entering));
	return phases.statuses.filter((status, index) => index < at && status.state === "missing");
}

/** One line: the phase entered, what is missing before it, and the skip escape. */
export function jumpLine(entering: string, missingBefore: Status[]): string {
	const list = missingBefore.map((status) => `${status.name} (${status.note})`).join("; ");
	const skip = missingBefore[0]?.name ?? "<phase>";
	return `anchorloop: ${entering} comes before ${list}; skip with \`anchorloop_stage skip ${skip} <reason>\`.`;
}

/** The phase line `read` and the close summary show. */
export function describe(phases: Phases): string {
	const parts = [`${phases.kind} · phase ${phases.current}${phases.current === "start" ? "" : " ✓"} → ${phases.next}${phases.missing ? ` (missing: ${phases.missing})` : ""}`];
	if (phases.skipped.length) parts.push(`skipped: ${phases.skipped.join(", ")}`);
	if (phases.backs.length) parts.push(`back: ${phases.backs.join(", ")}`);
	return parts.join(" · ");
}

/** Remembers which incomplete phases a jump already warned about; a regression adds one and warns again. */
export class JumpMemory {
	private warned = new Map<string, Set<string>>();

	/** True when `missingNames` holds a phase not yet warned about for this book and entering phase. */
	fresh(bookId: string, entering: string, missingNames: string[]): boolean {
		const key = `${bookId}|${entering}`;
		const before = this.warned.get(key) ?? new Set<string>();
		const news = missingNames.some((name) => !before.has(name));
		if (missingNames.length === 0) this.warned.delete(key);
		else this.warned.set(key, new Set(missingNames));
		return news;
	}
}

export { lastIndex };
