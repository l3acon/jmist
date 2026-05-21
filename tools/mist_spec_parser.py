#!/usr/bin/env python3
"""
Mist OpenAPI 3.1.0 spec parser for Ansible module generation.

Parses the Juniper Mist OpenAPI spec and extracts CRUD resource definitions
into intermediate structures suitable for generating Ansible modules.
"""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional


def load_spec(spec_path: str) -> dict:
    with open(spec_path, encoding="utf-8") as f:
        return json.load(f)


def resolve_ref(ref: str, spec: dict) -> dict:
    """Resolve a $ref pointer within the spec."""
    if not ref.startswith("#/"):
        return {}
    parts = ref[2:].split("/")
    obj = spec
    for part in parts:
        part = part.replace("~1", "/").replace("~0", "~")
        obj = obj.get(part, {})
        if not obj:
            return {}
    return obj


def resolve_schema(schema: dict, spec: dict, depth: int = 0, seen: set = None) -> dict:
    """Recursively resolve $ref in a schema, with cycle detection."""
    if seen is None:
        seen = set()
    if depth > 10:
        return schema

    if not isinstance(schema, dict):
        return schema

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen:
            return {"type": "object", "description": "(circular reference)"}
        seen = seen | {ref}
        resolved = resolve_ref(ref, spec)
        if resolved:
            return resolve_schema(resolved, spec, depth + 1, seen)
        return schema

    result = {}
    for k, v in schema.items():
        if k == "properties" and isinstance(v, dict):
            result[k] = {}
            for pk, pv in v.items():
                result[k][pk] = resolve_schema(pv, spec, depth + 1, seen)
        elif k == "items" and isinstance(v, dict):
            result[k] = resolve_schema(v, spec, depth + 1, seen)
        elif k == "allOf" and isinstance(v, list):
            merged = {}
            for item in v:
                resolved_item = resolve_schema(item, spec, depth + 1, seen)
                if "properties" in resolved_item:
                    merged.setdefault("properties", {}).update(resolved_item["properties"])
                if "required" in resolved_item:
                    merged.setdefault("required", []).extend(resolved_item["required"])
                for rk, rv in resolved_item.items():
                    if rk not in ("properties", "required"):
                        merged[rk] = rv
            merged["type"] = "object"
            result.update(merged)
        elif k == "oneOf" and isinstance(v, list):
            if v:
                result.update(resolve_schema(v[0], spec, depth + 1, seen))
        elif k == "anyOf" and isinstance(v, list):
            if v:
                result.update(resolve_schema(v[0], spec, depth + 1, seen))
        else:
            result[k] = v

    return result


def openapi_type_to_ansible(schema: dict) -> dict:
    """Convert an OpenAPI schema type to Ansible argspec type info."""
    oa_type = schema.get("type", "string")

    if isinstance(oa_type, list):
        oa_type = next((t for t in oa_type if t != "null"), "string")

    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "list",
        "object": "dict",
    }

    result = {"type": type_map.get(oa_type, "str")}

    if oa_type == "array":
        items = schema.get("items", {})
        items_type = items.get("type", "string")
        if isinstance(items_type, list):
            items_type = next((t for t in items_type if t != "null"), "string")
        if items_type == "object" and "properties" in items:
            result["elements"] = "dict"
            result["suboptions"] = build_suboptions(items, depth=1)
        else:
            result["elements"] = type_map.get(items_type, "str")

    if oa_type == "object" and "properties" in schema:
        result["suboptions"] = build_suboptions(schema, depth=1)

    if "enum" in schema:
        result["choices"] = schema["enum"]

    return result


