# Jotunheim

**The Giant Homelab — Modular, Automated, Self-Hosted Infrastructure**

---

## Overview

Jotunheim is a fully automated, self-hosted infrastructure stack managed with Ansible. Designed for flexibility and modularity, it supports a wide range of homelab deployments from Raspberry Pis to full rack-mounted servers.

The project uses:
- **Ansible** for configuration management
- **Pre-commit hooks** and linters for quality control
- A custom tool [`ansible-execute`](https://github.com/ibiscardigan/ansible-execute) to standardize Ansible usage

---

## Features

- Modular Ansible roles for common services like:
  - DNS (Unbound, Pi-hole)
  - Monitoring (VictoriaMetrics, vmagent)
  - Scheduling (Nomad)
  - Discovery (Consul)
- Environment-based configuration via inventories
- Preflight checks and structured logging
- Role-based execution using tags and dynamic facts
- Designed for both bare-metal and virtualized deployments

---

## Getting Started

### Requirements

- Python 3.10+
- Ansible 9+
- `ansible-execute` tool:
  ```bash
  pip install --upgrade --force-reinstall git+https://github.com/ibiscardigan/ansible-execute.git
  ```

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/ibiscardigan/Jotunheim.git
   cd Jotunheim
   ```

2. Install dependencies:
   ```bash
   ansible-galaxy install -r requirements.yml
   ```

3. Configure your environment:
   - Set up `execute_config.yml` (see template)
   - Define your environments in `ansible/inventory/`

4. Run a playbook:
   ```bash
   ansible-execute -e dev -p deploy_unbound.yml
   ```

---

## Project Structure

```bash
Jotunheim/
├── ansible/
│   ├── inventory/         # Environment-specific host inventories
│   ├── playbooks/         # Entry-point playbooks
│   └── roles/             # Modular Ansible roles
├── execute_config.yml     # Configuration for ansible-execute
├── requirements.yml       # Ansible Galaxy roles/collections
├── .pre-commit-config.yaml
├── .ansible-lint, .flake8, .pylintrc, .yamllint
```

---

## Development

Run lint checks with:

```bash
pre-commit run --all-files
```

---

## Security

This project follows security best practices:

- Secrets should be managed via Ansible Vault
- Pre-commit enforces linting of YAML and Python
- Enable GitHub secret scanning for additional protection

Future improvements:
- Add `SECURITY.md`
- Enable CI/CD workflows (e.g., GitHub Actions)

---

## License

MIT License

---

## Contributions

Pull requests, issues, and forks are welcome

---
