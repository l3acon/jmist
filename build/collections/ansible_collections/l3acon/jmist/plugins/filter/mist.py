#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Filter plugins for the l3acon.jmist collection."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible.errors import AnsibleFilterError


def mac_to_ap_id(mac):
    """Convert a MAC address to a Mist AP device ID.

    Mist AP IDs follow the format: 00000000-0000-0000-1000-{mac_without_separators}
    """
    clean_mac = re.sub(r'[:\-.]', '', mac).lower()
    if len(clean_mac) != 12:
        raise AnsibleFilterError(
            "Invalid MAC address: '{mac}' (expected 12 hex characters)".format(mac=mac)
        )
    if not re.match(r'^[0-9a-f]{12}$', clean_mac):
        raise AnsibleFilterError(
            "Invalid MAC address: '{mac}' (contains non-hex characters)".format(mac=mac)
        )
    return "00000000-0000-0000-1000-{mac}".format(mac=clean_mac)


class FilterModule(object):
    """Mist filter plugins."""

    def filters(self):
        return {
            'mac_to_ap_id': mac_to_ap_id,
        }
