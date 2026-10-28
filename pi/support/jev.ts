/** Shared access to Jev (TypeSafe's typed-decision model) through pi's classifier registry. */

import type { ExtensionContext } from "@earendil-works/pi-coding-agent";

export const TIMEOUT_MS = 15_000;

export type Question = { type: "bool" | "choice" | "score"; instructions: string; criteria: unknown };
export type Answers = Record<string, { type: string; probability?: number; choice?: string; probabilities?: Record<string, number>; score?: number }>;

/** The classification answers, or the reason none came: no key, a timeout, or a failure. */
export async function classify(ctx: ExtensionContext, state: Record<string, string>, questions: Record<string, Question>): Promise<{ answers?: Answers; reason: string }> {
	const jev = ctx.modelRegistry.findOfType("classifier", "typesafe", "jev-latest");
	type AuthModel = Parameters<typeof ctx.modelRegistry.hasConfiguredAuth>[0];
	if (!jev) return { reason: "no-auth" };
	// SAFETY: hasConfiguredAuth is typed for chat models but reads only `provider`, which a classifier has too.
	const authModel = jev as unknown as AuthModel;
	if (!ctx.modelRegistry.hasConfiguredAuth(authModel)) return { reason: "no-auth" };
	try {
		const result = await ctx.modelRegistry.classify(
			jev,
			{ state, questions } as Parameters<typeof ctx.modelRegistry.classify>[1],
			{ signal: AbortSignal.any([AbortSignal.timeout(TIMEOUT_MS), ...(ctx.signal ? [ctx.signal] : [])]) },
		);
		return result.stopReason === "stop" ? { answers: result.answers as Answers, reason: "stop" } : { reason: result.stopReason };
	} catch (error) {
		return { reason: error instanceof Error ? error.message : String(error) };
	}
}
