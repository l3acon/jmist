#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_services"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_services
short_description: Manage services in Juniper Mist
description:
  - Manage Orgs Services resources in Juniper Mist
  - This module supports state-based management of services resources.
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
    service_id:
      description:
        - "Unique identifier of the services resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    addresses:
      description:
        - "If `type`==`custom`, IPv4 and/or IPv6 subnets (e.g. 10.0.0.0/8, fd28::/128)"
      type: list
      elements: str
    app_categories:
      description:
        - "When `type`==`app_categories`, list of application categories are available through [List App Category Definitions](/#operations/listAppCategoryDefinitions)"
      type: list
      elements: str
    app_subcategories:
      description:
        - "When `type`==`app_categories`, list of application categories are available through [List App Sub Category Definitions](/#operations/listAppSubCategoryDefinitions)"
      type: list
      elements: str
    apps:
      description:
        - "When `type`==`apps`, list of applications are available through:   * [List Applications](/#operations/listApplications)   * [List Gateway Applications](/#operations/listGatewayApplications)   * /in..."
      type: list
      elements: str
    client_limit_down:
      description:
        - "0 means unlimited, value from 0 to 107374182"
      type: int
      default: 0
    client_limit_up:
      description:
        - "0 means unlimited, value from 0 to 107374182"
      type: int
      default: 0
    description:
      description:
        - "The description parameter."
      type: str
    dscp:
      description:
        - "For SSR only, when `traffic_type`==`custom`. 0-63 or variable"
      type: str
    failover_policy:
      description:
        - "enum: `non_revertible`, `none`, `revertible`"
      type: str
      choices: ["non_revertible", "none", "revertible"]
      default: "revertible"
    hostnames:
      description:
        - "If `type`==`custom`, web filtering"
      type: list
      elements: str
    max_jitter:
      description:
        - "For SSR only, when `traffic_type`==`custom`, for uplink selection. 0-2147483647 or variable"
      type: str
    max_latency:
      description:
        - "For SSR only, when `traffic_type`==`custom`, for uplink selection. 0-2147483647 or variable"
      type: str
    max_loss:
      description:
        - "For SSR only, when `traffic_type`==`custom`, for uplink selection. 0-100 or variable"
      type: str
    name:
      description:
        - "The name parameter."
      type: str
    service_limit_down:
      description:
        - "0 means unlimited, value from 0 to 107374182"
      type: int
      default: 0
    service_limit_up:
      description:
        - "0 means unlimited, value from 0 to 107374182"
      type: int
      default: 0
    sle_enabled:
      description:
        - "Whether to enable measure SLE"
      type: bool
      default: false
    specs:
      description:
        - "When `type`==`custom`, optional, if it doesn't exist, http and https is assumed"
      type: list
      elements: dict
    ssr_relaxed_tcp_state_enforcement:
      description:
        - "The ssr_relaxed_tcp_state_enforcement parameter."
      type: bool
      default: false
    traffic_class:
      description:
        - "when `traffic_type`==`custom`. enum: `best_effort`, `high`, `low`, `medium`"
      type: str
      choices: ["best_effort", "high", "low", "medium"]
      default: "best_effort"
    traffic_type:
      description:
        - "values from [List Traffic Types](/#operations/listTrafficTypes)"
      type: str
      default: "data_best_effort"
    type:
      description:
        - "enum: `app_categories`, `apps`, `custom`, `urls`"
      type: str
      choices: ["app_categories", "apps", "custom", "urls"]
      default: "custom"
    urls:
      description:
        - "When `type`==`urls`, no need for spec as URL can encode the ports being used"
      type: list
      elements: str
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a services resource
  l3acon.jmist.mist_org_services:
    org_id: "your-org-id"
    state: present
    name: "example-services"

- name: Delete a services resource
  l3acon.jmist.mist_org_services:
    org_id: "your-org-id"
    service_id: "resource-uuid"
    state: absent

- name: Gather services resources
  l3acon.jmist.mist_org_services:
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
        'addresses',
        'app_categories',
        'app_subcategories',
        'apps',
        'client_limit_down',
        'client_limit_up',
        'description',
        'dscp',
        'failover_policy',
        'hostnames',
        'max_jitter',
        'max_latency',
        'max_loss',
        'name',
        'service_limit_down',
        'service_limit_up',
        'sle_enabled',
        'specs',
        'ssr_relaxed_tcp_state_enforcement',
        'traffic_class',
        'traffic_type',
        'type',
        'urls',
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
        service_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        addresses=dict(type='list', elements='str'),
        app_categories=dict(type='list', elements='str'),
        app_subcategories=dict(type='list', elements='str'),
        apps=dict(type='list', elements='str'),
        client_limit_down=dict(type='int', default=0),
        client_limit_up=dict(type='int', default=0),
        description=dict(type='str'),
        dscp=dict(type='str'),
        failover_policy=dict(type='str', choices=['non_revertible', 'none', 'revertible'], default='revertible'),
        hostnames=dict(type='list', elements='str'),
        max_jitter=dict(type='str'),
        max_latency=dict(type='str'),
        max_loss=dict(type='str'),
        name=dict(type='str'),
        service_limit_down=dict(type='int', default=0),
        service_limit_up=dict(type='int', default=0),
        sle_enabled=dict(type='bool', default=False),
        specs=dict(type='list', elements='dict'),
        ssr_relaxed_tcp_state_enforcement=dict(type='bool', default=False),
        traffic_class=dict(type='str', choices=['best_effort', 'high', 'low', 'medium'], default='best_effort'),
        traffic_type=dict(type='str', default='data_best_effort'),
        type=dict(type='str', choices=['app_categories', 'apps', 'custom', 'urls'], default='custom'),
        urls=dict(type='list', elements='str'),
    )

    required_if = [
        ('state', 'absent', ['service_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id']
    resource_id = module.params.get('service_id')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/services'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/services/{service_id}'.format(org_id=org_id, service_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/services'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="service_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/services/{service_id}'.format(org_id=org_id, service_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
