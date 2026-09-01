---
name: design-synthesis
description: Use after final visual sign-off and repository-grounded grilling to write the selected mock-up's detailed design document for planning hand-off.
---

# Design synthesis

Require an explicitly signed-off mock-up, settled behavior decisions, detailed repository facts, genuinely
unresolved technical facts, and an approved `DESIGN.md` path beside the selected artifact under `experiments/`.
Inspect the latest artifact before writing so authoritative user edits are carried forward.

Write only what is supported by the selected design, settled decisions, and repository evidence. Report a
contradiction between them instead of inventing precedence. The document should include the applicable parts of:

- purpose, mental model, terminology, non-goals, and retained capabilities;
- visible anatomy, information hierarchy, responsive behavior, and visual roles;
- meaningful states, conditions, transitions, action visibility, and empty states;
- persistence, pending, error, recovery, and replacement semantics;
- copy rules, component-owned or model-owned language, and anti-duplication rules;
- tokens, reusable component boundaries, and motion behavior;
- keyboard, focus, semantics, announcements, contrast, and reduced motion;
- current repository components, models, APIs, ownership boundaries, and focused tests affected; and
- settled invariants and unresolved technical facts clearly separated.

Include a compact adoption boundary that distinguishes details canonical implementation must preserve, details it
may translate onto repository conventions, and artifact-only content it must exclude. Give the most important
visual or interaction anchors stable section references so a downstream Plan can link them without copying the
whole document.

Keep the document implementation-ready but not implementation-prescriptive. Do not define Plan stages, progress,
proof execution, lifecycle mechanics, or implementation authorization. The final mock-up communicates composition;
the design document communicates behavior, constraints, and repository meaning.

```text
RESULT: WRITTEN | CONTRADICTION | BLOCKED
MOCK-UP: <signed-off artifact path>
DESIGN: <exact DESIGN.md path>
GROUNDING: <repository areas mapped>
UNRESOLVED: none | <technical facts that planning must resolve>
HAND-OFF: <concise evidence summary for assessment and planning>
ISSUE: none | <contradiction or blocker>
```

Do not edit product source, tests, Plans, canonical documentation, rejected alternatives, or unrelated `Scratch`
content.
