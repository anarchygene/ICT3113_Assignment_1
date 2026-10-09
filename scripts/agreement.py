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
# Row order of the label-count table, as in the workbook summary.
TABLE_ORDER = ["Credit card", "Credit reporting", "Mortgage", "Consumer loan",
               "Debt collection", "Bank account or service", "Money transfer or service"]
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

    n = len(rows)
    nums = [int(r[0]) for r in rows]
    agree = sum(x == y for x, y in zip(a, b))
    first_changed = sum(o != x for o, x in zip(source, a))
    final_changed = sum(o != f for o, f in zip(source, final))
    po, pe, k = kappa(a, b)
    po2, _, k2 = kappa(source, final)
    pct = lambda x: f"{100 * x / n:.2f}%"
    lines = [
        f"Golden set: {n} tickets, rows {min(nums)}-{max(nums)} (the last {n} of the team's rows)",
        'Source: "ICT3113 Golden Set P1-9.xlsx", sheet "Final Golden Set"',
        "Original = the label the consumer selected in the dataset (source_label).",
        "",
        "Relabelling against the original label",
        f"  First check changed {first_changed} ({pct(first_changed)}); {n - first_changed} ({pct(n - first_changed)}) kept the original",
        f"  Final golden label differs from the original on {final_changed} ({pct(final_changed)})",
        f"  Resolving disagreements reverted {sum(o != x and o == f for o, x, f in zip(source, a, final))} "
        f"first-check changes and added {sum(o == x and o != f for o, x, f in zip(source, a, final))} new ones",
        "",
        "Inter-annotator agreement (first check vs review)",
        f"  {agree} agree ({pct(agree)}), {n - agree} disagree ({pct(n - agree)})",
        f"  Observed agreement po = {po:.4f}; chance agreement pe = {pe:.4f}; Cohen's kappa = {k:.3f}",
        "  Caveat: the reviewer saw the first label (review design, not blind double-labelling), which tends to inflate kappa.",
        "",
        "Label counts",
        f"  {'Label':<27}{'Original':>9}{'First check':>13}{'Final':>7}",
    ]
    co, ca, cf = Counter(source), Counter(a), Counter(final)
    lines += [f"  {c:<27}{co[c]:>9}{ca[c]:>13}{cf[c]:>7}" for c in TABLE_ORDER]
    lines += ["", "Disagreements and resolutions (row: first check / review -> final):"]
    lines += [f"  {r[0]}: {x} / {y} -> {f}" for r, x, y, f in zip(rows, a, b, final) if x != y]
    lines += ["", f"Original label vs final golden label: po = {po2:.4f}, kappa = {k2:.3f}"]
    out = Path("evidence/step1/agreement.txt")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
