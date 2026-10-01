# Step 3: Workload model (Team 9)

Authors: Tan Ye Kai, Youxiong. Compiled 1 Oct 2026.

Every figure below is labelled **[Sourced]** (with a reference), **[Measured]** (from our dataset) or **[Estimate]** (with the reasoning). Evidence lives in [`sources/`](sources/) (index: [`sources/SOURCES.md`](sources/SOURCES.md)), and the full research trail is in [`research-notes.md`](research-notes.md).

## Summary

| Metric | Off-peak | Average | Peak | Peak + growth headroom |
|---|---|---|---|---|
| Tickets (`POST /tickets`) per hour | ~18 | ~43 | **~81** | **~105** |
| Tickets per minute | 0.30 | 0.72 | 1.35 | 1.75 |
| Agents working | ~9 | ~22 | ~41 | ~53 |
| Searches (`GET /search`) per hour | ~55 | ~130 | **~243** | **~316** |
| Ticket length (words) | median 140 · p95 305 · p99 352 · max 369 | | | |

Short bursts above the peak (for stress testing):

| Burst | Ticket rate | Basis |
|---|---|---|
| First 15 minutes of the peak hour | ~130/hr (2.2/min) | **[Sourced]** 1.6× within-hour burst [R6] |
| Incident surge (e.g. app outage) | ~243/hr (4.0/min) | **[Estimate]** 3× peak hour, see §4.3 |

## 1. Client volume

| Step | Value | Label |
|---|---|---|
| Barclays Bank UK PLC complaints opened, 1 Jan – 30 Jun 2026 | 94,535 | **[Sourced]** [R1], screenshot S6 |
| Annualised (× 2) | **189,070 per year** | Calculated |

**Why Barclays.** The client is a single financial-services company, so we need one firm's *own* complaint intake. UK firms must report this to the FCA (1.74m complaints across all UK firms in 2025 H2 [R4]), while US banks don't publish theirs. CFPB per-company counts (e.g. KeyCorp 620 in 2024 [R3]) only cover complaints escalated to the regulator, so they are far smaller than a desk's real intake (hundreds to low thousands a year for mid-sized US banks [R3], versus 94,535 in six months at Barclays). Barclays Bank UK PLC is a large retail bank (current accounts, credit cards, mortgages, loans), so its product range covers all 7 of our categories. We excluded the other two Barclays firms: Clydesdale Financial Services has 34,133 opened but only 1,275 closed, which isn't normal desk flow, and Barclays Bank PLC is mainly the corporate and investment bank.

**Caveat.** Barclays reports that volumes were down 40% compared with H1 2025 [R1], so 189,070 comes from a low half-year. The growth headroom in §5 partly covers this.

## 2. Daily pattern

Our service receives **written** complaints (typed narratives via `POST /tickets`), comparable to the CFPB's online complaint form, which accepts submissions every day. So we model arrivals over **365 days**.

| Step | Value | Label |
|---|---|---|
| Average day: 189,070 ÷ 365 | 518 tickets/day | Calculated |
| Busiest day vs 7-day average | **1.25×** | **[Sourced]** CFPB daily counts, two sample weeks [R3] |
| Busiest day: 518 × 1.25 | **648 tickets/day** | Calculated |
| Quietest day (Sunday) vs 7-day average | 0.42–0.50× | **[Sourced]** same |
| Weekend share of weekly volume | ~16% | **[Sourced]** same |

CFPB daily counts, all companies ([research-notes §6](research-notes.md) lists the API query for every day):

| | Mon | Tue | Wed | Thu | Fri | Sat | Sun |
|---|---|---|---|---|---|---|---|
| 2–8 Oct 2023 | 4,290 | 4,776 | 4,975 | 4,894 | 4,622 | 2,652 | 1,672 |
| 4–10 Mar 2024 | 6,140 | 7,386 | 7,182 | 7,477 | 6,626 | 4,018 | 2,977 |

Monday is the quietest weekday for written complaints, and Tuesday–Thursday are busiest. Industry sources say Monday is busiest for **phone** contact centres [R6], but that doesn't apply to a written channel, so we use the CFPB pattern.

## 3. Hourly pattern

