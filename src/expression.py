"""A small, safe expression evaluator for story conditions.

Supports: boolean ops (and/or/not), comparisons, arithmetic, attribute access
on small proxy objects (flag.stat), numeric literals, and a single allowed
call `inv_has(item)` to check inventory. Any evaluation error returns False.
"""
from __future__ import annotations
import ast
from typing import Any, Dict


class AttrProxy:
    def __init__(self, backing: Dict[str, Any]):
        self._b = backing

    def __getattr__(self, item: str) -> Any:
        return self._b.get(item, False)


_ALLOWED_NODES = (
    ast.Expression,
    ast.BoolOp,
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.Name,
    ast.Load,
    ast.Constant,
    ast.Attribute,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.Call,
)


def _safe_node_check(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if not isinstance(n, _ALLOWED_NODES):
            return False
    return True


def safe_eval(expr: str, local: Dict[str, Any]) -> Any:
    try:
        tree = ast.parse(expr, mode='eval')
    except Exception:
        return False
    if not _safe_node_check(tree):
        return False

    def _eval(n: ast.AST) -> Any:
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return local.get(n.id, False)
        if isinstance(n, ast.Attribute):
            val = _eval(n.value)
            try:
                return getattr(val, n.attr)
            except Exception:
                return False
        if isinstance(n, ast.BinOp):
            left = _eval(n.left)
            right = _eval(n.right)
            if isinstance(n.op, ast.Add):
                return left + right
            if isinstance(n.op, ast.Sub):
                return left - right
            if isinstance(n.op, ast.Mult):
                return left * right
            if isinstance(n.op, ast.Div):
                return left / right
            if isinstance(n.op, ast.Mod):
                return left % right
            return False
        if isinstance(n, ast.UnaryOp):
            val = _eval(n.operand)
            if isinstance(n.op, ast.USub):
                return -val
            if isinstance(n.op, ast.UAdd):
                return +val
            if isinstance(n.op, ast.Not):
                return not val
            return False
        if isinstance(n, ast.BoolOp):
            if isinstance(n.op, ast.And):
                for v in n.values:
                    if not _eval(v):
                        return False
                return True
            if isinstance(n.op, ast.Or):
                for v in n.values:
                    if _eval(v):
                        return True
                return False
        if isinstance(n, ast.Compare):
            left = _eval(n.left)
            for op, comp in zip(n.ops, n.comparators):
                right = _eval(comp)
                if isinstance(op, ast.Eq) and not (left == right):
                    return False
                if isinstance(op, ast.NotEq) and not (left != right):
                    return False
                if isinstance(op, ast.Lt) and not (left < right):
                    return False
                if isinstance(op, ast.LtE) and not (left <= right):
                    return False
                if isinstance(op, ast.Gt) and not (left > right):
                    return False
                if isinstance(op, ast.GtE) and not (left >= right):
                    return False
                left = right
            return True
        if isinstance(n, ast.Call):
            # Only allow inv_has(name) style calls
            if isinstance(n.func, ast.Name) and n.func.id == 'inv_has':
                if len(n.args) != 1:
                    return False
                arg = _eval(n.args[0])
                return bool(arg)
            return False
        return False

    try:
        return _eval(tree)
    except Exception:
        return False


def make_local_map(state) -> Dict[str, Any]:
    return {
        'flag': AttrProxy(state.flags),
        'stat': AttrProxy(state.stats),
        'reputation': AttrProxy(state.reputation),
        'inventory': state.inventory,
        'inv_has': lambda item: state.inventory.get(item, 0) > 0,
    }
