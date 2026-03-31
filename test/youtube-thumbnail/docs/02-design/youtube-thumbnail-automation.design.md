# Design: 유튜브 섬네일 자동화

> **Feature**: youtube-thumbnail-automation
> **Version**: 1.0
> **Created**: 2026-03-25
> **Updated**: 2026-03-27
> **Status**: Completed
> **PDCA Phase**: Design → Do 완료

---

## 1. 시스템 아키텍처

```
[사용자 입력]
  영상 제목 + 템플릿 ID
       │
       ▼
┌─────────────────┐
│  prompt_builder  │ ← config/prompts/prompt-patterns.json
│                  │ ← config/brand.json
└────────┬────────┘
         │ 완성 프롬프트
         ▼
┌─────────────────┐
│   api_client     │ → NanoBanana Pro (Google GenAI SDK)
│                  │ ← 완성 이미지 (텍스트 포함)
└────────┬────────┘
         │ PNG/JPEG
         ▼
┌─────────────────┐
│   validator      │ → quality_checker (규격)
│                  │ → policy_checker (정책)
└────────┬────────┘
         │ 통과
         ▼
┌─────────────────┐
│   youtube        │ → auth (OAuth 2.0)
│                  │ → uploader (thumbnails.set)
└────────┬────────┘
         │ 업로드 완료
         ▼
┌─────────────────┐
│   analytics      │ → performance_tracker (CTR, 노출수)
└─────────────────┘
```

---

## 2. 모듈 설계

### 2.1 src/generator/

| 파일 | 역할 |
|------|------|
| `api_client.py` | Google GenAI SDK 클라이언트. `generate_thumbnail(prompt, output_path, model, max_retries, initial_delay)`. exponential backoff 재시도 내장 (기본 3회) |
| `prompt_builder.py` | 패턴 로드 + `{{title}}` 치환. `build_prompt(pattern_id, title)` |
| `cli.py` | `--template`, `--title`, `--output`, `--list`, `--model` |

### 2.2 src/youtube/

| 파일 | 역할 |
|------|------|
| `auth.py` | OAuth 2.0 인증 + 토큰 캐시/자동 갱신 |
| `uploader.py` | `thumbnails.set` + `QuotaTracker` (50 units/회) |
| `metadata.py` | `list_videos()`, `get_video()` |
| `cli.py` | `upload`, `list`, `info` 서브커맨드 |

### 2.3 src/validator/

| 파일 | 역할 |
|------|------|
| `quality_checker.py` | 파일크기/해상도/포맷/비율 검증. `check_thumbnail(path)` → `CheckResult` |
| `policy_checker.py` | 금지키워드(차단) + 클릭베이트(경고) + 관련성(경고). `check_all()` → `PolicyResult` |
| `cli.py` | `--image`, `--title`, `--text` |

### 2.4 src/testing/

| 파일 | 역할 |
|------|------|
| `e2e_test.py` | 제목→생성→검증→업로드 E2E. `--output-dir` 옵션으로 출력 디렉토리 지정 가능 |
| `ab_test.py` | 다중 템플릿 변형 생성. `--output-dir` 옵션으로 출력 디렉토리 지정 가능 |

### 2.5 src/analytics/

| 파일 | 역할 |
|------|------|
| `performance_tracker.py` | YouTube Analytics API CTR/노출수 수집 + JSON 리포트 저장 |

---

## 3. 데이터 모델

### 3.1 브랜드 설정 (`config/brand.json`)

```
channel: { category, tone, visual_direction }
colors: { primary, secondary, dark } (각 name, hex, rgb)
fonts: { primary, secondary } (family, weight)
text_style: { max_words, font_size_range, color_combos }
layout: { canvas 1280x720, safe_zone, types: screen_demo/full_bg/character_text }
```

### 3.2 프롬프트 패턴 (`config/prompts/prompt-patterns.json`)

5개 패턴: tech-gradient, screen-glow, ai-neural, workspace-desk, futuristic-ui
- 각 패턴에 `{{title}}` 변수 → 한글 제목 삽입
- 브랜드 컬러 HEX 직접 명시

### 3.3 YouTube API 엔티티

- **Video**: id, title, tags, publishedAt, thumbnails
- **Thumbnail**: videoId, default/medium/high URL
- **Performance**: impressions, CTR, views, avgViewDuration (일별)

---

## 4. 보안

| 민감 파일 | 위치 | .gitignore | 환경변수 |
|-----------|------|------------|----------|
| Google API Key | `.env` | Yes | `GOOGLE_API_KEY` |
| OAuth Client Secret | `config/client_secret.json` | Yes | `YOUTUBE_CLIENT_SECRET` (경로 지정) |
| OAuth Token | `config/.youtube-token.json` | Yes | - |

---

## 5. 핵심 CLI 인터페이스

```bash
# 생성 (--model 옵션으로 모델 ID 변경 가능)
python -m src.generator.cli -t tech-gradient --title "AI 자동화" -o output/thumb.png
python -m src.generator.cli -t tech-gradient --title "AI 자동화" -o output/thumb.png --model gemini-2.0-flash

# 검증
python -m src.validator.cli -i output/thumb.png --title "AI 자동화" --text "AI 자동화"

# 업로드
python -m src.youtube.cli upload --video-id VIDEO_ID --thumbnail output/thumb.png

# E2E (--output-dir 옵션으로 출력 디렉토리 지정 가능)
python -m src.testing.e2e_test --title "AI 자동화" -t tech-gradient
python -m src.testing.e2e_test --title "AI 자동화" -t tech-gradient --output-dir results/

# A/B 변형 (--output-dir 옵션으로 출력 디렉토리 지정 가능)
python -m src.testing.ab_test --title "AI 자동화" --templates tech-gradient,screen-glow,ai-neural
python -m src.testing.ab_test --title "AI 자동화" --templates tech-gradient,screen-glow --output-dir results/ab/
```

---

## 6. v2.0 예정 기능

다음 기능들은 v1.0 범위 외이며 향후 구현 예정입니다.

| 기능 | 모듈 | 설명 |
|------|------|------|
| 브랜드 일관성 검증 | `src/validator/brand_checker.py` | 섬네일 색상/폰트를 `config/brand.json` 기준과 비교 검증 |
| 기술 규격 자동 보정 | `src/validator/quality_checker.py` 확장 | 2MB 초과 시 JPEG 품질 자동 하향, 해상도 미달 시 자동 리사이즈 |
| 검증 통과율 통계 리포트 | `src/validator/report.py` | 다중 섬네일 일괄 검증 후 통과율/실패 원인 통계 출력 |
