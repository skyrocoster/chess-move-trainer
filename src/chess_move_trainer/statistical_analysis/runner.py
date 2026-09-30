"""Checkpointed question execution; an interrupted family is never a complete report."""

import time
from pathlib import Path

from .artifacts import Budget, digest, read_json, write_json
from .audit import iter_records
from .inference import correct_and_gate, fit_contrast, support_failures
from .models import prepare_frame
from .protocol import DEFAULT_PROTOCOL as P
from .registry import questions
from .snapshot import code_provenance


def run_questions(
    directory: Path,
    *,
    identifiers=None,
    seconds=300,
    fit_seconds=30,
    replicates=P.bootstrap_replicates,
    diagnostic=False,
):
    budget = Budget(seconds)
    if not diagnostic:
        raise ValueError(
            "historical inference is blocked until the complete calibration/sensitivity "
            "suite is accepted; diagnostic=True is exploratory only"
        )
    extraction = read_json(directory / "extraction.json")
    registry = read_json(directory / "registry.json")
    pilot_path = directory / "pilot.json"
    pilot = read_json(pilot_path) if pilot_path.exists() else None
    if pilot is not None and (
        pilot.get("status") != "complete"
        or pilot.get("identity")
        != extraction.get("pilot_identity", extraction.get("identity"))
    ):
        raise ValueError("pilot and extraction identities disagree")
    if digest({k: v for k, v in registry.items() if k != "identity"}) != registry["identity"]:
        raise ValueError("registry contents changed")
    if extraction["status"] != "complete":
        raise ValueError("complete extraction required")
    if registry["protocol_sha256"] != P.identity or registry["questions"] != [
        q.to_dict() for q in questions()
    ]:
        # JSON turns tuples into lists; canonical identities are used below instead.
        if (
            digest(registry["questions"]) != digest([q.to_dict() for q in questions()])
            or registry["protocol_sha256"] != P.identity
        ):
            raise ValueError("registry changed; do not reuse an old frozen family")
    all_questions = {q.id: q for q in questions()}
    chosen = list(all_questions) if identifiers is None else list(identifiers)
    if set(chosen) - all_questions.keys():
        raise ValueError("unknown question ID")
    identity = digest(
        {
            "extraction": extraction["identity"],
            "registry": registry["identity"],
            "replicates": replicates,
            "mode": "exploratory_diagnostic",
            "implementation": code_provenance(),
        }
    )
    path = directory / "diagnostics.json"
    ledger = read_json(path) if path.exists() else {"identity": identity, "results": {}}
    if ledger["identity"] != identity:
        raise ValueError("run settings changed; cannot merge different inference runs")
    ledger["status"] = "run_incomplete"
    ledger["mode"] = (
        "exploratory_pilot_diagnostic_not_confirmatory"
        if pilot is not None
        else "exploratory_diagnostic_not_confirmatory"
    )
    if pilot is not None:
        ledger["pilot_identity"] = pilot["identity"]
    write_json(path, ledger)
    # Each question scans the frozen records; bounded memory rather than loading all rich records.
    try:
        for identifier in chosen:
            budget.check()
            if identifier in ledger["results"]:
                continue
            q = all_questions[identifier]
            frame, counts = prepare_frame(iter_records(directory / "records.db"), q)
            failures = support_failures(frame, counts)
            result = {
                "question": q.to_dict(),
                "counts": counts,
                "gate_failures": failures,
                "status": "support_blocked",
            }
            if not failures:
                try:
                    result.update(
                        fit_contrast(
                            frame,
                            q,
                            len(all_questions),
                            replicates=replicates,
                            seconds=max(0.001, seconds - (time.monotonic() - budget.started)),
                            fit_seconds=fit_seconds,
                        )
                    )
                except (ValueError, RuntimeError, TimeoutError) as error:
                    result.update(
                        status="model_failed", gate_failures=["model_failed"], error=str(error)
                    )
            if pilot is not None:
                result["gate_failures"] = sorted(
                    set(result.get("gate_failures", [])) | {"pilot_sample_not_promotable"}
                )
            ledger["results"][identifier] = result
            write_json(path, ledger)
        complete = set(ledger["results"]) == set(all_questions)
        # Correct a copy: unexecuted placeholders must not become resume-complete slots.
        import copy

        corrected = correct_and_gate(
            copy.deepcopy(ledger["results"]), list(all_questions), complete=complete
        )
        ledger["status"] = "complete_initial_family" if complete else "run_incomplete"
        ledger["corrected"] = corrected
        write_json(path, ledger)
        return ledger
    except BaseException:
        write_json(path, ledger)
        raise
