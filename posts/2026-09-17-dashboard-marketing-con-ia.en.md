---
title: How I generated a marketing dashboard with AI in 2 minutes
description: I built a tool that turns a campaign CSV into a client-ready dashboard with AI-written insights. Here is how it works and how you can replicate it.
date: 2026-09-17
lang: en
tags: AI, Marketing, Automation, Python
---

At an agency, the monthly report is always the same ritual: open the Meta export, the Google export, paste everything into Excel, build pivot tables, check that the numbers reconcile, make the charts, and write the analysis. Three hours later you have something the client looks at for five minutes.

I built a tool to kill that ritual: **mktdash**. You upload your campaign file and in seconds you get KPIs, charts, and an AI-written executive summary, all exportable as a single HTML file with your agency's branding.

## The real problem is not making charts

Making a chart is easy. The problem is everything that happens **before**: every platform exports columns with different names, in English or Spanish, and every client asks for different metrics. The expensive part of the report is translation: understanding which column is what, computing the right KPIs, and telling the story with those numbers.

That is where AI is perfect for half the job and dangerous for the other half.

## What it looks like

Here is the full flow, with real screenshots of the tool:

![Paste your Gemini API key (optional), choose the brand, and upload a CSV or Excel file — or use the demo data](../assets/img/mktdash-form.webp)

The result: eleven KPIs computed by the deterministic engine and, with an API key, an executive summary written by AI.

![Generated dashboard: spend, revenue, ROAS, conversions, CPA, CTR, CPC, CPM, and CVR over 90 days of demo data](../assets/img/mktdash-dashboard.webp)

Charts render in the browser and stay interactive: zoom, hover, and read every point.

![Interactive charts: spend vs revenue, ROAS trend, channel comparison, top campaigns, and conversion funnel](../assets/img/mktdash-charts.webp)

And everything exports as a self-contained HTML report with the client's branding, ready to email or print as a PDF.

![Exported HTML report with KPIs, executive summary, and all charts](../assets/img/mktdash-report.webp)

## The architecture: AI to understand, code to calculate

The common mistake is asking a model to "generate the dashboard". Language models write convincing text, but they are not reliable at math. A miscalculated ROAS in a client report is a serious problem.

So I split responsibilities:

- **Gemini does what it is good at**: it reads your column names plus five sample rows and infers the mapping (for example, that "Inversión" is spend and "Campaña" is the dimension). Then it reads the already-computed KPI table and writes the executive summary.
- **Python calculates everything**: the pandas engine computes spend, revenue, ROAS, conversions, CPA, CTR, CPC, CPM, and CVR. Charts come from Plotly. Zero invented numbers.

The rule is simple: **AI interprets and narrates; code calculates**. If the model fails or there is no API key, the system keeps working with name-based column detection and no summary.

## What I learned building it

1. **Column names are chaos.** The same field is called `spend`, `Cost`, `Inversión`, or `importe_gastado`. Good mapping removes 80% of adoption friction.
2. **People do not trust what they cannot edit.** Showing which column mapped to which field (and letting them fix it) is worth more than any promise of accuracy.
3. **Data arrives dirty.** Currency symbols, commas as decimals, mixed date formats. Validation is half the work.
4. **The executive summary is what sells.** The charts already existed inside the ads platform; translating them into decisions is what saves time.

## How to replicate it

The stack is short: Python, pandas, Plotly, and the Gemini API. The local version is about 400 lines plus the metrics engine; the web version adds FastAPI and Next.js.

If you want to build something like this for your agency or team, you need three things: a clean campaign export, a Gemini API key, and a decision about which KPIs matter to your client. The rest is plumbing.

If you find this useful, I publish the technical and business decisions behind what I build right here. And if you want me to bring this to your team, get in touch.
