---
name: grilling
description: Interview the user one decision at a time until every branch of a plan, design, decision, or idea is settled. Use whenever the user asks to be grilled, interviewed in depth, questioned exhaustively, stress-test an idea, reach shared understanding before acting, or explore a decision tree.
---

# Grilling

Interview the user relentlessly until both sides share a complete understanding. Treat the subject as a design tree: each decision branches into the decisions that depend on it.

## Work the decision tree

1. Build and continuously revise an internal tree of decisions, their prerequisites, and their dependent branches.
2. Mark as the current **frontier** every unsettled decision whose prerequisites are settled. These are the questions that can be answered now without guessing about another open answer.
3. Choose the single highest-leverage question on the frontier. Ask exactly that one question, then stop.
4. Wait for the user's answer before asking another question.
5. Apply those answers to the tree, including any new branches or changed premises they reveal, then recompute the frontier.
6. Keep working outward until the frontier is empty and every branch has been visited. Surface hidden assumptions as decisions rather than silently choosing them.

A question whose answer depends on another question still open in the current round is not on the frontier. Hold it for a later round.

Do not repeat settled questions. If an answer is partial, contradictory, or creates a new prerequisite, keep that branch unsettled and ask the smallest clarifying decision in a later frontier round.

## Ask decisions, find facts

Finding facts is the agent's job. Never ask the user for repository, filesystem, tool, or environment facts that can be retrieved directly.

Before the first question in a repository-dependent or deliberately vague conversation, retrieve enough bounded
facts to ground the first decision. When any later frontier branch needs an environmental fact:

- Dispatch an appropriate sub-agent to retrieve it, with a bounded factual question and no authority to make the decision.
- Treat the running lookup as an unsettled prerequisite. Hold only the questions downstream of that fact.
- Do not ask a question whose recommendation depends on a pending lookup. Complete the bounded lookup first.
- Incorporate the returned evidence, recompute the frontier, and put the resulting decisions to the user.

Scouting is repeatable, not limited to conversation entry. Trigger another bounded lookup whenever the evidence
needed for the next question is missing, stale, contradictory, or insufficient for a grounded recommendation.

Facts constrain the tree; they do not settle the user's decisions. Never answer a question on the user's behalf.
Give a recommendation for every decision, but always wait for the user to choose.

## Question format

Number questions continuously across the session. Ask exactly one question per assistant turn. Give explicit,
mutually distinguishable options whenever the decision is not naturally free-form, and identify one option as the
recommendation. Format the question exactly like this:

```markdown
❓ **Q1** - **<question title>**: <question body>

Options: **A.** <option> · **B.** <option> · **C.** <option>

➡️ **Recommended: <option letter and label>.** <concise reason>
```

Keep separate decisions as separate numbered questions and separate turns. Options and recommendations are advice,
not inferred answers; the user must choose or provide their own answer.

## Completion gate

The session is not complete merely because the user says the current answers look good. It is complete only when the recomputed frontier is empty: all known branches are settled, no lookup is pending, and nothing material remains silently assumed.

When the frontier first becomes empty:

1. Present a concise shared-understanding summary containing the settled decisions, important reasons, constraints, and explicit exclusions.
2. State that the decision tree has no remaining frontier.
3. Ask the user to confirm that shared understanding is complete.

Do not plan implementation, edit files, execute the agreed work, or hand it to another workflow until the user explicitly confirms. After confirmation, stop the grilling session and respond to whatever action the user requests next.
