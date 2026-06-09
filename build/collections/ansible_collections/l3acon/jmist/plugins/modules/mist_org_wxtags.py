#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_wxtags"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_wxtags
short_description: Manage WxTags (labels) in Juniper Mist
description:
  - Manage WxTag label resources in Juniper Mist organizations.
  - WxTags are used to classify and tag devices, clients, and resources
    for use in WxLAN policies.
  - This module supports creating, updating, deleting, and gathering WxTags.
version_added: "1.0.0"
author:
  - Juniper Mist Ansible Collection Contributors
options:
    api_token:
      description:
        - "API token for Mist authentication. Can also be set via MIST_API_TOKEN env var."
      type: str
      no_log: true
    base_url:
      description:
        - "Base URL for the Mist API endpoint."
      type: str
      default: "https://api.mist.com"
    validate_certs:
      description:
        - "Whether to validate SSL certificates."
      type: bool
      default: true
    timeout:
      description:
        - "HTTP request timeout in seconds."
      type: int
      default: 30
    org_id:
      description:
        - "Organization ID for the resource."
      type: str
      required: true
    wxtag_id:
      description:
        - "Unique identifier of the WxTag. Required for state=absent or updating an existing tag."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    name:
      description:
        - "The name of the WxTag label."
      type: str
    type:
      description:
        - "The type of WxTag."
      type: str
      choices: ["client", "match", "resource", "spec", "subnet", "vlan"]
    match:
      description:
        - "Match criteria when type is 'match'."
      type: str
      choices: ["ap_id", "app", "asset_mac", "client_mac", "hostname", "ip_range_subnet", "port", "psk_name", "psk_role", "radius_attr", "radius_class", "radius_group", "radius_username", "sdkclient_uuid", "wlan_id"]
    op:
      description:
        - "Operation type for match tags (inclusive or exclusive)."
      type: str
      choices: ["in", "not_in"]
      default: "in"
    values:
      description:
        - "List of values for the tag. Content depends on the type and match fields."
        - "For match=ap_id, this is a list of AP IDs."
        - "For match=client_mac, this is a list of client MAC addresses."
        - "By default, values are merged with existing values (see values_mode)."
      type: list
      elements: str
    values_mode:
      description:
        - "How to handle the values list when updating an existing tag."
        - "merge (default): Add the provided values to the existing list (deduplicated)."
        - "replace: Replace the entire values list with the provided values."
        - "remove: Remove the provided values from the existing list."
      type: str
      choices: ["merge", "replace", "remove"]
      default: "merge"
    mac:
      description:
        - "Client MAC address when type is 'client'."
      type: str
    subnet:
      description:
        - "Subnet when type is 'subnet'."
      type: str
    vlan_id:
      description:
        - "VLAN ID when type is 'vlan'."
      type: str
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a WxTag label for AP matching
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: present
    name: "my-ap-label"
    type: match
    match: ap_id
    values:
      - "00000000-0000-0000-1000-a8537d897e7d"

- name: Add APs to an existing WxTag (merge is the default)
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values:
      - "00000000-0000-0000-1000-a8537d897e7d"
      - "00000000-0000-0000-1000-aabbccddeeff"

- name: Replace all values on a WxTag (overwrite existing)
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values_mode: replace
    values:
      - "00000000-0000-0000-1000-a8537d897e7d"

- name: Remove specific APs from a WxTag
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values_mode: remove
    values:
      - "00000000-0000-0000-1000-aabbccddeeff"

- name: Delete a WxTag
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: absent

- name: Gather all WxTags
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    state: gathered
"""

RETURN = """
response:
  description: The API response from Mist.
  returned: when state is present
  type: dict
gathered:
  description: List of gathered WxTag resources when state=gathered.
  returned: when state is gathered
  type: list
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.l3acon.jmist.plugins.module_utils.mist_api import MistApiClient


def build_payload(module):
    """Build the API request payload from module parameters."""
    payload = {}
    config_params = [
        'name',
        'type',
        'match',
        'op',
        'values',
        'mac',
        'subnet',
        'vlan_id',
    ]
    for param in config_params:
        value = module.params.get(param)
        if value is not None:
            payload[param] = value
    return payload


def main():
    argument_spec = dict(
        api_token=dict(type='str', no_log=True),
        base_url=dict(type='str', default='https://api.mist.com'),
        validate_certs=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        follow_redirects=dict(type='str', choices=['all', 'no', 'safe', 'urllib2'], default='all'),
        org_id=dict(type='str', required=True),
        wxtag_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        name=dict(type='str'),
        type=dict(type='str', choices=['client', 'match', 'resource', 'spec', 'subnet', 'vlan']),
        match=dict(type='str', choices=['ap_id', 'app', 'asset_mac', 'client_mac', 'hostname', 'ip_range_subnet', 'port', 'psk_name', 'psk_role', 'radius_attr', 'radius_class', 'radius_group', 'radius_username', 'sdkclient_uuid', 'wlan_id']),
        op=dict(type='str', choices=['in', 'not_in'], default='in'),
        values=dict(type='list', elements='str'),
        values_mode=dict(type='str', choices=['merge', 'replace', 'remove'], default='merge'),
        mac=dict(type='str'),
        subnet=dict(type='str'),
        vlan_id=dict(type='str'),
    )

    required_if = [
        ('state', 'absent', ['wxtag_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id']
    resource_id = module.params.get('wxtag_id')

    result = dict(changed=False)

    values_mode = module.params.get('values_mode', 'merge')
    new_values = module.params.get('values')

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/wxtags'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            # For updates, handle values merge/replace/remove
            if new_values is not None and values_mode != 'replace':
                current = client.get(
                    '/api/v1/orgs/{org_id}/wxtags/{wxtag_id}'.format(org_id=org_id, wxtag_id=resource_id),
                )
                existing_values = current.get('values', []) or []

                if values_mode == 'merge':
                    merged = list(dict.fromkeys(existing_values + new_values))
                    payload['values'] = merged
                elif values_mode == 'remove':
                    payload['values'] = [v for v in existing_values if v not in new_values]

                if payload.get('values') == existing_values:
                    result['changed'] = False
                    result['response'] = current
                    module.exit_json(**result)
                    return

            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/wxtags/{wxtag_id}'.format(org_id=org_id, wxtag_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/wxtags'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="wxtag_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/wxtags/{wxtag_id}'.format(org_id=org_id, wxtag_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
