# LEAG FX — Knowledge Base Entry Schema

**Phase 2 / Step 2**

---

## Why a Schema First

Every knowledge base entry must look the same shape, so both humans and the Phase 9 query function can rely on consistent fields — no entry should be "special" or freeform.

## The Schema

Every entry is a `.yaml` file with these fields:

```yaml
id: string              # unique identifier, snake_case, matches filename
title: string            # human-readable name
category: string         # one of: fed_policy, boj_policy, us_indicator,
                          #         japan_indicator, market_structure
summary: string           # 1-3 sentence plain-language explanation
details: string            # fuller explanation, plain language, first-principles
why_it_matters_for_usdjpy: string   # explicit connection to the pair
related_entries: list       # ids of related entries (for future graph migration)
sources: list                # where this information/understanding came from
last_updated: string           # YYYY-MM-DD
```

## Example Entry

```yaml
id: fed_funds_rate
title: Federal Funds Rate
category: fed_policy
summary: >
  The interest rate the US Federal Reserve sets for banks lending to each
  other overnight. It's the primary tool the Fed uses to influence the
  broader US economy.
details: >
  When the Fed raises the federal funds rate, borrowing becomes more
  expensive across the economy, which tends to slow spending and cool
  inflation. When it lowers the rate, borrowing becomes cheaper, which
  tends to stimulate spending. The rate is set at FOMC meetings, held
  roughly eight times a year.
why_it_matters_for_usdjpy: >
  A higher US interest rate relative to Japan's typically makes USD-
  denominated assets more attractive to investors seeking yield, which
  tends to strengthen the Dollar against the Yen. This "interest rate
  differential" is one of the most consistently cited drivers of
  USD/JPY movement.
related_entries:
  - fomc
  - boj_policy_rate
  - interest_rate_differential
sources:
  - Federal Reserve official publications
last_updated: "2026-07-03"
```

## Folder Convention

Files live under `src/knowledge_base/entries/`, one file per topic, named by `id`:

```
src/knowledge_base/entries/
├── fed_funds_rate.yaml
├── fomc.yaml
├── boj_policy_rate.yaml
├── boj_tankan_survey.yaml
├── us_cpi.yaml
├── us_nfp.yaml
├── us_gdp.yaml
├── us_pce.yaml
├── japan_cpi.yaml
├── japan_gdp.yaml
├── tokyo_session.yaml
├── london_session.yaml
├── new_york_session.yaml
└── session_overlaps.yaml
```

---

*This schema is deliberately simple and flat. If Phase 9 later requires relationship-traversal that flat files can't support well, `related_entries` is exactly what migrates into a graph structure — nothing here is wasted by starting simple.*
