# Mock-ups

Keep each topic's noncanonical review artifacts in its topic folder until the coordinator and user explicitly adopt
them.

Each artifact uses the lowest fidelity sufficient for the current decision:

- self-contained HTML/CSS/JS for static or lightly interactive surfaces; or
- isolated React when shared state, transitions, conditional behavior, focus, or realistic interaction is material.

React mock-ups use the experiments workspace and its dependencies (see `../README.md`) and stay isolated under
their topic folder. They never import application code unless a brief explicitly requests a repository-integrated
review.
