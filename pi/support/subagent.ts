// pi-herdr-agents marks its children with PI_SUBAGENT_ID, pi-subagents with PI_SUBAGENT_CHILD,
// and avtc's pi-subagent with PI_SUBAGENT_CHILD_AGENT plus PI_SUBAGENT_PARENT_PID.
export function isSubagent(env: NodeJS.ProcessEnv = process.env): boolean {
	return Boolean(env.PI_SUBAGENT_ID) || env.PI_SUBAGENT_CHILD === "1" || Boolean(env.PI_SUBAGENT_CHILD_AGENT && env.PI_SUBAGENT_PARENT_PID);
}
