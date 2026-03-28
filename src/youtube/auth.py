"""YouTube Data API v3 OAuth 2.0 인증."""

import os
import json
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/youtube",          # 섬네일 업로드
    "https://www.googleapis.com/auth/youtube.readonly",  # 영상 목록 조회
    "https://www.googleapis.com/auth/yt-analytics.readonly",  # Analytics 데이터 조회
]

TOKEN_PATH = Path(__file__).resolve().parent.parent.parent / "config" / ".youtube-token.json"
CLIENT_SECRET_PATH = Path(
    os.environ.get("YOUTUBE_CLIENT_SECRET", "config/client_secret.json")
)


def get_credentials() -> Credentials:
    """OAuth 2.0 자격증명 획득. 토큰 캐시 및 자동 갱신."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
    elif not creds or not creds.valid:
        if not CLIENT_SECRET_PATH.exists():
            raise FileNotFoundError(
                f"OAuth 클라이언트 시크릿 파일 없음: {CLIENT_SECRET_PATH}\n"
                "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하세요:\n"
                "https://console.cloud.google.com/apis/credentials"
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
        creds = flow.run_local_server(port=0)
        _save_token(creds)

    return creds


def build_youtube_client():
    """인증된 YouTube API 클라이언트 반환."""
    creds = get_credentials()
    return build("youtube", "v3", credentials=creds)


def _save_token(creds: Credentials):
    """토큰을 파일에 저장."""
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
