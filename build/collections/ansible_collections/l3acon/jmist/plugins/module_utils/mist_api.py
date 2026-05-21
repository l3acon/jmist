#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Mist API client utility for Ansible modules."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError


class MistApiClient:
    """HTTP client for the Juniper Mist REST API."""

    def __init__(self, module):
        self.module = module
        self.api_token = module.params.get("api_token") or self._get_env_token()
        self.base_url = (
            module.params.get("base_url") or "https://api.mist.com"
        ).rstrip("/")

        if not self.api_token:
            module.fail_json(msg="api_token is required (parameter or MIST_API_TOKEN env var)")

    def _get_env_token(self):
        """Try to read the API token from environment."""
        import os
        return os.environ.get("MIST_API_TOKEN")

    def _headers(self):
        return {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, data=None):
        """Make an HTTP request to the Mist API."""
        url = f"{self.base_url}{path}"
        body = json.dumps(data) if data else None

        try:
            response = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                validate_certs=self.module.params.get("validate_certs", True),
                timeout=self.module.params.get("timeout", 30),
            )
            response_body = response.read()
            if response_body:
                return json.loads(response_body)
            return {}
        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            self.module.fail_json(
                msg=f"Mist API request failed: {method} {url} returned {e.code}",
                status_code=e.code,
                response=error_body,
            )
        except URLError as e:
            self.module.fail_json(
                msg=f"Failed to connect to Mist API: {e.reason}",
                url=url,
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Unexpected error calling Mist API: {str(e)}",
                url=url,
            )

    def get(self, path):
        """HTTP GET request."""
        return self._request("GET", path)

    def post(self, path, data=None):
        """HTTP POST request."""
        return self._request("POST", path, data=data)

    def put(self, path, data=None):
        """HTTP PUT request."""
        return self._request("PUT", path, data=data)

    def delete(self, path):
        """HTTP DELETE request."""
        return self._request("DELETE", path)
