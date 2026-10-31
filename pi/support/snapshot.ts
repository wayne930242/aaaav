/** The loop state Jev judges, read from the book, the todo list, and the phase machine. */

import {
	type Book,
	allFriction,
	childLines,
	currentIntent,
	currentKind,
	diffAgainstBases,
	diffText,
	isOpenTask,
	latestAnchor,
	replayTodos,
	reviewClearAfterLastAct,
	reviewTrend,
	stagesDone,
	TASK_LEGEND,
	taskLines,
	verifyAfterLastAct,
} from "./book.ts";
import { computePhases } from "./phases.ts";

export type Snapshot = {
	state: Record<string, string>;
	/** The program's next phase and what it lacks, in a few words. */
	next: string;
	missing: string;
	/** The last phase the book shows complete. */
	current: string;
	/** A review recorded after the last change with no blocking finding on it. */
	reviewClear: boolean;
};

export function snapshot(book: Book, ctx: { cwd: string; sessionManager: { getBranch(): unknown[] } }): Snapshot {
	const { entries } = book;
	const todos = replayTodos(ctx.sessionManager.getBranch());
	const open = todos.filter(isOpenTask).length;
	const phases = computePhases(book, { cwd: ctx.cwd, todos });
	const check = verifyAfterLastAct(entries);
	const verify = [
		`stages: ${stagesDone(entries).join(", ") || "none"}`,
		`last check: ${check ? `${check.declared ? `declared ${check.result}` : `exit ${check.exit ?? "unknown"}`}${check.last ? ` — ${check.last}` : ""}` : "none after the last change"}`,
		`reviews: ${reviewTrend(entries)}`,
		...childLines(entries).map((line) => `child ${line}`),
	].join("; ");
	const items = allFriction(entries);
	const friction = [
		...(items.length ? [`${items.length} recorded, ${items.filter((item) => item.reflected).length} reflected`] : []),
		...items.map((item) => `${item.ref}: ${item.tried} → ${item.found} [${item.reflected ? `${item.class}${item.action ? `: ${item.action}` : ""}` : "unreflected"}]`),
	];
	return {
		state: {
			kind: currentKind(entries) ?? "not declared",
			intent: (currentIntent(entries) ?? "not declared").slice(0, 500),
			anchor: (latestAnchor(entries) ?? "none").slice(0, 500),
			diff: diffText(diffAgainstBases(entries)),
			phase: `current: ${phases.current}; next: ${phases.next}${phases.missing ? `; missing: ${phases.missing}` : ""}${phases.skipped.length ? `; skipped: ${phases.skipped.join(", ")}` : ""}`.slice(0, 600),
			verify: verify.slice(0, 1200),
			todos: `${open} open of ${todos.length}`,
			tasks: [`legend: ${TASK_LEGEND}`, ...taskLines(entries, todos, ctx.cwd)].join("\n").slice(0, 1500),
			friction: (friction.join("\n") || "none").slice(0, 800),
		},
		next: phases.next,
		missing: phases.missing,
		current: phases.current,
		reviewClear: reviewClearAfterLastAct(entries),
	};
}
