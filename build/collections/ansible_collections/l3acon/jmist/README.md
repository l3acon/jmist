# Juniper Mist Ansible Collection

Ansible collection for managing Juniper Mist cloud infrastructure via REST API.

## Requirements

- Python >= 3.9
- Ansible >= 2.15

## Installation

```bash
ansible-galaxy collection install l3acon.jmist
```

## Authentication

All modules require a Mist API token. You can provide it in three ways:

1. Module parameter: `api_token: "your-token"`
2. Environment variable: `export MIST_API_TOKEN="your-token"`
3. Ansible variable: Set in inventory or playbook vars

## Available Modules

| Module | Description |
|--------|-------------|
| `l3acon.jmist.mist_org_sites` | Manage sites within an organization |
| `l3acon.jmist.mist_org_networks` | Manage networks |
| `l3acon.jmist.mist_org_wlans` | Manage organization-level WLANs |
| `l3acon.jmist.mist_org_psks` | Manage pre-shared keys |
| `l3acon.jmist.mist_org_webhooks` | Manage webhooks |
| `l3acon.jmist.mist_org_sitegroups` | Manage site groups |
| `l3acon.jmist.mist_org_templates` | Manage templates |
| `l3acon.jmist.mist_org_servicepolicies` | Manage service policies |
| `l3acon.jmist.mist_org_services` | Manage services |
| `l3acon.jmist.mist_org_vpns` | Manage VPNs |
| `l3acon.jmist.mist_site_wlans` | Manage site-level WLANs |
| `l3acon.jmist.mist_site_psks` | Manage site-level pre-shared keys |
| `l3acon.jmist.mist_site_webhooks` | Manage site-level webhooks |

## Usage Examples

### Create a site

```yaml
- name: Create a new site
  l3acon.jmist.mist_org_sites:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: present
    name: "Branch Office NYC"
    address: "123 Main St, New York, NY"
    timezone: "America/New_York"
    country_code: "US"
```

### Create a WLAN

```yaml
- name: Create corporate WLAN
  l3acon.jmist.mist_org_wlans:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: present
    ssid: "Corporate-WiFi"
    auth:
      type: "psk"
      psk: "SecurePassword123"
    band_steer: true
```

### Gather all networks

```yaml
- name: Get all networks
  l3acon.jmist.mist_org_networks:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: gathered
  register: networks

- debug:
    var: networks.gathered
```

### Delete a resource

```yaml
- name: Remove a webhook
  l3acon.jmist.mist_org_webhooks:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    webhook_id: "{{ webhook_to_delete }}"
    state: absent
```

## Regional Endpoints

Mist has multiple regional API endpoints. Set `base_url` to target a specific region:

| Region | URL |
|--------|-----|
| Global 01 (default) | `https://api.mist.com` |
| EMEA 01 | `https://api.eu.mist.com` |
| APAC 01 | `https://api.ac5.mist.com` |

```yaml
- name: Use EU endpoint
  l3acon.jmist.mist_org_sites:
    api_token: "{{ mist_token }}"
    base_url: "https://api.eu.mist.com"
    org_id: "{{ org_id }}"
    state: gathered
```

## Module States

All modules support the following states:

- `present` - Create or update a resource
- `absent` - Delete a resource (requires the resource ID)
- `gathered` - Retrieve all resources of this type

## License

GNU General Public License v3.0 or later.
