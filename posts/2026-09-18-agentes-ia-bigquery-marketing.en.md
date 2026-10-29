---
title: BigQuery + AI: Building a Text-to-SQL Agent for Marketing
description: How to connect an LLM to Google Cloud BigQuery to create a secure, low-cost Text-to-SQL agent delivering verified campaign insights in seconds.
date: 2026-09-18
lang: en
tags: AI, BigQuery, Agents, Python, SQL, Marketing
---

Every week in growth teams and agencies, the exact same routine plays out: a client or marketing director drops into Slack asking: **"Which channel delivered the best ROAS last week, and how does Meta CPA compare against Google Ads?"**.

An analyst has to stop their current task, open the **Google BigQuery** console, locate the dataset, write a 30-line SQL query with aggregations and date filters, wait for execution, paste numbers into a spreadsheet, and write a summary. Fifteen minutes later, they post a reply that takes ten seconds to read.

Hooking up an LLM to answer natural language questions (Text-to-SQL) seems like the obvious fix. But doing it naively — the way most tutorials show — is an operational time bomb: an unconstrained bot generates unoptimized queries that scan 400 GB full tables, ballooning your Google Cloud invoice into hundreds of dollars while hallucinating missing columns.

> **Engineering Takeaways:**
> - **The naive Text-to-SQL trap:** Pointing a chatbot straight at your data warehouse without middleware. It hallucinates schemas, skips partition filters, and burns compute budget.
> - **The production architecture:** A **decoupled 4-layer pipeline** enforcing strict read-only IAM, a Python AST linter with *Dry Run* cost auditing before query execution, and deterministic aggregation in BigQuery.
> - **The outcome:** Team members query millions of ad performance rows inside Slack or Teams without touching SQL, running at less than $0.003 USD per query.

Here is how the architecture is designed to stay fast, secure, and cost-controlled in production.

## Why Static Dashboards Fall Short for Ad-Hoc Inquiries

BI dashboards in **Looker Studio, Tableau, or Power BI** are great for high-level health monitoring: pacing monthly budgets or tracking aggregate CTR trends.

The friction starts with **ad-hoc questions**:
- *"Which video creatives saw the highest completion rate during the last holiday flash sale?"*
- *"How did cost per acquisition (CPA) trend across Latam on payday weekends?"*
- *"What percentage of spend went toward top-of-funnel reach versus dynamic retargeting last quarter?"*

Building a dedicated card or custom filter for every one-off question clutters dashboards and drains data team bandwidth. An **AI Data Agent** bridges this gap.

## The 4-Layer Architecture: From Natural Language to BigQuery

To run an AI agent safely in an enterprise environment, you never give it raw database access. You implement a **governed 4-stage pipeline**:

![Architecture of an AI Marketing Agent on Google BigQuery](../assets/img/bigquery-agent-architecture.webp)

### 1. Business Interface Layer
Team members (media buyers, planners, or clients) submit inquiries in their standard channels: Slack, Microsoft Teams, or an internal web UI. No SQL knowledge required.

### 2. Semantic & Schema Context Layer (The LLM)
A technical reasoning model (like Gemini or Claude) handles translation. Instead of passing the entire database schema, the agent receives a curated **Schema Context**:
- Key table definitions (`campaigns_performance`, `conversions_attribution`).
- Canonical business definitions (e.g., *"ROAS is revenue divided by spend, never the average of the ratio column"*).
- Partitioning keys (typically event date `event_date`).

With this context, the model translates intent into clean GoogleSQL.

### 3. Guardrails & Cost Auditing Layer (Python)
This is the critical stage that demo tutorials skip:
- **Strict read-only enforcement:** A Python AST parser rejects any query containing mutating tokens (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `GRANT`).
- **Pre-execution cost auditing with Dry Run:** Before running the query, the system evaluates it with `dry_run = True` in the Google Cloud BigQuery client. BigQuery returns the exact byte scan estimate in milliseconds **for zero cost**. If the query attempts to scan more than 500 MB (because the user omitted date parameters), the agent blocks execution and requests a bounded timeframe.

### 4. Deterministic Execution & Synthesis Layer
BigQuery processes the query across partitioned rows in milliseconds. The resulting tabular records return to the agent, which drafts the executive narrative highlighting key findings and generating interactive visualizations.

## Live Interaction Flow

Here is how the agent behaves in an operational environment:

![Chat demo of a Marketing Data Agent connected to BigQuery](../assets/img/bigquery-agent-chat-demo.webp)

The pipeline executes seamlessly:
1. The user asks a conversational question regarding Cyber Monday performance.
2. The agent generates partitioned GoogleSQL.
3. BigQuery scans just **14.2 MB in 1.4 seconds**.
4. The response delivers verified figures (Meta ROAS 4.32x vs. Google ROAS 3.78x) with an actionable strategic summary.

## Benchmark: Naive Bot vs. Production Agent

The difference between pointing a raw LLM at a database and building a governed architecture with guardrails is night and day:

![Benchmark: Naive AI Bot vs Production Agent on BigQuery](../assets/img/bigquery-guardrails-benchmark.webp)

| Metric | Naive Bot (Basic Text-to-SQL) | Production Agent (Governed Architecture) |
| :--- | :--- | :--- |
| **GCP Query Cost** | **$1.50 to $3.00 USD** (400+ GB full table scans) | **< $0.003 USD** (enforces partitions and clusters) |
| **Response Latency** | 10 to 20 seconds (risk of Slack timeouts) | **1 to 2 seconds** (instant conversational reply) |
| **Data Security** | Vulnerable to hallucinated schema mutations | **100% Read-Only** (enforced by IAM and AST linter) |
| **Math Reliability** | ~70% (hallucinates unweighted averages) | **100% Deterministic** (computed by BigQuery engine) |

## Production Engineering Challenges

Delivering a robust agent requires solving real data plumbing details that cannot be fixed with prompt engineering alone:

1. **Multi-Channel Schema Normalization:** When Meta calls spend `spend`, Google Ads uses `cost`, and TikTok logs `stat_cost`, your BigQuery warehouse must expose unified views so the model never confuses dimensions.
2. **Partitioning & Clustering Strategy:** Partitioning by event day (`PARTITION BY DATE(date)`) and clustering by channel and campaign ensures queries process fractions of a gigabyte.
3. **In-Memory Query Caching:** If multiple stakeholders ask similar performance questions throughout the morning, the agent serves cached results without hitting the warehouse.
4. **Least-Privilege Cloud IAM:** The Google Cloud Service Account must hold strict read-only permissions on designated reporting datasets (`roles/bigquery.dataViewer`).

AI in data operations is not about giving a bot carte blanche; it is about building the architectural guardrails so language models deliver speed and clarity with zero financial or operational risk.

---

## Frequently Asked Questions

### How does the agent prevent runaway BigQuery costs?
By running queries through `dry_run = True` via the Google Cloud API before execution. This calculates the exact byte scan size for free. If estimated scan size exceeds predefined safety thresholds (e.g., 500 MB), execution halts automatically.

### Can the bot accidentally drop or modify tables?
No. Mutating statements are blocked at two independent checkpoints: first by a Python AST parser that rejects DDL/DML syntax, and second by GCP IAM service accounts limited strictly to read-only roles.

### What is the average response latency?
Between 1 and 3 seconds on properly partitioned and clustered BigQuery datasets.
