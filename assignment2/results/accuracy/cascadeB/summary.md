# Accuracy: cascade:gemma3:1b-it-q4_K_M>llama3.1:8b-instruct-q4_K_M

Overall: **58/80 = 72.5%**  
Output conformance: 80/80 = 100.0% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 80, mean 14390.4, p50 12273.9, p95 28173.8, p99 36030.2, max 36030.2

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 19 | 13 | 68.4% | FAIL |
| Debt collection | 11 | 7 | 63.6% | FAIL |
| Mortgage | 7 | 5 | 71.4% | pass |
| Credit card | 6 | 6 | 100.0% | pass |
| Bank account or service | 14 | 10 | 71.4% | pass |
| Consumer loan | 8 | 4 | 50.0% | FAIL |
| Money transfer or service | 15 | 13 | 86.7% | pass |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 13 | 2 | 1 | 2 | 1 | 0 | 0 | 0 |
| DC | 2 | 7 | 0 | 0 | 2 | 0 | 0 | 0 |
| Mtg | 0 | 0 | 5 | 1 | 0 | 1 | 0 | 0 |
| CC | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Bank | 1 | 0 | 0 | 1 | 10 | 0 | 2 | 0 |
| Loan | 1 | 0 | 2 | 0 | 1 | 4 | 0 | 0 |
| MT | 0 | 0 | 1 | 1 | 0 | 0 | 13 | 0 |
