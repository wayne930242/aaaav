/**
 * pi extension: runs hooks/validate_tool_use.py after write and edit tool
 * results and appends its suggestions to the model-visible result content.
 */

import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const HOOK_SCRIPT = fileURLToPath(new URL("../hooks/validate_tool_use.py", import.meta.url));

function validate(filePath: string, cwd: string): string | undefined {
	const payload = JSON.stringify({ tool_name: "Edit", tool_input: { file_path: filePath }, cwd });
	const proc = spawnSync("python3", [HOOK_SCRIPT], { input: payload, encoding: "utf-8", timeout: 15_000 });
	if (proc.error || proc.status !== 0) {
		const reason = proc.error?.message || proc.stderr.trim() || `exit ${proc.status}`;
		return `⚠ [aaaav] Validator did not run: ${reason}`;
	}
	if (!proc.stdout.trim()) return undefined;
	return JSON.parse(proc.stdout).hookSpecificOutput?.additionalContext;
}

export default function (pi: ExtensionAPI) {
	pi.on("tool_result", async (event, ctx) => {
		if (event.isError || (event.toolName !== "write" && event.toolName !== "edit")) return;
		const filePath = event.input.path;
		if (typeof filePath !== "string") return;
		const advice = validate(filePath, ctx.cwd);
		if (!advice) return;
		return { content: [...event.content, { type: "text", text: advice }] };
	});
}
