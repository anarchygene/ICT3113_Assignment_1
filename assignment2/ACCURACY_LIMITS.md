# Assignment 2 accuracy limits

Source: Assignment 1 Llama prediction records, even dataset rows only.

**Reuse verification: pending confirmation from the Lenovo owner.**
Confirm unchanged model digest, prompt, Ollama version and machine.

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
