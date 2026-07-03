"""
Step 8: YouTube API 업로드
OAuth credentials.json이 준비되면 실행 가능.

사용법:
  1. Google Cloud Console에서 credentials.json 다운로드
  2. python upload.py --video-id VIDEO_ID --thumbnail ../step-5/thumbnail_with_text.png
"""

import argparse
import os
import json
from pathlib import Path

def get_authenticated_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    creds = None
    token_path = Path(__file__).parent / "token.json"
    creds_path = Path(__file__).parent.parent.parent / "credentials.json"

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def upload_thumbnail(video_id: str, thumbnail_path: str):
    from googleapiclient.http import MediaFileUpload

    youtube = get_authenticated_service()

    media = MediaFileUpload(thumbnail_path, mimetype="image/png", resumable=True)
    request = youtube.thumbnails().set(videoId=video_id, media_body=media)
    response = request.execute()

    print(f"업로드 완료: video_id={video_id}")
    print(f"응답: {json.dumps(response, indent=2, ensure_ascii=False)}")

    # 결과 저장
    result = {
        "video_id": video_id,
        "thumbnail_path": thumbnail_path,
        "status": "uploaded",
        "response": response
    }
    with open(Path(__file__).parent / "upload_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube 썸네일 업로드")
    parser.add_argument("--video-id", required=True, help="YouTube 영상 ID")
    parser.add_argument("--thumbnail", required=True, help="썸네일 이미지 경로")
    args = parser.parse_args()

    upload_thumbnail(args.video_id, args.thumbnail)
