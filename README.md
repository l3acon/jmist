# l3acon.jmist

Ansible collection for managing Juniper Mist cloud infrastructure via REST API.

## Prerequisites

- Python >= 3.9
- Ansible >= 2.15

## Quick Start

```bash
# Clone and set up the development environment
git clone https://github.com/l3acon/jmist.git
cd jmist
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Download the Mist OpenAPI spec (not stored in repo)
./scripts/download_spec.sh
```

## Authentication

Create a `.env` file in the project root (git-ignored):

```bash
ORG_ID="your-org-id"
MIST_TOKEN="your-api-token"
MIST_BASE_URL="https://api.mist.com"  # or your regional endpoint
```

Export these before running playbooks:

```bash
source .env && export ORG_ID MIST_TOKEN MIST_BASE_URL
```

Modules accept credentials via:

1. Module parameter: `api_token: "{{ mist_token }}"`
2. Environment variable: `MIST_API_TOKEN` or `MIST_TOKEN`
3. Playbook variable passed to `api_token`

### Regional Endpoints

| Region | URL |
|--------|-----|
| Global 01 (default) | `https://api.mist.com` |
| Global 04 | `https://api.gc4.mist.com` |
| EMEA 01 | `https://api.eu.mist.com` |
| APAC 01 | `https://api.ac5.mist.com` |

## Deploying to Ansible Automation Platform

Add `AAP_HOSTNAME` (the full HTTPS URL) and either `AAP_OAUTH_TOKEN` or
`AAP_USERNAME` and `AAP_PASSWORD` to `.env`, alongside the Mist settings above.
The account needs permission to create credential types, projects, inventories,
credentials, templates, users, and role assignments.

```bash
ansible-galaxy collection install -r casc/requirements.yml \
  --server https://galaxy.ansible.com -p ./build/collections
set -a
source .env
set +a
ansible-playbook -i localhost, casc/configure_aap.yaml
```

The deployment uses the AAP gateway and controller APIs. When no valid OAuth
token is supplied, it creates a temporary gateway token using the supplied
username/password and revokes it when the deployment finishes. The current lab
configuration disables AAP certificate validation.

This creates the `Juniper Mist Collection` project from GitHub's `master` branch,
the `Localhost` inventory, a `Juniper Mist API` credential type, the `Mist API - Lab`
credential populated from `.env`, and these survey-driven job templates:

- `Mist - Assign AP to WxTag`
- `Mist - Remove AP from WxTag`

It also provisions the operator account and execute permissions defined in
`casc/users.yaml`. Review that file before deploying to another environment.
The operator password is applied to both the controller and the AAP gateway.

Launch either template with one or more AP MAC addresses and a label name.
Paste MAC addresses into **AP MAC Addresses**, one per line or separated by
commas or spaces. All devices in the job use the selected label. Assign merges
the devices into the label; Remove removes only the listed devices and leaves
the other devices on the label. These jobs manage label membership for
installations/decommissioning; they do not claim or delete devices in Mist.

The entire batch is validated before any Mist API calls, and duplicate MACs
are handled once. Colon, hyphen, dotted, and unseparated MAC formats are
supported. Choose the `Check` job type to verify API connectivity and preview
the operation without changing Mist. The label choices are configured in
`casc/job_templates.yaml`. Re-run the deployment playbook after deploying these
changes to update the existing template surveys.

For CLI or API launches, pass `ap_macs` as text or a YAML/JSON list, for example
in `devices.yaml`:

```yaml
ap_macs:
  - "a8:53:7d:89:7e:7d"
  - "d4:dc:09:2a:7b:4d"
tag_name: matt-label1
```

```bash
# With Mist credentials supplied as playbook variables or an AAP credential
ansible-playbook playbooks/mist_wxtag_assign_ap.yaml -e @devices.yaml --check
ansible-playbook playbooks/mist_wxtag_remove_ap.yaml -e @devices.yaml --check
```

The legacy single-device `ap_mac` variable is still supported when `ap_macs`
is omitted. When both are supplied, `ap_macs` takes precedence.

Mist secrets are stored in the AAP credential and injected into jobs; `.env`
stays local and is not part of the GitHub project.

## Project Structure

```
.
├── build/collections/ansible_collections/l3acon/jmist/   # The collection
│   ├── plugins/modules/          # Resource modules
│   ├── plugins/lookup/           # Lookup plugins
│   ├── plugins/module_utils/     # Shared API client
│   └── plugins/httpapi/          # HTTPAPI connection plugin
├── tools/                        # Code generation tooling
│   ├── mist_spec_parser.py       # Parses OpenAPI spec → intermediate JSON
│   └── generate_modules.py       # Generates Ansible modules from JSON
├── scripts/
│   └── download_spec.sh          # Downloads the OpenAPI spec
├── specs/                        # OpenAPI spec (git-ignored)
├── test_playbook.yaml            # Basic module validation
└── test_wxtag_playbook.yaml      # WxTag + lookup plugin tests
```

