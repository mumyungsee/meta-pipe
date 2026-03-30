"""YouTube 섬네일 업로드."""

from pathlib import Path

from googleapiclient.http import MediaFileUpload


QUOTA_PER_UPLOAD = 50
DAILY_QUOTA_LIMIT = 10000


class QuotaTracker:
    """일일 API 쿼터 사용량 추적."""

    def __init__(self):
        self.used = 0

    @property
    def remaining(self) -> int:
        return DAILY_QUOTA_LIMIT - self.used

    @property
    def max_uploads_left(self) -> int:
        return self.remaining // QUOTA_PER_UPLOAD

    def consume(self, units: int):
        self.used += units
        if self.remaining < QUOTA_PER_UPLOAD:
            print(f"경고: 남은 쿼터 {self.remaining} units. 추가 업로드 불가.")

    def status(self) -> str:
        return (
            f"쿼터: {self.used}/{DAILY_QUOTA_LIMIT} 사용 "
            f"(남은 업로드: {self.max_uploads_left}회)"
        )


quota = QuotaTracker()


def upload_thumbnail(youtube, video_id: str, image_path: str | Path) -> dict:
    """섬네일을 YouTube 영상에 업로드.

    Args:
        youtube: 인증된 YouTube API 클라이언트
        video_id: 대상 영상 ID
        image_path: 섬네일 이미지 파일 경로

    Returns:
        YouTube API 응답 dict
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"이미지 파일 없음: {image_path}")

    size_mb = image_path.stat().st_size / (1024 * 1024)
    if size_mb > 2.0:
        raise ValueError(f"파일 크기 {size_mb:.2f}MB > 2MB YouTube 제한")

    if quota.remaining < QUOTA_PER_UPLOAD:
        raise RuntimeError(f"쿼터 부족. {quota.status()}")

    media = MediaFileUpload(str(image_path), mimetype="image/png", resumable=False)

    response = (
        youtube.thumbnails()
        .set(videoId=video_id, media_body=media)
        .execute()
    )

    quota.consume(QUOTA_PER_UPLOAD)
    print(f"업로드 완료: video_id={video_id}")
    print(f"  {quota.status()}")

    return response
