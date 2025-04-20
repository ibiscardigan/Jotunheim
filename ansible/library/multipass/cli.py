"""CLI utility functions for managing Multipass VMs from within an Ansible module."""

from multipass.logging_utils import log
from multipass.utils import run_command


def list_vms() -> list[str]:
    """List all active Multipass VM names."""
    log.info("Listing current VMs")
    result = run_command(["multipass", "list"])
    return [
        line.split()[0]
        for line in result.stdout.splitlines()
        if line and not line.startswith(("Name", "No"))
    ]


def count_vms() -> int:
    """Return the number of active Multipass VMs."""
    return len(list_vms())


def purge_vms() -> tuple[bool, str]:
    """Purge all deleted Multipass VMs."""
    log.debug("Purging multipass instances")
    result = run_command(["multipass", "purge", "--verbose"])

    if result.returncode == 0:
        return True, "Multipass purged"

    log.error(result.stderr)
    return False, result.stderr


def multipass_installed() -> bool:
    """Check if Multipass is installed and accessible."""
    return run_command(["multipass", "version"]).returncode == 0
