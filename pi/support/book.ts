/**
 * The loop book: one YAML file per open loop, kept under the agent dir.
 * A header is written once; every later fact is one JSON flow-mapping line under `entries:`, appended
 * with a single O_APPEND write, so parallel writers never interleave and the file stays valid YAML.
 * Each extension reads the book from disk, so no state is shared between extensions in memory.
 */

import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { closeSync, existsSync, mkdirSync, openSync, readdirSync, readFileSync, realpathSync, statSync, unlinkSync, writeSync } from "node:fs";
import { homedir } from "node:os";
import { basename, dirname, join, resolve } from "node:path";

export const KINDS = ["quick", "inline", "reviewed", "durable"] as const;
export type Kind = (typeof KINDS)[number];

export type Entry = { ts: string; stage: string; [key: string]: unknown };
export type Book = { path: string; header: Record<string, unknown>; entries: Entry[] };

/** What the book needs to know about the calling session. */
export type Who = {
	cwd: string;
	sessionManager: { getSessionId?(): string; getSessionFile?(): string | undefined; getBranch(): unknown[] };
};

const STALE_UNSAVED_MS = 24 * 60 * 60 * 1000;

export function booksRoot(env: NodeJS.ProcessEnv = process.env): string {
	if (env.ANCHORLOOP_BOOKS_DIR) return env.ANCHORLOOP_BOOKS_DIR;
	return join(env.PI_CODING_AGENT_DIR || join(homedir(), ".pi", "agent"), "anchorloop", "books");
}

function real(path: string): string {
	try {
		return realpathSync(path);
	} catch {
		return resolve(path);
	}
}

