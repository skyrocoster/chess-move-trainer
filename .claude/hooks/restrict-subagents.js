// PreToolUse hook for the Agent tool. Allows only the named subagents and requires an explicit,
// non-Opus model on every call. Edit ALLOWED_AGENTS to change which agents are permitted.
const ALLOWED_AGENTS = ["scout", "jesus", "vicar"];

let raw = "";
process.stdin.on("data", (chunk) => (raw += chunk));
process.stdin.on("end", () => {
  let input = {};
  try {
    input = JSON.parse(raw).tool_input || {};
  } catch {
    // Unreadable payload: fall through and deny below.
  }
  const agent = input.subagent_type;
  const model = typeof input.model === "string" ? input.model.trim() : "";

  const problems = [];
  if (!ALLOWED_AGENTS.includes(agent)) {
    problems.push(
      `subagent_type "${agent ?? "(none)"}" is not allowed; use one of ${ALLOWED_AGENTS.join(", ")}`,
    );
  }
  if (!model) {
    problems.push("model is missing; pass it explicitly (scout/vicar -> haiku, jesus -> sonnet)");
  } else if (/opus/i.test(model)) {
    problems.push(`model "${model}" is not allowed for subagents`);
  }

  if (problems.length > 0) {
    process.stdout.write(
      JSON.stringify({
        hookSpecificOutput: {
          hookEventName: "PreToolUse",
          permissionDecision: "deny",
          permissionDecisionReason: `Blocked by .claude/hooks/restrict-subagents.js: ${problems.join("; ")}. See the repository CLAUDE.md.`,
        },
      }),
    );
  }
});
