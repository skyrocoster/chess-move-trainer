from subprocess import CompletedProcess
from unittest.mock import Mock, call

import pytest

from scripts import dev


@pytest.mark.parametrize("port", [5666, 8444])
def test_clear_port_accepts_a_free_port(port: int) -> None:
    run = Mock(return_value=CompletedProcess([], 0, "", ""))

    dev.subprocess.run = run
    dev.clear_port(port)

    assert run.call_count == 1
    assert f"-LocalPort {port}" in run.call_args.args[0][-1]
    assert "-State Listen" in run.call_args.args[0][-1]


@pytest.mark.parametrize("port", [5666, 8444])
def test_clear_port_stops_only_positive_listener_pids(port: int) -> None:
    run = Mock(
        side_effect=[
            CompletedProcess([], 0, "0\n4321\n4321\n", ""),
            CompletedProcess([], 0, "", ""),
        ]
    )

    dev.subprocess.run = run
    dev.clear_port(port)

    inspection_call = run.call_args_list[0]
    assert inspection_call.kwargs == {"check": False, "capture_output": True, "text": True}
    assert f"-LocalPort {port}" in inspection_call.args[0][-1]
    assert "-State Listen" in inspection_call.args[0][-1]
    assert run.call_args_list[1] == call(
        ["powershell", "-NoProfile", "-Command", "Stop-Process -Id 4321 -Force"], check=True
    )


def test_clear_port_surfaces_inspection_failure() -> None:
    dev.subprocess.run = Mock(return_value=CompletedProcess([], 1, "", "inspection failed"))

    with pytest.raises(RuntimeError, match="inspection failed"):
        dev.clear_port(5666)


def test_frontend_command_uses_windows_npm_executable() -> None:
    assert dev.command_for("frontend") == ["npm.cmd", "run", "dev", "--prefix", "frontend"]
