"""YouTube 영상 메타데이터 조회."""


def list_videos(youtube, channel_id: str | None = None, max_results: int = 10) -> list[dict]:
    """채널의 최근 영상 목록 조회.

    Args:
        youtube: 인증된 YouTube API 클라이언트
        channel_id: 채널 ID (None이면 인증된 사용자의 채널)
        max_results: 최대 결과 수

    Returns:
        영상 정보 리스트 [{id, title, published_at, thumbnail_url}]
    """
    if channel_id:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            type="video",
            order="date",
            maxResults=max_results,
        )
    else:
        request = youtube.search().list(
            part="snippet",
            forMine=True,
            type="video",
            order="date",
            maxResults=max_results,
        )

    response = request.execute()

    return [
        {
            "id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "published_at": item["snippet"]["publishedAt"],
            "thumbnail_url": item["snippet"]["thumbnails"].get("high", {}).get("url"),
        }
        for item in response.get("items", [])
    ]


def get_video(youtube, video_id: str) -> dict:
    """단일 영상 메타데이터 조회."""
    response = (
        youtube.videos()
        .list(part="snippet,statistics", id=video_id)
        .execute()
    )

    items = response.get("items", [])
    if not items:
        raise ValueError(f"영상 없음: {video_id}")

    item = items[0]
    snippet = item["snippet"]
    return {
        "id": video_id,
        "title": snippet["title"],
        "description": snippet["description"],
        "tags": snippet.get("tags", []),
        "published_at": snippet["publishedAt"],
        "thumbnail_url": snippet["thumbnails"].get("high", {}).get("url"),
        "view_count": item["statistics"].get("viewCount"),
    }
