# CIAP Analytics Platform

A platform-agnostic creator analytics engine built on top of the [ciap-proxy](https://ciap-proxy.onrender.com/api-docs) API. Pulls YouTube channel metrics, normalises them into a clean internal model, runs statistical analysis, and outputs a visual dashboard and structured reports.

Designed to expand to additional social platforms (TikTok, Instagram, X) without touching the analysis or visualisation layer.

---

## Table of contents

- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Authentication](#authentication)
  - [Path A — email signup](#path-a--email-signup)
  - [Path B — Google OAuth login](#path-b--google-oauth-login)
  - [Token management](#token-management)
- [Running the platform](#running-the-platform)
- [Outputs](#outputs)
- [Analytics engine](#analytics-engine)
- [Adding a new platform](#adding-a-new-platform)
- [Troubleshooting](#troubleshooting)

---

## Architecture

```
ciap-proxy API
      │
      ▼
Platform Adapter          platforms/youtube.py
(fetch + normalise)       Handles both raw /auth/socials/google/youtube/metrics
      │                   and enriched /creators/insights/* endpoints.
      │                   Merges and normalises into core models.
      ▼
Core Models               core/models.py
(platform-agnostic)       ChannelProfile, ContentItem, TimeSeriesPoint,
      │                   AudienceMetrics, PerformanceReport, FullAnalyticsSnapshot
      ▼
Analytics Engine          core/engine.py
(compute derived          Linear regression trend, momentum windows (7d/30d),
 metrics)                 composite content scoring, channel health score
      │
      ├──▶ Dashboard       visualizations/dashboard.py
      │    (matplotlib)    6-panel dark-theme PNG — to be replaced with JS/D3
      │
      └──▶ Reports         reports/generator.py
           (text + JSON)   Structured text report + machine-readable JSON
```

The adapter layer is the only code that knows about any specific API. Everything downstream — engine, visualisations, reports — is fully platform-agnostic and works identically regardless of what feeds it.

---

## Project structure

```
analytics_platform/
├── auth_client.py              CLI auth helper — login, signup, connect YouTube
├── main.py                     Main entry point and CLI
│
├── core/
│   ├── models.py               Platform-agnostic dataclasses
│   ├── engine.py               All statistical computation
│   └── base_adapter.py         Abstract adapter interface
│
├── platforms/
│   └── youtube.py              YouTube adapter (ciap-proxy)
│
├── visualizations/
│   └── dashboard.py            Matplotlib dashboard builder
│
└── reports/
    └── generator.py            Text and JSON report generator
```

---

## Requirements

Python 3.10 or later.

```bash
pip install requests matplotlib seaborn pandas numpy python-dateutil
```

No API key is required in your code. The ciap-proxy API uses Bearer tokens issued at login — see [Authentication](#authentication).

---

## Quick start

```bash
# Verify everything works — no API needed
python main.py --demo

# Authenticate (one-time setup)
python auth_client.py --login --email you@example.com --password yourpassword

# Connect your YouTube channel (opens browser)
python auth_client.py --connect-youtube

# Run against the live API
python main.py
```

---

## Authentication

The ciap-proxy API has two separate paths to authenticate. Both end up in the same place: a user record with a stored Google OAuth token. After either path, you have a single `accessToken` that you use for all subsequent requests — you never manage the Google token directly, the server holds it.

### Path A — email signup

Use this if you registered with an email and password. YouTube access is linked as a separate step.

**Step 1 — create your account (once)**

```bash
python auth_client.py --signup --email you@example.com --password yourpassword
```

**Step 2 — log in and save your token**

```bash
python auth_client.py --login --email you@example.com --password yourpassword
```

This writes your `accessToken` to `~/.ciap_token`. All subsequent commands load it automatically.

**Step 3 — connect your YouTube channel (once)**

```bash
python auth_client.py --connect-youtube
```

Opens your browser to a Google OAuth consent page. After you grant access, Google redirects back to the server, which stores your Google credentials server-side. Your `accessToken` is unchanged — no new token is issued.

### Path B — Google OAuth login

Use this if you want to log in with Google directly (combines app auth and YouTube access in one step).

```bash
python auth_client.py --google-login
```

Opens your browser to Google's consent page. After login, the server issues an `accessToken` in the callback response. Copy it and save it manually:

```bash
echo '{"access_token": "YOUR_TOKEN_HERE"}' > ~/.ciap_token
```

### Token management

| Command | What it does |
|---|---|
| `--whoami` | Verify token is valid, print your user profile |
| `--refresh` | Rotate the access token using the stored refresh token |
| `--print-token` | Print the raw stored token (useful for curl/Postman) |

Tokens are stored in `~/.ciap_token` as JSON:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

You can override the token for a single run without touching the file:

```bash
python main.py --token eyJhbGci...
```

---

## Running the platform

```bash
python main.py [OPTIONS]
```

| Flag | Default | Description |
|---|---|---|
| `--demo` | off | Run with synthetic data — no API or token required |
| `--url` | `https://ciap-proxy.onrender.com` | API base URL |
| `--token` | loaded from `~/.ciap_token` | Bearer token (override stored token) |
| `--days` | `30` | Analytics lookback window in days |
| `--max-content` | `10` | Number of videos to analyse |
| `--out-dir` | `.` | Directory for output files |
| `--no-chart` | off | Skip generating the dashboard PNG |
| `--json` | off | Also save a JSON report |

**Examples**

```bash
# Demo mode — great for development
python main.py --demo

# Live data, 60-day window, save everything to ./reports/
python main.py --days 60 --out-dir ./reports --json

# Last 7 days only, no chart
python main.py --days 7 --no-chart

# Use a specific token without overwriting the saved one
python main.py --token eyJhbGci...

# Point at a different environment
python main.py --url https://staging-api.example.com --token eyJ...
```

---

## Outputs

Three files are written on each run, timestamped to avoid overwrites.

**Dashboard PNG** — `dashboard_YYYYMMDD_HHMMSS.png`

A six-panel dark-theme image:

- Daily views time series with trend line and peak marker
- Subscriber delta (gained vs lost per day)
- Channel health radar across four dimensions
- Content composite score leaderboard (colour-coded by percentile)
- Views vs engagement rate scatter
- Daily watch hours

**Text report** — `report_YYYYMMDD_HHMMSS.txt`

Human-readable summary covering channel overview, window metrics, health scores, trend analysis, top performers, and underperformers.

**JSON report** — `report_YYYYMMDD_HHMMSS.json` (with `--json`)

Machine-readable version of the same data. Useful for feeding into downstream systems, building dashboards, or storing historical snapshots.

```json
{
  "generated_at": "2026-05-01T07:00:00",
  "channel": { ... },
  "kpi": { "subscribers": 48230, "watch_hours": 2363.1, ... },
  "health": { "overall": 72.4, "label": "Good", ... },
  "trend": { "direction": "up", "momentum_7d": 8.2, ... },
  "content": [ { "title": "...", "composite_score": 81.4, ... } ]
}
```

---

## Analytics engine

The engine (`core/engine.py`) computes all derived metrics from the normalised snapshot. It has no knowledge of any platform or API.

**Channel health score (0–100)**

A weighted composite across four dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| Growth | 30% | Net subscriber rate + 30-day momentum |
| Engagement | 25% | Engagement rate relative to platform benchmarks |
| Consistency | 25% | Inverse of view count coefficient of variation |
| Influence | 20% | Influence score from the API (passthrough) |

Labels: `Excellent` (≥80) · `Good` (≥60) · `Needs Attention` (≥40) · `At Risk` (<40)

**Content composite score (0–100)**

Per-video weighted index:

- 50% normalised view count (relative to the window's top video)
- 30% engagement rate (capped at 20% to reduce outlier distortion)
- 20% algorithmic signals from the API (engagement score + recommendation score)

Each video also receives a percentile rank among all videos in the snapshot.

**Trend analysis**

- Linear regression slope (views/day) over the full window
- Direction classification: `up` (slope > 2), `down` (slope < −2), `flat`
- 7-day and 30-day momentum: percentage change vs the equivalent prior window
- Volatility: standard deviation of daily views

---

## Adding a new platform

Create a new file in `platforms/` that inherits from `BasePlatformAdapter` and implements two methods:

```python
# platforms/tiktok.py

from core.base_adapter import BasePlatformAdapter
from core.models import FullAnalyticsSnapshot

class TikTokAdapter(BasePlatformAdapter):
    PLATFORM_NAME = "tiktok"

    def fetch_snapshot(self, days: int = 30, max_content: int = 10) -> FullAnalyticsSnapshot:
        # fetch from your TikTok API
        # normalise into FullAnalyticsSnapshot
        ...

    def health_check(self) -> bool:
        ...
```

Then in `main.py`, instantiate your adapter instead of `YouTubeAdapter`. The engine, visualisations, and reports require no changes — they operate entirely on the normalised `FullAnalyticsSnapshot`.

The core models are the contract between adapters and everything downstream. As long as your adapter produces a valid `FullAnalyticsSnapshot`, the rest of the platform works.

---

## Troubleshooting

**401 Unauthorized on login**

Run the diagnostic script to detect what field names the API expects:

```bash
python diagnose.py --email you@example.com --password yourpassword
```

Common causes: account doesn't exist yet (run `--signup` first), wrong password, or the API expects a different field name than `email`/`password`.

**404 on YouTube metrics**

Your account hasn't connected a YouTube channel yet. Run:

```bash
python auth_client.py --connect-youtube
```

**Token expired**

```bash
python auth_client.py --refresh
```

If refresh also fails, log in again with `--login`.

**Dashboard PNG is blank / missing panels**

Usually means the API returned empty time series or content data. Run with `--demo` to confirm the visualisation layer works, then check what the API is returning:

```bash
python auth_client.py --whoami
python main.py --no-chart  # see the text report first
```

**Render.com cold start**

The API is hosted on Render's free tier and may take 30–60 seconds to respond on the first request after a period of inactivity. If you get a connection timeout, wait a moment and retry.