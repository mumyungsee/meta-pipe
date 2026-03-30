"""YouTube Analytics 성과 추적.

YouTube Analytics API로 섬네일 CTR, 노출수 등을 수집.
YouTube Studio > Analytics와 동일한 데이터.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

from googleapiclient.discovery import build


REPORT_DIR = Path(__file__).resolve().parent.parent.parent / "output" / "reports"


def build_analytics_client(credentials):
    """YouTube Analytics API 클라이언트 생성."""
    return build("youtubeAnalytics", "v2", credentials=credentials)


def get_thumbnail_performance(
    analytics,
    channel_id: str,
    video_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    """영상의 섬네일 성과 지표 조회.

    Args:
        analytics: YouTube Analytics API 클라이언트
        channel_id: 채널 ID
        video_id: 영상 ID
        start_date: 시작일 (YYYY-MM-DD, 기본 7일 전)
        end_date: 종료일 (YYYY-MM-DD, 기본 오늘)

    Returns:
        {impressions, ctr, views, avg_view_duration}
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    response = analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate=start_date,
        endDate=end_date,
        metrics="impressions,impressionClickThroughRate,views,averageViewDuration",
        dimensions="day",
        filters=f"video=={video_id}",
        sort="day",
    ).execute()

    rows = response.get("rows", [])
    if not rows:
        return {"video_id": video_id, "period": f"{start_date}~{end_date}", "data": []}

    daily = []
    for row in rows:
        daily.append({
            "date": row[0],
            "impressions": row[1],
            "ctr": round(row[2] * 100, 2),  # % 변환
            "views": row[3],
            "avg_duration_sec": row[4],
        })

    total_impressions = sum(d["impressions"] for d in daily)
    total_views = sum(d["views"] for d in daily)
    avg_ctr = round((total_views / total_impressions * 100) if total_impressions else 0, 2)

    return {
        "video_id": video_id,
        "period": f"{start_date}~{end_date}",
        "summary": {
            "total_impressions": total_impressions,
            "total_views": total_views,
            "avg_ctr": avg_ctr,
        },
        "daily": daily,
    }


def save_report(data: dict, filename: str | None = None) -> Path:
    """성과 리포트를 JSON으로 저장."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    if not filename:
        filename = f"perf_{data['video_id']}_{datetime.now().strftime('%Y%m%d')}.json"
    path = REPORT_DIR / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"리포트 저장: {path}")
    return path
