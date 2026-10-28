/**
 * pi extension: inside an open loop, asks Jev what the agent should do next and whether the
 * book's evidence covers the loop's intent. Jev sees only what the loop book holds: the kind,
 * intent, anchor, diff summary, verify state (stages, review rounds, child checks), and open
 * todo count. It runs when a run settles and the book gained an entry since the last judgment,
 * and at a `close` declaration. The main output is a next-stage suggestion; the advisory leads
 * with it and continues the run once, only when the suggestion is verify, review, or fix and the
 * book shows that stage missing after the last change. A run that arranged a wake (a monitor, a
 * loop, a subagent) is waiting, not finished, and is not judged. Outside a loop nothing runs.
 * A subagent session registers nothing: the agent that spawned it judges its result.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import {
	type Book,
	childLines,
	currentIntent,
	currentKind,
	diffAgainstBases,
	diffText,
	isBlocking,
	isOpenTask,
	latestAnchor,
	lastIndex,
	openBook,
	replayTodos,
	reviewClearAfterLastAct,
	reviewTrend,
	reviews,
	stagesDone,
	TASK_LEGEND,
	taskLines,
	verifyAfterLastAct,
} from "./support/book.ts";
import { type Answers, classify } from "./support/jev.ts";
import { isSubagent } from "./support/subagent.ts";

export { isSubagent };

export const ENTRY_TYPE = "anchorloop-second-thought";
const WAIT_TOOLS = new Set(["MonitorCreate", "LoopCreate", "goal_wait", "subagent", "subagent_resume", "subagent_send"]);

export const THRESHOLDS = { doneBelow: 0.25, qualityBelow: 1.5, reviewTier: "full" };

export const NEXT_STAGES = ["continue", "verify", "review", "fix", "close", "ask-user"] as const;
export type Next = (typeof NEXT_STAGES)[number];

export const QUESTIONS = {
	next: {
		type: "choice" as const,
		instructions:
			"What should the agent do next in this loop? `kind` is the loop kind, `intent` what it delivers, `anchor` the check that observes the result, `diff` what changed, `verify` the stages, check evidence, and reviews recorded so far, `todos` the open count, and `tasks` each work item with its own anchor, last exit code, and spec references.",
		criteria: {
			continue: "work on the intent remains to be done",
			verify: "the change was made or altered after the last check, or no check observed the anchor",
			review: "the kind or the diff needs an independent review that is not recorded, or the last one predates the last change",
			fix: "a recorded check or review shows a failure or a blocking finding that is not yet fixed",
			close: "the verify evidence covers the intent, any needed review is clear, and no todo is open",
			"ask-user": "a decision or judgment that belongs to the user blocks progress",
		},
	},
	done: {
		type: "bool" as const,
		instructions: "Does the `verify` evidence show, with observed results, that `intent` is fully met?",
		criteria: {
			true: "every part of the intent has observed evidence: command output, a test result, a review verdict, or an artifact",
			false: "some part failed, was skipped, is left for later, or rests only on a claim",
		},
	},
	review: {
		type: "choice" as const,
		instructions: "What review should the `diff` still get before it is merged or released, given the reviews recorded in `verify`?",
		criteria: {
			none: "trivial, fully covered by a passing check, or already reviewed with no blocking finding",
			focused: "one independent reviewer on the changed lines",
			full: "independent review plus an adversarial pass: security, data, permissions, migration, or a shared contract",
		},
	},
	quality: {
		type: "score" as const,
		instructions: "How acceptable is the work recorded in the loop against its `intent`?",
		criteria: [
			"unacceptable: wrong or broken",
			"weak: works but misses requirements",
			"acceptable: meets the intent",
			"strong: meets it with direct evidence and no excess",
		],
	},
};

export type Verdict = { next: Next; done: number; review: string; reviewProbability: number; quality: number };

export function readVerdict(answers: Answers): Verdict | undefined {
	const { next, done, review, quality } = answers;
	if (next?.type !== "choice" || done?.type !== "bool" || review?.type !== "choice" || quality?.type !== "score") return undefined;
	if (!(NEXT_STAGES as readonly string[]).includes(next.choice ?? "")) return undefined;
	const choice = review.choice ?? "";
	return {
		next: next.choice as Next,
		done: done.probability ?? 0,
		review: choice,
		reviewProbability: review.probabilities?.[choice] ?? 0,
		quality: quality.score ?? 0,
	};
}

export type Snapshot = {
	state: Record<string, string>;
	/** The book facts that back the suggestion, in a few words. */
	facts: string;
	/** A review recorded after the last act with no blocking finding on it. */
	reviewClear: boolean;
	/** The stage the book shows missing after the last act, if any. */
	missing: Next[];
};

