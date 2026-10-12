"""Reflection against a clearly labeled, seeded negative audit fixture.

Missing symbols are expected in the fixture, not accepted in published docs.
No assertion here establishes that a real external model hallucinated.
"""
import ast
import builtins
from pathlib import Path
import re
import unittest

import foodflow.order_service as module
from foodflow import OrderService

ROOT = Path(__file__).resolve().parents[1]


def referenced_symbols(path):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    docs = '\n'.join(ast.get_docstring(node) or '' for node in ast.walk(tree)
                     if isinstance(node, (ast.Module, ast.ClassDef,
                                          ast.FunctionDef, ast.AsyncFunctionDef)))
    return set(re.findall(r'``([A-Z][A-Za-z0-9_]*(?:\.[a-z_]+)?)``', docs))


def missing_symbols(references):
    missing = set()
    for reference in references:
        parts = reference.split('.')
        obj = getattr(module, parts[0], getattr(builtins, parts[0], None))
        for part in parts[1:]:
            obj = getattr(obj, part, None)
        if obj is None:
            missing.add(reference)
    return missing


class HallucinationTests(unittest.TestCase):
    def test_fixture_exposes_missing_method_and_type(self):
        references = referenced_symbols(ROOT / 'review/ai_candidate_docstring.py')
        self.assertEqual(missing_symbols(references),
                         {'OrderService.refund_order', 'RefundReceipt'})

    def test_corrected_snapshot_has_no_missing_symbol(self):
        references = referenced_symbols(ROOT / 'review/manual_docstring.py')
        self.assertEqual(missing_symbols(references), set())

    def test_all_published_public_methods_exist(self):
        self.assertEqual({name for name, value in vars(OrderService).items()
                          if not name.startswith('_') and callable(value)},
                         {'place_order', 'get_order', 'cancel_order'})

    def test_candidate_and_corrected_implementation_are_identical(self):
        def without_docs(path):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
                    if node.body and isinstance(node.body[0], ast.Expr):
                        value = node.body[0].value
                        if isinstance(value, ast.Constant) and isinstance(value.value, str):
                            node.body.pop(0)
            return ast.dump(tree, include_attributes=False)
        self.assertEqual(without_docs(ROOT / 'review/manual_docstring.py'),
                         without_docs(ROOT / 'review/ai_candidate_docstring.py'))


if __name__ == '__main__':
    unittest.main()