## Usage

Playbooks reference the collection path via `ansible.cfg`:

```ini
[defaults]
collections_path=./build/collections
```

### Managing WxTags (AP Labels)

```yaml
- hosts: localhost
  connection: local
  gather_facts: false
  vars:
    org_id: "{{ lookup('ansible.builtin.env', 'ORG_ID') }}"
    mist_token: "{{ lookup('ansible.builtin.env', 'MIST_TOKEN') }}"
    mist_base_url: "{{ lookup('ansible.builtin.env', 'MIST_BASE_URL') }}"

  tasks:
    - name: Look up AP ID from MAC address
      ansible.builtin.set_fact:
        ap_id: "{{ lookup('l3acon.jmist.lookup_ap_by_mac', 'aa:bb:cc:dd:ee:00') }}"

    - name: Look up tag ID by name
      ansible.builtin.set_fact:
        tag_id: "{{ lookup('l3acon.jmist.lookup_label_id_by_name', 'my-tag', org_id=org_id, api_token=mist_token, base_url=mist_base_url) }}"

    - name: Add AP to WxTag (merge is the default - won't remove existing APs)
      l3acon.jmist.mist_org_wxtags:
        api_token: "{{ mist_token }}"
        base_url: "{{ mist_base_url }}"
        org_id: "{{ org_id }}"
        wxtag_id: "{{ tag_id }}"
        state: present
        values:
          - "{{ ap_id }}"
```

### The `values_mode` Parameter

When updating WxTag values, the module defaults to **merge** behavior to prevent accidentally overwriting the AP list:

| Mode | Behavior |
|------|----------|
| `merge` (default) | Adds provided values to the existing list (deduplicated) |
| `replace` | Overwrites the entire values list |
| `remove` | Removes provided values from the existing list |

```yaml
- name: Replace all APs on a tag
  l3acon.jmist.mist_org_wxtags:
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values_mode: replace
    values:
      - "00000000-0000-0000-0000-000000000000"

- name: Remove a specific AP from a tag
  l3acon.jmist.mist_org_wxtags:
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values_mode: remove
    values:
      - "00000000-0000-0000-1000-aabbccddeeff"
```

### Other Resource Modules

All resource modules follow the same pattern with `state: present|absent|gathered`:

```yaml
- name: Create a site
  l3acon.jmist.mist_org_sites:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: present
    name: "Branch Office"

- name: Gather all networks
  l3acon.jmist.mist_org_networks:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: gathered
  register: networks
```

## Available Plugins

### Modules

| Module | Description |
|--------|-------------|
| `mist_org_sites` | Manage sites |
| `mist_org_networks` | Manage networks |
| `mist_org_wlans` | Manage organization WLANs |
| `mist_org_psks` | Manage pre-shared keys |
| `mist_org_webhooks` | Manage webhooks |
| `mist_org_sitegroups` | Manage site groups |
| `mist_org_templates` | Manage templates |
| `mist_org_servicepolicies` | Manage service policies |
| `mist_org_services` | Manage services |
| `mist_org_vpns` | Manage VPNs |
| `mist_org_wxtags` | Manage WxTags (AP labels) |
| `mist_site_wlans` | Manage site-level WLANs |
| `mist_site_psks` | Manage site-level PSKs |
| `mist_site_webhooks` | Manage site-level webhooks |

### Lookup Plugins

| Plugin | Description |
|--------|-------------|
| `lookup_ap_by_mac` | Convert AP MAC address to Mist device ID |
| `lookup_label_id_by_name` | Find a WxTag ID by its name |

## Testing

### Offline Demo Tests

```bash
python3 -m unittest discover -s tests -v
```

These run the demo playbooks against a local fake Mist API to check batch
assignment/removal, validation, duplicate handling, idempotency, and check mode.
They do not require Mist credentials or change real devices.

### Running Test Playbooks

```bash
source .env && export ORG_ID MIST_TOKEN MIST_BASE_URL
source .venv/bin/activate

# Basic module check-mode test (no API calls)
ansible-playbook test_playbook.yaml --check

# Live WxTag + lookup plugin test (makes API calls)
ansible-playbook test_wxtag_playbook.yaml
```

### Check Mode

All modules support `--check` for dry-run validation without making API changes.

## Regenerating Modules

If the upstream OpenAPI spec changes:

```bash
# Download fresh spec
./scripts/download_spec.sh

# Parse spec into intermediate JSON
python tools/mist_spec_parser.py

# Regenerate module files
python tools/generate_modules.py
```

## License

GPL-3.0-or-later
