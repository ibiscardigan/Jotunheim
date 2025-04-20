"""Ansible module wrapper to manage Multipass VMs.

Supports creation, deletion, purging, listing, and state-checking of VMs using
the `multipass` CLI. Logging integrates with ansible-execute’s JSON logging framework.
"""

from multipass.logging_utils import setup_logger
from multipass.vm import MultipassVM, ProvisionSpec
from multipass.cli import list_vms, count_vms, purge_vms, multipass_installed

from ansible.module_utils.basic import AnsibleModule

log, log_path = setup_logger()


def run_module():
    """Main module logic for processing arguments and calling Multipass helpers."""
    module_args = {
        "name": {"type": "str", "required": False, "default": None},
        "state": {
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "cores": {"type": "int", "default": 1},
        "disk_space": {"type": "int", "default": 8},
        "memory": {"type": "int", "default": 1},
        "image": {"type": "str", "default": "lts"},
        "cloud_init": {"type": "str"},
        "purge": {"type": "bool", "default": False},
        "list": {"type": "bool", "default": False},
    }

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)
    p = module.params

    if not multipass_installed():
        module.fail_json(msg="Multipass is not installed", changed=False)

    if p["list"]:
        module.exit_json(changed=False, vm_list=list_vms(), log_path=log_path)

    if p["purge"]:
        before = count_vms()
        success, msg = purge_vms()
        after = count_vms()
        module.exit_json(
            changed=success and before != after, message=msg, log_path=log_path
        )

    if not p["name"]:
        module.fail_json(msg="Missing required 'name' when not using purge/list")

    vm = MultipassVM(p["name"], p["state"])

    if module.check_mode:
        module.exit_json(changed=False, state=vm.state)

    if p["state"] == "present":
        spec = ProvisionSpec(
            memory=p["memory"],
            cores=p["cores"],
            disk=p["disk_space"],
            image=p["image"],
            cloud_init=p["cloud_init"],
        )
        changed, msg = vm.provision(spec)
    else:
        changed, msg = vm.remove()

    module.exit_json(changed=changed, message=msg, log_path=log_path)


def main():
    """Entry point for Ansible to invoke the module."""
    run_module()
