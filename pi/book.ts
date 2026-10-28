/**
 * pi extension: the loop book. The first `todo` create or `kind` declaration opens a loop and its book. The agent declares only
 * what the program cannot observe (`kind` with its intent and anchor command, a non-command `verify`,
 * `fresh-read`, `friction`, `reflect`, `skip`, `back`, `close`); the extension derives the rest from
 * evidence: production edits, the exit code of the anchor command, reviewer results, durable artifacts,
 * and the fresh-reader subagent. A phase machine over that evidence warns once per jump and never blocks;
 * only `close` refuses, while a todo is neither done nor disposed of.
 */

import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import {
	type Book,
	KINDS,
	allFriction,
	anchorCommand,
	appendEntry,
	artifactKind,
	childId,
	childIds,
	childLines,
	createBook,
	currentIntent,
	currentKind,
	deleteBook,
	diffAgainstBases,
	findChildBook,
	frictionOf,
	guarded,
	isOpenTask,
	latestTasks,
	openLoop,
	replayTodos,
	refsOf,
	resolveRef,
	reviewTrend,
	reviews,
	reviewsStalled,
	specFolder,
	stagesDone,
	summarizeArtifact,
	taskLines,
	taskDetails,
	sweep,
	touchRepo,
	touchRepoBeforeMerge,
	validFollowup,
	verifyAfterLastAct,
} from "./support/book.ts";
import { classify } from "./support/jev.ts";
import { SEQUENCES, computePhases, describe, incompleteBefore, outsideWork } from "./support/phases.ts";
import { type Snapshot, snapshot } from "./support/snapshot.ts";
import { isSubagent } from "./support/subagent.ts";

export const SESSION_ENTRY = "anchorloop-loop";
const STAGES = ["kind", "verify", "fresh-read", "friction", "reflect", "skip", "back", "close", "read"] as const;
const REVIEWERS = new Set(["reviewer", "adversarial-reviewer"]);
const BLOCKING = /Blocking\s*:?\**\s*:?\s*P0\s*=\s*(\d+)\D{0,5}P1\s*=\s*(\d+)/gi;
const ANCHOR_LINE = /Reality anchor:[ \t]*(.*)/;

export const OPEN_LINE =
	"anchorloop: a loop is open. Declare it with `anchorloop_stage` {stage: kind, kind: quick|inline|reviewed|durable, intent: <one line>, anchor: <check command>}.";

type Params = {
	stage: (typeof STAGES)[number];
	kind?: (typeof KINDS)[number];
	intent?: string;
	anchor?: string;
	note?: string;
	result?: "pass" | "fail";
	tried?: string;
	found?: string;
	led_by?: string;
	friction?: (string | number)[];
	class?: "misdirection" | "gap" | "resolved";
	action?: string;
	phase?: string;
	reason?: string;
	verdict?: "landed" | "blocked" | "abandoned";
	view?: "summary" | "all";
};

type Block = { type?: string; text?: string };
type BranchEntry = { type?: string; message?: { role?: string; content?: unknown } };

/** The P0 and P1 counts of the last `Blocking: P0=<n> P1=<m>` line in a reviewer report, tolerant of markdown emphasis. */
export function parseBlocking(text: string): { p0: number; p1: number } | undefined {
	const found = [...text.matchAll(BLOCKING)].at(-1);
	return found ? { p0: Number(found[1]), p1: Number(found[2]) } : undefined;
}

function textOf(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return (content as Block[]).map((block) => (block && typeof block.text === "string" ? block.text : "")).filter(Boolean).join("\n");
}

function lastLine(text: string): string {
	return (
		text
			.split("\n")
			.map((line) => line.trim())
			.filter(Boolean)
			.at(-1) ?? ""
	).slice(0, 200);
}

/** The exit code of a bash tool result: the structured code, else 0 when the call did not error, else the code the message names. */
export function bashExit(event: { isError?: boolean; structuredContent?: unknown; content?: unknown }): number | null {
	const code = (event.structuredContent as { exit_code?: unknown } | undefined)?.exit_code;
	if (typeof code === "number") return code;
	if (event.isError !== true) return 0;
	const named = /Command exited with code (\d+)/.exec(textOf(event.content));
	return named ? Number(named[1]) : null;
}

/** An anchor with an environment prefix (`. venv/bin/activate && pytest -q`) matches on its last `&&` segment. */
export function anchorSegment(anchor: string): string {
	return anchor.split("&&").at(-1)?.trim() || anchor;
}

