# Complaints desk workload: research notes

Compiled 1 October 2026 for the complaints-desk workload model. These notes bring together everything researched so far, so a teammate can use the numbers without the original chat.

**How to read the status labels**

| Label | Meaning |
|---|---|
| **human-verified** | A teammate checked it by hand in the original source. Applies only to the items listed in the table below. |
| **verified from source text** | Read from the source's text, an API response, or a page pasted in full. Not yet checked by a person. |
| **read from chart** | Taken from a chart image. No text value was available to check against. |
| **unverified / could not access** | The source could not be opened, or different reads gave conflicting values. Do not cite. |
| **calculated** | Arithmetic on the numbers above it. Inputs and formula are shown. |
| **assumption** | A modelling choice, not data. It needs a written reason. |

**Page numbers.** "PDF page" means the page index shown in a PDF viewer. "Printed page" means the number in the page footer. For the CFPB product sections (§4), only printed pages were read. Check them in a PDF viewer before citing.

---

## 1. Summary table

| # | Figure | Value | Source | Location | URL | Status |
|---|---|---|---|---|---|---|
| 1 | CFPB complaints received, 2023 | ~1,657,600 | CFPB Consumer Response Annual Report 2023 | PDF p.9 (primary); also PDF p.5 | https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2023-03.pdf | human-verified |
| 2 | CFPB complaints sent to companies, 2023 | ~1,348,200 (81%) | same | PDF p.9 | same | human-verified |
| 3 | CFPB complaints received, 2024 | ~3,187,900 | CFPB Consumer Response Annual Report 2024 | PDF p.9 (primary); also PDF p.5 | https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2025-05.pdf | human-verified |
| 4 | CFPB complaints sent to companies, 2024 | ~2,829,400 (89%) | same | PDF p.9 | same | human-verified |
| 5 | CFPB database, all complaints, 2023 | 1,292,049 | CFPB API | query below | [2023 total](https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-01-01&date_received_max=2023-12-31&size=0&no_aggs=true) | verified from source text |
| 6 | CFPB database, all complaints, 2024 | 2,734,268 | CFPB API | query below | [2024 total](https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&frm=0) | verified from source text |
| 7 | CFPB database, KEYCORP, 2024 | 620 | CFPB API | §3 | see §3 | human-verified |
| 8 | CFPB database, all companies, 2 Oct 2023 | 4,290 | CFPB API | §6 | see §6 | human-verified |
| 9 | Barclays Bank UK PLC complaints opened, H1 2026 | 94,535 | Barclays UK complaints data, Jan–Jun 2026 | BBUKPLC table, "Total" row | https://home.barclays/who-we-are/reporting/uk-complaints-data/january-to-june-2026/ | verified from source text (page pasted in full) |
| 10 | Barclays Bank UK PLC, annualised | 189,070 | — | 94,535 × 2 | — | calculated |
| 11 | FCA: firm complaints, 2025 H2 | 1.74m (H1: 1.83m) | FCA aggregate complaints data 2025 H2 | Key findings | https://www.fca.org.uk/data/complaints-data/aggregate-complaints-data-2025-h2 | human-verified |
| 12 | FOS new complaints, H2 2025 | 146,603 | FOS half-yearly complaints data H2 2025 | business table | https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/half-yearly-complaints-data-h2-2025 | verified from source text |
| 13 | FOS new complaints, Barclays Bank UK PLC, H2 2025 | 6,826 | same | business table | same | verified from source text |
| 14 | UK escalation ratio, all firms | ~8.4% (≈1 in 12) | — | 146,603 ÷ 1,740,909 | — | calculated |
| 15 | Barclays escalation ratio | ~7.2% | — | 6,826 ÷ 94,535 (different periods) | — | calculated |
| 16 | CFPB busiest weekday vs weekday average | 1.06–1.07× (Tue–Thu) | CFPB API daily counts | §6 | see §6 | calculated from verified counts |
| 17 | CFPB busiest day vs 7-day average | 1.25× | same | §6 | see §6 | calculated |
| 18 | Taylor (2012), US bank: busiest half-hour vs median | 2,521 ÷ 1,278 ≈ 1.97× | Management Science 58:534–549 | Data section | https://users.ox.ac.uk/~mast0315/CallCenterStat&LogisticCountModels.pdf | verified from source text (inputs); ratio calculated |
| 19 | Share of an hour's calls arriving in its first 15 min | 40% (→ 1.6×) | Call Centre Helper | "10 Things" article | https://www.callcentrehelper.com/10-things-to-know-about-call-centres-51312.htm | verified from source text |
| 20 | FIDReC scam-related claims | 829 → 1,285 (+55%) | FIDReC news, 26 Nov 2025 | article text | https://www.fidrec.com.sg/knowledgebase/article/KA-01328/en-us | verified from source text |

---

## 2. CFPB totals 2023 and 2024

