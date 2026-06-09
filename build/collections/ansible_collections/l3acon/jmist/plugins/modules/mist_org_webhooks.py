#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_webhooks"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_webhooks
short_description: Manage webhooks in Juniper Mist
description:
  - Manage Orgs Webhooks resources in Juniper Mist
  - This module supports state-based management of webhooks resources.
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
    webhook_id:
      description:
        - "Unique identifier of the webhooks resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    assetfilter_ids:
      description:
        - "Only if `type`==`asset-raw-rssi`. List of ids to associated asset filters. These filters will be applied to messages routed to a filtered-asset-rssi webhook"
      type: list
      elements: str
    enabled:
      description:
        - "Whether webhook is enabled"
      type: bool
      default: true
    headers:
      description:
        - "If `type`=`http-post`, additional custom HTTP headers to add. The headers name and value must be string, total bytes of headers name and value must be less than 1000"
      type: dict
    name:
      description:
        - "Name of the webhook"
      type: str
    oauth2_client_id:
      description:
        - "Required when `oauth2_grant_type`==`client_credentials`"
      type: str
    oauth2_client_secret:
      description:
        - "Required when `oauth2_grant_type`==`client_credentials`"
      type: str
    oauth2_grant_type:
      description:
        - "required when `type`==`oauth2`. enum: `client_credentials`, `password`"
      type: str
      choices: ["client_credentials", "password"]
    oauth2_password:
      description:
        - "Required when `oauth2_grant_type`==`password`"
      type: str
    oauth2_scopes:
      description:
        - "Required when `type`==`oauth2`, if provided, will be used in the token request"
      type: list
      elements: str
    oauth2_token_url:
      description:
        - "Required when `type`==`oauth2`"
      type: str
    oauth2_username:
      description:
        - "Required when `oauth2_grant_type`==`password`"
      type: str
    secret:
      description:
        - "Only if `type`=`http-post`   when `secret` is provided, two HTTP headers will be added:    * X-Mist-Signature-v2: HMAC_SHA256(secret, body)   * X-Mist-Signature: HMAC_SHA1(secret, body)"
      type: str
    single_event_per_message:
      description:
        - "Some solutions may not be able to parse multiple events from a single message (e.g. IBM Qradar, DSM). When set to `true`, only a single event will be sent per message. this feature is only availabl..."
      type: bool
      default: false
    splunk_token:
      description:
        - "Required if `type`=`splunk`. If splunk_token is not defined for a type Splunk webhook, it will not send, regardless if the webhook receiver is configured to accept it."
      type: str
    topics:
      description:
        - "List of supported webhook topics available with the API Call [List Webhook Topics](/#operations/listWebhookTopics)"
      type: list
      elements: str
    type:
      description:
        - "enum: `aws-sns`, `google-pubsub`, `http-post`, `oauth2`, `splunk`"
      type: str
      choices: ["aws-sns", "google-pubsub", "http-post", "oauth2", "splunk"]
      default: "http-post"
    url:
      description:
        - "The url parameter."
      type: str
    verify_cert:
      description:
        - "When url uses HTTPS, whether to verify the certificate"
      type: bool
      default: true
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a webhooks resource
  l3acon.jmist.mist_org_webhooks:
    org_id: "your-org-id"
    state: present
    name: "example-webhooks"

- name: Delete a webhooks resource
  l3acon.jmist.mist_org_webhooks:
    org_id: "your-org-id"
    webhook_id: "resource-uuid"
    state: absent

- name: Gather webhooks resources
  l3acon.jmist.mist_org_webhooks:
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
        'assetfilter_ids',
        'enabled',
        'headers',
        'name',
        'oauth2_client_id',
        'oauth2_client_secret',
        'oauth2_grant_type',
        'oauth2_password',
        'oauth2_scopes',
        'oauth2_token_url',
        'oauth2_username',
        'secret',
        'single_event_per_message',
        'splunk_token',
        'topics',
        'type',
        'url',
        'verify_cert',
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
        webhook_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        assetfilter_ids=dict(type='list', elements='str'),
        enabled=dict(type='bool', default=True),
        headers=dict(type='dict'),
        name=dict(type='str'),
        oauth2_client_id=dict(type='str'),
        oauth2_client_secret=dict(type='str'),
        oauth2_grant_type=dict(type='str', choices=['client_credentials', 'password']),
        oauth2_password=dict(type='str'),
        oauth2_scopes=dict(type='list', elements='str'),
        oauth2_token_url=dict(type='str'),
        oauth2_username=dict(type='str'),
        secret=dict(type='str'),
        single_event_per_message=dict(type='bool', default=False),
        splunk_token=dict(type='str'),
        topics=dict(type='list', elements='str'),
        type=dict(type='str', choices=['aws-sns', 'google-pubsub', 'http-post', 'oauth2', 'splunk'], default='http-post'),
        url=dict(type='str'),
        verify_cert=dict(type='bool', default=True),
    )

    required_if = [
        ('state', 'absent', ['webhook_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id']
    resource_id = module.params.get('webhook_id')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/webhooks'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/webhooks/{webhook_id}'.format(org_id=org_id, webhook_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/webhooks'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="webhook_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/webhooks/{webhook_id}'.format(org_id=org_id, webhook_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