/**
 * The exit to record for a bash call that ran `anchor`: the call's exit code, except `unknown` when something after the anchor
 * can replace it: `||`, `;`, a newline, or a pipe straight after the anchor unless the command starts with `set -o pipefail`.
 * A chain `anchor && other` keeps a failed anchor's code, so it stands.
 */
export function anchorExit(command: string, anchorText: string, exit: number | null): number | "unknown" {
	if (exit === null) return "unknown";
	const anchor = anchorSegment(anchorText);
	const at = command.lastIndexOf(anchor);
	// `! anchor` inverts the code and `x || anchor` may never run it.
	if (at < 0 || /(!|\|\|)\s*$/.test(command.slice(0, at))) return "unknown";
	const rest = command.slice(at + anchor.length);
	const pipefail = /\bset\s+(-\w+\s+|-o\s+\w+\s+)*-o\s+pipefail\b|\bset\s+-\w*e\w*o\s+pipefail\b|\bset\s+-\w*o\s+pipefail\b/.test(command.slice(0, at));
	let chained = false;
	// `&&` keeps a failed anchor's exit; `||`, `;`, and a newline can replace it, and so can a pipe
	// straight after the anchor unless pipefail is set.
	for (const [separator] of rest.matchAll(/&&|\|\||\||(?<![<>&])&(?![&>])|;|\n/g)) {
		if (separator === "&&") chained = true;
		else if (separator === "|") {
			if (!chained && !pipefail) return "unknown";
		} else return "unknown";
	}
	return exit;
}

/** The text a `Reality anchor:` line states in an assistant message, if any. */
function statedAnchor(message: { role?: string; content?: unknown } | undefined): string | undefined {
	if (message?.role !== "assistant") return undefined;
	const found = ANCHOR_LINE.exec(textOf(message.content));
	return found ? found[1].trim().slice(0, 300) || "(stated on the next line)" : undefined;
}

const reply = (text: string) => ({ content: [{ type: "text" as const, text }], details: undefined });