def build_suboptions(schema: dict, depth: int = 0) -> dict:
    """Build Ansible suboptions from an object schema."""
    if depth > 5:
        return {}

    suboptions = {}
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    for name, prop in properties.items():
        if name.startswith("_") or name in ("id", "created_time", "modified_time",
                                             "org_id", "site_id", "for_site"):
            continue

        option = {}
        desc = prop.get("description", "")
        if desc:
            option["description"] = desc

        type_info = openapi_type_to_ansible(prop)
        option.update(type_info)

        if name in required:
            option["required"] = True

        if "default" in prop:
            option["default"] = prop["default"]

        snake_name = camel_to_snake(name)
        suboptions[snake_name] = option

    return suboptions


def camel_to_snake(name: str) -> str:
    """Convert camelCase or kebab-case to snake_case."""
    name = name.replace("-", "_")
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def find_crud_resources(spec: dict) -> list[dict]:
    """Find all CRUD resources in the spec (collection + detail endpoints)."""
    paths = spec.get("paths", {})
    resources = []

    for path, path_item in sorted(paths.items()):
        methods = {k: v for k, v in path_item.items()
                   if k in ("get", "post", "put", "delete", "patch")}

        if "post" not in methods or "get" not in methods:
            continue

        parts = path.rstrip("/").split("/")
        last = parts[-1]
        if last.startswith("{"):
            continue

        # Check for detail endpoint
        detail_path = None
        for candidate in paths:
            if candidate.startswith(path + "/{") and candidate.count("/") == path.count("/") + 1:
                detail_path = candidate
                break

        if not detail_path:
            continue

        detail_item = paths[detail_path]
        detail_methods = {k: v for k, v in detail_item.items()
                         if k in ("get", "post", "put", "delete", "patch")}

        scope = "org" if "{org_id}" in path else "site" if "{site_id}" in path else "global"
        resource_name = last

        resources.append({
            "name": resource_name,
            "scope": scope,
            "collection_path": path,
            "detail_path": detail_path,
            "collection_methods": list(methods.keys()),
            "detail_methods": list(detail_methods.keys()),
            "collection_operations": methods,
            "detail_operations": detail_methods,
        })

    return resources


def extract_request_schema(operation: dict, spec: dict) -> Optional[dict]:
    """Extract the request body schema from an operation."""
    request_body = operation.get("requestBody", {})
    if not request_body:
        return None

    content = request_body.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})

    if not schema:
        return None

    return resolve_schema(schema, spec)


def extract_response_schema(operation: dict, spec: dict) -> Optional[dict]:
    """Extract the success response schema from an operation."""
    responses = operation.get("responses", {})
    for code in ("200", "201"):
        resp = responses.get(code, {})
        content = resp.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        if schema:
            return resolve_schema(schema, spec)
    return None


def generate_module_definition(resource: dict, spec: dict) -> dict:
    """Generate an Ansible module definition for a resource."""
    name = resource["name"]
    scope = resource["scope"]
    module_name = f"mist_{scope}_{name}"

    # Get the POST (create) schema for parameters
    post_op = resource["collection_operations"].get("post", {})
    create_schema = extract_request_schema(post_op, spec)

    # Get the PUT (update) schema
    put_op = resource["detail_operations"].get("put", {})
    update_schema = extract_request_schema(put_op, spec)

    # Merge schemas (update usually has same/superset of create)
    merged_schema = update_schema or create_schema or {}

    # Build module options from schema
    options = {}
    if merged_schema and "properties" in merged_schema:
        properties = merged_schema.get("properties", {})
        required = merged_schema.get("required", [])

        for prop_name, prop_schema in properties.items():
            if prop_name.startswith("_") or prop_name in (
                "id", "created_time", "modified_time", "org_id", "site_id", "for_site"
            ):
                continue

            option = {}
            desc = prop_schema.get("description", "")
            if desc:
                option["description"] = desc

            type_info = openapi_type_to_ansible(prop_schema)
            option.update(type_info)

            if prop_name in required:
                option["required"] = True

            if "default" in prop_schema:
                option["default"] = prop_schema["default"]

            snake_name = camel_to_snake(prop_name)
            options[snake_name] = option

    # Get description from tags or operation summary
    description = ""
    tags = post_op.get("tags", [])
    if tags:
        description = f"Manage {tags[0]} resources in Juniper Mist"
    else:
        summary = post_op.get("summary", "")
        description = summary or f"Manage {name} resources"

    has_delete = "delete" in resource["detail_methods"]
    has_update = "put" in resource["detail_methods"] or "patch" in resource["detail_methods"]

    states = ["present", "gathered"]
    if has_delete:
        states.append("absent")

    return {
        "module_name": module_name,
        "resource_name": name,
        "scope": scope,
        "collection_path": resource["collection_path"],
        "detail_path": resource["detail_path"],
        "description": description,
        "options": options,
        "states": sorted(states),
        "has_update": has_update,
        "has_delete": has_delete,
    }


