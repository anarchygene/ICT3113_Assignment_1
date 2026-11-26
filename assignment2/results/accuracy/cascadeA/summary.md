# Accuracy: cascade:gemma3:1b-it-q4_K_M>llama3.1:8b-instruct-q4_K_M

Overall: **55/80 = 68.8%**  
Output conformance: 80/80 = 100.0% (R7 needs >= 99.0%)  
Sequential single-request latency (ms): n 80, mean 16584.4, p50 13219.7, p95 38463.7, p99 77466.4, max 77466.4

| Category | n | Correct | Accuracy | R6 (>= 70%) |
|---|---:|---:|---:|---|
| Credit reporting | 19 | 11 | 57.9% | FAIL |
| Debt collection | 11 | 7 | 63.6% | FAIL |
| Mortgage | 7 | 5 | 71.4% | pass |
| Credit card | 6 | 6 | 100.0% | pass |
| Bank account or service | 14 | 10 | 71.4% | pass |
| Consumer loan | 8 | 3 | 37.5% | FAIL |
| Money transfer or service | 15 | 13 | 86.7% | pass |

## Confusion matrix (rows = golden, columns = predicted)

| golden \ predicted | CR | DC | Mtg | CC | Bank | Loan | MT | Invalid |
|---|---|---|---|---|---|---|---|---|
| CR | 11 | 4 | 1 | 2 | 1 | 0 | 0 | 0 |
| DC | 2 | 7 | 0 | 0 | 2 | 0 | 0 | 0 |
| Mtg | 0 | 0 | 5 | 1 | 0 | 1 | 0 | 0 |
| CC | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 |
| Bank | 1 | 0 | 0 | 1 | 10 | 0 | 2 | 0 |
| Loan | 1 | 1 | 2 | 0 | 1 | 3 | 0 | 0 |
| MT | 0 | 0 | 1 | 1 | 0 | 0 | 13 | 0 |
