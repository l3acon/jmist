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
    clean_mac = re.sub(r'[:\-.]', '', mac.strip()).lower()
    if len(clean_mac) != 12:
        raise AnsibleFilterError(
            "Invalid MAC address: '{mac}' (expected 12 hex characters)".format(mac=mac)
        )
    if not re.match(r'^[0-9a-f]{12}$', clean_mac):
        raise AnsibleFilterError(
            "Invalid MAC address: '{mac}' (contains non-hex characters)".format(mac=mac)
        )
    return "00000000-0000-0000-1000-{mac}".format(mac=clean_mac)


def macs_to_ap_ids(macs):
    """Validate a batch of MACs and return unique AP IDs in input order.

    Accept a YAML list or text separated by commas or whitespace (including
    newlines), as provided by an Automation Controller textarea survey.
    """
    if isinstance(macs, str):
        macs = [mac for mac in re.split(r'[\s,]+', macs.strip()) if mac]
    if not isinstance(macs, (list, tuple)) or not macs:
        raise AnsibleFilterError(
            "ap_macs must contain at least one MAC address, as a list or "
            "text separated by commas, spaces, or newlines"
        )

    ap_ids = []
    for index, mac in enumerate(macs, start=1):
        if not isinstance(mac, str):
            raise AnsibleFilterError(
                "Invalid MAC address at position {0}: expected a string".format(index)
            )
        try:
            ap_ids.append(mac_to_ap_id(mac))
        except AnsibleFilterError as error:
            raise AnsibleFilterError(
                "Invalid MAC address at position {0}: {1}".format(index, error)
            ) from error
    return list(dict.fromkeys(ap_ids))


class FilterModule(object):
    """Mist filter plugins."""

    def filters(self):
        return {
            'mac_to_ap_id': mac_to_ap_id,
            'macs_to_ap_ids': macs_to_ap_ids,
        }
