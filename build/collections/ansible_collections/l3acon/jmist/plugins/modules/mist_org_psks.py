#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_psks"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_psks
short_description: Manage psks in Juniper Mist
description:
  - Manage Orgs Psks resources in Juniper Mist
  - This module supports state-based management of psks resources.
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
    psk_id:
      description:
        - "Unique identifier of the psks resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    admin_sso_id:
      description:
        - "sso id for psk created from psk portal"
      type: str
    email:
      description:
        - "email to send psk expiring notifications to"
      type: str
    expire_time:
      description:
        - "Expire time for this PSK key (epoch time in seconds). Default `null` (as no expiration)"
      type: int
    expiry_notification_time:
      description:
        - "Number of days before psk is expired. Used as to when to start sending reminder notification when the psk is about to expire"
      type: int
    mac:
      description:
        - "If `usage`==`single`, the mac that this PSK ties to, empty if `auto-binding`"
      type: str
    macs:
      description:
        - "If `usage`==`macs`, this list contains N number of client mac addresses or mac patterns(1122*) or both. This list is capped at 5000"
      type: list
      elements: str
    max_usage:
      description:
        - "For Org PSK Only. Max concurrent users for this PSK key. Default is 0 (unlimited)"
      type: int
      default: 0
    name:
      description:
        - "The name parameter."
      type: str
      required: true
    note:
      description:
        - "The note parameter."
      type: str
    notify_expiry:
      description:
        - "If set to true, reminder notification will be sent when psk is about to expire"
      type: bool
      default: false
    notify_on_create_or_edit:
      description:
        - "If set to true, notification will be sent when psk is created or edited"
      type: bool
    old_passphrase:
      description:
        - "previous passphrase of the PSK if it has been rotated"
      type: str
    passphrase:
      description:
        - "passphrase of the PSK (8-63 character or 64 in hex)"
      type: str
      required: true
    role:
      description:
        - "The role parameter."
      type: str
    ssid:
      description:
        - "SSID this PSK should be applicable to"
      type: str
      required: true
    usage:
      description:
        - "enum: `macs`, `multi`, `single`"
      type: str
      choices: ["macs", "multi", "single"]
      default: "multi"
    vlan_id:
      description:
        - "VLAN for this PSK key"
      type: str
    vlan_name:
      description:
        - "VLAN name to be assigned. Optional, `vlan_id` takes precedence if both are provided"
      type: str
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a psks resource
  l3acon.jmist.mist_org_psks:
    org_id: "your-org-id"
    state: present
    name: "example-psks"

- name: Delete a psks resource
  l3acon.jmist.mist_org_psks:
    org_id: "your-org-id"
    psk_id: "resource-uuid"
    state: absent

- name: Gather psks resources
  l3acon.jmist.mist_org_psks:
    org_id: "your-org-id"
    state: gathered
"""

RETURN = """
response:
  description: The API response from Mist.
  returned: always
  type: dict
gathered:
  description: List of gathered resources when state=gathered.
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
        'admin_sso_id',
        'email',
        'expire_time',
        'expiry_notification_time',
        'mac',
        'macs',
        'max_usage',
        'name',
        'note',
        'notify_expiry',
        'notify_on_create_or_edit',
        'old_passphrase',
        'passphrase',
        'role',
        'ssid',
        'usage',
        'vlan_id',
        'vlan_name',
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
        psk_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        admin_sso_id=dict(type='str'),
        email=dict(type='str'),
        expire_time=dict(type='int'),
        expiry_notification_time=dict(type='int'),
        mac=dict(type='str'),
        macs=dict(type='list', elements='str'),
        max_usage=dict(type='int', default=0),
        name=dict(type='str'),
        note=dict(type='str'),
        notify_expiry=dict(type='bool', default=False),
        notify_on_create_or_edit=dict(type='bool'),
        old_passphrase=dict(type='str'),
        passphrase=dict(type='str'),
        role=dict(type='str'),
        ssid=dict(type='str'),
        usage=dict(type='str', choices=['macs', 'multi', 'single'], default='multi'),
        vlan_id=dict(type='str'),
        vlan_name=dict(type='str'),
    )

    required_if = [
        ('state', 'absent', ['psk_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id'].strip()
    resource_id = module.params.get('psk_id')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/psks'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/psks/{psk_id}'.format(org_id=org_id, psk_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/psks'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="psk_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/psks/{psk_id}'.format(org_id=org_id, psk_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