def select_target_resources(resources: list[dict], targets: Optional[list[str]] = None) -> list[dict]:
    """Filter resources to only include specified targets."""
    if targets is None:
        return resources

    # Include "sites" in the name-match list
    return [r for r in resources if r["name"] in targets or
            f"{r['scope']}_{r['name']}" in targets]


DEFAULT_TARGETS = [
    "sites",
    "networks",
    "wlans",
    "webhooks",
    "psks",
    "sitegroups",
    "templates",
    "servicepolicies",
    "services",
    "vpns",
]

# Sites has a non-standard detail path (/api/v1/sites/{site_id} instead of
# /api/v1/orgs/{org_id}/sites/{site_id}), so we handle it manually.
MANUAL_RESOURCES = [
    {
        "name": "sites",
        "scope": "org",
        "collection_path": "/api/v1/orgs/{org_id}/sites",
        "detail_path": "/api/v1/sites/{site_id}",
        "collection_methods": ["get", "post"],
        "detail_methods": ["get", "put", "delete"],
        "collection_operations": None,
        "detail_operations": None,
    }
]


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "specs/mist.openapi.json"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "tools/output"

    print(f"Loading spec from {spec_path}...")
    spec = load_spec(spec_path)

    print("Finding CRUD resources...")
    resources = find_crud_resources(spec)
    print(f"Found {len(resources)} CRUD resources")

    # Add manual resources with operations populated from spec
    for manual in MANUAL_RESOURCES:
        manual = dict(manual)
        coll_path = manual["collection_path"]
        detail_path = manual["detail_path"]
        if coll_path in spec.get("paths", {}):
            path_item = spec["paths"][coll_path]
            manual["collection_operations"] = {
                k: v for k, v in path_item.items()
                if k in ("get", "post", "put", "delete", "patch")
            }
        if detail_path in spec.get("paths", {}):
            path_item = spec["paths"][detail_path]
            manual["detail_operations"] = {
                k: v for k, v in path_item.items()
                if k in ("get", "post", "put", "delete", "patch")
            }
        resources.append(manual)

    # Filter to targets
    targets = select_target_resources(resources, DEFAULT_TARGETS)
    print(f"Selected {len(targets)} target resources for generation")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    module_defs = []
    for resource in targets:
        print(f"  Processing: {resource['scope']}/{resource['name']}...")
        module_def = generate_module_definition(resource, spec)
        module_defs.append(module_def)

        # Write individual module definition
        mod_file = output_path / f"{module_def['module_name']}.json"
        with open(mod_file, "w") as f:
            json.dump(module_def, f, indent=2, default=str)

    # Write summary
    summary = {
        "modules": [
            {
                "module_name": m["module_name"],
                "resource_name": m["resource_name"],
                "scope": m["scope"],
                "collection_path": m["collection_path"],
                "detail_path": m["detail_path"],
                "states": m["states"],
                "option_count": len(m["options"]),
            }
            for m in module_defs
        ]
    }
    with open(output_path / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nGenerated {len(module_defs)} module definitions in {output_dir}/")
    for m in module_defs:
        print(f"  {m['module_name']}: {len(m['options'])} options, states={m['states']}")


if __name__ == "__main__":
    main()
