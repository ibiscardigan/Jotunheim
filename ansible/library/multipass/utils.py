"""Shared utility functions for Multipass module components."""

import subprocess


def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    """
    Run a subprocess command with consistent flags.

    Args:
        cmd: Command to execute as a list.

    Returns:
        CompletedProcess: The result of subprocess.run().
    """
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