export function projectSlug(cwd: string): string {
	return real(cwd).replace(/[^A-Za-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(-80) || "root";
}

export function childId(env: NodeJS.ProcessEnv = process.env): string | undefined {
	return env.PI_SUBAGENT_ID || undefined;
}

function safe(id: string): string {
	return id.replace(/[^A-Za-z0-9._-]/g, "_");
}

export function bookPath(who: Who, env: NodeJS.ProcessEnv = process.env): string {
	const dir = join(booksRoot(env), projectSlug(who.cwd));
	const child = childId(env);
	if (child) return join(dir, "agents", `${safe(child)}.yml`);
	return join(dir, `${safe(who.sessionManager.getSessionId?.() || `pid-${process.pid}`)}.yml`);
}

export function parseBook(path: string): Book | undefined {
	let text: string;
	try {
		text = readFileSync(path, "utf-8");
	} catch {
		return undefined;
	}
	const header: Record<string, unknown> = {};
	const entries: Entry[] = [];
	let inEntries = false;
	for (const line of text.split("\n")) {
		if (!line || line.startsWith("#")) continue;
		if (line === "entries:") {
			inEntries = true;
		} else if (inEntries) {
			if (!line.startsWith("- ")) continue;
			try {
				entries.push(JSON.parse(line.slice(2)) as Entry);
			} catch {
				// A line that is not an entry is skipped; the book stays readable.
			}
		} else {
			const split = line.indexOf(": ");
			if (split < 0) continue;
			try {
				header[line.slice(0, split)] = JSON.parse(line.slice(split + 2));
			} catch {
				// A header line that is not JSON is skipped.
			}
		}
	}
	return { path, header, entries };
}

export function openBook(who: Who, env: NodeJS.ProcessEnv = process.env): Book | undefined {
	return parseBook(bookPath(who, env));
}

function appendBytes(path: string, text: string): void {
	const fd = openSync(path, "a");
	try {
		const bytes = Buffer.from(text);
		const written = writeSync(fd, bytes);
		if (written !== bytes.length) throw new Error(`short write: ${written} of ${bytes.length} bytes`);
	} finally {
		closeSync(fd);
	}
}

export function createBook(who: Who, env: NodeJS.ProcessEnv = process.env): Book {
	const path = bookPath(who, env);
	mkdirSync(dirname(path), { recursive: true });
	const child = childId(env);
	const header = {
		id: basename(path, ".yml"),
		owner: child ? env.PI_SUBAGENT_NAME || child : "main",
		session: (child ? env.PI_SUBAGENT_SESSION : undefined) || who.sessionManager.getSessionFile?.() || null,
		cwd: real(who.cwd),
		opened: new Date().toISOString(),
	};
	const lines = ["# anchorloop loop book", ...Object.entries(header).map(([key, value]) => `${key}: ${JSON.stringify(value)}`), "entries:", ""];
	appendBytes(path, lines.join("\n"));
	return { path, header, entries: [] };
}

export function appendEntry(path: string, stage: string, fields: Record<string, unknown> = {}): Entry {
	const entry: Entry = { ts: new Date().toISOString(), stage, ...fields };
	appendBytes(path, `- ${JSON.stringify(entry)}\n`);
	return entry;
}

/** The book of the child `id` among all projects, or undefined. */
export function findChildBook(id: string, env: NodeJS.ProcessEnv = process.env): Book | undefined {
	const root = booksRoot(env);
	if (!existsSync(root)) return undefined;
	for (const project of readdirSync(root)) {
		const book = parseBook(join(root, project, "agents", `${safe(id)}.yml`));
		if (book) return book;
	}
	return undefined;
}

export function deleteBook(path: string): void {
	try {
		unlinkSync(path);
	} catch {
		// Already gone.
	}
}

export type Sweep = { deleted: string[]; open: string[] };

/** Deletes books whose owner session file is gone and child books no open book links; lists the rest. */
export function sweep(env: NodeJS.ProcessEnv = process.env): Sweep {
	const root = booksRoot(env);
	const result: Sweep = { deleted: [], open: [] };
	if (!existsSync(root)) return result;
	const linked = new Set<string>();
	const children: Book[] = [];
	for (const project of readdirSync(root)) {
		const dir = join(root, project);
		if (!statSync(dir).isDirectory()) continue;
		for (const file of readdirSync(dir)) {
			if (file.endsWith(".yml")) {
				const book = parseBook(join(dir, file));
				if (!book) continue;
				const session = book.header.session;
				const stale = typeof session === "string" ? !existsSync(session) : Date.now() - statSync(book.path).mtimeMs > STALE_UNSAVED_MS;
				if (stale) {
					deleteBook(book.path);
					result.deleted.push(book.path);
				} else {
					result.open.push(`${book.path} (${currentKind(book.entries) ?? "no kind"}: ${currentIntent(book.entries) ?? "no intent"})`);
					for (const entry of book.entries) if (entry.stage === "link" && typeof entry.child === "string") linked.add(safe(entry.child));
				}
			}
		}
		const agents = join(dir, "agents");
		if (existsSync(agents)) {
			for (const file of readdirSync(agents)) if (file.endsWith(".yml")) children.push({ path: join(agents, file), header: {}, entries: [] });
		}
	}
	for (const child of children) {
		if (linked.has(basename(child.path, ".yml"))) continue;
		deleteBook(child.path);
		result.deleted.push(child.path);
	}
	return result;
}

// --- derived state -------------------------------------------------------------------------------

export function currentKind(entries: Entry[]): Kind | undefined {
	const found = [...entries].reverse().find((entry) => entry.stage === "kind" && typeof entry.kind === "string");
	return found?.kind as Kind | undefined;
}

export function currentIntent(entries: Entry[]): string | undefined {
	const found = [...entries].reverse().find((entry) => entry.stage === "kind" && typeof entry.intent === "string");
	return found?.intent as string | undefined;
}

export function stagesDone(entries: Entry[]): string[] {
	const seen: string[] = [];
	for (const entry of entries) {
		if (["base", "link", "close", "task", "taskrun"].includes(entry.stage) || entry.stage === "verification") continue;
		if (!seen.includes(entry.stage)) seen.push(entry.stage);
	}
	return seen;
}

export function lastIndex(entries: Entry[], ...stages: string[]): number {
	for (let i = entries.length - 1; i >= 0; i--) if (stages.includes(entries[i].stage)) return i;
	return -1;
}

export function hasAnchor(entries: Entry[]): boolean {
	return entries.some((entry) => entry.stage === "anchor");
}

export function reviews(entries: Entry[]): Entry[] {
	return entries.filter((entry) => entry.stage === "review");
}

export function isBlocking(entry: Entry): boolean {
	return entry.blocking === true;
}

/** True when the two latest review rounds both still had blocking findings. */
export function reviewsStalled(entries: Entry[]): boolean {
	const rounds = reviews(entries);
	return rounds.length >= 2 && isBlocking(rounds[rounds.length - 1]) && isBlocking(rounds[rounds.length - 2]);
}

export function reviewTrend(entries: Entry[]): string {
	const rounds = reviews(entries);
	if (rounds.length === 0) return "no review";
	return `${rounds.length} round(s): ${rounds.map((round) => (round.blocking === true ? `blocking${round.p0 !== undefined ? ` P0=${round.p0} P1=${round.p1}` : ""}` : round.blocking === false ? "clear" : "unknown")).join(" → ")}`;
}

/** A review recorded after the last act with no blocking finding on it. */
export function reviewClearAfterLastAct(entries: Entry[]): boolean {
	const review = lastIndex(entries, "review");
	return review >= 0 && review > lastIndex(entries, "act") && entries[review].blocking === false;
}

export function latestAnchor(entries: Entry[]): string | undefined {
	const found = [...entries].reverse().find((entry) => entry.stage === "anchor" && typeof entry.check === "string");
	return found?.check as string | undefined;
}

function evidenceLine(entry: Entry): string {
	return `${entry.stage} ${entry.skip ? `skipped (${entry.skip})` : `exit ${entry.exit ?? "unknown"}${entry.last ? `: ${entry.last}` : ""}`}`;
}

/** The latest check or verify entry after the last act, or undefined when none follows it. */
export function verifyAfterLastAct(entries: Entry[]): Entry | undefined {
	const index = lastIndex(entries, "check", "verify");
	return index >= 0 && index > lastIndex(entries, "act") ? entries[index] : undefined;
}

export function childIds(entries: Entry[]): string[] {
	return entries.filter((entry) => entry.stage === "link" && typeof entry.child === "string").map((entry) => entry.child as string);
}

/** One line per linked child book that exists. */
export function childLines(entries: Entry[], env: NodeJS.ProcessEnv = process.env): string[] {
	const lines: string[] = [];
	for (const id of childIds(entries)) {
		const link = entries.find((entry) => entry.stage === "link" && entry.child === id);
		const child = findChildBook(id, env);
		if (!child) continue;
		const lastCheck = [...child.entries].reverse().find((entry) => entry.stage === "check");
		lines.push(`${link?.name ?? id}: ${currentKind(child.entries) ?? "no kind"}; stages ${stagesDone(child.entries).join(", ") || "none"}; ${lastCheck ? evidenceLine(lastCheck) : "no check"}`);
	}
	return lines;
}

// --- todos ---------------------------------------------------------------------------------------

export type Task = { id: number; subject: string; status: string; metadata?: Record<string, unknown> };

const TASK_STATUSES = new Set(["pending", "in_progress", "completed", "deleted"]);

export function taskDetails(value: unknown): Task[] | undefined {
	if (!value || typeof value !== "object") return undefined;
	const tasks = (value as { tasks?: unknown }).tasks;
	if (!Array.isArray(tasks)) return undefined;
	const valid = tasks.every((task) => task && typeof task.subject === "string" && TASK_STATUSES.has(task.status));
	return valid ? (tasks as Task[]) : undefined;
}

/** The todo list as of the latest `rpiv-todo-state` entry, else the latest `todo` tool result, on the branch. */
export function replayTodos(branch: unknown[]): Task[] {
	let fromEntries: Task[] | undefined;
	let fromResults: Task[] | undefined;
	for (const raw of branch) {
		const entry = raw as { type?: string; customType?: string; data?: unknown; message?: { role?: string; toolName?: string; details?: unknown } };
		if (entry.type === "custom") {
			if (entry.customType === "rpiv-todo-state") fromEntries = taskDetails(entry.data) ?? fromEntries;
		} else if (entry.type === "message" && entry.message?.role === "toolResult" && entry.message.toolName === "todo") {
			fromResults = taskDetails(entry.message.details) ?? fromResults;
		}
	}
	return (fromEntries ?? fromResults ?? []).filter((task) => task.status !== "deleted");
}

export const isOpenTask = (task: Task): boolean => task.status === "pending" || task.status === "in_progress";

const TICKET = /^(#\d+|[A-Za-z][A-Za-z0-9]*-\d+)$/;

/** True when `followup` is a ticket id, `memory`, or `drop — <reason>`. */
export function validFollowup(followup: unknown): boolean {
	if (typeof followup !== "string") return false;
	const value = followup.trim();
	return TICKET.test(value) || value === "memory" || /^drop\s*[—–-]\s*\S/.test(value);
}

// --- git -----------------------------------------------------------------------------------------

function git(cwd: string, args: string[]): string | undefined {
	try {
		return execFileSync("git", ["-C", cwd, ...args], { encoding: "utf-8", timeout: 5000, stdio: ["ignore", "pipe", "ignore"] }).trim();
	} catch {
		return undefined;
	}
}

function existingDir(path: string): string {
	let dir = path;
	while (!existsSync(dir) && dirname(dir) !== dir) dir = dirname(dir);
	return dir;
}

/** The repo root and HEAD that contain `path`, or undefined outside a repo or before its first commit. */
export function repoOf(path: string): { repo: string; head: string } | undefined {
	const dir = existingDir(dirname(resolve(path)));
	const repo = git(dir, ["rev-parse", "--show-toplevel"]);
	const head = repo ? git(repo, ["rev-parse", "HEAD"]) : undefined;
	return repo && head ? { repo: real(repo), head } : undefined;
}

export function bases(entries: Entry[]): { repo: string; head: string }[] {
	return entries.filter((entry) => entry.stage === "base").map((entry) => ({ repo: String(entry.repo), head: String(entry.head) }));
}

/** Adds the repo of `path` to the book with its HEAD when the book has no base for it yet. */
export function touchRepo(book: Book, path: string): boolean {
	const found = repoOf(path);
	if (!found) return false;
	if (bases(book.entries).some((base) => base.repo === found.repo)) return false;
	const entry = appendEntry(book.path, "base", found);
	book.entries.push(entry);
	return true;
}

export type Diff = { summary: string; files: string[] };

/** The diff of each base's repo against its recorded HEAD, as one summary line per repo and the changed files. */
export function diffAgainstBases(entries: Entry[]): Diff {
	const lines: string[] = [];
	const files: string[] = [];
	for (const { repo, head } of bases(entries)) {
		const stat = git(repo, ["diff", "--shortstat", head]);
		const names = git(repo, ["diff", "--name-only", head])?.split("\n").filter(Boolean) ?? [];
		const untracked = git(repo, ["ls-files", "--others", "--exclude-standard"])?.split("\n").filter(Boolean) ?? [];
		if (stat === undefined) {
			lines.push(`${basename(repo)}: diff unavailable`);
			continue;
		}
		lines.push(`${basename(repo)}: ${stat || "no tracked changes"}${untracked.length ? `; ${untracked.length} untracked` : ""}`);
		files.push(...names.map((name) => `${basename(repo)}/${name}`), ...untracked.map((name) => `${basename(repo)}/${name}`));
	}
	return { summary: lines.join("\n") || "no repository", files };
}

export function diffText(diff: Diff, limit = 1200): string {
	const shown = diff.files.slice(0, 30).join(", ");
	return `${diff.summary}${shown ? `\nfiles: ${shown}${diff.files.length > 30 ? ", …" : ""}` : ""}`.slice(0, limit);
}

// --- durable artifacts ---------------------------------------------------------------------------

const ARTIFACT = /(?:^|\/)docs\/specs\/[^/]+\/(decision|spec|design|verification)\.md$/;

export function artifactKind(path: string): "decision" | "spec" | "design" | "verification" | undefined {
	return ARTIFACT.exec(path.replace(/\\/g, "/"))?.[1] as "decision" | "spec" | "design" | "verification" | undefined;
}

const hash = (text: string): string => createHash("sha1").update(text).digest("hex").slice(0, 8);

function sections(text: string): Record<string, string> {
	const found: Record<string, string> = {};
	let heading: string | undefined;
	let body: string[] = [];
	const flush = () => {
		if (heading === undefined) return;
		let key = heading;
		for (let n = 2; key in found; n++) key = `${heading} #${n}`;
		found[key] = hash(body.join("\n").trim());
	};
	for (const line of text.split("\n")) {
		const match = /^#{1,6}\s+(.*\S)\s*$/.exec(line);
		if (match) {
			flush();
			heading = match[1];
			body = [];
		} else {
			body.push(line);
		}
	}
	flush();
	return found;
}

function tableRows(text: string): string[][] {
	return text
		.split("\n")
		.filter((line) => /^\s*\|.*\|\s*$/.test(line))
		.map((line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map((cell) => cell.trim()))
		.filter((cells) => cells.length >= 2 && !cells.every((cell) => /^:?-{2,}:?$/.test(cell)));
}

function previous(entries: Entry[], stage: string, path: string): Entry | undefined {
	return [...entries].reverse().find((entry) => entry.stage === stage && entry.auto === true && entry.path === path);
}

/** The entry fields summarising `text` of an artifact, compared with the book's last entry for the same file. */
export function summarizeArtifact(entries: Entry[], path: string, text: string): { stage: string; fields: Record<string, unknown> } | undefined {
	const kind = artifactKind(path);
	if (!kind) return undefined;
	const before = previous(entries, kind, path);
	const fields: Record<string, unknown> = { auto: true, path };
	if (kind === "decision") {
		const rows = tableRows(text).filter((cells) => ["grounded", "confirmed", "open"].includes(cells[cells.length - 1].toLowerCase()));
		const state: Record<string, string> = {};
		const questions: Record<string, string> = {};
		const counts: Record<string, number> = { grounded: 0, confirmed: 0, open: 0 };
		for (const cells of rows) {
			const status = cells[cells.length - 1].toLowerCase();
			counts[status]++;
			state[hash(cells[0])] = status;
			questions[hash(cells[0])] = cells[0];
		}
		const old = (before?.rowState ?? {}) as Record<string, string>;
		fields.counts = counts;
		fields.changed = Object.keys(state).filter((key) => old[key] !== state[key]).map((key) => questions[key]);
		fields.rowState = state;
		return { stage: kind, fields };
	}
	const now = sections(text);
	const old = (before?.sections ?? {}) as Record<string, string>;
	fields.sections = now;
	fields.changed = Object.keys(now).filter((heading) => old[heading] !== now[heading]);
	if (before) fields.removed = Object.keys(old).filter((heading) => !(heading in now));
	if (kind === "spec") fields.status = /^\s*Status:\s*(\S+)/m.exec(text)?.[1] ?? null;
	if (kind === "verification") {
		const counts: Record<string, number> = { pass: 0, fail: 0, unknown: 0 };
		for (const cells of tableRows(text)) {
			const result = cells[cells.length - 1].toLowerCase();
			if (result in counts) counts[result]++;
		}
		fields.counts = counts;
	}
	return { stage: kind, fields };
}

/** The `Status:` value of the latest spec the book recorded, or undefined when none is recorded or readable. */
export function specStatus(entries: Entry[], cwd: string): string | undefined {
	const spec = [...entries].reverse().find((entry) => entry.stage === "spec" && typeof entry.path === "string");
	if (!spec) return undefined;
	try {
		return /^\s*Status:\s*(\S+)/m.exec(readFileSync(resolve(cwd, spec.path as string), "utf-8"))?.[1];
	} catch {
		return undefined;
	}
}

// --- todo links ----------------------------------------------------------------------------------

/** The `ref` metadata of a task as a list of `<path>#<heading>` pointers. */
export function refsOf(metadata: Record<string, unknown> | undefined): string[] {
	const ref = metadata?.ref;
	const list = Array.isArray(ref) ? ref : [ref];
	return list.filter((item): item is string => typeof item === "string" && item.includes("#"));
}

/** The line range of the section `<path>#<heading>` names, such as `L88-L101`, or `missing` when the file or heading is gone. */
export function resolveRef(ref: string, cwd: string, entries: Entry[]): string {
	const split = ref.indexOf("#");
	const path = ref.slice(0, split);
	const heading = ref.slice(split + 1).trim();
	const dirs = [cwd, ...new Set(entries.filter((entry) => typeof entry.path === "string").map((entry) => dirname(resolve(cwd, entry.path as string))))];
	for (const dir of dirs) {
		let lines: string[];
		try {
			lines = readFileSync(resolve(dir, path), "utf-8").split("\n");
		} catch {
			continue;
		}
		const found = lines.map((line) => /^(#{1,6})\s+(.*\S)\s*$/.exec(line));
		let start = found.findIndex((match) => match?.[2] === heading);
		if (start < 0) start = found.findIndex((match) => match?.[2].toLowerCase() === heading.toLowerCase());
		if (start < 0) continue;
		const depth = found[start]?.[1].length ?? 1;
		let end = lines.length;
		for (let i = start + 1; i < lines.length; i++) {
			const match = found[i];
			if (match && match[1].length <= depth) {
				end = i;
				break;
			}
		}
		while (end > start + 1 && !lines[end - 1].trim()) end--;
		return `L${start + 1}-L${end}`;
	}
	return "missing";
}

/** The latest `task` entry of each task id, in id order. */
export function latestTasks(entries: Entry[]): Entry[] {
	const byId = new Map<number, Entry>();
	for (const entry of entries) if (entry.stage === "task" && typeof entry.id === "number") byId.set(entry.id, entry);
	return [...byId.values()].sort((a, b) => (a.id as number) - (b.id as number));
}

export const TASK_LEGEND = "#id status subject — anchor (last exit) — ref → line range; missing = heading gone";

/** One line per live task: its own anchor with the last exit code of a matching bash call, and its refs with current line ranges. */
export function taskLines(entries: Entry[], todos: Task[], cwd: string): string[] {
	const live = new Map(todos.map((task) => [task.id, task]));
	const exits = new Map<number, Entry>();
	for (const entry of entries) if (entry.stage === "taskrun" && typeof entry.id === "number") exits.set(entry.id, entry);
	return latestTasks(entries)
		.filter((entry) => live.has(entry.id as number))
		.map((entry) => {
			const task = live.get(entry.id as number);
			const run = exits.get(entry.id as number);
			const anchor = typeof entry.anchor === "string" ? `${entry.anchor}${run ? ` (exit ${run.exit})` : ""}` : "loop anchor";
			const refs = ((entry.refs ?? []) as { ref: string }[]).map((item) => `${item.ref} → ${resolveRef(item.ref, cwd, entries)}`);
			return [`#${entry.id} ${task?.status} ${task?.subject}`, anchor, ...(refs.length ? [refs.join(", ")] : [])].join(" — ");
		});
}
