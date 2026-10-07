#!/usr/bin/env python3
"""Step 1 inter-annotator agreement (Cohen's kappa) from the golden-set workbook.

Labeller A = 'New_Label'. Labeller B = A's label where 'Agree?' is YES, otherwise
'New2_Label'. Label spellings are normalised to the seven exact category names.
Writes evidence/step1/agreement.txt.

Usage: python scripts/agreement.py   (requires openpyxl)
"""
from collections import Counter
from pathlib import Path

import openpyxl

CATEGORIES = ["Credit reporting", "Debt collection", "Mortgage", "Credit card",
              "Bank account or service", "Consumer loan", "Money transfer or service"]
CANON = {c.lower(): c for c in CATEGORIES} | {"consumer loans": "Consumer loan"}


def norm(label) -> str:
    return CANON[str(label).strip().lower()]


def kappa(x: list[str], y: list[str]) -> tuple[float, float, float]:
    n = len(x)
    po = sum(a == b for a, b in zip(x, y)) / n
    cx, cy = Counter(x), Counter(y)
    pe = sum(cx[k] * cy[k] for k in CATEGORIES) / (n * n)
    return po, pe, (po - pe) / (1 - pe)


def main() -> int:
    wb = openpyxl.load_workbook("ICT3113 Golden Set P1-9.xlsx", read_only=True, data_only=True)
    rows = [r for r in wb["Final Golden Set"].iter_rows(min_row=2, max_col=9, values_only=True) if r[0] is not None]
    a = [norm(r[3]) for r in rows]
    b = [norm(r[3]) if str(r[6]).strip().upper() == "YES" else norm(r[7]) for r in rows]
    final = [norm(r[8]) for r in rows]
    source = [norm(r[1]) for r in rows]

    po, pe, k = kappa(a, b)
    lines = [
        f"Tickets: {len(rows)}",
        f"Labeller vs reviewer: {sum(x == y for x, y in zip(a, b))} agree, {sum(x != y for x, y in zip(a, b))} disagree",
        f"Observed agreement po = {po:.4f}; chance agreement pe = {pe:.4f}; Cohen's kappa = {k:.3f}",
        "Caveat: the reviewer saw the first label (review design, not blind double-labelling), which tends to inflate kappa.",
        "",
        "Disagreements (row: labeller A / reviewer B -> final):",
    ]
    lines += [f"  {r[0]}: {x} / {y} -> {f}" for r, x, y, f in zip(rows, a, b, final) if x != y]
    po2, _, k2 = kappa(source, final)
    lines += ["", f"Raw consumer label vs final golden label: po = {po2:.4f}, kappa = {k2:.3f} "
                  f"({sum(s != f for s, f in zip(source, final))} of {len(rows)} relabelled)"]
    out = Path("evidence/step1/agreement.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
