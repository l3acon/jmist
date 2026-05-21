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
