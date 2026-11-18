# Assignment 2 accuracy limits

Source: Assignment 1 Llama prediction records, even dataset rows only.

**Reuse verified on the Lenovo service PC (18 Nov 2026).** Model ID `46e0c10c039e` unchanged
(`ollama list`); no change to `app/`, `compose.yaml`, `Dockerfile` or `requirements.txt` since the
Assignment 1 freeze commit `3567f80` (prompt and request options identical); Ollama 0.12.3; same
machine with the same Docker limits (8 CPUs, 7.53 GiB).

**Re-run check.** Llama was also re-run on all 80 test tickets through `POST /tickets`
(`assignment2/results/step1_top_model_test_set/`). It returned 61/80 with **the same answer as
Assignment 1 on every one of the 80 tickets**, so the limits below are reproduced, not only reused.
The narratives were taken from `assignment2/data/test_set.csv` (the frozen Assignment 1 text);
the Excel sheet has collapsed double spaces in 26 narratives, so it is not used as model input.

| Category | Correct | Wrong | Accuracy | Minimum accuracy | Minimum correct |
|---|---:|---:|---:|---:|---:|
| Overall | 61/80 | 19 | 76.25% | 66.25% | 53/80 |
| Credit reporting | 14/19 | 5 | 73.68% | 58.68% | 12/19 |
| Debt collection | 7/11 | 4 | 63.64% | 48.64% | 6/11 |
| Mortgage | 5/7 | 2 | 71.43% | 56.43% | 4/7 |
| Credit card | 6/6 | 0 | 100.00% | 85.00% | 6/6 |
| Bank account or service | 10/14 | 4 | 71.43% | 56.43% | 8/14 |
| Consumer loan | 5/8 | 3 | 62.50% | 47.50% | 4/8 |
| Money transfer or service | 14/15 | 1 | 93.33% | 78.33% | 12/15 |

Percentages are rounded for display; pass counts use exact fractions.
A configuration must pass the overall limit and all seven category limits.

Mortgage, Credit card and Consumer loan have fewer than ten test tickets.
Individual errors therefore cause large percentage changes.

These test outcomes must not be used to design the escalation rule.
