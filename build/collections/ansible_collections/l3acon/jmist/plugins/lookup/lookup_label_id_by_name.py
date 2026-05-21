#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Lookup plugin to find a WxTag (label) ID by its name."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
name: lookup_label_id_by_name
short_description: Look up a Mist WxTag (label) ID by name
description:
  - Queries the Mist API to find a WxTag by its name and returns its ID.
  - Searches within the specified organization's WxTags.
version_added: "1.0.0"
options:
  _terms:
    description:
      - The name(s) of the WxTag label to look up.
    required: true
  org_id:
    description:
      - The organization ID to search within.
    required: true
    vars:
      - name: org_id
    env:
      - name: ORG_ID
  api_token:
    description:
      - Mist API token for authentication.
    required: true
    vars:
      - name: mist_token
      - name: api_token
    env:
      - name: MIST_API_TOKEN
      - name: MIST_TOKEN
  base_url:
    description:
      - Base URL for the Mist API.
    default: "https://api.mist.com"
    vars:
      - name: mist_base_url
    env:
      - name: MIST_BASE_URL
requirements:
  - python >= 3.9
author:
  - Juniper Mist Ansible Collection Contributors
"""

EXAMPLES = """
---
- name: Look up a tag ID by name
  ansible.builtin.debug:
    msg: "{{ lookup('l3acon.jmist.lookup_label_id_by_name', 'my-tag-name', org_id=org_id, api_token=mist_token) }}"

- name: Use in a task (with env vars MIST_TOKEN and ORG_ID set)
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ lookup('l3acon.jmist.lookup_label_id_by_name', 'this-matt-tag') }}"
    state: present
    values:
      - "{{ ap_id }}"
"""

RETURN = """
_raw:
  description:
    - The ID(s) of the WxTag(s) matching the given name(s).
  type: list
  elements: str
"""

import json
import os

from ansible.errors import AnsibleError
from ansible.module_utils.urls import open_url
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        org_id = self.get_option('org_id')
        if not org_id:
            raise AnsibleError("org_id is required for lookup_label_id_by_name")

        api_token = self.get_option('api_token')
        if not api_token:
            raise AnsibleError(
                "api_token is required (pass directly, set mist_token var, "
                "or export MIST_TOKEN/MIST_API_TOKEN env var)"
            )

        base_url = self.get_option('base_url') or 'https://api.mist.com'
        base_url = base_url.rstrip('/')

        url = f"{base_url}/api/v1/orgs/{org_id}/wxtags"
        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = open_url(url, method="GET", headers=headers)
            wxtags = json.loads(response.read())
        except Exception as e:
            raise AnsibleError(f"Failed to fetch WxTags from Mist API: {str(e)}")

        results = []
        for term in terms:
            found = False
            for tag in wxtags:
                if tag.get('name') == term:
                    results.append(tag['id'])
                    found = True
                    break
            if not found:
                raise AnsibleError(f"WxTag with name '{term}' not found in org {org_id}")

        return results