| Step | Value | Label |
|---|---|---|
| Arrival window | **12 hours (8am–8pm)** | **[Estimate]** Online submission isn't limited to office hours, but few complaints arrive overnight. Taylor's bank call centre was open 14 hours [R7]; office hours would be 9. We take 12 as a middle value. |
| Average hour, busiest day: 648 ÷ 12 | 54/hr | Calculated |
| Busiest hour vs average hour | **1.5×** | **[Estimate]** No published hourly share exists for financial-services complaints. Industry data puts the daily peak at 10am–12pm [R6]. Taylor (2012) found the busiest half-hour in 34 weeks was ~2× the median [R7], an upper bound that includes busy days too. 1.5× sits between these. |
| **Peak hour: 54 × 1.5** | **~81 tickets/hr** | Calculated |

**Cross-check.** Applying Taylor's 2× worst-case ratio to the average hour (518 ÷ 12 = 43/hr) gives ~86/hr, close to our 81/hr. A separate calculation by Youxiong (Barclays volume → peak day ÷ working hours) also reached ~80/hr.

**Off-peak.** Sunday (0.42× the 7-day average) ÷ 12 hours ≈ 18/hr.

## 4. Bursts within the peak

### 4.1 Within-hour burst [Sourced]
Call Centre Helper reports that 40% of an hour's calls arrive in its first 15 minutes [R6], which is 1.6× the hour's average rate. This is phone data; we apply it to written tickets as the best available figure. Peak hour × 1.6 = **~130/hr for ~15 minutes**.

### 4.2 Natural randomness
Even at a steady average rate, arrivals are random, so some minutes see several tickets at once. Open-loop load testing (JMeter Open Model Thread Group) reproduces this, so we don't add a separate factor for it.

### 4.3 Incident surge [Estimate]
Taylor's 2× [R7] comes from a phone call centre (published 2012), where callers queue and many give up during busy periods. We estimate a **3× peak-hour surge (~243/hr, 4 per minute)** for a modern written channel because:
- mobile and web submission is available at all hours and has no queue to discourage customers, and
- bank-wide incidents such as an app outage or a card-payment failure make many customers complain within the same hour.

No published figure for written complaint bursts was found, so this is a labelled estimate. It defines a stress-test level, not a normal operating requirement.

## 5. Growth headroom [Estimate, supported]

| Evidence | Direction | Label |
|---|---|---|
| FIDReC: claims against banks and finance companies 1,387 → 1,831 (+32%), FY2023/24 → FY2024/25 | Up | **[Sourced]** [R5] |
| CFPB complaints received 1,657,600 (2023) → 3,187,900 (2024) | Up (mostly credit reporting) | **[Sourced]** [R2] |
| Barclays complaints −40% vs H1 2025 | Down | **[Sourced]** [R1] |

Complaint volumes swing both ways. We add **30% headroom** (peak 81 → **~105/hr**) so the system can absorb one year of growth at the rate FIDReC observed for claims against banks.

## 6. Agent search rate

Agents use `GET /search` to find related past complaints while handling a ticket. We size the agent count at the **peak hour**, because requirements must hold at peak and searches happen at the same time as peak ticket intake.

