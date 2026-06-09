#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for mist_org_wlans"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: mist_org_wlans
short_description: Manage wlans in Juniper Mist
description:
  - Manage Orgs Wlans resources in Juniper Mist
  - This module supports state-based management of wlans resources.
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
    wlan_id:
      description:
        - "Unique identifier of the wlans resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: ["absent", "gathered", "present"]
      default: present
    acct_immediate_update:
      description:
        - "Enable coa-immediate-update and address-change-immediate-update on the access profile."
      type: bool
      default: false
    acct_interim_interval:
      description:
        - "How frequently should interim accounting be reported, 60-65535. default is 0 (use one specified in Access-Accept request from RADIUS Server). Very frequent messages can affect the performance of th..."
      type: int
      default: 0
    acct_servers:
      description:
        - "List of RADIUS accounting servers, optional, order matters where the first one is treated as primary"
      type: list
      elements: dict
    airwatch:
      description:
        - "Airwatch wlan settings"
      type: dict
    allow_ipv6_ndp:
      description:
        - "Only applicable when `limit_bcast`==`true`, which allows or disallows ipv6 Neighbor Discovery packets to go through"
      type: bool
      default: true
    allow_mdns:
      description:
        - "Only applicable when `limit_bcast`==`true`, which allows mDNS / Bonjour packets to go through"
      type: bool
      default: false
    allow_ssdp:
      description:
        - "Only applicable when `limit_bcast`==`true`, which allows SSDP"
      type: bool
      default: false
    ap_ids:
      description:
        - "List of device ids"
      type: list
      elements: str
    app_limit:
      description:
        - "Bandwidth limiting for apps (applies to up/down)"
      type: dict
    app_qos:
      description:
        - "APP qos wlan settings"
      type: dict
    apply_to:
      description:
        - "enum: `aps`, `site`, `wxtags`"
      type: str
      choices: ["aps", "site", "wxtags"]
    arp_filter:
      description:
        - "Whether to enable smart arp filter"
      type: bool
      default: false
    auth:
      description:
        - "Authentication wlan settings"
      type: dict
    auth_server_selection:
      description:
        - "When ordered, AP will prefer and go back to the first server if possible. enum: `ordered`, `unordered`"
      type: str
      choices: ["ordered", "unordered"]
      default: "ordered"
    auth_servers:
      description:
        - "List of RADIUS authentication servers, at least one is needed if `auth type`==`eap`, order matters where the first one is treated as primary"
      type: list
      elements: dict
    auth_servers_nas_id:
      description:
        - "Optional, up to 48 bytes, will be dynamically generated if not provided. used only for authentication servers"
      type: str
    auth_servers_nas_ip:
      description:
        - "Optional, NAS-IP-ADDRESS to use"
      type: str
    auth_servers_retries:
      description:
        - "Radius auth session retries. Following fast timers are set if 'fast_dot1x_timers' knob is enabled. ‘retries’ are set to value of auth_servers_retries. ‘max-requests’ is also set when setting auth_s..."
      type: int
      default: 2
    auth_servers_timeout:
      description:
        - "Radius auth session timeout. Following fast timers are set if 'fast_dot1x_timers' knob is enabled. ‘quite-period’  and ‘transmit-period’ are set to half the value of auth_servers_timeout. ‘supplica..."
      type: int
      default: 5
    band:
      description:
        - "`band` is deprecated and kept for backward compatibility. Use bands instead"
      type: str
    band_steer:
      description:
        - "Whether to enable band_steering, this works only when band==both"
      type: bool
      default: false
    band_steer_force_band5:
      description:
        - "Force dual_band capable client to connect to 5G"
      type: bool
      default: false
    bands:
      description:
        - "List of radios that the wlan should apply to. enum: `24`, `5`, `5-dedicated`, `5-selectable`, `6`, `6-dedicated`, `6-selectable`"
      type: list
      elements: str
      default: ['24', '5', '6']
    block_blacklist_clients:
      description:
        - "Whether to block the clients in the blacklist (up to first 256 macs)"
      type: bool
      default: false
    bonjour:
      description:
        - "Bonjour gateway wlan settings"
      type: dict
    cisco_cwa:
      description:
        - "Cisco CWA (central web authentication) required RADIUS with COA in order to work. See CWA: https://www.cisco.com/c/en/us/support/docs/security/identity-services-engine/115732-central-web-auth-00.html"
      type: dict
    client_limit_down:
      description:
        - "In kbps, value from 1 to 999000"
      type: int
    client_limit_down_enabled:
      description:
        - "If downlink limiting per-client is enabled"
      type: bool
      default: false
    client_limit_up:
      description:
        - "In kbps, value from 1 to 999000"
      type: int
    client_limit_up_enabled:
      description:
        - "If uplink limiting per-client is enabled"
      type: bool
      default: false
    coa_servers:
      description:
        - "List of COA (change of authorization) servers, optional"
      type: list
      elements: dict
    disable_11ax:
      description:
        - "Some old WLAN drivers may not be compatible"
      type: bool
      default: false
    disable_11be:
      description:
        - "To disable Wi-Fi 7 EHT IEs"
      type: bool
      default: false
    disable_ht_vht_rates:
      description:
        - "To disable ht or vht rates"
      type: bool
      default: false
    disable_message_authenticator_check:
      description:
        - "whether to disable Message-Authenticator Check, which is used to verify the integrity of RADIUS messages, default is false (i.e. for better security)"
      type: bool
      default: false
    disable_uapsd:
      description:
        - "Whether to disable U-APSD"
      type: bool
      default: false
    disable_v1_roam_notify:
      description:
        - "Disable sending v2 roam notification messages"
      type: bool
      default: false
    disable_v2_roam_notify:
      description:
        - "Disable sending v2 roam notification messages"
      type: bool
      default: false
    disable_when_gateway_unreachable:
      description:
        - "When any of the following is true, this WLAN will be disabled    * cannot get IP    * cannot obtain default gateway    * cannot reach default gateway"
      type: bool
      default: false
    disable_when_mxtunnel_down:
      description:
        - "The disable_when_mxtunnel_down parameter."
      type: bool
      default: false
    disable_wmm:
      description:
        - "Whether to disable WMM"
      type: bool
      default: false
    dns_server_rewrite:
      description:
        - "For radius_group-based DNS server (rewrite DNS request depending on the Group RADIUS server returns)"
      type: dict
    dtim:
      description:
        - "The dtim parameter."
      type: int
      default: 2
    dynamic_psk:
      description:
        - "For dynamic PSK where we get per_user PSK from Radius. dynamic_psk allows PSK to be selected at runtime depending on context (wlan/site/user/...) thus following configurations are assumed (currentl..."
      type: dict
    dynamic_vlan:
      description:
        - "For 802.1x"
      type: dict
    enable_local_keycaching:
      description:
        - "Enable AP-AP keycaching via multicast"
      type: bool
      default: false
    enable_wireless_bridging:
      description:
        - "By default, we'd inspect all DHCP packets and drop those unrelated to the wireless client itself in the case where client is a wireless bridge (DHCP packets for other MACs will need to be forwarded..."
      type: bool
      default: false
    enable_wireless_bridging_dhcp_tracking:
      description:
        - "If the client bridge is doing DHCP on behalf of other devices (L2-NAT), enable dhcp_tracking will cut down DHCP response packets to be forwarded to wireless"
      type: bool
      default: false
    enabled:
      description:
        - "If this wlan is enabled"
      type: bool
      default: true
    fast_dot1x_timers:
      description:
        - "If set to true, sets default fast-timers with values calculated from ‘auth_servers_timeout’ and ‘auth_server_retries’ ."
      type: bool
      default: false
    hide_ssid:
      description:
        - "Whether to hide SSID in beacon"
      type: bool
      default: false
    hostname_ie:
      description:
        - "Include hostname inside IE in AP beacons / probe responses"
      type: bool
      default: false
    hotspot20:
      description:
        - "Hostspot 2.0 wlan settings"
      type: dict
    inject_dhcp_option_82:
      description:
        - "The inject_dhcp_option_82 parameter."
      type: dict
    interface:
      description:
        - "where this WLAN will be connected to. enum: `all`, `eth0`, `eth1`, `eth2`, `eth3`, `mxtunnel`, `site_mxedge`, `wxtunnel`"
      type: str
      choices: ["all", "eth0", "eth1", "eth2", "eth3", "mxtunnel", "site_mxedge", "wxtunnel"]
      default: "all"
    isolation:
      description:
        - "Whether to stop clients to talk to each other"
      type: bool
      default: false
    l2_isolation:
      description:
        - "If isolation is enabled, whether to deny clients to talk to L2 on the LAN"
      type: bool
      default: false
    legacy_overds:
      description:
        - "Legacy devices requires the Over-DS (for Fast BSS Transition) bit set (while our chip doesn’t support it). Warning! Enabling this will cause problem for iOS devices."
      type: bool
      default: false
    limit_bcast:
      description:
        - "Whether to limit broadcast packets going to wireless (i.e. only allow certain bcast packets to go through)"
      type: bool
      default: false
    limit_probe_response:
      description:
        - "Limit probe response base on some heuristic rules"
      type: bool
      default: false
    max_idletime:
      description:
        - "Max idle time in seconds"
      type: int
      default: 1800
    max_num_clients:
      description:
        - "Maximum number of client connected to the SSID. `0` means unlimited"
      type: int
      default: 0
    mist_nac:
      description:
        - "The mist_nac parameter."
      type: dict
    msp_id:
      description:
        - "The msp_id parameter."
      type: str
    mxtunnel_id:
      description:
        - "(deprecated, use mxtunnel_ids instead) when `interface`==`mxtunnel`, id of the Mist Tunnel"
      type: str
    mxtunnel_ids:
      description:
        - "When `interface`=`mxtunnel`, id of the Mist Tunnel"
      type: list
      elements: str
    mxtunnel_name:
      description:
        - "When `interface`=`site_mxedge`, name of the mxtunnel that in mxtunnels under Site Setting"
      type: list
      elements: str
    no_static_dns:
      description:
        - "Whether to only allow client to use DNS that we’ve learned from DHCP response"
      type: bool
      default: false
    no_static_ip:
      description:
        - "Whether to only allow client that we’ve learned from DHCP exchange to talk"
      type: bool
      default: false
    portal:
      description:
        - "Portal wlan settings"
      type: dict
    portal_allowed_hostnames:
      description:
        - "List of hostnames without http(s):// (matched by substring)"
      type: list
      elements: str
      default: []
    portal_allowed_subnets:
      description:
        - "List of CIDRs"
      type: list
      elements: str
      default: []
    portal_api_secret:
      description:
        - "API secret (auto-generated) that can be used to sign guest authorization requests, only generated when auth is set to `external`"
      type: str
      default: ""
    portal_denied_hostnames:
      description:
        - "List of hostnames without http(s):// (matched by substring), this takes precedence over portal_allowed_hostnames"
      type: list
      elements: str
      default: []
    portal_image:
      description:
        - "Url of portal background image"
      type: str
      default: ""
    portal_sso_url:
      description:
        - "URL used in the SSO process, auto-generated when auth is set to `sso`"
      type: str
    portal_template_url:
      description:
        - "N.B portal_template will be forked out of wlan objects soon. To fetch portal_template, please query portal_template_url. To update portal_template, use Wlan Portal Template."
      type: str
      default: ""
    qos:
      description:
        - "The qos parameter."
      type: dict
    radsec:
      description:
        - "RadSec settings"
      type: dict
    rateset:
      description:
        - "Property key is the RF band. enum: `24`, `5`, `6`"
      type: dict
    reconnect_clients_when_roaming_mxcluster:
      description:
        - "When different mxcluster is on different subnet, we'd want to disconnect clients (so they'll reconnect and get new IPs)"
      type: bool
      default: false
    roam_mode:
      description:
        - "enum: `11r`, `OKC`, `NONE`"
      type: str
      choices: ["11r", "NONE", "OKC"]
      default: "NONE"
    schedule:
      description:
        - "WLAN operating schedule, default is disabled"
      type: dict
    sle_excluded:
      description:
        - "Whether to exclude this WLAN from SLE metrics"
      type: bool
      default: false
    ssid:
      description:
        - "Name of the SSID"
      type: str
      required: true
    template_id:
      description:
        - "The template_id parameter."
      type: str
      default: ""
    thumbnail:
      description:
        - "Url of portal background image thumbnail"
      type: str
      default: ""
    use_eapol_v1:
      description:
        - "If `auth.type`==`eap` or `auth.type`==`psk`, should only be set for legacy client, such as pre-2004, 802.11b devices"
      type: bool
      default: false
    vlan_enabled:
      description:
        - "If vlan tagging is enabled"
      type: bool
      default: false
    vlan_id:
      description:
        - "The vlan_id parameter."
      type: str
    vlan_ids:
      description:
        - "If `vlan_enabled`==`true` and `vlan_pooling`==`true`. List of VLAN IDs to be used in the VLAN Pool"
      type: str
    vlan_pooling:
      description:
        - "Requires `vlan_enabled`==`true` to be set to `true`. Vlan pooling allows AP to place client on different VLAN using a deterministic algorithm"
      type: bool
      default: false
    wlan_limit_down:
      description:
        - "In kbps, value from 1 to 999000"
      type: int
    wlan_limit_down_enabled:
      description:
        - "If downlink limiting for whole wlan is enabled"
      type: bool
      default: false
    wlan_limit_up:
      description:
        - "In kbps, value from 1 to 999000"
      type: int
    wlan_limit_up_enabled:
      description:
        - "If uplink limiting for whole wlan is enabled"
      type: bool
      default: false
    wxtag_ids:
      description:
        - "List of wxtag_ids"
      type: list
      elements: str
    wxtunnel_id:
      description:
        - "When `interface`=`wxtunnel`, id of the WXLAN Tunnel"
      type: str
      default: ""
    wxtunnel_remote_id:
      description:
        - "When `interface`=`wxtunnel`, remote tunnel identifier"
      type: str
      default: ""
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a wlans resource
  l3acon.jmist.mist_org_wlans:
    org_id: "your-org-id"
    state: present
    name: "example-wlans"

