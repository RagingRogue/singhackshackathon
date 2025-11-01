# policybrain/compare.py
from __future__ import annotations
from .models import Policy

def _fmt_money(x):
    if x is None:
        return "-"
    try:
        n = float(x)
        if n.is_integer():
            n = int(n)
        return f"SGD {n:,}"
    except Exception:
        return str(x)

def compare_medical_md(pa: Policy, pb: Policy) -> str:
    a = pa.benefits.get("medical")
    b = pb.benefits.get("medical")
    rows = [
        ("Medical Coverage", _fmt_money(a.max_limit) if a else "-", _fmt_money(b.max_limit) if b else "-"),
        ("Per", (a.per or "-") if a else "-", (b.per or "-") if b else "-"),
        ("TCM sub-limit", _fmt_money(a.sublimits.get("tcm")) if a else "-", _fmt_money(b.sublimits.get("tcm")) if b else "-"),
    ]
    md = f"| Medical Coverage   | {pa.product_name}   | {pb.product_name}   |\n"
    md += "|--------------------|--------------|----------------|\n"
    for name, va, vb in rows:
        md += f"| {name:<18} | {va:<12} | {vb:<14} |\n"
    return md
