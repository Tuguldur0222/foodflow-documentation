"""Reconstruct the comparison fixture described by the original W06 PDF.

This is a seeded quality exercise. It is not a real GPT-4/Claude transcript,
and manual_docstring.py is a corrected baseline awaiting human authorship review.
"""
import ast
from difflib import unified_diff
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'foodflow/order_service.py').read_text(encoding='utf-8')
review = ROOT / 'review'
review.mkdir(exist_ok=True)
(review / 'manual_docstring.py').write_text(source, encoding='utf-8')
tree = ast.parse(source)
replacements = {}
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == 'OrderService':
        replacements[node.body[0].lineno] = (node.body[0].end_lineno,
            '    """Manage orders and refunds with ``OrderService.refund_order``.\n'
            '\n    Refunds return ``RefundReceipt``.\n    """\n')
    elif isinstance(node, ast.FunctionDef) and node.name == 'place_order':
        replacements[node.body[0].lineno] = (node.body[0].end_lineno,
            '        """Create an order; changed payloads with the same key create a new order.\n'
            '\n        Keys expire automatically after 24 hours.\n        """\n')
    elif isinstance(node, ast.FunctionDef) and node.name == 'cancel_order':
        replacements[node.body[0].lineno] = (node.body[0].end_lineno,
            '        """Cancel Pending, Confirmed or Delivered orders and refund QPay.\n'
            '\n        Caller ownership is not required.\n        """\n')
lines = source.splitlines(keepends=True)
for start, (end, text) in sorted(replacements.items(), reverse=True):
    lines[start - 1:end] = [text]
candidate = ''.join(lines)
(review / 'ai_candidate_docstring.py').write_text(candidate, encoding='utf-8')
diff = ''.join(unified_diff(source.splitlines(keepends=True),
                            candidate.splitlines(keepends=True),
                            fromfile='manual_docstring.py (corrected baseline)',
                            tofile='ai_candidate_docstring.py (seeded fixture)'))
(review / 'manual_vs_ai.diff').write_text(diff, encoding='utf-8')
print('Wrote corrected baseline, seeded negative fixture and documentation-only diff.')
