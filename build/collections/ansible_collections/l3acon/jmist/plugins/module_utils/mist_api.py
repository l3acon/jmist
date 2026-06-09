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
        self.api_token = (module.params.get("api_token") or self._get_env_token() or "").strip()
        self.base_url = (
            module.params.get("base_url") or "https://api.mist.com"
        ).strip().rstrip("/")
        self.follow_redirects = module.params.get("follow_redirects") or "all"

        if not self.api_token:
            module.fail_json(msg="api_token is required (parameter or MIST_API_TOKEN env var)")

        self._validate_connectivity()

    def _get_env_token(self):
        """Try to read the API token from environment."""
        import os
        return os.environ.get("MIST_API_TOKEN")

    def _validate_connectivity(self):
        url = f"{self.base_url}/api/v1/self"
        try:
            response = open_url(
                url,
                method="GET",
                headers=self._headers(),
                validate_certs=self.module.params.get("validate_certs", True),
                timeout=self.module.params.get("timeout", 30),
                follow_redirects=self.follow_redirects,
            )
            data = json.loads(response.read())
        except HTTPError as e:
            if e.code == 401:
                self.module.fail_json(
                    msg=f"Authentication failed against {self.base_url}. "
                        "Verify your api_token or MIST_API_TOKEN is correct and not expired.",
                )
            if e.code == 403:
                self.module.fail_json(
                    msg=f"Authorization denied by {self.base_url}. "
                        "The API token is valid but lacks permission for this operation.",
                )
            self.module.fail_json(
                msg=f"Unexpected HTTP {e.code} from {self.base_url}/api/v1/self. "
                    "Verify base_url points to the correct Mist API region "
                    "(e.g. https://api.gc1.mist.com, https://api.gc2.mist.com).",
            )
        except URLError as e:
            self.module.fail_json(
                msg=f"Cannot reach Mist API at {self.base_url}: {e.reason}. "
                    "Check that base_url is correct and the host is reachable. "
                    "Common Mist API regions: https://api.mist.com, "
                    "https://api.gc1.mist.com, https://api.gc2.mist.com, "
                    "https://api.gc3.mist.com, https://api.gc4.mist.com, "
                    "https://api.ac2.mist.com, https://api.ac99.mist.com",
            )
        except Exception as e:
            self.module.fail_json(
                msg=f"Failed to validate connectivity to {self.base_url}: {str(e)}",
            )

        org_id = (self.module.params.get("org_id") or "").strip()
        if org_id:
            privileges = data.get("privileges") or []
            accessible_orgs = {
                p.get("org_id") for p in privileges
                if p.get("scope") in ("org", "site") and p.get("org_id")
            }
            if org_id not in accessible_orgs:
                self.module.fail_json(
                    msg=f"Organization '{org_id}' is not accessible with this API token. "
                        "Verify the org_id is correct and the token has been granted access. "
                        f"Accessible orgs: {', '.join(sorted(accessible_orgs)) or 'none'}",
                )

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
                follow_redirects=self.follow_redirects,
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
                msg=f"Failed to connect to Mist API at {self.base_url}: {e.reason}. "
                    "Check that base_url is correct and the host is reachable.",
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
