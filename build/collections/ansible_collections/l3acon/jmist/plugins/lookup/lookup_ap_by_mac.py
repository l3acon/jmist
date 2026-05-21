#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Lookup plugin to find a Mist AP ID by its MAC address."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
name: lookup_ap_by_mac
short_description: Look up a Mist AP device ID by its MAC address
description:
  - Converts an AP MAC address to its Mist device ID.
  - Mist AP IDs follow the format 00000000-0000-0000-1000-{mac_without_colons}.
  - Optionally validates the AP exists in the org via API call.
version_added: "1.0.0"
options:
  _terms:
    description:
      - MAC address(es) to convert to AP IDs (e.g. 'a8:53:7d:89:7e:7d').
    required: true
  org_id:
    description:
      - The organization ID. Required only if validate=true.
    vars:
      - name: org_id
    env:
      - name: ORG_ID
  api_token:
    description:
      - Mist API token. Required only if validate=true.
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
  validate:
    description:
      - Whether to validate the AP exists via API call.
      - If false (default), performs a local MAC-to-ID conversion only.
    type: bool
    default: false
requirements:
  - python >= 3.9
author:
  - Juniper Mist Ansible Collection Contributors
"""

EXAMPLES = """
---
- name: Convert AP MAC to device ID
  ansible.builtin.debug:
    msg: "{{ lookup('l3acon.jmist.lookup_ap_by_mac', 'a8:53:7d:89:7e:7d') }}"
  # Returns: 00000000-0000-0000-1000-a8537d897e7d

- name: Use in wxtag assignment
  l3acon.jmist.mist_org_wxtags:
    api_token: "{{ mist_token }}"
    org_id: "{{ org_id }}"
    wxtag_id: "{{ tag_id }}"
    state: present
    values:
      - "{{ lookup('l3acon.jmist.lookup_ap_by_mac', 'a8:53:7d:89:7e:7d') }}"

- name: Validate AP exists before using
  ansible.builtin.debug:
    msg: "{{ lookup('l3acon.jmist.lookup_ap_by_mac', 'a8:53:7d:89:7e:7d', org_id=org_id, validate=true) }}"
"""

RETURN = """
_raw:
  description:
    - The Mist AP device ID(s) corresponding to the MAC address(es).
  type: list
  elements: str
"""

import json
import os
import re

from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

display = Display()


def mac_to_ap_id(mac):
    """Convert a MAC address to a Mist AP device ID.

    Mist AP IDs follow the format: 00000000-0000-0000-1000-{mac_without_separators}
    """
    clean_mac = re.sub(r'[:\-.]', '', mac).lower()
    if len(clean_mac) != 12:
        raise AnsibleError(f"Invalid MAC address: '{mac}' (expected 12 hex characters)")
    if not re.match(r'^[0-9a-f]{12}$', clean_mac):
        raise AnsibleError(f"Invalid MAC address: '{mac}' (contains non-hex characters)")
    return f"00000000-0000-0000-1000-{clean_mac}"

    # let's make sure to add device type (for places that have lots of switches)

class LookupModule(LookupBase):
    def run(self, terms, variables=None, **kwargs):
        self.set_options(var_options=variables, direct=kwargs)

        validate = self.get_option('validate')
        org_id = self.get_option('org_id')
        api_token = self.get_option('api_token')
        base_url = (self.get_option('base_url') or 'https://api.mist.com').rstrip('/')

        results = []
        for term in terms:
            ap_id = mac_to_ap_id(term)

            if validate:
                if not org_id:
                    raise AnsibleError("org_id is required when validate=true")
                if not api_token:
                    raise AnsibleError("api_token is required when validate=true")

                from ansible.module_utils.urls import open_url
                clean_mac = re.sub(r'[:\-.]', '', term).lower()
                url = f"{base_url}/api/v1/orgs/{org_id}/inventory?mac={clean_mac}"
                headers = {
                    "Authorization": f"Token {api_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                try:
                    response = open_url(url, method="GET", headers=headers)
                    devices = json.loads(response.read())
                except Exception as e:
                    raise AnsibleError(f"Failed to fetch inventory from Mist API: {str(e)}")

                found = any(d.get('id') == ap_id or d.get('mac') == clean_mac
                           for d in devices)
                if not found:
                    display.warning(f"AP with MAC '{term}' (ID: {ap_id}) not found in org {org_id}")

            results.append(ap_id)

        return results
