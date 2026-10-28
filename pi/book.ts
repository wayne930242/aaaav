/**
 * pi extension: the loop book. The first `todo` create opens a loop and its book; the agent declares
 * where the loop stands with the `anchorloop_stage` tool, and the extension attaches evidence (diff
 * stats, bash exit codes, review counts, durable artifact summaries) and keeps one YAML book per open
 * loop. Missing stages warn; only `close` refuses, while a todo is neither done nor disposed of.
 */

import { readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";
import {
	type Book,
	KINDS,
	appendEntry,
	artifactKind,
	childIds,
	childLines,
	createBook,
	currentIntent,
	currentKind,
	deleteBook,
	diffAgainstBases,
	findChildBook,
	isOpenTask,
	latestTasks,
	latestAnchor,
	openBook,
	replayTodos,
	refsOf,
	resolveRef,
	reviewTrend,
	reviews,
	reviewsStalled,
	stagesDone,
	summarizeArtifact,
	taskLines,
	taskDetails,
	sweep,
	touchRepo,
	validFollowup,
	verifyAfterLastAct,
} from "./support/book.ts";
import { classify } from "./support/jev.ts";
import { isSubagent } from "./support/subagent.ts";

export const SESSION_ENTRY = "anchorloop-loop";
const STAGES = ["kind", "anchor", "act", "check", "verify", "review", "decision", "spec", "design", "close", "read"] as const;
const REVIEWERS = new Set(["reviewer", "adversarial-reviewer"]);
const BASH_MEMORY = 50;
const BLOCKING = /Blocking\s*:?\**\s*:?\s*P0\s*=\s*(\d+)\D{0,5}P1\s*=\s*(\d+)/gi;

export const OPEN_LINE =
	"anchorloop: a loop is open. Declare its kind with `anchorloop_stage` {stage: kind, kind: quick|inline|reviewed|durable, intent: <one line>}.";

type Params = {
	stage: (typeof STAGES)[number];
	kind?: (typeof KINDS)[number];
	intent?: string;
	check?: string;
	note?: string;
	skip?: string;
	verdict?: "landed" | "blocked" | "abandoned";
	view?: "summary" | "all";
};

type BashResult = { command: string; exit: number | null; last: string };
type ReviewResult = { name: string; agent: string; text: string };

/** The P0 and P1 counts of the last `Blocking: P0=<n> P1=<m>` line in a reviewer report, tolerant of markdown emphasis. */
export function parseBlocking(text: string): { p0: number; p1: number } | undefined {
	const found = [...text.matchAll(BLOCKING)].at(-1);
	return found ? { p0: Number(found[1]), p1: Number(found[2]) } : undefined;
}

function textOf(content: unknown): string {
	if (typeof content === "string") return content;
	if (!Array.isArray(content)) return "";
	return content.map((block) => (block && typeof block === "object" && (block as { text?: unknown }).text) || "").filter((part) => typeof part === "string").join("\n");
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

const reply = (text: string) => ({ content: [{ type: "text" as const, text }], details: undefined });

export default function (pi: ExtensionAPI) {
	const subagent = isSubagent();
	const bash: BashResult[] = [];
	let latestReview: ReviewResult | undefined;

	function evidence(book: Book, override?: string): { command?: string; exit: number | "unknown"; last?: string } {
		const anchor = override ?? latestAnchor(book.entries);
		const ran = anchor ? [...bash].reverse().find((result) => result.command.includes(anchor)) : undefined;
		if (!ran || ran.exit === null) return { command: anchor, exit: "unknown" };
		return { command: anchor, exit: ran.exit, last: ran.last };
	}

	async function blocking(ctx: ExtensionContext, note: string | undefined): Promise<{ p0?: number; p1?: number; blocking: boolean | null; source: string }> {
		const result = latestReview;
		const counts = result ? parseBlocking(result.text) : undefined;
		if (counts) return { ...counts, blocking: counts.p0 + counts.p1 > 0, source: `reviewer ${result?.name}` };
		const text = result?.text ?? note;
		if (!text) return { blocking: null, source: "none" };
		const { answers } = await classify(ctx, { review: text.slice(-3000) }, {
			blocking: {
				type: "bool",
				instructions: "Does `review` report any blocking finding, a P0 or P1 defect that must be fixed before the change is merged?",
				criteria: { true: "the review names at least one defect it says must be fixed before merge", false: "the review finds no blocking defect, or only lower-priority notes" },
			},
		});
		const probability = answers?.blocking?.type === "bool" ? answers.blocking.probability : undefined;
		return { blocking: probability === undefined ? null : probability >= 0.5, source: "jev" };
	}

	function summaryLines(book: Book, ctx: ExtensionContext): string[] {
		const kind = currentKind(book.entries);
		const verify = [...book.entries].reverse().find((entry) => entry.stage === "verify" || entry.stage === "check");
		const open = replayTodos(ctx.sessionManager.getBranch()).filter(isOpenTask).length;
		return [
			`kind: ${kind ?? "not declared"}${currentIntent(book.entries) ? ` — ${currentIntent(book.entries)}` : ""}`,
			`stages: ${stagesDone(book.entries).join(", ") || "none"}`,
			`last ${verify?.stage ?? "verify"}: ${verify ? `exit ${verify.exit ?? "unknown"}${verify.last ? ` — ${verify.last}` : ""}${verifyAfterLastAct(book.entries) ? "" : " (before the last change)"}` : "none"}`,
			`reviews: ${reviewTrend(book.entries)}; open todos: ${open}`,
			...childLines(book.entries).map((line) => `child ${line}`),
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

	function close(book: Book, ctx: ExtensionContext, verdict: string) {
		const todos = replayTodos(ctx.sessionManager.getBranch());
		const undisposed = todos.filter((task) => isOpenTask(task) && !validFollowup(task.metadata?.followup));
		if (undisposed.length > 0) {
			throw new Error(
				`Cannot close: ${undisposed.length} todo(s) are pending or in progress without metadata.followup (a ticket id, \`memory\`, or \`drop — <reason>\`):\n` +
					undisposed.map((task) => `- #${task.id} ${task.subject}`).join("\n"),
			);
		}
		const diff = diffAgainstBases(book.entries);
		const followups = todos.filter((task) => isOpenTask(task)).map((task) => ({ task: task.subject, followup: task.metadata?.followup }));
		const summary = {
			intent: currentIntent(book.entries) ?? null,
			kind: currentKind(book.entries) ?? null,
			verdict,
			stages: stagesDone(book.entries),
			reviewRounds: reviews(book.entries).length,
			reviewTrend: reviewTrend(book.entries),
			diff: diff.summary,
			followups,
		};
		pi.appendEntry(SESSION_ENTRY, summary);
		for (const id of childIds(book.entries)) {
			const child = findChildBook(id);
			if (child) deleteBook(child.path);
		}
		deleteBook(book.path);
		return `Loop closed (${verdict}): ${summary.stages.join(", ")}; ${summary.reviewTrend}; diff ${diff.summary}. The book is deleted. Clear the todo list now (todo action: clear).`;
	}

	pi.registerTool({
		name: "anchorloop_stage",
		label: "Loop stage",
		description:
			"Declare where the anchorloop loop stands; the extension attaches evidence and keeps the loop book. " +
			"`kind` (kind + intent) first: quick (act, check, close), inline (anchor, act, verify, close), reviewed (adds review rounds), durable (adds decision, spec, design). " +
			"`anchor` (check: the command or review), `act`, `check`/`verify`, `review`, `decision`/`spec`/`design`, `close` (verdict), `read` (view). Any stage accepts `skip: <reason>`. " +
			"A loop opens with the first `todo` create; `close` refuses while a pending or in-progress todo lacks metadata.followup.",
		parameters: {
			type: "object",
			properties: {
				stage: { type: "string", enum: [...STAGES] },
				kind: { type: "string", enum: [...KINDS], description: "stage kind: the loop kind; a second call upgrades it" },
				intent: { type: "string", description: "stage kind: one line on what the loop delivers" },
				check: { type: "string", description: "stage anchor: the command or review that observes the result; on check/verify, the command to find evidence for" },
				note: { type: "string", description: "Optional note" },
				skip: { type: "string", description: "Skip this stage and say why" },
				verdict: { type: "string", enum: ["landed", "blocked", "abandoned"], description: "stage close" },
				view: { type: "string", enum: ["summary", "all"], description: "stage read; default summary" },
			},
			required: ["stage"],
			additionalProperties: false,
		},
		async execute(_toolCallId: string, params: Params, _signal: unknown, _onUpdate: unknown, ctx: ExtensionContext) {
			const book = openBook(ctx);
			if (!book) return reply("No loop is open, so nothing was recorded. A loop opens with the first `todo` create.");
			const { stage } = params;
			if (stage === "read") {
				const lines = [...summaryLines(book, ctx), ...taskLines(book.entries, replayTodos(ctx.sessionManager.getBranch()), ctx.cwd)];
				if (params.view === "all") lines.push("entries:", ...book.entries.map((entry) => JSON.stringify(entry).slice(0, 300)));
				return reply(lines.join("\n"));
			}
			if (stage === "close") {
				if (!params.verdict) throw new Error("close needs a verdict: landed, blocked, or abandoned");
				return reply(close(book, ctx, params.verdict));
			}
			if (params.skip) {
				appendEntry(book.path, stage, { skip: params.skip });
				return reply(`${stage}: skipped (${params.skip}).`);
			}
			const notes: string[] = [];
			const fields: Record<string, unknown> = params.note ? { note: params.note } : {};
			let recorded = stage as string;
			if (stage === "kind") {
				const had = currentKind(book.entries);
				if (!params.kind) throw new Error("kind needs `kind`");
				if (!had && !params.intent) throw new Error("the first kind declaration needs a one-line `intent`");
				appendEntry(book.path, "kind", { kind: params.kind, ...(params.intent ? { intent: params.intent } : {}) });
				touchRepo(book, join(ctx.cwd, "_"));
				notes.push(had && had !== params.kind ? `kind changed: ${had} → ${params.kind}` : `kind: ${params.kind}`);
				return reply(notes.join("\n"));
			}
			if (stage === "anchor") {
				if (!params.check) throw new Error("anchor needs `check`: the command or review that observes the result");
				fields.check = params.check;
				notes.push(`anchor: ${params.check}`);
			} else if (stage === "act") {
				const diff = diffAgainstBases(book.entries);
				fields.diff = diff.summary;
				fields.files = diff.files.length;
				notes.push(`diff: ${diff.summary}`);
			} else if (stage === "check" || stage === "verify") {
				if (subagent) recorded = "check";
				const found = evidence(book, params.check);
				Object.assign(fields, found.command ? { command: found.command.slice(0, 200) } : {}, { exit: found.exit, ...(found.last ? { last: found.last } : {}) });
				notes.push(`${recorded}: exit ${found.exit}${found.last ? ` — ${found.last}` : ""}${found.exit === "unknown" ? " (no bash call ran the anchor command)" : ""}`);
			} else if (stage === "review") {
				if (subagent) return reply("review is recorded by the main session only; nothing was recorded.");
				const result = await blocking(ctx, params.note);
				fields.round = reviews(book.entries).length + 1;
				Object.assign(fields, result.p0 === undefined ? {} : { p0: result.p0, p1: result.p1 }, { blocking: result.blocking, source: result.source });
				notes.push(`review round ${fields.round}: ${result.p0 === undefined ? `blocking ${result.blocking === null ? "unknown" : result.blocking ? "yes" : "no"} (${result.source})` : `P0=${result.p0} P1=${result.p1}`}`);
			}
			const entry = appendEntry(book.path, recorded, fields);
			book.entries.push(entry);
			if (stage === "review" && reviewsStalled(book.entries)) {
				notes.push("Two consecutive review rounds still raised blocking findings: stop and hand the trend to the user.");
			}
			return reply(notes.join("\n") || `${recorded} recorded.`);
		},
	});

	pi.on("session_start", (_event, ctx) => {
		const swept = sweep();
		const lines = [
			...swept.deleted.map((path) => `deleted stale loop book: ${path}`),
			...swept.open.map((path) => `open loop book: ${path}`),
		];
		if (lines.length > 0) ctx.ui.notify(`anchorloop books\n${lines.join("\n")}`, "info");
	});

	pi.on("tool_call", (event, ctx) => {
		if (event.toolName !== "write" && event.toolName !== "edit") return;
		const path = (event.input as { path?: unknown }).path;
		const book = typeof path === "string" ? openBook(ctx) : undefined;
		if (book && typeof path === "string") touchRepo(book, resolve(ctx.cwd, path));
	});

	pi.on("tool_result", (event, ctx) => {
		if (event.toolName === "bash") {
			const structured = event.structuredContent as { exit_code?: unknown; output?: unknown } | undefined;
			const output = typeof structured?.output === "string" ? structured.output : textOf(event.content);
			bash.push({
				command: String((event.input as { command?: unknown }).command ?? ""),
				exit: typeof structured?.exit_code === "number" ? structured.exit_code : null,
				last: lastLine(output),
			});
			if (bash.length > BASH_MEMORY) bash.shift();
			const book = openBook(ctx);
			const ran = bash[bash.length - 1];
			for (const task of book ? latestTasks(book.entries) : []) {
				if (book && typeof task.anchor === "string" && ran.command.includes(task.anchor)) appendEntry(book.path, "taskrun", { id: task.id, exit: ran.exit ?? "unknown", last: ran.last });
			}
			return;
		}
		if (event.isError) return;
		if (event.toolName === "todo") {
			const input = event.input as { action?: unknown; id?: unknown };
			let open = openBook(ctx);
			const opens = !open && input.action === "create";
			if (!open && opens) open = createBook(ctx);
			if (!open) return;
			recordTasks(open, event.details, input, ctx.cwd);
			return opens ? { content: [...event.content, { type: "text" as const, text: OPEN_LINE }] } : undefined;
		}
		const book = openBook(ctx);
		if (!book) return;
		if (event.toolName === "subagent") {
			const id = (event.details as { id?: unknown; name?: unknown; agent?: unknown } | undefined)?.id;
			if (typeof id === "string") {
				const details = event.details as { name?: unknown; agent?: unknown };
				appendEntry(book.path, "link", { child: id, name: details.name, agent: details.agent });
			}
			return;
		}
		if (event.toolName !== "write" && event.toolName !== "edit") return;
		const path = (event.input as { path?: unknown }).path;
		if (typeof path !== "string" || !artifactKind(path)) return;
		let text: string;
		try {
			text = readFileSync(resolve(ctx.cwd, path), "utf-8");
		} catch {
			return;
		}
		const summary = summarizeArtifact(book.entries, path, text);
		if (summary) appendEntry(book.path, summary.stage, summary.fields);
	});

	pi.on("message_end", (event) => {
		const message = event.message as { role?: string; customType?: string; details?: { agent?: unknown; name?: unknown; resultContent?: unknown } };
		if (message.role !== "custom" || message.customType !== "subagent_result") return;
		const agent = String(message.details?.agent ?? "");
		if (!REVIEWERS.has(agent)) return;
		latestReview = { name: String(message.details?.name ?? agent), agent, text: textOf(message.details?.resultContent) };
	});
}
