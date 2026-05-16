"""
Analytics Platform — Main Entry Point

Usage:
    python main.py --url https://api.yourplatform.com --token YOUR_TOKEN
    python main.py --demo           # runs with rich synthetic data (no API needed)

Architecture:
    API -> Adapter (normalize) -> Engine (compute) -> Visualizer + Reporter
"""
import argparse
import os
import sys
import random
import math
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from core.models import (
    ChannelProfile, ContentItem, TimeSeriesPoint,
    AudienceMetrics, GrowthWindow, PerformanceReport, FullAnalyticsSnapshot,
)
from core.engine import AnalyticsEngine
from visualizations.dashboard import build_dashboard
from reports.generator import ReportGenerator


# ─── Demo data generator ─────────────────────────────────────────────────────

def generate_demo_snapshot(days: int = 30) -> FullAnalyticsSnapshot:
    """Generates a realistic synthetic snapshot for demo/testing."""
    random.seed(42)
    base_date = datetime.utcnow() - timedelta(days=days)

    # Channel
    channel = ChannelProfile(
        platform="youtube",
        channel_id="UCdemo123456",
        channel_title="TechVision Pro",
        subscriber_count=48_230,
        total_view_count=2_340_000,
        video_count=142,
    )

    # Synthetic time series with realistic shape: growth curve + noise
    ts = []
    for i in range(days):
        d    = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        base = 800 + i * 12                               # organic growth
        wave = math.sin(i / 7 * math.pi) * 150           # weekly cycle
        noise = random.gauss(0, 80)
        views = max(0, int(base + wave + noise))

        # Spike on day 10 (viral video)
        if i == 10:
            views = int(views * 4.5)

        sub_g = max(0, int(random.gauss(18, 6) + views / 400))
        sub_l = max(0, int(random.gauss(4, 2)))
        watch = int(views * random.uniform(3.5, 5.5))

        ts.append(TimeSeriesPoint(
            date=d,
            views=views,
            subscribers_gained=sub_g,
            subscribers_lost=sub_l,
            estimated_minutes_watched=watch,
        ))

    total_views   = sum(p.views for p in ts)
    total_gained  = sum(p.subscribers_gained for p in ts)
    total_lost    = sum(p.subscribers_lost for p in ts)
    total_watch   = sum(p.estimated_minutes_watched for p in ts)

    audience = AudienceMetrics(
        views=total_views,
        estimated_minutes_watched=total_watch,
        average_view_duration_seconds=int(total_watch * 60 / max(total_views, 1)),
        subscribers_gained=total_gained,
        subscribers_lost=total_lost,
        influence_score=72.4,
    )

    # Content
    video_titles = [
        "I tried every AI coding tool for 30 days — honest review",
        "Python async/await: the guide nobody else explains properly",
        "How I went from 0 to 40K subscribers in 14 months",
        "Building a SaaS in 72 hours: full breakdown",
        "The dark side of creator burnout — my story",
        "10 VS Code extensions I actually use every day",
        "Mistral vs GPT-4o vs Claude 3.5 — benchmark battle",
        "Why most tutorial channels fail (and how to avoid it)",
        "Live coding a REST API from scratch in FastAPI",
        "My content calendar system for YouTube creators",
    ]

    content_items = []
    for rank, title in enumerate(video_titles, 1):
        base_v = int(80_000 / (rank ** 0.65))
        views  = int(base_v * random.uniform(0.8, 1.2))
        likes  = int(views * random.uniform(0.03, 0.07))
        coms   = int(views * random.uniform(0.003, 0.012))
        pub_d  = base_date + timedelta(days=random.randint(0, days - 1))
        content_items.append(ContentItem(
            platform="youtube",
            content_id=f"vid_{rank:03d}",
            title=title,
            view_count=views,
            like_count=likes,
            comment_count=coms,
            published_at=pub_d,
            engagement_score=round(random.uniform(0.55, 0.95), 2),
            growth_score=round(random.uniform(0.45, 0.90), 2),
            recommendation_score=round(random.uniform(0.50, 0.92), 2),
            performance_rank=rank,
        ))

    weekly_growth  = GrowthWindow(7,  total_gained // 4,  total_views // 4, total_watch // 4)
    monthly_growth = GrowthWindow(30, total_gained,        total_views,      total_watch)

    performance = PerformanceReport(
        window_days=days,
        weekly_growth=weekly_growth,
        monthly_growth=monthly_growth,
        engagement_rate=round(random.uniform(0.038, 0.058), 4),
        time_series=ts,
        top_content=content_items[:3],
        platform_breakdown=[{
            "platform": "youtube",
            "followerGrowth": total_gained,
            "views": total_views,
            "engagementRate": 0.045,
        }],
    )

    return FullAnalyticsSnapshot(
        channel=channel,
        audience=audience,
        content_items=content_items,
        performance=performance,
        raw_time_series=ts,
    )


# ─── Live API runner ──────────────────────────────────────────────────────────

def run_live(base_url: str, token: str, days: int, max_content: int) -> FullAnalyticsSnapshot:
    from platforms.youtube import YouTubeAdapter
    adapter = YouTubeAdapter(base_url=base_url, auth_token=token)
    return adapter.fetch_snapshot(days=days, max_content=max_content)


def load_saved_token() -> str:
    import json
    token_file = os.path.expanduser("~/.ciap_token")
    if os.path.exists(token_file):
        with open(token_file) as f:
            return json.load(f).get("access_token", "")
    return ""


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    DEFAULT_URL = "https://ciap-proxy.onrender.com"
    parser = argparse.ArgumentParser(description="Social Analytics Platform")
    parser.add_argument("--url",         default=DEFAULT_URL, help=f"API base URL (default: {DEFAULT_URL})")
    parser.add_argument("--token",       default=None,  help="Bearer token (auto-loaded from ~/.ciap_token if omitted)")
    parser.add_argument("--days",        default=30, type=int)
    parser.add_argument("--max-content", default=10, type=int)
    parser.add_argument("--demo",        action="store_true", help="Run with synthetic demo data (no API needed)")
    parser.add_argument("--out-dir",     default=".",   help="Output directory")
    parser.add_argument("--no-chart",    action="store_true", help="Skip dashboard image")
    parser.add_argument("--json",        action="store_true", help="Save JSON report")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    print("▶  Fetching analytics snapshot …")
    if args.demo:
        snapshot = generate_demo_snapshot(days=args.days)
        print(f"   Demo mode · {args.days}-day synthetic data generated")
    else:
        token = args.token or load_saved_token()
        if not token:
            print("   No token found. Authenticate first:")
            print("     python auth_client.py --login --email YOU@example.com --password PW")
            print("   Or use --demo to test with synthetic data.")
            sys.exit(1)
        print(f"   Connecting to {args.url} …")
        snapshot = run_live(args.url, token, args.days, args.max_content)

    print("▶  Running analytics engine …")
    engine  = AnalyticsEngine()
    summary = engine.analyze(snapshot)

    print("▶  Generating text report …")
    reporter = ReportGenerator()
    report   = reporter.text_report(snapshot, summary)
    print(report)

    ts_tag = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    text_path = os.path.join(args.out_dir, f"report_{ts_tag}.txt")
    reporter.save_text(snapshot, summary, text_path)
    print(f"\n   Report saved → {text_path}")

    if args.json:
        json_path = os.path.join(args.out_dir, f"report_{ts_tag}.json")
        reporter.save_json(snapshot, summary, json_path)
        print(f"   JSON saved  → {json_path}")

    if not args.no_chart:
        print("▶  Building dashboard …")
        chart_path = os.path.join(args.out_dir, f"dashboard_{ts_tag}.png")
        build_dashboard(snapshot, summary, output_path=chart_path, show=False)
        print(f"   Dashboard   → {chart_path}")

    print("\n✓  Done.")
    return snapshot, summary


if __name__ == "__main__":
    main()
