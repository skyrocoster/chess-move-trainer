---
name: browser-validation-invoke
description: Invoke-only guidance for isolated browser validation when an approved brief requires live UI evidence.
---

# Browser Validation Invocation

This is an invoke-only validation boundary. Do not edit repository files, reuse servers or profiles, or
interpret browser results as implementation proof.

The coordinator's brief must provide:

- the startup command, if a local service is required;
- the target URL and exact user scenario;
- any data setup and cleanup commands;
- the case identifier and expected observable evidence.

Use the configured Playwright tooling to run only that brief. Return the captured result and artifact
paths, keeping `PASS`, `PRODUCT_FAIL`, and `INFRA_FAIL` distinct. The adopting repository may add a
browser-validation script later, but this skeleton does not require one.
