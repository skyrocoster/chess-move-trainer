import { tool } from "@opencode-ai/plugin"

const WARNING_TOKENS = 100_000
const DECISION_TOKENS = 120_000
const ROLLOVER_TOKENS = 200_000

export const ContextBudget = async ({ client, directory }) => ({
  tool: {
    context_budget: tool({
      description: "Measure a retained subagent session's active context before deciding whether to resume it.",
      args: {
        session_id: tool.schema.string().describe("The retained OpenCode subagent session ID"),
      },
      async execute({ session_id }) {
        const response = await client.session.messages({
          path: { id: session_id },
          query: { directory },
        })
        const messages = response.data ?? []
        const assistants = messages
          .map((message) => message.info)
          .filter((info) => info.role === "assistant" && info.time.completed != null)
        const latest = assistants.at(-1)

        if (!latest) {
          return JSON.stringify({
            status: "UNAVAILABLE",
            session_id,
            reason: "No completed assistant message with token telemetry was found.",
          })
        }

        const active_tokens = latest.tokens.input + latest.tokens.cache.read
        let status = "OK"
        let default_action = "RESUME"
        if (active_tokens >= ROLLOVER_TOKENS) {
          status = "ROLLOVER-DEFAULT"
          default_action = "ROLLOVER"
        } else if (active_tokens >= DECISION_TOKENS) {
          status = "DECISION-REQUIRED"
          default_action = "DECIDE"
        } else if (active_tokens >= WARNING_TOKENS) {
          status = "WARNING"
        }

        return JSON.stringify({
          status,
          session_id,
          active_tokens,
          measurement: "latest completed assistant input + cache.read",
          warning_tokens: WARNING_TOKENS,
          decision_tokens: DECISION_TOKENS,
          rollover_tokens: ROLLOVER_TOKENS,
          default_action,
          compacted: messages.some((message) =>
            message.parts.some((part) => part.type === "compaction"),
          ),
        })
      },
    }),
  },
})

export default ContextBudget
