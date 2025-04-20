"""Encapsulates Multipass VM state, provisioning, and teardown logic."""

from dataclasses import dataclass
from multipass.logging_utils import log
from multipass.utils import run_command


@dataclass
class ProvisionSpec:
    """Arguments required to provision a Multipass VM."""

    memory: int
    cores: int
    disk: int
    image: str
    cloud_init: str


class MultipassVM:
    """Representation of a Multipass-managed VM and its lifecycle."""

    def __init__(self, name: str, intended_state: str):
        """
        Initialize a VM object and determine if it currently exists.

        Args:
            name: Name of the Multipass instance.
            intended_state: Desired state of the instance ("present" or "absent").
        """
        self.name = name
        self.intended_state = intended_state
        self.state = "absent"
        self.cores = self.memory_gb = self.disk_gb = None

        info = run_command(["multipass", "info", name])
        if info.returncode == 0:
            self.state = "present"
            log.info("VM found")
            self._parse_info(info.stdout)
        else:
            log.info("VM not found")

        log.debug(
            "%s initialized: intended=%s, actual=%s",
            self.name,
            self.intended_state,
            self.state,
        )

    @staticmethod
    def _convert_to_gb(val: str) -> float:
        """Convert a memory or disk value to GB."""
        if val.endswith("Mib"):
            return round(float(val[:-3]) / 1000, 2)
        if val.endswith("Gib"):
            return round(float(val[:-3]), 2)
        raise ValueError(f"Unexpected memory/disk format: {val}")

    def _parse_info(self, info: str):
        """Parse the output from `multipass info`."""
        out = dict(
            line.strip().split(": ", 1) for line in info.splitlines() if ": " in line
        )
        self.cores = int(out.get("CPU(s)", "1"))
        self.memory_gb = self._convert_to_gb(out.get("Memory usage", "0Gib").split()[0])
        self.disk_gb = self._convert_to_gb(out.get("Disk usage", "0Gib").split()[0])

    def provision(self, spec: ProvisionSpec) -> tuple[bool, str]:
        """
        Provision a new VM if one does not exist.

        Args:
            spec: A ProvisionSpec containing configuration values.

        Returns:
            Tuple[bool, str]: Whether provisioning changed state and message.
        """
        if self.state == "present":
            return False, "Host already present"

        cmd = [
            "multipass",
            "launch",
            spec.image,
            "--name",
            self.name,
            "--disk",
            f"{spec.disk}G",
            "--memory",
            f"{spec.memory}G",
            "--cpus",
            str(spec.cores),
            "--network",
            "en0",
            "--cloud-init",
            spec.cloud_init,
        ]
        log.info("Provisioning: %s", cmd)
        result = run_command(cmd)

        if result.returncode == 0:
            self.state = "present"
            return True, "Provisioned"

        log.error(result.stderr)
        return False, result.stderr

    def remove(self) -> tuple[bool, str]:
        """Remove the VM if present."""
        if self.state != "present":
            return False, f"Host already {self.state}"

        result = run_command(["multipass", "delete", self.name])
        if result.returncode == 0:
            self.state = "absent"
            return True, "Deleted"

        log.error(result.stderr)
        return False, result.stderr
