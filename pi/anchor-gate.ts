/**
 * pi extension: warns once when write or edit runs before the assistant has
 * stated a `Reality anchor:` line since the user's latest message.
 */

import { existsSync, realpathSync } from "node:fs";
import { tmpdir } from "node:os";
import { basename, dirname, extname, isAbsolute, join, relative, resolve } from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const ANCHOR = /Reality anchor:/;
const EXEMPT_IN_PROJECT = ["scratch", "docs/specs"];
const EXEMPT_ROOTS = [tmpdir(), "/tmp", "/var/folders"];
const EXEMPT_EXTENSIONS = [".md", ".txt"];

export const WARNING =
	"aaaav anchor gate: a change ran before the reply stated " +
	"`Reality anchor: <the exact check that observes the result, and its checkpoint>`.";

type Block = { type: string; text?: string };
type Message = { role?: string; content?: string | Block[] };

function statesAnchor(message: Message): boolean {
	if (message.role !== "assistant" || !Array.isArray(message.content)) return false;
	return message.content.some((block) => block.type === "text" && ANCHOR.test(block.text ?? ""));
}

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

/** Markdown and text files, scratch and spec folders in the project, and temp files outside it; a project that lives in a temp dir is still gated. */
export function exempt(filePath: string, cwd: string): boolean {
	if (EXEMPT_EXTENSIONS.includes(extname(filePath).toLowerCase())) return true;
	const root = real(cwd);
	const target = real(resolve(cwd, filePath));
	if (within(root, target)) return EXEMPT_IN_PROJECT.some((dir) => within(join(root, dir), target));
	return EXEMPT_ROOTS.some((tmp) => within(real(tmp), target));
}

export default function (pi: ExtensionAPI) {
	let anchored = false;
	let warned = false;

	pi.on("session_start", (_event, ctx) => {
		anchored = false;
		const branch = ctx.sessionManager.getBranch() as Array<{ type: string; message?: Message }>;
		for (let i = branch.length - 1; i >= 0; i--) {
			const message = branch[i].type === "message" ? branch[i].message : undefined;
			if (!message) continue;
			if (message.role === "user") return;
			if (statesAnchor(message)) {
				anchored = true;
				return;
			}
		}
	});

	// User messages that steer a running loop end here too, so the gate closes for each of them.
	pi.on("message_end", (event) => {
		const message = event.message as Message;
		if (message.role === "user") {
			anchored = false;
			warned = false;
		}
		else if (statesAnchor(message)) anchored = true;
	});

	pi.on("tool_call", (event, ctx) => {
		if (anchored || warned || (event.toolName !== "write" && event.toolName !== "edit")) return;
		const filePath = (event.input as { path?: unknown }).path;
		if (typeof filePath !== "string" || exempt(filePath, ctx.cwd)) return;
		warned = true;
		ctx.ui.notify(WARNING, "warning");
	});
}
