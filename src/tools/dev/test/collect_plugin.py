"""Minimal pytest plugin that prints collected node ids.

pytest 9's quiet ``--collect-only`` output prints per-file counts instead of
node ids. ``sg test`` needs stable case identity, so discovery loads this plugin
with ``-p tools.dev.test.collect_plugin`` and reads the printed node ids.
"""

from __future__ import annotations


def pytest_collection_finish(session) -> None:
    """Print one node id per collected item."""
    for item in session.items:
        print(item.nodeid)