- name: Delete a wlans resource
  l3acon.jmist.mist_org_wlans:
    org_id: "your-org-id"
    wlan_id: "resource-uuid"
    state: absent

- name: Gather wlans resources
  l3acon.jmist.mist_org_wlans:
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
        'acct_immediate_update',
        'acct_interim_interval',
        'acct_servers',
        'airwatch',
        'allow_ipv6_ndp',
        'allow_mdns',
        'allow_ssdp',
        'ap_ids',
        'app_limit',
        'app_qos',
        'apply_to',
        'arp_filter',
        'auth',
        'auth_server_selection',
        'auth_servers',
        'auth_servers_nas_id',
        'auth_servers_nas_ip',
        'auth_servers_retries',
        'auth_servers_timeout',
        'band',
        'band_steer',
        'band_steer_force_band5',
        'bands',
        'block_blacklist_clients',
        'bonjour',
        'cisco_cwa',
        'client_limit_down',
        'client_limit_down_enabled',
        'client_limit_up',
        'client_limit_up_enabled',
        'coa_servers',
        'disable_11ax',
        'disable_11be',
        'disable_ht_vht_rates',
        'disable_message_authenticator_check',
        'disable_uapsd',
        'disable_v1_roam_notify',
        'disable_v2_roam_notify',
        'disable_when_gateway_unreachable',
        'disable_when_mxtunnel_down',
        'disable_wmm',
        'dns_server_rewrite',
        'dtim',
        'dynamic_psk',
        'dynamic_vlan',
        'enable_local_keycaching',
        'enable_wireless_bridging',
        'enable_wireless_bridging_dhcp_tracking',
        'enabled',
        'fast_dot1x_timers',
        'hide_ssid',
        'hostname_ie',
        'hotspot20',
        'inject_dhcp_option_82',
        'interface',
        'isolation',
        'l2_isolation',
        'legacy_overds',
        'limit_bcast',
        'limit_probe_response',
        'max_idletime',
        'max_num_clients',
        'mist_nac',
        'msp_id',
        'mxtunnel_id',
        'mxtunnel_ids',
        'mxtunnel_name',
        'no_static_dns',
        'no_static_ip',
        'portal',
        'portal_allowed_hostnames',
        'portal_allowed_subnets',
        'portal_api_secret',
        'portal_denied_hostnames',
        'portal_image',
        'portal_sso_url',
        'portal_template_url',
        'qos',
        'radsec',
        'rateset',
        'reconnect_clients_when_roaming_mxcluster',
        'roam_mode',
        'schedule',
        'sle_excluded',
        'ssid',
        'template_id',
        'thumbnail',
        'use_eapol_v1',
        'vlan_enabled',
        'vlan_id',
        'vlan_ids',
        'vlan_pooling',
        'wlan_limit_down',
        'wlan_limit_down_enabled',
        'wlan_limit_up',
        'wlan_limit_up_enabled',
        'wxtag_ids',
        'wxtunnel_id',
        'wxtunnel_remote_id',
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
        wlan_id=dict(type='str'),
        state=dict(type='str', choices=["absent", "gathered", "present"], default='present'),
        acct_immediate_update=dict(type='bool', default=False),
        acct_interim_interval=dict(type='int', default=0),
        acct_servers=dict(type='list', elements='dict'),
        airwatch=dict(type='dict'),
        allow_ipv6_ndp=dict(type='bool', default=True),
        allow_mdns=dict(type='bool', default=False),
        allow_ssdp=dict(type='bool', default=False),
        ap_ids=dict(type='list', elements='str'),
        app_limit=dict(type='dict'),
        app_qos=dict(type='dict'),
        apply_to=dict(type='str', choices=['aps', 'site', 'wxtags']),
        arp_filter=dict(type='bool', default=False),
        auth=dict(type='dict'),
        auth_server_selection=dict(type='str', choices=['ordered', 'unordered'], default='ordered'),
        auth_servers=dict(type='list', elements='dict'),
        auth_servers_nas_id=dict(type='str'),
        auth_servers_nas_ip=dict(type='str'),
        auth_servers_retries=dict(type='int', default=2),
        auth_servers_timeout=dict(type='int', default=5),
        band=dict(type='str'),
        band_steer=dict(type='bool', default=False),
        band_steer_force_band5=dict(type='bool', default=False),
        bands=dict(type='list', elements='str', default=['24', '5', '6']),
        block_blacklist_clients=dict(type='bool', default=False),
        bonjour=dict(type='dict'),
        cisco_cwa=dict(type='dict'),
        client_limit_down=dict(type='int'),
        client_limit_down_enabled=dict(type='bool', default=False),
        client_limit_up=dict(type='int'),
        client_limit_up_enabled=dict(type='bool', default=False),
        coa_servers=dict(type='list', elements='dict'),
        disable_11ax=dict(type='bool', default=False),
        disable_11be=dict(type='bool', default=False),
        disable_ht_vht_rates=dict(type='bool', default=False),
        disable_message_authenticator_check=dict(type='bool', default=False),
        disable_uapsd=dict(type='bool', default=False),
        disable_v1_roam_notify=dict(type='bool', default=False),
        disable_v2_roam_notify=dict(type='bool', default=False),
        disable_when_gateway_unreachable=dict(type='bool', default=False),
        disable_when_mxtunnel_down=dict(type='bool', default=False),
        disable_wmm=dict(type='bool', default=False),
        dns_server_rewrite=dict(type='dict'),
        dtim=dict(type='int', default=2),
        dynamic_psk=dict(type='dict'),
        dynamic_vlan=dict(type='dict'),
        enable_local_keycaching=dict(type='bool', default=False),
        enable_wireless_bridging=dict(type='bool', default=False),
        enable_wireless_bridging_dhcp_tracking=dict(type='bool', default=False),
        enabled=dict(type='bool', default=True),
        fast_dot1x_timers=dict(type='bool', default=False),
        hide_ssid=dict(type='bool', default=False),
        hostname_ie=dict(type='bool', default=False),
        hotspot20=dict(type='dict'),
        inject_dhcp_option_82=dict(type='dict'),
        interface=dict(type='str', choices=['all', 'eth0', 'eth1', 'eth2', 'eth3', 'mxtunnel', 'site_mxedge', 'wxtunnel'], default='all'),
        isolation=dict(type='bool', default=False),
        l2_isolation=dict(type='bool', default=False),
        legacy_overds=dict(type='bool', default=False),
        limit_bcast=dict(type='bool', default=False),
        limit_probe_response=dict(type='bool', default=False),
        max_idletime=dict(type='int', default=1800),
        max_num_clients=dict(type='int', default=0),
        mist_nac=dict(type='dict'),
        msp_id=dict(type='str'),
        mxtunnel_id=dict(type='str'),
        mxtunnel_ids=dict(type='list', elements='str'),
        mxtunnel_name=dict(type='list', elements='str'),
        no_static_dns=dict(type='bool', default=False),
        no_static_ip=dict(type='bool', default=False),
        portal=dict(type='dict'),
        portal_allowed_hostnames=dict(type='list', elements='str', default=[]),
        portal_allowed_subnets=dict(type='list', elements='str', default=[]),
        portal_api_secret=dict(type='str', default=''),
        portal_denied_hostnames=dict(type='list', elements='str', default=[]),
        portal_image=dict(type='str', default=''),
        portal_sso_url=dict(type='str'),
        portal_template_url=dict(type='str', default=''),
        qos=dict(type='dict'),
        radsec=dict(type='dict'),
        rateset=dict(type='dict'),
        reconnect_clients_when_roaming_mxcluster=dict(type='bool', default=False),
        roam_mode=dict(type='str', choices=['11r', 'NONE', 'OKC'], default='NONE'),
        schedule=dict(type='dict'),
        sle_excluded=dict(type='bool', default=False),
        ssid=dict(type='str'),
        template_id=dict(type='str', default=''),
        thumbnail=dict(type='str', default=''),
        use_eapol_v1=dict(type='bool', default=False),
        vlan_enabled=dict(type='bool', default=False),
        vlan_id=dict(type='str'),
        vlan_ids=dict(type='str'),
        vlan_pooling=dict(type='bool', default=False),
        wlan_limit_down=dict(type='int'),
        wlan_limit_down_enabled=dict(type='bool', default=False),
        wlan_limit_up=dict(type='int'),
        wlan_limit_up_enabled=dict(type='bool', default=False),
        wxtag_ids=dict(type='list', elements='str'),
        wxtunnel_id=dict(type='str', default=''),
        wxtunnel_remote_id=dict(type='str', default=''),
    )

    required_if = [
        ('state', 'absent', ['wlan_id']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    org_id = module.params['org_id'].strip()
    resource_id = module.params.get('wlan_id')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('/api/v1/orgs/{org_id}/wlans'.format(org_id=org_id))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '/api/v1/orgs/{org_id}/wlans/{wlan_id}'.format(org_id=org_id, wlan_id=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '/api/v1/orgs/{org_id}/wlans'.format(org_id=org_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="wlan_id is required when state=absent")
        if not module.check_mode:
            client.delete(
                '/api/v1/orgs/{org_id}/wlans/{wlan_id}'.format(org_id=org_id, wlan_id=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
