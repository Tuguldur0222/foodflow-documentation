"""Executable checks for the W05 OpenAPI structure, references, and examples."""

from pathlib import Path
import re
import unittest

from jsonschema.exceptions import ValidationError
import yaml

from tests.openapi_helpers import UniqueKeyLoader, load_spec, resolve, validate_instance


class OpenAPIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = load_spec()

    def test_five_unique_operations_and_security(self):
        self.assertEqual(self.spec["openapi"], "3.0.3")
        operations = [operation for item in self.spec["paths"].values() for operation in item.values()]
        self.assertEqual(len(operations), 5)
        self.assertEqual(len({operation["operationId"] for operation in operations}), 5)
        self.assertEqual(self.spec["security"], [{"BearerAuth": []}])
        security = self.spec["components"]["securitySchemes"]["BearerAuth"]
        self.assertEqual((security["type"], security["scheme"]), ("http", "bearer"))

    def test_every_reference_resolves(self):
        def visit(value):
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertIsInstance(resolve(self.spec, value), dict)
                for child in value.values():
                    visit(child)
            elif isinstance(value, list):
                for child in value:
                    visit(child)
        visit(self.spec)

    def test_path_parameters_requests_and_response_examples(self):
        for path, item in self.spec["paths"].items():
            for method, operation in item.items():
                with self.subTest(path=path, method=method):
                    parameters = [resolve(self.spec, parameter) for parameter in operation["parameters"]]
                    declared = {parameter["name"] for parameter in parameters if parameter["in"] == "path"}
                    self.assertEqual(declared, set(re.findall(r"\{([^}]+)\}", path)))
                    for parameter in parameters:
                        self.assertTrue(parameter["required"])
                        validate_instance(self.spec, parameter["schema"], parameter["example"])
                    request = operation["requestBody"]
                    self.assertTrue(request["required"])
                    media = request["content"]["application/json"]
                    validate_instance(self.spec, media["schema"], media["example"])
                    self.assertTrue({"400", "401", "404", "409", "413", "415", "500"}.issubset(operation["responses"]))
                    self.assertTrue(any(status.startswith("2") for status in operation["responses"]))
                    for status, response in operation["responses"].items():
                        media = resolve(self.spec, response)["content"]["application/json"]
                        validate_instance(self.spec, media["schema"], media["example"])

    def test_all_schema_and_property_examples_are_valid(self):
        for name, schema in self.spec["components"]["schemas"].items():
            with self.subTest(schema=name):
                validate_instance(self.spec, schema, schema["example"])
                for property_name, property_schema in schema["properties"].items():
                    actual = resolve(self.spec, property_schema)
                    if "example" in actual:
                        validate_instance(self.spec, actual, actual["example"])

    def test_validator_detects_bad_quantities_and_extra_fields(self):
        schema = self.spec["components"]["schemas"]["ChangeQuantity"]
        for instance in ({"quantity": 0}, {"quantity": 11}, {"quantity": True}, {"quantity": 1.5}, {"quantity": 2, "unknown": 1}):
            with self.subTest(instance=instance), self.assertRaises(ValidationError):
                validate_instance(self.spec, schema, instance)

    def test_phone_schema_rejects_trailing_newline(self):
        schema = self.spec["components"]["schemas"]["Address"]
        invalid = {**schema["example"], "phone": "99112233\n"}
        with self.assertRaises(ValidationError):
            validate_instance(self.spec, schema, invalid)

    def test_duplicate_yaml_keys_are_rejected(self):
        with self.assertRaises(ValueError):
            yaml.load("quantity: 1\nquantity: 2\n", Loader=UniqueKeyLoader)

    def test_renderer_decision_contains_exactly_100_whitespace_words(self):
        report = (Path(__file__).resolve().parents[1] / "docs/api/renderer-decision.md").read_text(encoding="utf-8")
        passage = report.split("<!-- decision:start -->")[1].split("<!-- decision:end -->")[0].strip()
        self.assertEqual(len(passage.split()), 100)


if __name__ == "__main__":
    unittest.main()
