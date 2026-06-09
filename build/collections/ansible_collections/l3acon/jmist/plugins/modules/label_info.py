#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for label_info"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: label_info
short_description: Look up a Mist WxTag (label) by name
description:
  - Queries the Mist API to find a WxTag by its name and returns all
    available information about it.
  - Searches within the specified organization's WxTags.
version_added: "1.1.0"
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
        - "Organization ID to search within."
      type: str
      required: true
    name:
      description:
        - "The name of the WxTag label to look up."
      type: str
      required: true
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
  - This is an info module and does not modify any resources.
"""

EXAMPLES = """
---
- name: Look up a label by name
  l3acon.jmist.label_info:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    name: "my-tag-name"
  register: tag

- name: Use the label ID in another task
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag.label.id }}"
    state: present
    values:
      - "{{ ap_id }}"

- name: Print all label information
  ansible.builtin.debug:
    var: tag.label
"""

RETURN = """
label:
  description: The full WxTag resource from the Mist API.
  returned: success
  type: dict
  contains:
    id:
      description: The WxTag ID.
      type: str
    name:
      description: The WxTag name.
      type: str
    type:
      description: The WxTag type.
      type: str
    match:
      description: Match criteria (when type is 'match').
      type: str
    op:
      description: Operation type (in or not_in).
      type: str
    values:
      description: List of values for the tag.
      type: list
      elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.l3acon.jmist.plugins.module_utils.mist_api import MistApiClient


def main():
    argument_spec = dict(
        api_token=dict(type='str', no_log=True),
        base_url=dict(type='str', default='https://api.mist.com'),
        validate_certs=dict(type='bool', default=True),
        timeout=dict(type='int', default=30),
        follow_redirects=dict(type='str', choices=['all', 'no', 'safe', 'urllib2'], default='all'),
        org_id=dict(type='str', required=True),
        name=dict(type='str', required=True),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    org_id = module.params['org_id'].strip()
    name = module.params['name'].strip()

    wxtags = client.get('/api/v1/orgs/{org_id}/wxtags'.format(org_id=org_id))

    for tag in wxtags:
        if tag.get('name') == name:
            module.exit_json(changed=False, label=tag)
            return

    module.fail_json(msg="WxTag with name '{name}' not found in org {org_id}".format(
        name=name, org_id=org_id,
    ))


if __name__ == '__main__':
    main()
