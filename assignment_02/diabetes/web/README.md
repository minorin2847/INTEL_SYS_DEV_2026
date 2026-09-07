# Diabetes Screening — Web app (React + Vite)

A single-page client over the FastAPI service. It runs **no model in the browser** —
every estimate is a `POST /predict` call.

```
Browser (React)  ->  REST API  ->  preprocessing + random forest  ->  result  ->  Browser
```

The page has two views, switched from the header:

| View | What it does |
|---|---|
| **Screening** | one scrolling health questionnaire (rendered from `GET /questions`); on submit the result appears in place — a risk headline, an **interactive SHAP force plot**, the 5 most similar survey respondents, and a "what could change the estimate" panel with a live BMI slider. Your earlier screenings for this browser are in a panel at the bottom. |
| **Operator** | one decision: the referral cut-off. A slider with a plain-language "out of every 1,000 people screened…" readout, the recall-vs-flag-rate trade-off curve on held-out data, a "help me choose" helper, and a guarded **Save** (admin key). Recent server activity is in a collapsible. |

## Prerequisites

- Node 18+ (`node --version`)
- The API running: from `diabetes/`, `uvicorn api.main:app --port 8000`
  (and `python api/build_artifacts.py` once, so the Operator view has data)

## Run (development)

```bash
cd web
npm install
npm run dev          # http://localhost:5173
```

`npm run dev` proxies `/api/*` to `http://localhost:8000`. Point it elsewhere with

```bash
DIABETES_API_URL=http://192.168.1.20:8000 npm run dev
```

## Build (static site)

```bash
VITE_API_BASE=https://your-api-host npm run build   # -> web/dist/
npm run preview                                       # serve dist/ locally
```

`VITE_API_BASE` is baked in at build time; the built site calls that URL directly, so
the API must allow its origin (the API already sends `Access-Control-Allow-Origin: *`).

## Layout

```
web/
  index.html  vite.config.js  package.json
  src/
    App.jsx            view switch, session id, predict call
    api.js             fetch wrapper (BASE = /api in dev, VITE_API_BASE in prod)
    lib/format.js       %, band colours, phrasing helpers
    components/
      Header.jsx
      Questionnaire.jsx   form from /questions; yes/no rest at "No", no "not sure" checkbox
      ResultPanel.jsx     stitches the result cards
      RiskHeadline.jsx
      ForcePlot.jsx       hand-built interactive additive SHAP force plot (SVG)
      SimilarCases.jsx
      WhatYouCanChange.jsx  per-habit deltas + live BMI slider + counterfactual sentence
      HistoryPanel.jsx
      Dashboard.jsx       operator view (referral cut-off + trade-off)
      TradeoffCurve.jsx  Sparkline.jsx  Collapsible.jsx
  legacy_streamlit/     the earlier Streamlit client, kept for reference only
```

## Screenshots for the report

See `../Report_Deliverable.md` (IDs W1–W5) for exact captions.

1. Questionnaire with answers filled in.
2. Result, top — risk headline + SHAP force plot (hover a segment).
3. Result, scrolled — similar cases + what-if + counterfactual sentence.
4. Operator view — referral cut-off slider + 1,000-people readout + trade-off curve.