export function snapshot(book: Book, ctx: { cwd: string; sessionManager: { getBranch(): unknown[] } }): Snapshot {
	const { entries } = book;
	const todos = replayTodos(ctx.sessionManager.getBranch());
	const open = todos.filter(isOpenTask).length;
	const check = verifyAfterLastAct(entries);
	const rounds = reviews(entries);
	const lastReview = rounds.at(-1);
	const missing: Next[] = [];
	if (!check) missing.push("verify");
	if (lastIndex(entries, "review") <= lastIndex(entries, "act")) missing.push("review");
	if (lastReview && isBlocking(lastReview) && lastIndex(entries, "act") < lastIndex(entries, "review")) missing.push("fix");
	const facts = [
		check ? `verify ${check.skip ? "skipped" : `exit ${check.exit ?? "unknown"}`} after the last change` : "no verify after the last change",
		lastReview ? `review r${rounds.length} ${lastReview.blocking === true ? "blocking" : lastReview.blocking === false ? "clear" : "unknown"}` : "no review",
		`${open} open todo${open === 1 ? "" : "s"}`,
	].join(", ");
	const verify = [
		`stages: ${stagesDone(entries).join(", ") || "none"}`,
		`last check: ${check ? `exit ${check.exit ?? "unknown"}${check.last ? ` — ${check.last}` : ""}` : "none after the last change"}`,
		`reviews: ${reviewTrend(entries)}`,
		...childLines(entries).map((line) => `child ${line}`),
	].join("; ");
	return {
		state: {
			kind: currentKind(entries) ?? "not declared",
			intent: (currentIntent(entries) ?? "not declared").slice(0, 500),
			anchor: (latestAnchor(entries) ?? "none").slice(0, 500),
			diff: diffText(diffAgainstBases(entries)),
			verify: verify.slice(0, 1200),
			todos: `${open} open of ${todos.length}`,
			tasks: [`legend: ${TASK_LEGEND}`, ...taskLines(entries, todos, ctx.cwd)].join("\n").slice(0, 1500),
		},
		facts,
		reviewClear: reviewClearAfterLastAct(entries),
		missing,
	};
}

export function assess(verdict: Verdict, reviewClear: boolean): { found: string[]; notes: string[] } {
	const found: string[] = [];
	const notes: string[] = [];
	if (verdict.done < THRESHOLDS.doneBelow) found.push("evidence not shown to cover the intent");
	if (verdict.review === THRESHOLDS.reviewTier) {
		if (reviewClear) notes.push("review rated full, but a review recorded after the last change found no blocking finding");
		else found.push("needs full independent review");
	}
	if (verdict.quality < THRESHOLDS.qualityBelow) found.push("result below the intent");
	return { found, notes };
}

/** The stage to continue the run with: the suggestion, only when the book shows it missing after the last act. */
export function continues(verdict: Verdict, snap: Snapshot): boolean {
	return (verdict.next === "verify" || verdict.next === "review" || verdict.next === "fix") && snap.missing.includes(verdict.next);
}

export function message(verdict: Verdict, snap: Snapshot, found: string[], notes: string[]): string {
	const extra = [...found, ...notes];
	return (
		`Second thought (Jev, advisory): next → ${verdict.next} (${snap.facts}); ` +
		`done ${verdict.done.toFixed(2)}, review ${verdict.review}, quality ${verdict.quality.toFixed(2)}/3` +
		`${extra.length ? `; ${extra.join("; ")}` : ""}.` +
		(continues(verdict, snap) ? ` The book shows ${verdict.next} missing: do it now, or say why it does not apply.` : "") +
		" No reply needed."
	);
}

export default function (pi: ExtensionAPI) {
	if (isSubagent()) return;
	let waiting = false;
	let continued = false;
	// Entries each open book held when it was last judged.
	const judged = new Map<string, number>();
	// A close deletes its book, so what Jev needs is read when the call starts.
	const closing = new Map<string, Snapshot>();

	pi.on("session_start", () => {
		judged.clear();
		closing.clear();
	});

	pi.on("agent_settled", () => {
		waiting = false;
		continued = false;
	});

	pi.on("tool_call", (event, ctx) => {
		if (WAIT_TOOLS.has(event.toolName)) waiting = true;
		if (event.toolName !== "anchorloop_stage" || (event.input as { stage?: unknown }).stage !== "close") return;
		const book = openBook(ctx);
		if (book) closing.set(event.toolCallId, snapshot(book, ctx));
	});

	async function judge(ctx: Parameters<typeof classify>[0], snap: Snapshot) {
		const { answers, reason } = await classify(ctx, snap.state, QUESTIONS);
		if (reason === "no-auth") return undefined;
		return { verdict: answers ? readVerdict(answers) : undefined, reason };
	}

	pi.on("tool_result", async (event, ctx) => {
		const snap = closing.get(event.toolCallId);
		if (!snap) return;
		closing.delete(event.toolCallId);
		if (event.isError) return;
		const judgment = await judge(ctx, snap);
		if (!judgment?.verdict) return;
		const { found, notes } = assess(judgment.verdict, snap.reviewClear);
		pi.appendEntry(ENTRY_TYPE, { ...judgment.verdict, at: "close", concerns: found });
		return { content: [...event.content, { type: "text" as const, text: message(judgment.verdict, snap, found, notes) }] };
	});

	pi.on("agent_before_settle", async (event, ctx) => {
		if (waiting || event.outcome !== "completed") return;
		const book = openBook(ctx);
		if (!book) return;
		const id = String(book.header.id);
		if (book.entries.length <= (judged.get(id) ?? 0)) return;
		judged.set(id, book.entries.length);
		const snap = snapshot(book, ctx);
		const judgment = await judge(ctx, snap);
		if (!judgment) return;
		const record = (data: Record<string, unknown>) => ({ type: "custom" as const, customType: ENTRY_TYPE, data });
		if (!judgment.verdict) return { entries: [record({ verdict: "unknown", reason: judgment.reason })] };
		const { found, notes } = assess(judgment.verdict, snap.reviewClear);
		const proceed = !continued && continues(judgment.verdict, snap);
		if (proceed) continued = true;
		return {
			entries: [
				record({ ...judgment.verdict, concerns: found }),
				{ type: "custom_message" as const, customType: ENTRY_TYPE, content: message(judgment.verdict, snap, found, notes), display: true },
			],
			...(proceed ? { continue: true } : {}),
		};
	});
}
