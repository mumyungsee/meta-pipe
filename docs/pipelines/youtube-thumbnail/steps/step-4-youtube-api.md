# Step 4: YouTube API 연동 & 업로드

> **작성일**: 2026-03-27
> **의존**: Step 3 (섬네일 생성)

---

## 1. 아키텍처

```
src/youtube/
├── auth.py        # OAuth 2.0 인증 + 토큰 자동 갱신
├── uploader.py    # thumbnails.set 업로드 + 쿼터 추적
├── metadata.py    # 영상 목록/메타데이터 조회
└── cli.py         # CLI 인터페이스
```

---

## 2. 초기 설정

### 2.1 Google Cloud Console에서 OAuth 클라이언트 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. YouTube Data API v3 활성화
3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 앱)
4. `client_secret.json` 다운로드 → `config/client_secret.json`에 저장

### 2.2 첫 인증

```bash
python -m src.youtube.cli list
# → 브라우저가 열리며 Google 로그인/권한 승인
# → 토큰이 config/.youtube-token.json에 자동 저장
```

---

## 3. 사용법

### 내 영상 목록 조회

```bash
python -m src.youtube.cli list --max 5
```

### 영상 정보 조회

```bash
python -m src.youtube.cli info --video-id VIDEO_ID
```

### 섬네일 업로드

```bash
python -m src.youtube.cli upload --video-id VIDEO_ID --thumbnail output/thumb.png
```

---

## 4. 쿼터 관리

| 항목 | 값 |
| --- | --- |
| thumbnails.set | 50 units/회 |
| 일일 한도 | 10,000 units |
| 일일 최대 업로드 | 200회 |

쿼터 사용량은 업로드마다 콘솔에 자동 표시됩니다.

---

## 5. 보안

| 파일 | .gitignore |
| --- | --- |
| `config/client_secret.json` | 포함 (커밋 금지) |
| `config/.youtube-token.json` | 포함 (커밋 금지) |

---

## 6. 완료 기준

- [ ] `list` 명령으로 내 영상 목록 조회 성공
- [ ] `upload` 명령으로 섬네일 업로드 성공
- [ ] 토큰 만료 시 자동 갱신
- [ ] 쿼터 사용량 표시