export default function (pi: ExtensionAPI) {
	const subagent = isSubagent();
	function todosOf(ctx: ExtensionContext) {
		return replayTodos(ctx.sessionManager.getBranch());
	}

	function phasesOf(book: Book, ctx: ExtensionContext) {
		return computePhases(book, { cwd: ctx.cwd, todos: todosOf(ctx) });
	}

	/** The line that tells the agent Jev did not accept a returned subagent as the fresh read, while the read is still open. */
	function freshReadLine(book: Book, phases: ReturnType<typeof phasesOf>): string[] {
		const last = [...book.entries].reverse().find((entry) => entry.stage === "goldfish");
		const open = phases.statuses.find((status) => status.name === "read")?.state === "missing";
		return open && last?.source === "jev" && last.ok === false ? [`fresh read by ${String(last.child || "a subagent")} judged not fresh — declare \`fresh-read\` if it was`] : [];
	}

	function summaryLines(book: Book, ctx: ExtensionContext): string[] {
		const phases = phasesOf(book, ctx);
		const verify = [...book.entries].reverse().find((entry) => entry.stage === "verify" || entry.stage === "check");
		const open = todosOf(ctx).filter(isOpenTask).length;
		const friction = allFriction(book.entries);
		return [
			describe(phases),
			`intent: ${currentIntent(book.entries) ?? "not declared"}`,
			`last ${verify?.stage ?? "verify"}: ${verify ? `${verify.declared ? `declared ${verify.result}` : `exit ${verify.exit ?? "unknown"}`}${verify.last ? ` — ${verify.last}` : ""}${verifyAfterLastAct(book.entries) ? "" : " (before the last change)"}` : "none"}`,
			`reviews: ${reviewTrend(book.entries)}; open todos: ${open}; friction: ${friction.length} (${friction.filter((item) => !item.reflected).length} unreflected)`,
			...childLines(book.entries).map((line) => `child ${line}`),
			...friction.filter((item) => item.owner !== "main").map((item) => `friction ${item.ref}: ${item.tried} → ${item.found}${item.reflected ? ` [${item.class}]` : ""}`),
			...phases.hints,
			...freshReadLine(book, phases),
		];
	}

	function recordTasks(book: Book, details: unknown, input: { action?: unknown; id?: unknown }, cwd: string): void {
		const tasks = taskDetails(details) ?? [];
		const known = new Set(latestTasks(book.entries).map((entry) => entry.id));
		const touched = input.action === "create" ? tasks.filter((task) => !known.has(task.id)) : tasks.filter((task) => task.id === Number(input.id));
		for (const task of touched) {
			const refs = refsOf(task.metadata).map((ref) => ({ ref, range: resolveRef(ref, cwd, book.entries) }));
			const { anchor, followup } = task.metadata ?? {};
			book.entries.push(
				appendEntry(book.path, "task", {
					id: task.id,
					subject: task.subject,
					status: task.status,
					...(typeof anchor === "string" ? { anchor } : {}),
					...(refs.length ? { refs } : {}),
					...(followup !== undefined ? { followup } : {}),
				}),
			);
		}
	}

	/** A `Reality anchor:` line stated since the last user message, recorded when a loop opens after it. */
	function recordPriorAnchor(book: Book, ctx: ExtensionContext): void {
		const branch = ctx.sessionManager.getBranch() as BranchEntry[];
		for (let i = branch.length - 1; i >= 0; i--) {
			const message = branch[i].type === "message" ? branch[i].message : undefined;
			if (!message) continue;
			if (message.role === "user") return;
			const stated = statedAnchor(message);
			if (stated) {
				book.entries.push(appendEntry(book.path, "anchor", { check: stated, line: true }));
				return;
			}
		}
	}

	function close(book: Book, ctx: ExtensionContext, verdict: string): { text: string; snapshot?: Snapshot } {
		const todos = replayTodos(ctx.sessionManager.getBranch());
		const undisposed = todos.filter((task) => isOpenTask(task) && !validFollowup(task.metadata?.followup));
		if (undisposed.length > 0) {
			throw new Error(
				`Cannot close: ${undisposed.length} todo(s) are pending or in progress without metadata.followup (a ticket id, \`memory\`, or \`drop — <reason>\`):\n` +
					undisposed.map((task) => `- #${task.id} ${task.subject}`).join("\n"),
			);
		}
		const kept = childId() !== undefined;
		const kind = currentKind(book.entries);
		const phases = phasesOf(book, ctx);
		const missing = incompleteBefore(phases, "close");
		const notice = verdict === "landed" && missing.length ? `anchorloop: closed with phases not shown complete: ${missing.map((status) => `${status.name} (${status.note})`).join("; ")}.` : undefined;
		const diff = diffAgainstBases(book.entries);
		const friction = allFriction(book.entries);
		const phaseList = phases.statuses.map((status) => ({ phase: status.name, state: status.state === "skipped" && status.auto ? "auto-skipped" : status.state === "missing" ? "not shown complete" : status.state, ...(status.state === "skipped" ? { note: status.note } : {}) }));
		const summary = {
			intent: currentIntent(book.entries) ?? null,
			kind: kind ?? null,
			verdict,
			stages: stagesDone(book.entries),
			phases: phaseList,
			reviewRounds: reviews(book.entries).length,
			reviewTrend: reviewTrend(book.entries),
			diff: diff.summary,
			skipped: phases.skipped,
			back: phases.backs,
			friction: friction.map((item) => ({ ref: item.ref, owner: item.owner, tried: item.tried, found: item.found, led_by: item.led_by, class: item.class ?? null, action: item.action ?? null })),
			followups: todos.filter((task) => isOpenTask(task)).map((task) => ({ task: task.subject, followup: task.metadata?.followup })),
		};
		const unreflected = friction.filter((item) => !item.reflected);
		const tail = unreflected.length
			? ` Unreflected friction for the Reflexive Pass: ${unreflected.map((item) => `${item.ref} (${item.found})`).join("; ")}.`
			: "";
		const named = (item: (typeof phaseList)[number]) => `${item.phase}${item.note ? ` (${item.note})` : ""}`;
		const doneNames = phaseList.filter((item) => item.state === "done").map((item) => item.phase);
		const skippedNames = phaseList.filter((item) => item.state === "skipped" || item.state === "auto-skipped").map(named);
		const openNames = phaseList.filter((item) => item.state === "not shown complete").map((item) => item.phase);
		const shown = [
			`done: ${doneNames.join(", ") || "none"}`,
			...(skippedNames.length ? [`skipped: ${skippedNames.join(", ")}`] : []),
			...(openNames.length ? [`${verdict === "landed" ? "not complete" : "not reached"}: ${openNames.join(", ")}`] : []),
		].join("; ");
		const back = summary.back.length ? `; back ${summary.back.join(", ")}` : "";
		const text = `Loop closed (${verdict}): phases ${shown}; ${summary.reviewTrend}; diff ${diff.summary.split("\n").join("; ")}${back}.${tail}`;
		const after = notice ? `\n${notice}` : "";
		if (kept) {
			// A child's book stays for the main session to read and delete.
			appendEntry(book.path, "close", { verdict, summary: text.slice(0, 500) });
			return { text: `${text} The book stays for the main session.${after}` };
		}
		// Jev judges the loop as it stood at close; the book is gone by the time the result is judged.
		const snap = kind === "quick" ? undefined : snapshot(book, ctx);
		pi.appendEntry(SESSION_ENTRY, summary);
		for (const id of childIds(book.entries)) {
			const child = findChildBook(id);
			if (child) deleteBook(child.path);
		}
		deleteBook(book.path);
		return { text: `${text} The book is deleted. Clear the todo list now (todo action: clear).${after}`, snapshot: snap };
	}

	pi.registerTool({
		name: "anchorloop_stage",
		label: "Loop stage",
		description:
			"Declare only what the extension cannot observe in the anchorloop loop book. " +
			"`kind` (kind, intent, optional anchor command; call again to upgrade the kind or set the anchor): quick (act, check), inline (anchor, act, verify), reviewed (adds review), durable (adds decide, grill, spec, read, approve, design); every kind ends with reflect, close. " +
			"`verify` (note; only for an anchor that is not a command), `fresh-read` (a fresh-context read of the spec is done), `friction` (tried, found, led_by), `reflect` (friction ids, class misdirection|gap|resolved, action), " +
			"`skip` / `back` (phase, reason), `close` (verdict), `read` (view the book). Edits, anchor runs, reviews, and spec files are read from evidence. " +
			"A loop opens with the first `todo` create; `close` refuses while a pending or in-progress todo lacks metadata.followup.",
		parameters: {
			type: "object",
			properties: {
				stage: { type: "string", enum: [...STAGES] },
				kind: { type: "string", enum: [...KINDS], description: "stage kind: the loop kind; a second call upgrades it" },
				intent: { type: "string", description: "stage kind: one line on what the loop delivers" },
				anchor: { type: "string", description: "stage kind: the check command whose exit code observes the result" },
				note: { type: "string", description: "stage verify: what was observed; stage fresh-read: who read the spec" },
				result: { type: "string", enum: ["pass", "fail"], description: "stage verify; default pass" },
				tried: { type: "string", description: "stage friction: the attempt that failed" },
				found: { type: "string", description: "stage friction: what the failure revealed" },
				led_by: { type: "string", description: "stage friction: the skill or instruction line that prompted the attempt, or `none`" },
				friction: { type: "array", items: { type: ["string", "number"] }, description: "stage reflect: friction ids (`3`, or `worker#2` for a child's)" },
				class: { type: "string", enum: ["misdirection", "gap", "resolved"], description: "stage reflect" },
				action: { type: "string", description: "stage reflect: what was done, such as solid-loop, memory, or a commit" },
				phase: { type: "string", description: "stage skip or back: the phase" },
				reason: { type: "string", description: "stage skip or back: why" },
				verdict: { type: "string", enum: ["landed", "blocked", "abandoned"], description: "stage close" },
				view: { type: "string", enum: ["summary", "all"], description: "stage read; default summary" },
			},
			required: ["stage"],
			additionalProperties: false,
		},
		async execute(_toolCallId: string, raw: unknown, _signal: unknown, _onUpdate: unknown, ctx: ExtensionContext) {
			const params = raw as Params;
			const { stage } = params;
			if (!(STAGES as readonly string[]).includes(stage)) throw new Error(`unknown stage \`${String(stage)}\`; declare one of ${STAGES.join(", ")}`);
			let book = openLoop(ctx);
			if (!book && stage === "kind") {
				// A todo create in the same batch may not have landed yet; whichever comes first opens the loop.
				if (!params.kind || !params.intent) throw new Error("the first kind declaration needs `kind` and a one-line `intent`");
				book = createBook(ctx);
				recordPriorAnchor(book, ctx);
			}
			if (!book) return reply("No loop is open, so nothing was recorded. A loop opens with the first `todo` create or `kind`.");
			const had = currentKind(book.entries);
			const sequence = SEQUENCES[had ?? "inline"];
			if (stage === "read") {
				const lines = [...summaryLines(book, ctx), ...taskLines(book.entries, todosOf(ctx), ctx.cwd)];
				if (params.view === "all") lines.push("entries:", ...book.entries.map((entry) => JSON.stringify(entry).slice(0, 300)));
				return reply(lines.join("\n"));
			}
			if (stage === "close") {
				if (!params.verdict) throw new Error("close needs a verdict: landed, blocked, or abandoned");
				const closed = close(book, ctx, params.verdict);
				return { content: [{ type: "text" as const, text: closed.text }], details: closed.snapshot ? { snapshot: closed.snapshot } : undefined };
			}
			if (stage === "kind") {
				if (!params.kind && !params.intent && !params.anchor) throw new Error("kind needs `kind`, `intent`, or `anchor`");
				if (!had && (!params.kind || !params.intent)) throw new Error("the first kind declaration needs `kind` and a one-line `intent`");
				const notes: string[] = [];
				if (params.kind || params.intent) {
					appendEntry(book.path, "kind", { kind: params.kind ?? had, ...(params.intent ? { intent: params.intent } : {}) });
					notes.push(had && params.kind && had !== params.kind ? `kind changed: ${had} → ${params.kind}` : `kind: ${params.kind ?? had}`);
				}
				if (params.anchor) {
					appendEntry(book.path, "anchor", { check: params.anchor });
					notes.push(`anchor: ${params.anchor}`);
				}
				touchRepo(book, join(ctx.cwd, "_"));
				return reply(notes.join("\n"));
			}
			if (stage === "verify") {
				if (!params.note) throw new Error("verify needs a `note` saying what was observed");
				const result = params.result ?? "pass";
				const recorded = childId() !== undefined || had === "quick" ? "check" : "verify";
				appendEntry(book.path, recorded, { declared: true, note: params.note, result, exit: result === "pass" ? 0 : 1 });
				return reply(`${recorded} declared: ${result} — ${params.note}`);
			}
			if (stage === "fresh-read") {
				appendEntry(book.path, "goldfish", { source: "declared", ...(params.note ? { note: params.note } : {}) });
				return reply("fresh-read recorded.");
			}
			if (stage === "friction") {
				if (!params.tried || !params.found) throw new Error("friction needs `tried` and `found`");
				const id = frictionOf(book.entries).length + 1;
				appendEntry(book.path, "friction", { id, tried: params.tried, found: params.found, led_by: params.led_by || "none" });
				return reply(`friction #${id} recorded.`);
			}
			if (stage === "reflect") {
				const known = allFriction(book.entries).map((item) => item.ref);
				const ids = (params.friction ?? []).map(String);
				if (ids.length === 0 || !params.class) throw new Error(`reflect needs \`friction\` ids (${known.join(", ") || "none recorded"}) and \`class\``);
				const unknown = ids.filter((id) => !known.includes(id));
				if (unknown.length) throw new Error(`unknown friction ${unknown.join(", ")}; known: ${known.join(", ") || "none"}`);
				appendEntry(book.path, "reflect", { friction: ids, class: params.class, ...(params.action ? { action: params.action } : {}) });
				return reply(`reflect recorded for ${ids.join(", ")} (${params.class}).`);
			}
			// skip and back
			const phase = params.phase;
			const known = sequence.filter((name) => name !== "close");
			if (!phase || !known.includes(phase)) throw new Error(`${stage} needs \`phase\`, one of ${known.join(", ")} for a ${had ?? "undeclared"} loop`);
			if (!params.reason) throw new Error(`${stage} needs a \`reason\``);
			appendEntry(book.path, stage, { phase, reason: params.reason });
			return reply(stage === "skip" ? `${phase}: skipped (${params.reason}).` : `back to ${phase} (${params.reason}); later phases count as incomplete until their conditions hold again.`);
		},
	});

	pi.on(
		"session_start",
		guarded((_event, ctx) => {
			const swept = sweep(process.env, ctx.cwd);
			const lines = [
				...swept.deleted.map((path) => `deleted stale loop book: ${path}`),
				...swept.open.map((path) => `open loop book: ${path}`),
			];
			if (lines.length > 0) ctx.ui.notify(`anchorloop books\n${lines.join("\n")}`, "info");
		}),
	);

	pi.on(
		"tool_call",
		guarded((event, ctx) => {
			if (event.toolName !== "write" && event.toolName !== "edit") return;
			const path = (event.input as { path?: unknown }).path;
			const book = typeof path === "string" ? openLoop(ctx) : undefined;
			if (book && typeof path === "string") touchRepo(book, resolve(ctx.cwd, path));
		}),
	);

	/** Records what a finished bash call shows: runs of the loop anchor, of task anchors, and a first commit as the change. */
	function recordBash(book: Book, event: { input: unknown; isError?: boolean; structuredContent?: unknown; content?: unknown }): void {
		const structured = event.structuredContent as { output?: unknown } | undefined;
		const output = typeof structured?.output === "string" ? structured.output : textOf(event.content);
		const command = String((event.input as { command?: unknown }).command ?? "");
		const exit = bashExit(event);
		const last = lastLine(output);
		const anchor = anchorCommand(book.entries);
		if (anchor && command.includes(anchorSegment(anchor))) {
			const recorded = childId() !== undefined || currentKind(book.entries) === "quick" ? "check" : "verify";
			book.entries.push(appendEntry(book.path, recorded, { command: anchor.slice(0, 200), exit: anchorExit(command, anchor, exit), last }));
		}
		for (const task of latestTasks(book.entries)) {
			if (typeof task.anchor === "string" && command.includes(anchorSegment(task.anchor))) appendEntry(book.path, "taskrun", { id: task.id, exit: anchorExit(command, task.anchor, exit), last });
		}
		if (exit === 0 && /\bgit(\s+-C\s+\S+)?\s+(merge|cherry-pick|pull)(?=\s|$)(?![^|;&]*--(abort|quit)\b)/.test(command) && !/Already up to date/i.test(last ?? "") && book.entries.at(-1)?.stage !== "edit") {
			const named = /\bgit\s+-C\s+(\S+)/.exec(command)?.[1] ?? /\bcd\s+(\S+)/.exec(command)?.[1];
			touchRepoBeforeMerge(book, resolve(String(book.header.cwd ?? process.cwd()), named ?? "."));
			book.entries.push(appendEntry(book.path, "edit", { via: "merge" }));
		}
		if (exit === 0 && /\bgit\b[^|;&]*\bcommit\b/.test(command) && !book.entries.some((entry) => entry.stage === "edit")) {
			const cwd = String(book.header.cwd ?? "");
			if (diffAgainstBases(book.entries).paths.some((path) => !outsideWork(path, cwd))) appendEntry(book.path, "edit", { via: "commit" });
		}
	}

	pi.on(
		"tool_result",
		guarded((event, ctx) => {
			if (event.toolName === "bash") {
				const book = openLoop(ctx);
				if (book) recordBash(book, event);
				return;
			}
			if (event.isError) return;
			if (event.toolName === "todo") {
				const input = event.input as { action?: unknown; id?: unknown };
				let open = openLoop(ctx);
				const opens = !open && input.action === "create";
				if (!open && opens) {
					open = createBook(ctx);
					recordPriorAnchor(open, ctx);
				}
				if (!open) return;
				recordTasks(open, event.details, input, ctx.cwd);
				return opens ? { content: [...event.content, { type: "text" as const, text: OPEN_LINE }] } : undefined;
			}
			const book = openLoop(ctx);
			if (!book) return;
			if (event.toolName === "subagent") {
				const id = (event.details as { id?: unknown } | undefined)?.id;
				if (typeof id === "string") {
					const details = event.details as { name?: unknown; agent?: unknown };
					appendEntry(book.path, "link", { child: id, name: details.name, agent: details.agent });
				}
				return;
			}
			if (event.toolName !== "write" && event.toolName !== "edit") return;
			const path = (event.input as { path?: unknown }).path;
			if (typeof path !== "string") return;
			if (!artifactKind(path)) {
				if (!outsideWork(path, ctx.cwd) && book.entries.at(-1)?.stage !== "edit") appendEntry(book.path, "edit", { path });
				return;
			}
			let text: string;
			try {
				text = readFileSync(resolve(ctx.cwd, path), "utf-8");
			} catch {
				return;
			}
			const summary = summarizeArtifact(book.entries, path, text);
			if (summary) appendEntry(book.path, summary.stage, summary.fields);
		}),
	);

	async function recordReview(ctx: ExtensionContext, book: Book, name: string, text: string, failed: boolean): Promise<void> {
		const counts = parseBlocking(text);
		let blocking: boolean | null = null;
		let source = `reviewer ${name}`;
		if (failed || /\bStatus:?\*{0,2}\s*INCOMPLETE\b/i.test(text)) {
			source = "failed";
		} else if (!counts) {
			source = "jev";
			const { answers } = await classify(ctx, { review: text.slice(-3000) }, {
				blocking: {
					type: "bool",
					instructions: "Does `review` report any blocking finding, a P0 or P1 defect that must be fixed before the change is merged?",
					criteria: { true: "the review names at least one defect it says must be fixed before merge", false: "the review finds no blocking defect, or only lower-priority notes" },
				},
			});
			const probability = answers?.blocking?.type === "bool" ? answers.blocking.probability : undefined;
			blocking = probability === undefined ? null : probability >= 0.5;
		} else {
			blocking = counts.p0 + counts.p1 > 0;
		}
		const entry = appendEntry(book.path, "review", { round: reviews(book.entries).length + 1, ...(source === "failed" ? {} : (counts ?? {})), blocking, source });
		book.entries.push(entry);
		if (reviewsStalled(book.entries)) ctx.ui.notify("anchorloop: two consecutive review rounds still raised blocking findings; stop and hand the trend to the user.", "warning");
	}

	const HOST_LINE = /^\s*(Parent action:|Requested model|Session:|Resume:)/i;

/** The text without the lines pi-herdr adds around a subagent brief or result. */
function strip(text: string): string {
	return text
		.split("\n")
		.filter((line) => !HOST_LINE.test(line))
		.join("\n")
		.trim();
}

function headAndTail(text: string): string {
	return text.length <= 2500 ? text : `${text.slice(0, 1000)}\n…\n${text.slice(-1500)}`;
}

/** Jev judges whether a returned subagent was a fresh-context read of the spec; the spec path in its brief is only a pre-filter. */
	async function detectFreshRead(ctx: ExtensionContext, book: Book, details: { name?: unknown; task?: unknown; resultContent?: unknown }): Promise<void> {
		const phases = phasesOf(book, ctx);
		const read = phases.statuses.find((status) => status.name === "read");
		if (read?.state !== "missing" || !read.note.startsWith("a fresh-context")) return;
		const folder = specFolder(book.entries, todosOf(ctx), ctx.cwd);
		const brief = String(details.task ?? "");
		if (!folder || !(brief.includes(`${folder}/spec.md`) || brief.includes(resolve(ctx.cwd, folder, "spec.md")))) return;
		const { answers } = await classify(ctx, { brief: strip(brief).slice(0, 1500), result: headAndTail(strip(textOf(details.resultContent))) }, {
			fresh_read: {
				type: "bool",
				instructions: "Did this subagent read the spec and report on it: does its `result` restate the spec, or list gaps, guesses, or questions about it? The `brief` only needs to have handed it the spec.",
				criteria: { true: "the result restates the spec or lists gaps, guesses, or questions about it", false: "the subagent did other work and its result does not report on the spec" },
			},
		});
		const probability = answers?.fresh_read?.type === "bool" ? answers.fresh_read.probability : undefined;
		if (probability === undefined) return;
		appendEntry(book.path, "goldfish", { source: "jev", ok: probability >= 0.5, child: String(details.name ?? "") });
	}

	pi.on(
		"message_end",
		guarded(async (event, ctx) => {
			const message = event.message as { role?: string; content?: unknown; customType?: string; details?: { agent?: unknown; name?: unknown; task?: unknown; resultContent?: unknown; error?: unknown; errorMessage?: unknown; exitCode?: unknown } };
			const book = openLoop(ctx);
			if (!book) return;
			const stated = statedAnchor(message);
			if (stated && !book.entries.some((entry) => entry.stage === "anchor" && entry.check === stated)) appendEntry(book.path, "anchor", { check: stated, line: true });
			if (message.role !== "custom" || message.customType !== "subagent_result" || subagent) return;
			const agent = String(message.details?.agent ?? "");
			if (REVIEWERS.has(agent)) {
				const d = message.details ?? {};
				const failed = Boolean(d.error) || Boolean(d.errorMessage) || (typeof d.exitCode === "number" && d.exitCode !== 0);
				await recordReview(ctx, book, String(d.name ?? agent), textOf(d.resultContent), failed);
			}
			else await detectFreshRead(ctx, book, message.details ?? {});
		}),
	);
}
