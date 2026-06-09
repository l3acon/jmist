#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_sitegroups"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_sitegroups
short_description: Manage sitegroups in Juniper Mist
description:
  - Manage Orgs Sitegroups resources in Juniper Mist
  - This module supports state-based management of sitegroups resources.
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
    sitegroup_id:
      description:
        - "Unique identifier of the sitegroups resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    name:
      description:
        - "The name parameter."
      type: str
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a sitegroups resource
  l3acon.jmist.mist_org_sitegroups:
    org_id: "your-org-id"
    state: present
    name: "example-sitegroups"

- name: Delete a sitegroups resource
  l3acon.jmist.mist_org_sitegroups:
    org_id: "your-org-id"
    sitegroup_id: "resource-uuid"
    state: absent

- name: Gather sitegroups resources
  l3acon.jmist.mist_org_sitegroups:
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
        'name',
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
        sitegroup_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        name=dict(type='str'),
    )

    required_if = [
        ('state', 'absent', ['sitegroup_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id']
    resource_id = module.params.get('sitegroup_id')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/sitegroups'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}'.format(org_id=org_id, sitegroup_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/sitegroups'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="sitegroup_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/sitegroups/{sitegroup_id}'.format(org_id=org_id, sitegroup_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
