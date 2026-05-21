#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""HTTPAPI connection plugin for Juniper Mist."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
name: mist
short_description: HTTPAPI connection plugin for Juniper Mist
description:
  - This connection plugin provides HTTP API connectivity to the Juniper Mist cloud platform.
  - It handles token-based authentication and JSON request/response formatting.
version_added: "1.0.0"
author:
  - Juniper Mist Ansible Collection Contributors
options:
  mist_api_token:
    description:
      - API token for authenticating to the Mist API.
      - Can also be set via the MIST_API_TOKEN environment variable.
    type: str
    required: true
    env:
      - name: MIST_API_TOKEN
    vars:
      - name: ansible_httpapi_mist_api_token
  mist_base_url:
    description:
      - Base URL for the Mist API.
      - Defaults to the Global 01 cloud (api.mist.com).
      - Other options include regional endpoints like api.eu.mist.com.
    type: str
    default: https://api.mist.com
    env:
      - name: MIST_BASE_URL
    vars:
      - name: ansible_httpapi_mist_base_url
"""

import json

from ansible.module_utils.connection import ConnectionError
from ansible.plugins.httpapi import HttpApiBase


class HttpApi(HttpApiBase):
    """HTTPAPI plugin for Juniper Mist cloud platform."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api_token = None
        self._base_url = None

    @property
    def api_token(self):
        if self._api_token is None:
            self._api_token = self.get_option("mist_api_token")
        return self._api_token

    @property
    def base_url(self):
        if self._base_url is None:
            self._base_url = self.get_option("mist_base_url").rstrip("/")
        return self._base_url

    def login(self, username, password):
        """Mist uses token-based auth; login is a no-op if token is set."""
        if not self.api_token:
            raise ConnectionError("mist_api_token is required for authentication")

    def logout(self):
        """No logout required for token-based auth."""
        pass

    def get_headers(self):
        """Return common headers for all requests."""
        return {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def send_request(self, method, path, data=None):
        """Send a request to the Mist API."""
        headers = self.get_headers()
        body = json.dumps(data) if data else None

        try:
            response, response_data = self.connection.send(
                path,
                body,
                method=method,
                headers=headers,
            )
            return self._handle_response(response, response_data)
        except Exception as e:
            raise ConnectionError(f"Mist API request failed: {str(e)}")

    def _handle_response(self, response, response_data):
        """Process the API response."""
        try:
            response_body = response_data.read()
            if response_body:
                return json.loads(response_body)
            return {}
        except (ValueError, TypeError):
            return {"raw": response_body.decode("utf-8") if response_body else ""}

    def get(self, path):
        """HTTP GET."""
        return self.send_request("GET", path)

    def post(self, path, data=None):
        """HTTP POST."""
        return self.send_request("POST", path, data=data)

    def put(self, path, data=None):
        """HTTP PUT."""
        return self.send_request("PUT", path, data=data)

    def delete(self, path):
        """HTTP DELETE."""
        return self.send_request("DELETE", path)
