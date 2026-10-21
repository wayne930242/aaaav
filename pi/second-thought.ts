/**
 * pi extension: before a run that changed something settles, asks Jev whether the
 * final reply shows the request met, what review it needs, and how good it is.
 * Only what the user typed counts as the request: messages that extensions send
 * (intercom, monitor wakes) do not replace it. A run that arranged a wake (a monitor,
 * a loop, a subagent) is waiting, not finished, and is not judged. A wrong review tier
 * or low quality gets one advisory continuation; a low done score is only shown.
 * The agent is never blocked. Only the request and the final reply are sent.
 */

import { type ExtensionAPI, parseSkillBlock } from "@earendil-works/pi-coding-agent";

export const ENTRY_TYPE = "aaaav-second-thought";
const WORK_TOOLS = new Set(["write", "edit", "bash"]);
const WAIT_TOOLS = new Set(["MonitorCreate", "LoopCreate", "goal_wait", "subagent", "subagent_resume", "subagent_send"]);
const REQUEST_CHARS = 1500;
const REPLY_CHARS = 3000;
const TIMEOUT_MS = 15_000;

export const THRESHOLDS = { doneBelow: 0.25, qualityBelow: 1.5, reviewTier: "full" };

export const QUESTIONS = {
	done: {
		type: "bool",
		instructions: "Does `reply` show, with evidence, that `request` is fully met?",
		criteria: {
			true: "every part of the request has observed evidence in the reply: command output, a test result, or an artifact",
			false: "some part failed, was skipped, is left for later, or rests only on a claim",
		},
	},
	review: {
		type: "choice",
		instructions: "What review should the change described in `reply` get before it is merged or released?",
		criteria: {
			none: "trivial, fully covered by a passing check",
			focused: "one independent reviewer on the changed lines",
			full: "independent review plus an adversarial pass: security, data, permissions, migration, or a shared contract",
		},
	},
	quality: {
		type: "score",
		instructions: "How acceptable is the delivered work against `request`?",
		criteria: [
			"unacceptable: wrong or broken",
			"weak: works but misses requirements",
			"acceptable: meets the request",
			"strong: meets it with direct evidence and no excess",
		],
	},
} as const;

type Block = { type: string; text?: string };
type Answers = Record<string, { type: string; probability?: number; choice?: string; probabilities?: Record<string, number>; score?: number }>;
export type Verdict = { done: number; review: string; reviewProbability: number; quality: number };

export function readVerdict(answers: Answers): Verdict | undefined {
	const { done, review, quality } = answers;
	if (done?.type !== "bool" || review?.type !== "choice" || quality?.type !== "score") return undefined;
	const choice = review.choice ?? "";
	return {
		done: done.probability ?? 0,
		review: choice,
		reviewProbability: review.probabilities?.[choice] ?? 0,
		quality: quality.score ?? 0,
	};
}

export function concerns(verdict: Verdict): string[] {
	const found: string[] = [];
	if (verdict.done < THRESHOLDS.doneBelow) found.push("it does not read your reply as showing the request met");
	if (verdict.review === THRESHOLDS.reviewTier) found.push("it rates the change as needing a full independent review before merge");
	if (verdict.quality < THRESHOLDS.qualityBelow) found.push("it rates the result below what the request asks");
	return found;
}

export function needsRecheck(verdict: Verdict): boolean {
	return verdict.review === THRESHOLDS.reviewTier || verdict.quality < THRESHOLDS.qualityBelow;
}

export function message(verdict: Verdict, found: string[], recheck: boolean): string {
	return (
		`Second thought (Jev, advisory): done ${verdict.done.toFixed(2)}, review ${verdict.review} ` +
		`(${verdict.reviewProbability.toFixed(2)}), quality ${verdict.quality.toFixed(2)}/3. ` +
		`Jev says ${found.join("; ")}.` +
		(recheck
			? " Recheck your evidence against the request. If it holds, say so in one line and finish; otherwise continue the work."
			: "")
	);
}

function text(content: unknown): string {
	if (typeof content === "string") return content.trim();
	if (!Array.isArray(content)) return "";
	return (content as Block[])
		.filter((block) => block.type === "text")
		.map((block) => block.text ?? "")
		.join("\n")
		.trim();
}

export default function (pi: ExtensionAPI) {
	let request = "";
	let reply = "";
	let worked = false;
	let waiting = false;
	let asked = false;
	// Sources of submitted inputs, in order, until their user messages land.
	const sources: boolean[] = [];

	pi.on("input", (event) => {
		sources.push(event.source !== "extension");
	});

	// Each run is judged on its own work against the user's latest request.
	pi.on("agent_start", () => {
		reply = "";
		worked = false;
		waiting = false;
		asked = false;
	});

	pi.on("tool_call", (event) => {
		if (WORK_TOOLS.has(event.toolName)) worked = true;
		if (WAIT_TOOLS.has(event.toolName)) waiting = true;
	});

	// A message the user typed, including one that steers a running loop, starts a new request.
	pi.on("message_end", (event) => {
		const msg = event.message as { role?: string; content?: unknown };
		const said = text(msg.content);
		if (msg.role === "user") {
			if (!(sources.shift() ?? true)) return;
			const skill = parseSkillBlock(said);
			request = skill ? (skill.userMessage ?? `/skill:${skill.name}`) : said;
			reply = "";
			worked = false;
			asked = false;
		} else if (msg.role === "assistant" && said) {
			reply = said;
		}
	});

	pi.on("agent_before_settle", async (event, ctx) => {
		if (asked || !worked || waiting || !reply || !request || event.outcome !== "completed") return;
		asked = true;
		const record = (data: Record<string, unknown>) => ({ type: "custom" as const, customType: ENTRY_TYPE, data });
		const jev = ctx.modelRegistry.findOfType("classifier", "typesafe", "jev-latest");
		if (!jev || !ctx.modelRegistry.hasConfiguredAuth(jev)) return;
		let verdict: Verdict | undefined;
		let reason = "";
		try {
			const result = await ctx.modelRegistry.classify(
				jev,
				{ state: { request: request.slice(0, REQUEST_CHARS), reply: reply.slice(-REPLY_CHARS) }, questions: QUESTIONS },
				{ signal: AbortSignal.any([AbortSignal.timeout(TIMEOUT_MS), ...(ctx.signal ? [ctx.signal] : [])]) },
			);
			verdict = result.stopReason === "stop" ? readVerdict(result.answers as Answers) : undefined;
			reason = result.stopReason;
		} catch (error) {
			reason = error instanceof Error ? error.message : String(error);
		}
		if (!verdict) return { entries: [record({ verdict: "unknown", reason })] };
		const found = concerns(verdict);
		if (found.length === 0) return { entries: [record({ ...verdict, concerns: [] })] };
		const recheck = needsRecheck(verdict);
		return {
			entries: [
				record({ ...verdict, concerns: found }),
				{ type: "custom_message" as const, customType: ENTRY_TYPE, content: message(verdict, found, recheck), display: true },
			],
			...(recheck ? { continue: true } : {}),
		};
	});
}
