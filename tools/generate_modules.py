#!/usr/bin/env python3
"""
Generate Ansible module files from parsed Mist API definitions.

Reads module definitions from tools/output/ and generates complete
Ansible module Python files in the collection directory.
"""

import json
import re
import sys
import textwrap
from pathlib import Path

import yaml


COLLECTION_PATH = Path("build/collections/ansible_collections/l3acon/jmist")


def sanitize_description(desc: str) -> str:
    """Sanitize a description string for YAML documentation."""
    if isinstance(desc, list):
        desc = " ".join(desc)
    desc = desc.replace("\n", " ").strip()
    # Remove Jinja2-like templates that break Ansible's parser
    desc = re.sub(r"\{\{.*?\}\}", "VARIABLE", desc)
    # Escape backslashes and quotes
    desc = desc.replace("\\", "\\\\")
    desc = desc.replace('"', "'")
    # Truncate overly long descriptions
    if len(desc) > 200:
        desc = desc[:197] + "..."
    return desc


def generate_options_yaml(options: dict, indent_level: int = 0) -> str:
    """Generate YAML-formatted options for module DOCUMENTATION."""
    if not options:
        return ""

    lines = []
    prefix = "  " * indent_level

    for name, opt in sorted(options.items()):
        lines.append(f"{prefix}{name}:")
        desc = sanitize_description(opt.get("description", f"The {name} parameter."))
        lines.append(f"{prefix}  description:")
        lines.append(f'{prefix}    - "{desc}"')
        lines.append(f"{prefix}  type: {opt.get('type', 'str')}")

        if opt.get("required"):
            lines.append(f"{prefix}  required: true")
        if opt.get("choices"):
            choices = opt["choices"]
            if len(choices) <= 8:
                lines.append(f"{prefix}  choices: {json.dumps(choices)}")
        if opt.get("elements"):
            lines.append(f"{prefix}  elements: {opt['elements']}")
        if "default" in opt and opt["default"] is not None:
            val = opt["default"]
            if isinstance(val, bool):
                lines.append(f"{prefix}  default: {str(val).lower()}")
            elif isinstance(val, str):
                lines.append(f'{prefix}  default: "{val}"')
            else:
                lines.append(f"{prefix}  default: {val}")

    return "\n".join(lines)


def generate_argspec_code(options: dict) -> str:
    """Generate Python argument_spec dict assignment code."""
    lines = []
    for name, opt in sorted(options.items()):
        parts = []
        parts.append(f"type='{opt.get('type', 'str')}'")
        # Don't mark individual params as hard-required; use required_if instead
        # if opt.get("required"):
        #     parts.append("required=True")
        if opt.get("choices"):
            choices = opt["choices"]
            if len(choices) <= 8:
                parts.append(f"choices={choices}")
        if opt.get("elements"):
            parts.append(f"elements='{opt['elements']}'")
        if "default" in opt and opt["default"] is not None:
            val = opt["default"]
            if isinstance(val, bool):
                parts.append(f"default={val}")
            elif isinstance(val, str):
                parts.append(f"default='{val}'")
            else:
                parts.append(f"default={val}")

        lines.append(f"        {name}=dict({', '.join(parts)}),")
    return "\n".join(lines)


