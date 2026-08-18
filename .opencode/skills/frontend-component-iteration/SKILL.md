---
name: frontend-component-iteration
description: Make narrowly scoped frontend component design changes through user-led visual iteration. Use when the user provides an existing component and requests a visual or interaction adjustment.
---

# Frontend Component Iteration

Use this skill when the user is directing visual iteration on an existing frontend component and will perform the visual review themselves.

## Working Rules

- Read the repository guidance first, then inspect the component, its styles, stories, focused tests, direct dependencies, and the relevant active Plan or work order when one exists. Keep exploration bounded to those files.
- Diagnose the current layout or interaction behavior before editing. State the specific cause and the smallest change that addresses it.
- Preserve existing design-system tokens, accessibility semantics, component contracts, and unrelated worktree changes.
- Make exactly the requested visual or interaction change. Do not refactor, redesign, add speculative content, or modify unrelated functionality.
- If the request is ambiguous about order, visibility, or interaction behavior, ask one focused question before editing.
- Do not launch a browser, use browser automation, start a dev server, take screenshots, or perform visual checks. The user performs visual verification. You may inspect screenshots or other artifacts only when the user explicitly provides or names them.
- Do not run tests, linting, formatting, builds, or broad checks during iteration unless the user explicitly requests them.
- When checks are explicitly requested, run only the directly relevant focused commands. Do not widen to the full suite unless asked.
- If documentation closeout is explicitly requested, update the named work-order receipt with the final state, deviations, truthful proof results, dirty-path notes, and authorization audit. Run only the required documentation contract check after documentation edits.
- Do not commit changes.

## Iteration Protocol

1. Inspect the bounded context and identify the current cause.
2. Briefly state the diagnosis and the exact edit before changing files.
3. Apply the smallest patch for the requested adjustment.
4. Briefly report what changed and wait for the user's visual feedback.
5. Apply only the next requested adjustment; do not batch additional refinements or declare the design complete independently.
6. If the user explicitly requests focused checks, run them after the current iteration and report passes, warnings, and any checks intentionally not run.
7. When the user explicitly requests completion documentation, record the final implementation and proof state without overstating unrun checks.

Only run the repository's full test suite when the user explicitly requests it or the repository workflow requires it for the requested closeout.
