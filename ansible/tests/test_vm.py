"""Unit tests for the MultipassVM class in multipass.vm."""

from unittest.mock import patch, MagicMock
import pytest

from multipass.vm import MultipassVM, ProvisionSpec


@pytest.fixture
def _vm_name() -> str:
    """Fixture to provide a default VM name."""
    return "test-vm"


@pytest.fixture
def _default_spec() -> ProvisionSpec:
    """Fixture to provide a default provision spec."""
    return ProvisionSpec(
        memory=1,
        cores=1,
        disk=8,
        image="lts",
        cloud_init="/path/to/cloud-init.yaml",
    )


def make_completed_process(returncode=0, stdout="", stderr=""):
    """Create a mock subprocess.CompletedProcess result."""
    mock_proc = MagicMock()
    mock_proc.returncode = returncode
    mock_proc.stdout = stdout
    mock_proc.stderr = stderr
    return mock_proc


@patch("multipass.vm.run_command")
def test_vm_initializes_as_absent_when_not_found(mock_run, _vm_name):
    """Verify VM initializes as absent when multipass info fails."""
    mock_run.return_value = make_completed_process(returncode=1)

    vm = MultipassVM(_vm_name, "present")

    assert vm.state == "absent"
    assert vm.name == _vm_name


@patch("multipass.vm.run_command")
def test_vm_initializes_as_present_and_parses_info(mock_run, _vm_name):
    """Verify VM initializes as present and parses cores/mem/disk correctly."""
    mock_run.return_value = make_completed_process(
        stdout="""Name: test-vm
State: Running
CPU(s): 2
Memory usage: 1.0Gib out of 2.0Gib
Disk usage: 4.0Gib out of 8.0Gib
"""
    )

    vm = MultipassVM(_vm_name, "present")

    assert vm.state == "present"
    assert vm.cores == 2
    assert vm.memory_gb == 1.0
    assert vm.disk_gb == 4.0


@patch("multipass.vm.run_command")
def test_provision_skips_if_vm_present(mock_run, _vm_name, _default_spec):
    """Verify provision() skips when VM is already present."""
    mock_run.return_value = make_completed_process(stdout="CPU(s): 1")
    vm = MultipassVM(_vm_name, "present")

    changed, msg = vm.provision(_default_spec)

    assert changed is False
    assert msg == "Host already present"


@patch("multipass.vm.run_command")
def test_provision_succeeds(mock_run, _vm_name, _default_spec):
    """Verify successful provisioning changes state and returns success."""
    mock_run.side_effect = [
        make_completed_process(returncode=1),  # info
        make_completed_process(returncode=0),  # launch
    ]

    vm = MultipassVM(_vm_name, "present")
    changed, msg = vm.provision(_default_spec)

    assert changed is True
    assert msg == "Provisioned"
    assert vm.state == "present"


@patch("multipass.vm.run_command")
def test_provision_fails(mock_run, _vm_name, _default_spec):
    """Verify provision() returns stderr message on failure."""
    mock_run.side_effect = [
        make_completed_process(returncode=1),  # info
        make_completed_process(returncode=1, stderr="Boom"),  # launch
    ]

    vm = MultipassVM(_vm_name, "present")
    changed, msg = vm.provision(_default_spec)

    assert changed is False
    assert msg == "Boom"


@patch("multipass.vm.run_command")
def test_remove_skips_if_absent(mock_run, _vm_name):
    """Verify remove() is skipped when VM is already absent."""
    mock_run.return_value = make_completed_process(returncode=1)
    vm = MultipassVM(_vm_name, "absent")

    changed, msg = vm.remove()

    assert changed is False
    assert "already" in msg


@patch("multipass.vm.run_command")
def test_remove_succeeds(mock_run, _vm_name):
    """Verify remove() deletes the VM if it exists."""
    mock_run.side_effect = [
        make_completed_process(stdout="CPU(s): 1"),  # info
        make_completed_process(returncode=0),  # delete
    ]

    vm = MultipassVM(_vm_name, "absent")
    changed, msg = vm.remove()

    assert changed is True
    assert msg == "Deleted"
    assert vm.state == "absent"