def generate_module_file(module_def: dict) -> str:
    """Generate a complete Ansible module Python file."""
    module_name = module_def["module_name"]
    resource_name = module_def["resource_name"]
    scope = module_def["scope"]
    description = module_def["description"]
    collection_path = module_def["collection_path"]
    detail_path = module_def["detail_path"]
    options = module_def["options"]
    states = module_def["states"]

    options_yaml = generate_options_yaml(options, indent_level=2)
    argspec_code = generate_argspec_code(options)

    scope_id_param = "org_id" if scope == "org" else "site_id"
    scope_id_desc = "Organization ID" if scope == "org" else "Site ID"

    # Build the detail path ID parameter name
    detail_parts = detail_path.rstrip("/").split("/")
    detail_id_param = detail_parts[-1].strip("{}")

    module_code = f'''#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2026 Juniper Networks
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""The module file for {module_name}"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: {module_name}
short_description: Manage {resource_name} in Juniper Mist
description:
  - {description}
  - This module supports state-based management of {resource_name} resources.
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
    {scope_id_param}:
      description:
        - "{scope_id_desc} for the resource."
      type: str
      required: true
    {detail_id_param}:
      description:
        - "Unique identifier of the {resource_name} resource. Required for state=absent."
      type: str
    state:
      description:
        - "The desired state of the resource."
      type: str
      choices: {json.dumps(states)}
      default: present
{options_yaml}
requirements:
  - python >= 3.9
notes:
  - Requires a valid Mist API token.
"""

EXAMPLES = """
---
- name: Create a {resource_name} resource
  l3acon.jmist.{module_name}:
    {scope_id_param}: "your-{scope}-id"
    state: present
    name: "example-{resource_name}"

- name: Delete a {resource_name} resource
  l3acon.jmist.{module_name}:
    {scope_id_param}: "your-{scope}-id"
    {detail_id_param}: "resource-uuid"
    state: absent

- name: Gather {resource_name} resources
  l3acon.jmist.{module_name}:
    {scope_id_param}: "your-{scope}-id"
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
    payload = {{}}
    config_params = [
{chr(10).join(f"        '{name}'," for name in sorted(options.keys()))}
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
        {scope_id_param}=dict(type='str', required=True),
        {detail_id_param}=dict(type='str'),
        state=dict(type='str', choices={json.dumps(states)}, default='present'),
{argspec_code}
    )

    required_if = [
        ('state', 'absent', ['{detail_id_param}']),
    ]

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
    )

    client = MistApiClient(module)
    state = module.params['state']
    {scope_id_param} = module.params['{scope_id_param}']
    resource_id = module.params.get('{detail_id_param}')

    result = dict(changed=False)

    if state == 'gathered':
        if module.check_mode:
            result['gathered'] = []
        else:
            response = client.get('{collection_path}'.format({scope_id_param}={scope_id_param}))
            result['gathered'] = response
    elif state == 'present':
        payload = build_payload(module)
        if resource_id:
            if not module.check_mode:
                response = client.put(
                    '{detail_path}'.format({scope_id_param}={scope_id_param}, {detail_id_param}=resource_id),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
        else:
            if not module.check_mode:
                response = client.post(
                    '{collection_path}'.format({scope_id_param}={scope_id_param}),
                    data=payload,
                )
                result['response'] = response
            result['changed'] = True
    elif state == 'absent':
        if not resource_id:
            module.fail_json(msg="{detail_id_param} is required when state=absent")
        if not module.check_mode:
            client.delete(
                '{detail_path}'.format({scope_id_param}={scope_id_param}, {detail_id_param}=resource_id),
            )
        result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
'''
    return module_code


def main():
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "tools/output"
    collection_dir = sys.argv[2] if len(sys.argv) > 2 else str(COLLECTION_PATH)

    output_path = Path(output_dir)
    collection_path = Path(collection_dir)
    modules_dir = collection_path / "plugins" / "modules"
    modules_dir.mkdir(parents=True, exist_ok=True)

    summary_file = output_path / "summary.json"
    if not summary_file.exists():
        print(f"Error: {summary_file} not found. Run mist_spec_parser.py first.")
        sys.exit(1)

    with open(summary_file) as f:
        summary = json.load(f)

    generated = []
    for mod_info in summary["modules"]:
        mod_name = mod_info["module_name"]
        mod_file = output_path / f"{mod_name}.json"

        with open(mod_file) as f:
            module_def = json.load(f)

        module_code = generate_module_file(module_def)
        dest = modules_dir / f"{mod_name}.py"
        with open(dest, "w") as f:
            f.write(module_code)

        generated.append(mod_name)
        print(f"  Generated: {dest}")

    print(f"\nGenerated {len(generated)} modules in {modules_dir}/")


if __name__ == "__main__":
    main()
