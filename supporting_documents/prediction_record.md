# Prediction record — Group P1-9

Extract of `STEP4.md` as frozen at commit `3567f80` (7 Oct 2026, 23:36 SGT), before the first benchmark run (15:38 UTC = 23:38 SGT). The prediction text below is copied unchanged; only setup instructions and superseded draft wording were left out. Full original: `STEP4.md` in the repository.

## Candidate models

| Candidate | Exact Ollama tag | Parameter class | Approximate download | Purpose in the comparison | Licence |
|---|---|---:|---:|---|---|
| [Gemma 3 1B](https://ollama.com/library/gemma3/tags) | `gemma3:1b-it-q4_K_M` | Small, 1B | 815 MB | Fast, low-resource baseline | [Gemma Terms](https://ai.google.dev/gemma/terms) |
| [Qwen3 4B Instruct](https://ollama.com/library/qwen3/tags) | `qwen3:4b-instruct-2507-q4_K_M` | Medium, 4B | 2.5 GB | Predicted balance between accuracy and CPU performance | [Apache 2.0](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE) |
| [Llama 3.1 8B Instruct](https://ollama.com/library/llama3.1/tags) | `llama3.1:8b-instruct-q4_K_M` | Large, 8B | 4.9 GB | Accuracy ceiling and large-model comparison | [Llama 3.1 Community License](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/README.md) |

Pinned locally after pulling (`evidence/step4/ollama-list.txt`):

| Exact tag | Local Ollama model ID or digest | Pull date | Evidence file |
|---|---|---|---|
| `gemma3:1b-it-q4_K_M` | ID `8648f39daa8f`; weights `sha256:7cd4618c1faf8b7233c6c906dac1694b6a47684b37b8895d470ac688520b9c01` (999.89M params, Q4_K_M, 815 MB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `gemma3-1b-it-q4_K_M-show.txt`, `gemma3-1b-it-q4_K_M-modelfile.txt` |
| `qwen3:4b-instruct-2507-q4_K_M` | ID `0edcdef34593`; weights `sha256:85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9` (4.0B params, Q4_K_M, 2.5 GB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `qwen3-4b-instruct-2507-q4_K_M-show.txt`, `qwen3-4b-instruct-2507-q4_K_M-modelfile.txt` |
| `llama3.1:8b-instruct-q4_K_M` | ID `46e0c10c039e`; weights `sha256:667b0c1932bc6ffc593ed1d03f895bf2dc8dc6df21db3042284a6f4416b06a29` (8.0B params, Q4_K_M, 4.9 GB) | 2026-10-07 | `evidence/step4/ollama-list.txt`, `llama3-1-8b-instruct-q4_K_M-show.txt`, `llama3-1-8b-instruct-q4_K_M-modelfile.txt` |

## Requirements referred to below (R1–R8)

| Req | Statement (full text: `STEP4.md` section 4) |
|---|---|
| R1 | ≥ 105 successful classifications/h at 105 POST/h + 316 search/h, backlog not growing |
| R2 | `POST /tickets` p95 ≤ 30 s, p99 ≤ 60 s at the R1 load |
| R3 | `GET /search` p95 ≤ 2 s, p99 ≤ 5 s at the R1 load |
| R4 | ≤ 1.0% errors per endpoint at the R1 load |
| R5 | ≥ 85.0% overall accuracy on the golden set (≥ 136/160) |
| R6 | ≥ 70.0% accuracy in every category |
| R7 | ≥ 99.0% valid JSON with an exact category name |
| R8 | CPU-only local Ollama; 0 restarts or OOM kills |

## 1. Bottleneck prediction

1. **First component to saturate: Ollama CPU inference.** More than 95% of each `POST /tickets` response time will be spent waiting on the Ollama `/api/chat` call. Prompt processing (prefill of roughly 300 input tokens: system prompt plus narrative) will take most of that time, because the JSON answer is only about 12 output tokens. PostgreSQL insert time and API overhead together will stay under 100 ms per request.
2. **Symptom at saturation:** Ollama processes requests effectively one at a time on 8 CPU threads. Once the arrival rate exceeds about 3,600 / (single-request latency in seconds) tickets per hour, `POST /tickets` latency will grow steadily for as long as the overload lasts (unbounded queue growth, not a plateau). Once a queued request waits more than the API's 300-second Ollama timeout, it will fail with HTTP 502. Errors will appear only after that point; there will be no early connection failures.
3. **Predicted stress limit (Qwen3 4B):** the maximum sustainable arrival rate is about **700 tickets per hour** (3,600 / 5 s).
4. **Search is not the bottleneck:** `GET /search` p95 will stay below **0.5 seconds** for every candidate at the 105/h condition. Its latency will rise only when inference saturates all CPU cores, because PostgreSQL competes for the same CPU.

## 2. Per-model predictions: accuracy and single-request latency

| Candidate | Predicted overall accuracy | Predicted warm single-request latency | Predicted R1-R8 outcome | Reason for prediction |
|---|---:|---:|---|---|
| Gemma 3 1B | 52% (83/160) | 1.5 s | R1 pass, R2 pass, R3 pass, R4 **fail**, R5 **fail**, R6 **fail**, R7 **fail** (96% conformant), R8 pass | Smallest model. Fastest: about 0.8 GB of weights, prefill of about 300 tokens at about 400 tokens/s on 8 CPU threads. Least able to apply the protocol's priority rules from category names alone, and expected to emit a non-exact category string (for example `Bank account`) on about 4% of tickets. Those become HTTP 502, which also breaks the 1% error budget (R4). |
| Qwen3 4B Instruct | 74% (118/160) | 5 s | R1 pass, R2 pass, R3 pass, R4 pass, R5 **fail**, R6 **fail**, R7 pass, R8 pass | 2.5 GB of weights; prefill about 80 tokens/s and decode about 17 tokens/s on this CPU. Recent instruction tuning with no thinking tokens gives strong format compliance. Predicted to be the most accurate candidate, but still below 85% because the golden labels follow team-specific priority rules (for example Mortgage over loan or debt, and Money transfer as the lowest priority) that the prompt does not state. |
| Llama 3.1 8B Instruct | 71% (114/160) | 10 s | R1 pass, R2 pass, R3 pass, R4 pass, R5 **fail**, R6 **fail**, R7 pass, R8 pass | 4.9 GB of weights, about twice Qwen3 4B, so roughly twice the prefill and decode time. At 105/h, utilisation is about 0.3, so p95 (about 22 s, driven by p95-length tickets of about 305 words) remains under 30 s. Predicted slightly *less* accurate than Qwen3 4B despite its size, because it is an older (2024) instruction tune. |

Latency predictions are reasoned estimates, not measurements: no golden or load ticket was sent to any model before the freeze. Per-model throughput was estimated from the parameter count and download size relative to the service CPU (Intel Core Ultra 7 256V: 4 performance cores plus 4 low-power efficiency cores, 8 threads, LPDDR5X memory). Prefill is compute-bound and decode is memory-bandwidth-bound, so time per ticket is expected to scale roughly linearly with model size. The predicted value is the warm p50 of the sequential accuracy run.

## 3. Hardest-category prediction

1. **Money transfer or service will be the hardest category for every candidate** (predicted per-category accuracy: Qwen3 4B 55%, Llama 3.1 8B 50%, Gemma 3 1B 35%). Payment-app and digital-wallet complaints (Cash App, PayPal, Zelle, Apple Cash) look like account problems. The team protocol also makes Money transfer the lowest-priority category, so the golden labels resolve many of these narratives to `Bank account or service` (for example row 9840), and the models cannot know that rule. Expected confusion: mostly between Money transfer and Bank account, in both directions.
2. **Consumer loan will be second hardest** (Qwen3 4B about 60%). Narratives about repayment difficulty and collection calls will be classified as `Debt collection`, and student or auto loans that damage a credit file as `Credit reporting`.
3. **Credit card** (only 11 tickets, so one error costs 9 percentage points) will lose tickets to `Credit reporting` and `Debt collection`, because the protocol excludes credit-card debt from this category.
4. **Credit reporting and Mortgage will be easiest** (≥ 85% for Qwen3 4B and Llama 3.1 8B). Their vocabulary is distinctive (credit bureau names, "inaccurate information", escrow, foreclosure, servicer).

Every candidate is therefore predicted to fail R6, because Money transfer or service falls below 70%.