| Step | Value | Label |
|---|---|---|
| Agent time per complaint | 30 min | **[Estimate]** 56% of Barclays Bank UK PLC complaints close within 3 days [R1], which suggests most are routine. 30 minutes covers reading, investigating and a response. |
| Searches per agent per hour | 6 | **[Estimate]** About 3 searches per complaint (customer's previous tickets, similar issues, same product) × 2 complaints per hour. |
| Agents busy at peak: 81 × 0.5 | ~41 | Calculated, assuming agents keep pace with arrivals |
| **Searches at peak: 41 × 6** | **~243/hr** (~4/min) | Calculated |
| With headroom: 105 × 0.5 × 6 | ~316/hr | Calculated |

## 7. Ticket length distribution [Measured]

From our 1,000 rows (9000–9999) of `ict3113_tickets.csv`, produced by [`scripts/ticket_lengths.py`](../scripts/ticket_lengths.py). Output: [`ticket_lengths.json`](ticket_lengths.json), histogram [`ticket_lengths_hist.csv`](ticket_lengths_hist.csv).

| | min | mean | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|---|
| Words | 32 | 154.5 | 140 | 278 | 305 | 352 | 369 |
| Characters | 202 | 873.4 | 778 | 1,565 | 1,759 | 1,948 | 1,998 |

Histogram (words, 25-word bins):

```
 25– 49   56  ███████████
 50– 74  114  ███████████████████████
 75– 99  129  ██████████████████████████
100–124  137  ███████████████████████████
125–149   97  ███████████████████
150–174  101  ████████████████████
175–199   90  ██████████████████
200–224   71  ██████████████
225–249   56  ███████████
250–274   41  ████████
275–299   42  ████████
300–324   36  ███████
325–349   16  ███
350–374   14  ███
```

The distribution is right-skewed: most tickets are 50–200 words, with a long tail.

**Limitation.** All 50,000 rows in the course extract are between 200 and 2,000 characters, so the extract was clipped at both ends. Real complaints can be longer. Since LLM classification time grows with input length, real-world latency could be higher than what we measure.

**Load testing.** JMeter feeds narratives from our team's rows via CSV Data Set Config, so test traffic follows this real length distribution automatically.

## 8. Inputs for Step 4 and Step 5

Suggested arrival rates for load testing (to be confirmed in Step 4):

| Level | Tickets/hr | Tickets/min | Searches/hr (concurrent) |
|---|---|---|---|
| Off-peak | 18 | 0.30 | 55 |
| Average | 43 | 0.72 | 130 |
| **Peak** | **81** | **1.35** | **243** |
| **Peak + headroom** | **105** | **1.75** | **316** |
| Within-hour burst | 130 | 2.2 | 316 |
| Incident surge (stress) | 243 | 4.0 | 316 |
| Stress ramp | keep increasing until latency grows without bound or errors appear | | |

Searches for the two burst levels stay at the peak + headroom rate (316/hr), because the number of agents on shift doesn't change within an hour.

Requirements must hold at **peak + headroom** (105/hr). The surge level and the ramp beyond it belong to the stress test.

## 9. Assumptions and limitations

| # | Assumption / limitation | Effect if wrong |
|---|---|---|
| A1 | Barclays Bank UK PLC is a fair size proxy for the client. | Volume scales linearly: a client half Barclays' size would have half the rates. |
| A2 | H1 2026 × 2 represents a full year. Barclays volumes fell 40% year on year, so this may be low. | Partly covered by the 30% headroom. |
| A3 | The weekday pattern of US CFPB complaints applies to the client's written channel, whose volume is based on a UK bank. Based on two sample weeks only. | The busiest-day factor might differ. A full-year CFPB export would firm it up. |
| A4 | Tickets arrive within a 12-hour window; overnight arrivals are treated as negligible. | A 9-hour window gives a peak of ~108/hr; 14 hours gives ~69/hr. |
| A5 | Busiest hour = 1.5× the average hour. | Taylor's upper bound (2×) would give a peak of ~108/hr. |
| A6 | Incident surge = 3× the peak hour. | Only affects the stress test level, not the requirements. |
| A7 | 30 min of agent time per complaint and 6 searches per agent per hour; agents keep pace with arrivals. | Search load scales directly with both. |
| A8 | The course extract is clipped to 200–2,000 characters. | Real tickets can be longer and slower to classify. |

The stress test ramps load beyond every level above, so if any assumption is too low, the measured breaking point still shows how much margin the system has.

## References

- [R1] Barclays, *UK complaints data, January to June 2026*. https://home.barclays/who-we-are/reporting/uk-complaints-data/january-to-june-2026/
- [R2] CFPB, *Consumer Response Annual Report 2023* (PDF p.5, p.9). https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2023-03.pdf and *2024* (PDF p.5, p.9). https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2025-05.pdf
- [R3] CFPB, *Consumer Complaint Database* (API queries in [research-notes §3, §6](research-notes.md), retrieved 1 Oct 2026). https://www.consumerfinance.gov/data-research/consumer-complaints/
- [R4] FCA, *Aggregate complaints data: 2025 H2*. https://www.fca.org.uk/data/complaints-data/aggregate-complaints-data-2025-h2
- [R5] FIDReC, *FIDReC received a record 4,355 claims this fiscal year* (26 Nov 2025). https://www.fidrec.com.sg/knowledgebase/article/KA-01328/en-us
- [R6] Call Centre Helper, *10 Things You Need to Know About Call Centres*. https://www.callcentrehelper.com/10-things-to-know-about-call-centres-51312.htm
- [R7] Taylor, J.W. (2012). Density Forecasting of Intraday Call Center Arrivals using Models Based on Exponential Smoothing. *Management Science* 58, 534–549. https://users.ox.ac.uk/~mast0315/CallCenterStat&LogisticCountModels.pdf

All accessed 1 Oct 2026.
