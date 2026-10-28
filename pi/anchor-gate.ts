/**
 * pi extension: inside an open loop, warns once per jump when write or edit starts the `act` phase while an
 * earlier phase of the loop kind is incomplete: no anchor, or in a durable loop a decision, spec, read,
 * approval, or design still missing. The phase machine in support/phases.ts decides what is missing; the
 * warning names it and the `skip` escape. Outside a loop, or in a `quick` one, it stays silent.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { currentKind, guarded, openLoop, replayTodos } from "./support/book.ts";
import { JumpMemory, computePhases, exempt, incompleteBefore, jumpLine } from "./support/phases.ts";

export default function (pi: ExtensionAPI) {
	const jumps = new JumpMemory();

	pi.on(
		"tool_call",
		guarded((event, ctx) => {
			if (event.toolName !== "write" && event.toolName !== "edit") return;
			const filePath = (event.input as { path?: unknown }).path;
			if (typeof filePath !== "string") return;
			const book = openLoop(ctx);
			if (!book || exempt(filePath, ctx.cwd) || currentKind(book.entries) === "quick") return;
			const phases = computePhases(book, { cwd: ctx.cwd, todos: replayTodos(ctx.sessionManager.getBranch()) });
			const missing = incompleteBefore(phases, "act");
			if (jumps.fresh(String(book.header.id), "act", missing.map((status) => status.name))) ctx.ui.notify(jumpLine("act", missing), "warning");
		}),
	);
}
