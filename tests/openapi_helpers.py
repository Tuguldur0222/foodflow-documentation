"""Validate the JSON Schema subset used by this OpenAPI 3.0.3 contract.

This helper validates examples and local references. Redocly CLI remains the
authoritative OpenAPI linter; this helper is not a replacement for that tool.
"""

from pathlib import Path

from jsonschema import Draft4Validator
import yaml


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "docs/api/openapi.yaml"


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently replacing them."""


def unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_spec():
    return yaml.load(SPEC_PATH.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)


def resolve(spec, value):
    if not isinstance(value, dict) or "$ref" not in value:
        return value
    reference = value["$ref"]
    if not reference.startswith("#/"):
        raise ValueError(f"Only local references are allowed: {reference}")
    target = spec
    for part in reference[2:].split("/"):
        target = target[part.replace("~1", "/").replace("~0", "~")]
    return resolve(spec, target)


def inline_schema(spec, schema):
    schema = resolve(spec, schema)
    if isinstance(schema, dict):
        return {key: inline_schema(spec, value) for key, value in schema.items()}
    if isinstance(schema, list):
        return [inline_schema(spec, value) for value in schema]
    return schema


def validate_instance(spec, schema, instance):
    expanded = inline_schema(spec, schema)
    Draft4Validator.check_schema(expanded)
    Draft4Validator(expanded).validate(instance)


def response_media(spec, path, method, status):
    response = spec["paths"][path][method]["responses"][str(status)]
    return resolve(spec, response)["content"]["application/json"]
