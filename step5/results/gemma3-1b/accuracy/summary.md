# Accuracy: gemma3:1b-it-q4_K_M

Overall: **48/160 = 30.0%** (R5 needs >= 136/160)  
Output conformance: 131/160 = 81.9% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 131, mean 2389.3, p50 2404.7, p95 4143.6, p99 4650.3, max 5016.9

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 33 | 23 | 69.7% | FAIL |
| Debt collection | 24 | 7 | 29.2% | FAIL |
| Mortgage | 18 | 11 | 61.1% | FAIL |
| Credit card | 11 | 1 | 9.1% | FAIL |
| Bank account or service | 30 | 4 | 13.3% | FAIL |
| Consumer loan | 16 | 2 | 12.5% | FAIL |
| Money transfer or service | 28 | 0 | 0.0% | FAIL |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 23 | 3 | 1 | 0 | 0 | 2 | 0 | 4 |
| DC | 6 | 7 | 0 | 0 | 0 | 2 | 0 | 9 |
| Mtg | 4 | 0 | 11 | 0 | 0 | 0 | 0 | 3 |
| CC | 5 | 0 | 0 | 1 | 1 | 0 | 0 | 4 |
| Bank | 18 | 1 | 1 | 0 | 4 | 2 | 2 | 2 |
| Loan | 0 | 3 | 3 | 3 | 1 | 2 | 0 | 4 |
| MT | 8 | 1 | 1 | 1 | 3 | 11 | 0 | 3 |