**Sources**
- 2023 report, PDF: https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2023-03.pdf (landing page https://www.consumerfinance.gov/data-research/research-reports/consumer-response-annual-report-2023/, published 29 Mar 2024, data as of 1 Mar 2024)
- 2024 report, PDF: https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2025-05.pdf (landing page https://www.consumerfinance.gov/data-research/research-reports/2024-consumer-response-annual-report/, published 1 May 2025, data as of 3 Mar 2025)

The "2023-03" in the 2023 filename is not the publication date. Do not confuse it with the 2022 report (`cfpb_2022-consumer-response-annual-report_2023-03.pdf`).

### 2.1 Totals (Section 2 "Complaint numbers", PDF p.9)

| | 2023 | 2024 | Status |
|---|---|---|---|
| Received | ~1,657,600 | ~3,187,900 | human-verified |
| Sent to companies | ~1,348,200 (81%) | ~2,829,400 (89%) | human-verified |
| Referred to other regulators | 6% | 3% | verified from source text |
| Not actionable | 13% | 8% | verified from source text |

- The reports give referred and not-actionable complaints only as percentages, not counts.
- All report numbers are rounded ("approximately").
- Footnote 5 (p.5) says the counts exclude duplicates, whistleblower tips and complaints found not actionable.
- The later 2025 report repeats 3,187,900 for 2024 and gives ~6,635,400 for 2025 (p.5): https://files.consumerfinance.gov/f/documents/cfpb_2025-cr-annual-report_2026-03.pdf. Status: verified from source text.

### 2.2 By product (Section 4 "Complaint types")

Counts are received / sent to companies. Section numbers and printed pages are where each product's subsection starts. **Section numbers differ between years.**

| Product | 2023 received | 2023 sent | 2023 § / printed p. | 2024 received | 2024 sent | 2024 § / printed p. |
|---|---|---|---|---|---|---|
| Credit or consumer reporting | ~1,309,800 | 1,095,300 (84%) | §4.1 / p.19 | ~2,703,400 | ~2,451,400 (91%) | §4.1 / p.19 |
| Debt collection | ~109,900 | 69,600 (63%) | §4.2 / p.26 | ~207,800 | ~159,700 (77%) | §4.2 / p.24 |
| Credit card | ~70,000 | 56,600 (81%) | §4.3 / p.31 | ~92,100 | ~77,900 (85%) | §4.3 / p.32 |
| Checking or savings | ~64,500 | 51,300 (80%) | §4.4 / p.36 | ~67,900 | ~54,100 (80%) | §4.4 / p.39 |
| Mortgage | ~27,900 | 23,300 (84%) | §4.5 / p.41 | ~26,100 | ~22,100 (85%) | §4.6 / p.51 |
| Money transfer / money services / virtual currency | ~21,800 | ~13,700 (62.6%) | §4.6 / p.47 | ~27,400 | ~17,100 (62%) | §4.5 / p.45 |
| Vehicle loan or lease | ~17,700 | 13,000 (73%) | §4.7 / p.51 | ~18,900 | ~14,000 (74%) | §4.7 / p.57 |
| Student loan | ~12,000 | 10,700 (89%) | §4.8 / p.56 | ~16,700 | ~14,900 (89%) | §4.8 / p.62 |
| Personal loan | ~8,300 | 5,400 (65%) | §4.9 / p.61 | ~9,500 | ~6,900 (73%) | §4.9 / p.66 |

**Status of the product figures**
- **2023:** verified from source text. Read from a text extraction of the PDF; printed pages only.
- **2024:** verified from source text. These came from summarised extraction; each figure matched across two or more separate reads, and pages are printed pages only.
- **Unverified / could not access:** prepaid card, debt or credit management, payday loan, title loan and deposit advance (§§4.10–4.14) in both years. For 2023 the text extraction stopped at printed p.63. For 2024 separate reads gave conflicting values. Don't use any numbers for these products.
- About 400 complaints a year have no product recorded (footnote to Figure 3, p.11).

**"Consumer/personal loan" is not one CFPB category.** Personal loan (§4.9) is reported separately from vehicle, student, payday, title and deposit advance loans. If the model needs a broader consumer-lending figure, adding personal + vehicle + student gives:
- **2023:** ~38,000 received / 29,100 sent
- **2024:** ~45,100 received / 35,800 sent

These broader totals are calculated, not taken from the reports.

### 2.3 Consumer Complaint Database (cross-check)

Retrieved 1 Oct 2026; the API reported last update 2026-10-01T12:00-05:00. Status for all values in this subsection: verified from source text (API).

- 2023 product aggregation: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-01-01&date_received_max=2023-12-31&size=0
- 2024 product aggregation: https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=false

| Product (database name) | 2023 | 2024 |
|---|---|---|
| Credit reporting (old name + new name; 2023 = 644,815 + 402,054) | 1,046,869 | 2,365,586 |
| Debt collection | 68,107 | 155,894 |
| Credit card (2023: old "Credit card or prepaid card" 35,310 + new "Credit card" 21,872) | 57,182 (35,310 + 21,872; includes some old-product prepaid cards, see note) | 75,989 |
| Checking or savings account | 49,873 | 52,821 |
| Mortgage | 22,853 | 21,438 |
| Money transfer, virtual currency, or money service | 13,749 | 16,751 |
| Vehicle loan or lease | 12,794 | 13,360 |
| Student loan | 10,633 | 14,657 |
| Payday/title/personal (/advance) loan (2023: old 4,684 + new 2,559) | 7,243 | 9,036 |
| Prepaid card (new product from Aug 2023) | 2,262 | 6,323 |
| Debt or credit management (new product from Aug 2023) | 484 | 2,413 |
| **Total** | **1,292,049** | **2,734,268** |

Notes on the database figures:
- For 2023 credit cards, the credit-card-only figure is **54,413**: the old product's credit-card sub-products (28,959 general-purpose + 3,582 store cards = 32,541) plus the new "Credit card" (21,872). Including all of the old prepaid gives **59,444** (old 35,310 + new 21,872 + new prepaid 2,262). Both are calculated from API values.
- **Why product names change in 2023:** on 24 Aug 2023 CFPB changed the complaint-form products. Credit card and prepaid card were split, credit repair moved to "Debt or credit management", and "advance loan" was added to the payday product. Older complaints keep their original names. Source: https://files.consumerfinance.gov/f/documents/cfpb_consumer_complaint_form_product_issue_options_August_2023_FINAL.pdf
- **Why the database is lower than the reports:** CFPB says only complaints sent to companies are eligible for publication, and complaints referred to other regulators are not published (https://www.consumerfinance.gov/data-research/consumer-complaints/).
- **How the two sources line up (calculated):** the database equals about 95.8% (2023) and 96.6% (2024) of "sent to companies", but only about 78% and 86% of "received".

---

## 3. CFPB per-company counts, 2024 (mid-sized US banks)

Date received 1 Jan – 31 Dec 2024. Retrieved 1 Oct 2026.

| Bank | Database company name | 2024 complaints | API URL | Status |
|---|---|---|---|---|
| KeyBank | KEYCORP | 620 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=KEYCORP | human-verified |
| Regions | REGIONS FINANCIAL CORPORATION | 880 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=REGIONS%20FINANCIAL%20CORPORATION | verified from source text |
| M&T Bank | M&T BANK CORPORATION | 904 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=M%26T%20BANK%20CORPORATION | verified from source text |
| Huntington | HUNTINGTON NATIONAL BANK, THE | 910 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=HUNTINGTON%20NATIONAL%20BANK%2C%20THE | verified from source text (cached response dated 2026-08-15; re-run) |
| Fifth Third | FIFTH THIRD FINANCIAL CORPORATION | 1,389 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=FIFTH%20THIRD%20FINANCIAL%20CORPORATION | verified from source text |
| Citizens | CITIZENS FINANCIAL GROUP, INC. | 1,973 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-01-01&date_received_max=2024-12-31&size=0&no_aggs=true&company=CITIZENS%20FINANCIAL%20GROUP%2C%20INC. | verified from source text |

**To reproduce in the search interface**
1. Open https://www.consumerfinance.gov/data-research/consumer-complaints/search
2. Set "Date received" to 01/01/2024 – 12/31/2024.
3. Choose the company name from the Company filter's suggestions.
4. Read the match count. The database updates daily, so record the retrieval date.

**Caveat:** these counts only cover complaints that customers escalated to the CFPB. They are **not** the bank's own complaint volume; compare §4, where Barclays received 94,535 in six months. Use CFPB data for product mix and trends, and firm-reported data for volume.

---

## 4. Barclays UK complaints data, January–June 2026

Source: https://home.barclays/who-we-are/reporting/uk-complaints-data/january-to-june-2026/

The page blocked automated access, so a teammate pasted its full text. All values in this section are **verified from source text**.

### 4.1 Totals by firm (exact values from the page)

| Firm | Complaints opened | Complaints closed | Closed within 3 days | Closed >3 days, within 8 weeks | Upheld |
|---|---|---|---|---|---|
| Barclays Bank UK PLC (BBUKPLC) | 94,535 | 93,983 | 56% | 43% | 58% |
| Clydesdale Financial Services Ltd (CFSL) | 34,133 | 1,275 | "-" | "-" | 31% |
| Barclays Bank PLC (BBPLC) | 11,772 | 11,494 | 70% | 27% | 56% |

**Youxiong's figures are all correct.** The page labels the 94,535 "Number of complaints opened" (Total row), not "Total complaints".

**Which brands each firm covers (per the page)**
- **BBUKPLC:** Barclays Bank UK Plc., Barclaycard, Barclays Business Bank and Tesco Bank, plus Barclays Insurance Services Company Ltd.
- **CFSL:** Barclays Partner Finance.
- **BBPLC:** Barclays Bank PLC, Barclays Corporate Bank, Barclays Private Bank, Barclays Asset Management Ltd and Barclays Investment Solutions Ltd.

### 4.2 Product breakdown: yes, by the six FCA categories

Barclays Bank UK PLC:

| FCA category | Complaints per 1,000 accounts | Opened | Closed | ≤3 days | 3 days–8 weeks | Upheld | Main cause |
|---|---|---|---|---|---|---|---|
| Banking and Credit Cards | 2.14 | 85,021 | 84,465 | 57% | 43% | 57% | General admin / customer service |
| Home Finance | 5.92 | 5,356 | 5,398 | 52% | 47% | 73% | General admin / customer service |
| Insurance and Pure Protection | 1.31 | 277 | 269 | 38% | 51% | 16% | Advising, selling and arranging |
| Decumulation and Pensions | 0.09 | 2 | 3 | 0% | 100% | 33% | Advising, selling and arranging |
| Investments | 1.00 | 22 | 21 | 14% | 81% | 57% | General admin / customer service |
| Credit Related | 2.85 | 3,857 | 3,827 | 48% | 51% | 57% | General admin / customer service |
| **Total** | | **94,535** | **93,983** | **56%** | **43%** | **58%** | |

- The category rows add up exactly to the totals (calculated).
- Banking and Credit Cards is about 90% of BBUKPLC complaints (85,021 ÷ 94,535, calculated).

Barclays Bank PLC:

| FCA category | Per 1,000 accounts | Opened | Closed | ≤3 days | 3 days–8 weeks | Upheld |
|---|---|---|---|---|---|---|
| Banking and Credit Cards | 9.3 | 10,450 | 10,202 | 75% | 22% | 55% |
| Home Finance | 2.2 | 2 | 1 | 0% | 100% | 0% |
| Insurance and Pure Protection | — | n/a | n/a | n/a | n/a | n/a |
| Decumulation and Pensions | — | 52 | 56 | 36% | 59% | 59% |
| Investments | 2.4 | 1,258 | 1,225 | 28% | 67% | 65% |
| Credit Related | 15.0 | 10 | 10 | 10% | 90% | 90% |
| **Total** | 7.1 | **11,772** | **11,494** | **70%** | **27%** | **56%** |

Clydesdale Financial Services Ltd: one row only, **Credit Related**.
- 22.98 complaints per 1,000 accounts.
- 34,133 opened, 1,275 closed.
- Closure percentages shown as "-"; 31% upheld.
- Main cause: "Information Sums / Charges or Product Performance".

### 4.3 Other context on the page

- **Volumes are falling.** Overall complaint volumes were down 40% compared with H1 2025. Banking was down 42%, Home Finance 18%, Decumulation, Life & Pensions 78%, and Investments 35%.
- **Account base.** BBUKPLC has 42 million accounts, and BBPLC has over 1.2 million accounts in the Banking category (current and savings accounts plus credit cards).
- **Main cause.** Most complaints are classed as "general administration and customer service", such as delays and bank errors.
- **Period.** The data covers complaints received and closed from 1 Jan to 30 Jun 2026 inclusive.
- **Next release.** H2 2026 data is due 26 Feb 2027.

### 4.4 Is the Clydesdale figure a motor-finance backlog?

**The page does not say.** There is no footnote about motor finance, an FCA complaint-handling pause, or a backlog.

What the page does show is consistent with a backlog, but that reading is an inference:
- CFSL trades as Barclays Partner Finance.
- Its complaints are all "Credit Related", which the glossary defines as hire purchase, debt purchasing and home credit.
- Only 3.7% of opened complaints were closed (1,275 ÷ 34,133, calculated).
- The closure-time columns are blank.

Do not describe it as an FCA pause in the write-up without a separate source. **Either way, leave CFSL out of the desk model:** its flow is not normal complaint handling.

### 4.5 Annualising and the escalation ratio

| Calculation | Result | Status |
|---|---|---|
| BBUKPLC annualised: 94,535 × 2 | **189,070** per year | calculated |
| Escalation ratio: FOS new complaints about BBUKPLC, H2 2025 (6,826) ÷ BBUKPLC complaints opened, H1 2026 (94,535) | **7.2%** (≈1 in 14) | calculated |
| Same ratio on an annual basis: (6,826 × 2) ÷ 189,070 | **7.2%** | calculated |

**Caveats on these figures**
- **Different periods.** The FOS figure is for Jul–Dec 2025 and the Barclays figure for Jan–Jun 2026.
- **Volumes were falling.** Barclays' complaints were 40% lower in H1 2026 than in H1 2025, so its H2 2025 volume was probably higher than 94,535. If so, the true ratio for the same period would be **below** 7.2%. This is a direction only; the H2 2025 figure was not obtained.
- **Lag.** FOS cases lag the firm complaints they come from by weeks to months.
- **Annualising H1 2026** builds in a low-volume half-year. State that in the model.
- **Not yet obtained.** The matched-period ratio needs BBUKPLC's H2 2025 figure, either from https://home.barclays/who-we-are/reporting/uk-complaints-data/july-to-december-2025/ (could not access) or from the FCA firm-level file at https://www.fca.org.uk/data/complaints-data/firm-level. Status: unverified / could not access.

---

## 5. UK escalation ratio (all firms) and caveats

| Figure | Value | Source | Status |
|---|---|---|---|
| Complaints firms received, 2025 H2 (Jul–Dec 2025) | 1.74m (2025 H1: 1.83m) | FCA Key findings: https://www.fca.org.uk/data/complaints-data/aggregate-complaints-data-2025-h2 | human-verified |
| Product groups, 2025 H2 (H1 in brackets) | Banking & credit cards 857,757 (899,910); Insurance & pure protection 665,370 (697,635); Decumulation & pensions 87,844 (94,035); Home finance 75,658 (78,616); Investments 54,280 (58,305) | same | verified from source text |
| Sum of product groups, H2 / H1 | 1,740,909 / 1,828,501 | — | calculated (matches 1.74m / 1.83m) |
| Change H1 → H2 | about −4.8% | — | calculated |
| Other H2 metrics | 44.77% closed within 3 days; 49.67% in 3 days–8 weeks; 5.56% over 8 weeks; 55.54% upheld (H1: 57.88%); redress £236m (H1: £284m) | same | verified from source text |
| FOS new complaints, H2 2025 | 146,603 | https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/half-yearly-complaints-data-h2-2025 | verified from source text |
| **Escalation ratio, all firms** | 146,603 ÷ 1,740,909 = **8.4% (≈1 in 12)** | — | calculated |

**Caveats**
- **Don't cite the FCA's percentage change.** The FCA text says "0.4% decrease", but 1.83m → 1.74m is about 4.8–4.9%.
- **Conflicting press figure.** Press coverage reported 1.87m for H2 2025 (https://theintermediary.co.uk/2026/04/financial-services-complaints-rise-to-1-87-million-in-h2-2025-fca/). This was not reconciled. Use the FCA's 1.74m; with 1.87m the ratio would be 7.8%. Status: unverified / could not access (reconciliation).
- **The UK ratio is an escalation rate.** UK customers must complain to the firm first and can go to the FOS only after a final response or 8 weeks. The CFPB is a direct channel, so the UK ratio can't be applied one-to-one to US banks.
- **FOS volumes in 2024/25 were inflated.** That year the FOS received 305,726 complaints, up from 198,798 in 2023/24 (https://www.financial-ombudsman.org.uk/who-we-are/data-insight/news/financial-ombudsman-service-receives-305000-complaints-2024-25). Drivers included motor-finance commission (73,328) and irresponsible or unaffordable lending (71,685). About 50% of cases were brought by professional representatives, up from 25%. The uphold rate was 27% for represented cases and 37% for direct consumer cases. Status: verified from source text.
- **FOS 2024/25 by product:** hire purchase (motor) 76,160; credit cards 60,364; current accounts 36,221; car/motorcycle insurance 14,082; conditional sale (motor) 11,521; fraud and scams 35,416. Status: verified from source text.
- **Unhappy customers don't all complain.** FCA Financial Lives 2024 (p.16) found that only 4% of investment-product holders who had a problem complained, and 57% of those who tried found it difficult or couldn't complain (https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf). Status: verified from source text.
- **No US equivalent.** No published US estimate was found of complaints made directly to a bank per complaint made to the CFPB.

**Suggested US estimation approach** (the multipliers are assumptions)
1. Scale by account base, using Barclays' complaints per 1,000 accounts in §4.2.
2. Cross-check by dividing a bank's CFPB count by about 8%. Treat the result as a lower bound.
3. Run a sensitivity analysis on the multiplier.

---

## 6. CFPB weekday pattern

Each value is one API query for a single date received, retrieved 1 Oct 2026 (last update 2026-10-01T12:00-05:00). Index = day ÷ Monday–Friday average (calculated). Status for every count: verified from source text, except 2 Oct 2023, which is human-verified.

**Week 1: 2–8 October 2023**

| Day | Date | Count | Index | API URL |
|---|---|---|---|---|
| Mon | 2023-10-02 | 4,290 | 0.91 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-02&date_received_max=2023-10-02&size=0&no_aggs=true |
| Tue | 2023-10-03 | 4,776 | 1.01 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-03&date_received_max=2023-10-03&size=0&no_aggs=true |
| Wed | 2023-10-04 | 4,975 | 1.06 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-04&date_received_max=2023-10-04&size=0&no_aggs=true |
| Thu | 2023-10-05 | 4,894 | 1.04 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-05&date_received_max=2023-10-05&size=0&no_aggs=true |
| Fri | 2023-10-06 | 4,622 | 0.98 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-06&date_received_max=2023-10-06&size=0&no_aggs=true |
| Sat | 2023-10-07 | 2,652 | 0.56 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-07&date_received_max=2023-10-07&size=0&no_aggs=true |
| Sun | 2023-10-08 | 1,672 | 0.35 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2023-10-08&date_received_max=2023-10-08&size=0&no_aggs=true |

Week total 27,881; weekday average 4,711; 7-day average 3,983 (all calculated).

**Week 2: 4–10 March 2024**

| Day | Date | Count | Index | API URL |
|---|---|---|---|---|
| Mon | 2024-03-04 | 6,140 | 0.88 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-04&date_received_max=2024-03-04&size=0&no_aggs=true |
| Tue | 2024-03-05 | 7,386 | 1.06 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-05&date_received_max=2024-03-05&size=0&no_aggs=true |
| Wed | 2024-03-06 | 7,182 | 1.03 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-06&date_received_max=2024-03-06&size=0&no_aggs=true |
| Thu | 2024-03-07 | 7,477 | 1.07 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-07&date_received_max=2024-03-07&size=0&no_aggs=true |
| Fri | 2024-03-08 | 6,626 | 0.95 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-08&date_received_max=2024-03-08&size=0&no_aggs=true |
| Sat | 2024-03-09 | 4,018 | 0.58 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-09&date_received_max=2024-03-09&size=0&no_aggs=true&frm=0 |
| Sun | 2024-03-10 | 2,977 | 0.43 | https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/?date_received_min=2024-03-10&date_received_max=2024-03-10&size=0&no_aggs=true |

Week total 41,806; weekday average 6,962; 7-day average 5,972 (all calculated).

**Findings (calculated)**
- **Monday is the quietest weekday,** at 0.88–0.91 of the weekday average. Tuesday to Thursday are busiest, at 1.01–1.07.
- **Weekend share:** Saturday and Sunday account for 15.5% and 16.7% of the week.
- **Busiest day vs 7-day average:** 1.25× in both weeks.

**Caveats**
- Only two weeks were sampled, which is small. A full-year CSV export, counted by weekday, would be stronger.
- CFPB complaints are mostly written online submissions. Phone queues may peak on Monday instead (§8).
- The database has only a date, no time of day, so it can't give an hourly multiplier.

---

## 7. Monthly seasonality, 2023 and 2024

Source: CFPB trends API, monthly counts by date received.
https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/trends?lens=overview&trend_interval=month&date_received_min=2023-01-01&date_received_max=2024-12-31

The response ignored the date filters and returned the full history; only 2023–2024 are shown here. Status: verified from source text.

| Month | 2023 | 2024 |
|---|---|---|
| Jan | 93,933 | 143,365 |
| Feb | 86,539 | 157,614 |
| Mar | 110,635 | 177,815 |
| Apr | 97,084 | 191,120 |
| May | 106,211 | 211,961 |
| Jun | 104,425 | 204,168 |
| Jul | 106,773 | 232,654 |
| Aug | 119,711 | 263,816 |
| Sep | 112,887 | 264,821 |
| Oct | 117,420 | 295,878 |
| Nov | 113,365 | 287,077 |
| Dec | 123,066 | 303,981 |
| **Sum** | **1,292,049** | **2,734,270** |

**Checks and findings (calculated)**
- **2023** sums exactly to the 2023 database total. Busiest month (Dec) = 1.14× the monthly mean; quietest (Feb) = 0.80×. Most of that range reflects February being shorter and steady growth through the year.
- **2024** sums to 2,734,270, which is 2 more than the current total of 2,734,268, so the trends response was probably cached. The busiest month is 1.33× the mean, but the gap is mostly growth: volume roughly doubled from January to December. No seasonal factor can be separated out.
- **For the model:** growth matters more than seasonality. Add growth headroom (see §9) rather than a monthly seasonal factor.

---

## 8. Intraday and peak-hour evidence

| Source | What it shows | Numbers | Status |
|---|---|---|---|
| Call Centre Helper, "10 Things You Need to Know About Call Centres" (https://www.callcentrehelper.com/10-things-to-know-about-call-centres-51312.htm) | Monday is typically the busiest day, higher still if the centre is closed at weekends; Monday absenteeism is highest. More customers call between 10am and 12pm than at any other time. | 40% of an hour's calls arrive in its first 15 minutes, and 30% in each of the other two segments. Implied within-hour peak rate = 0.40 ÷ 0.25 = **1.6×**. | verified from source text (industry article, not peer-reviewed); 1.6× calculated |
| Taylor (2012), "Density Forecasting of Intraday Call Center Arrivals using Models Based on Exponential Smoothing", *Management Science* 58, 534–549 (https://users.ox.ac.uk/~mast0315/CallCenterStat&LogisticCountModels.pdf) | US bank call centre: weekdays 7am–9pm, 34 weeks, half-hourly data. Also a UK credit-card centre (Mon–Sat, 9am–8pm, 70 weeks) with a repeating weekly cycle. | US bank: 97 to 2,521 calls per half-hour, median 1,278. Busiest half-hour ÷ median = **≈1.97×**; this is a worst case over 34 weeks, not a typical daily peak. | verified from source text; ratio calculated |
| Brown et al. (2005), "Statistical Analysis of a Telephone Call Center: A Queueing-Science Perspective", *JASA* 100(469) (http://www.columbia.edu/~ww2040/4615S13/Brown2005.pdf) | Israeli bank call centre, Sun–Thu 7am–midnight, all of 1999. Regular calls show a two-peak daily pattern. | About 100,000–120,000 calls per month. The intraday profile is shown only in Figure 1, with no text values. | verified from source text (no peak ratio available) |

No published table of hourly volume shares for financial-services contact centres was found.

---

## 9. FIDReC growth figures (Singapore)

Source: FIDReC, "27 November 2025 – FIDReC received a record 4,355 claims this fiscal year" (page dated 26 Nov 2025). https://www.fidrec.com.sg/knowledgebase/article/KA-01328/en-us

| Figure | Value | Status |
|---|---|---|
| Total claims received | 4,355 (FY2024/25) vs 2,894 (FY2023/24), +50% | verified from source text |
| Claims accepted for handling | 2,646 (FY2024/25), +22% | verified from source text |
| Scam-related claims | 1,285 vs 829, +55%; 49% of handled claims | verified from source text |
| Claims against banks and finance companies | 1,831 vs 1,387 (+32%, calculated) | verified from source text |
| Compromised-credential cases as share of scam claims | 64% (prior year 44%) | verified from source text |
| Other sectors, FY2024/25 | General insurers 297; capital markets services licensees 94; licensed financial advisers and insurance brokers 84; payment service providers 17; life insurance 323 (prior 387) | verified from source text |
| Consumer and personal finance claims | 354 (2021/22) → 1,601 (2024/25), ≈4.5× | read from chart, by Youxiong; the chart has no text values, so it was not independently checked |

**The 64% figure in context.** The article says most scam cases involved compromised credentials, where consumers found unauthorised transactions on bank accounts, payment cards or digital wallets. Those cases were 64% of scam-related claims. Youxiong's description of it is accurate.

**How to use these figures**
- The +32% and +50% annual growth rates support growth headroom, for example testing at 1.3× today's peak (an assumption).
- They do **not** support an intraday spike multiplier. Annual growth and hourly bursts are different time scales.

---

## 10. Review of Youxiong's calculator, line by line

The calculator was based on https://www.hivedesk.com/blog/workforce-management/weekly-employee-shift-planning-template. That page was not reviewed.

| Line | Youxiong's value | Check | Verdict |
|---|---|---|---|
| Source volume | Barclays Bank UK PLC, H1 2026 | 94,535 opened, confirmed against the page (§4) | Correct. State that it covers BBUKPLC only, excludes CFSL and BBPLC, and comes from a half-year when volumes were down 40% year on year. |
| Tickets per year | ~189,000 | 94,535 × 2 = 189,070 | Correct |
| Average weekday | ~590 | 189,070 ÷ 590 ≈ 320 days. 260 weekdays would give ~727; 365 days would give ~518. | **Divisor not stated.** Choose one and state it. |
| Peak day (Monday) | ~710 | 590 × 1.2 = 708 | Arithmetic correct, but **the CFPB data shows Monday as the quietest weekday** (§6). Busiest day vs 7-day average is 1.25× in the CFPB data, but that day falls midweek. For a phone channel, Call Centre Helper does support Monday. |
| Busiest hour | ~80 | 710 ÷ 8 h × 1.5 ≈ 133. 80 only fits a ~13-hour day. | **No working shown.** State the operating hours. |
| Spike hour | ~240 (4/min) | 80 × 3 = 240; 240 ÷ 60 = 4 | Arithmetic correct. 3× has no source; 2.0× is supported by Taylor (2012). |
| Desk agents | ~49 | 591 × 0.5 ÷ 6 = 49.25 | Arithmetic correct, but this staffs for the **average** day. Peak day: 710 × 0.5 ÷ 6 ≈ 59. No allowance for absence or breaks. 30 min per complaint is an assumption. |
| Searches | ~295 | 49 × 6 = 294 | Correct; label it as per hour. 6 searches per agent per hour is an assumption. |
| FIDReC point 1 (spike) | +55% supports the 3× spike | Annual growth, not an intraday burst | **Doesn't support it.** Use §8 evidence. |
| FIDReC point 2 (growth) | 1.3× headroom from +32% | 1,387 → 1,831 = +32% | Correct and reasonable |
| FIDReC point 3 (product focus) | 64% unauthorised transactions | Matches the article wording (§9) | Correct |
| Conclusion | The four guesses need reasons | — | Agree |

---

## 11. Suggested multipliers

| Parameter | Suggested value | Evidence | Status |
|---|---|---|---|
| Annual volume (UK firm benchmark) | 189,070 | Barclays BBUKPLC H1 2026 × 2 | calculated from verified source text |
| Busiest day vs 7-day average | 1.25× | CFPB daily counts, two weeks (§6) | calculated from verified counts |
| Busiest day vs weekday average | 1.06–1.07× (Tue–Thu) | same | calculated |
| Weekend share of weekly volume | ~16% | same | calculated |
| Busiest hour vs average hour | 1.5× | Between the 10am–12pm industry peak and Taylor's ≈2× worst half-hour; no direct published figure | assumption, with supporting evidence |
| Worst-case peak vs median interval | 2.0× | Taylor (2012): 2,521 ÷ 1,278 | calculated from verified source text |
| First 15 minutes vs hour average | 1.6× | Call Centre Helper (40% in first 15 minutes) | calculated from verified source text |
| Growth headroom | 1.3× | FIDReC banks/finance claims +32%; FIDReC total +50%; CFPB 2024 ≈1.9× 2023 | assumption, with supporting evidence |
| Handling time per complaint | 30 min | None found. For context, 56% of BBUKPLC complaints close within 3 days. | assumption |
| Searches per agent per hour | 6 | None found | assumption |
| Monday uplift | Not supported for written complaints | CFPB: Monday is 0.88–0.91 of the weekday average. Phone channel: Call Centre Helper says Monday is busiest. | Depends on channel. State which channel the desk handles. |

---

## 12. References

All accessed 1 October 2026.

1. CFPB, *Consumer Response Annual Report, January 1 – December 31, 2023*. https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2023-03.pdf (landing page: https://www.consumerfinance.gov/data-research/research-reports/consumer-response-annual-report-2023/)
2. CFPB, *Consumer Response Annual Report, January 1 – December 31, 2024*. https://files.consumerfinance.gov/f/documents/cfpb_cr-annual-report_2025-05.pdf (landing page: https://www.consumerfinance.gov/data-research/research-reports/2024-consumer-response-annual-report/)
3. CFPB, *Consumer Response Annual Report 2025*. https://files.consumerfinance.gov/f/documents/cfpb_2025-cr-annual-report_2026-03.pdf
4. CFPB, *Consumer Complaint Database*. https://www.consumerfinance.gov/data-research/consumer-complaints/ (search interface: https://www.consumerfinance.gov/data-research/consumer-complaints/search; API queries listed in §§2.3, 3, 6, 7)
5. CFPB, *Consumer complaint form product and issue options, August 2023*. https://files.consumerfinance.gov/f/documents/cfpb_consumer_complaint_form_product_issue_options_August_2023_FINAL.pdf
6. Barclays, *UK complaints data, January to June 2026*. https://home.barclays/who-we-are/reporting/uk-complaints-data/january-to-june-2026/ (text supplied by a teammate; automated access blocked)
7. Barclays, *UK complaints data, July to December 2025*. https://home.barclays/who-we-are/reporting/uk-complaints-data/july-to-december-2025/ (could not access)
8. FCA, *Aggregate complaints data: 2025 H2*. https://www.fca.org.uk/data/complaints-data/aggregate-complaints-data-2025-h2
9. FCA, *Firm specific complaints data*. https://www.fca.org.uk/data/complaints-data/firm-level
10. FCA, *Key findings from the FCA's Financial Lives May 2024 survey*. https://www.fca.org.uk/publication/financial-lives/financial-lives-survey-2024-key-findings.pdf
11. The Intermediary, *Financial services complaints rise to 1.87 million in H2 2025*. https://theintermediary.co.uk/2026/04/financial-services-complaints-rise-to-1-87-million-in-h2-2025-fca/
12. Financial Ombudsman Service, *Half-yearly complaints data: H2 2025*. https://www.financial-ombudsman.org.uk/businesses/resolving-complaint/our-insight/half-yearly-complaints-data-h2-2025
13. Financial Ombudsman Service, *Financial Ombudsman Service receives over 305,000 complaints in 2024/25*. https://www.financial-ombudsman.org.uk/who-we-are/data-insight/news/financial-ombudsman-service-receives-305000-complaints-2024-25
14. FIDReC, *27 November 2025 – FIDReC received a record 4,355 claims this fiscal year*. https://www.fidrec.com.sg/knowledgebase/article/KA-01328/en-us
15. Call Centre Helper, *10 Things You Need to Know About Call Centres*. https://www.callcentrehelper.com/10-things-to-know-about-call-centres-51312.htm
16. Taylor, J.W. (2012). Density Forecasting of Intraday Call Center Arrivals using Models Based on Exponential Smoothing. *Management Science*, 58, 534–549. https://users.ox.ac.uk/~mast0315/CallCenterStat&LogisticCountModels.pdf
17. Brown, L., Gans, N., Mandelbaum, A., Sakov, A., Shen, H., Zeltyn, S., Zhao, L. (2005). Statistical Analysis of a Telephone Call Center: A Queueing-Science Perspective. *Journal of the American Statistical Association*, 100(469). http://www.columbia.edu/~ww2040/4615S13/Brown2005.pdf
18. HiveDesk, *Weekly employee shift planning template* (basis of Youxiong's calculator; not reviewed). https://www.hivedesk.com/blog/workforce-management/weekly-employee-shift-planning-template
