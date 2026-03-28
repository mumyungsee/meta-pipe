# Phase A: Discover - 유튜브 섬네일 자동화 도메인 조사

> **도메인**: 유튜브 섬네일 자동화 **조사 일자**: 2026-03-25 **상태**: Complete

---

## 1. 핵심 용어 표준

### 1.1 섬네일 기본 용어

| 용어 | 영문 | 설명 |
| --- | --- | --- |
| 섬네일 (Thumbnail) | Thumbnail | 동영상을 대표하는 미리보기 이미지. 1280x720px, 16:9 비율, 2MB 이하 |
| 맞춤 섬네일 (Custom Thumbnail) | Custom Thumbnail | 자동 추출 대신 직접 디자인한 섬네일. CTR 향상에 필수 |
| CTR | Click-Through Rate | 노출 대비 클릭 비율. 섬네일 성능의 핵심 지표 |
| 노출 (Impression) | Impression | 섬네일이 시청자에게 표시된 횟수 |
| A/B 테스트 | A/B Test | 2\~3개 섬네일 변형을 교대 노출하여 성과 비교 |
| 클릭베이트 | Clickbait | 영상 내용과 불일치하는 과장된 섬네일/제목. YouTube 정책 위반 |
| FOMO | Fear Of Missing Out | 놓칠까 두려움을 이용한 심리적 클릭 유도 기법 |
| 포컬 포인트 | Focal Point | 시선이 가장 먼저 닿는 섬네일의 핵심 요소 |

### 1.2 디자인 관련 용어

| 용어 | 설명 |
| --- | --- |
| Safe Zone | 섬네일 내 텍스트/요소가 잘리지 않는 안전 영역 |
| Text Overlay | 섬네일 위에 올리는 텍스트 (5단어 이하 권장) |
| Brand Template | 채널 일관성을 위한 디자인 템플릿 (색상 2-3개, 폰트 1-2개) |
| Variant | A/B 테스트에서 비교하는 섬네일 디자인 변형 |

**출처:**

- [YouTube Thumbnail: Definition and Best Practices](https://thesocialcat.com/glossary/youtube-thumbnail)
- [YouTube Glossary](https://www.oneupweb.com/blog/youtube-glossary/)
- [What Are Video Thumbnails & Why Do They Matter?](https://www.techsmith.com/blog/what-are-video-thumbnails/)

---

## 2. 워크플로우 Best Practice

### 2.1 표준 섬네일 제작 프로세스

```
1. 기획 (Pre-production)
   - 영상 촬영 전에 섬네일 콘셉트 기획
   - 제목과 섬네일을 동시에 구상 (Top 크리에이터 공통 패턴)

2. 소재 준비 (Asset Preparation)
   - 전용 촬영 이미지 (영상 프레임 캡처 X)
   - 배경 이미지, 아이콘, 브랜드 에셋 수집

3. 디자인 (Design)
   - 캔버스: 1280x720px (또는 1920x1080px에서 다운스케일)
   - 포컬 포인트 설정 (1초 이내 이해 가능해야 함)
   - 텍스트 오버레이: 5단어 이하, Bold Sans-serif
   - 색상: 2-3개 대비 색상, 주요 피사체 배경 대비 30%+ 차이
   - 얼굴 표정: 감정 표현이 CTR 최대 30% 향상

4. 브랜딩 (Branding)
   - 채널 컬러 일관성 유지 (HEX 코드 정의)
   - 1-2개 고정 폰트
   - 레이아웃 템플릿 재사용

5. 모바일 최적화 (Mobile-First)
   - YouTube 조회수의 70%가 모바일
   - 작은 화면에서도 텍스트 가독성 확인
   - 심플한 구성 필수

6. A/B 테스트 (Test & Compare)
   - YouTube 네이티브: 최대 3개 변형 업로드
   - 최소 1,000 노출 / 변형, 7-14일 운영
   - Watch Time 기준 최적화 (CTR만이 아님)

7. 반복 최적화 (Iterate)
   - 성과 데이터 기반 디자인 패턴 학습
   - 저성과 영상 섬네일 교체
```

### 2.2 핵심 디자인 원칙

| 원칙 | 설명 |
| --- | --- |
| 1초 규칙 | 1초 안에 영상 주제와 톤을 전달해야 함 |
| 감정 트리거 | 눈 맞춤(Eye Contact)과 극적 표정이 CTR 30% 향상 |
| 텍스트 최소화 | 5단어 이하, bold sans-serif (Montserrat Extra Bold 등) |
| 대비 극대화 | 배경-전경 간 색상/명도 대비 |
| 모바일 우선 | 70% 모바일 시청자 고려한 심플 구성 |

**출처:**

- [11 Youtube Thumbnail Design Best Practices for Creators in 2025](https://usevisuals.com/blog/youtube-thumbnail-design-best-practices)
- [YouTube Thumbnail Best Practices November 2025](https://ventress.app/blog/youtube-thumbnail-guide-november-2025/)
- [YouTube Thumbnail Design Tips - vidIQ](https://vidiq.com/blog/post/youtube-thumbnail-design-tips/)

---

## 3. 기술 스택

### 3.1 프로그래매틱 이미지 생성

| 도구 | 유형 | 설명 | 장단점 |
| --- | --- | --- | --- |
| **Pillow (PIL)** | Python Library | 이미지 리사이즈, 텍스트 오버레이, 합성 | 가볍고 유연, GPU 불필요 |
| **Sharp** | Node.js Library | 고성능 이미지 처리 (libvips 기반) | 매우 빠름, 서버 최적화 |
| **ImageMagick** | CLI Tool | 범용 이미지 처리. 배치 작업에 강점 | CLI 기반, 스크립트 연동 용이 |
| **Canvas API** | Browser/Node | HTML5 Canvas 기반 이미지 생성 | 웹 통합 용이 |

### 3.2 AI 이미지 생성 (채택 스택)

#### 채택: 나노바나나 Pro (NanoBanana Pro) 중심 전략

| 도구 | 유형 | 비용 | 용도 |
| --- | --- | --- | --- |
| **Google AntiGravity IDE** | Google IDE (VS Code 포크) | 무료 | 나노바나나 Pro 이미지 생성. 프롬프트 실험/초안 제작 |
| **NanoBanana Pro** (Gemini 2.5 Pro Image) | API | 유료 | 메인 이미지 생성 모델. 고품질 배경 생성 |
| **Stable Diffusion** | 로컬 모델 | 무료 (GPU 필요) | 프로덕션 단계에서 템플릿 기반 대량 생성 (추후 옵션) |

#### 이미지 생성 2단계 하이브리드 전략

```
[Stage 1: 초안 - 무료]
  AntiGravity IDE에서 나노바나나로 프롬프트 실험
    -> 배경 이미지만 생성 (텍스트 없이!)
    -> 프롬프트 검증 & 저장
    -> 괜찮으면 Stage 2로

[Stage 2: 자동화 - 무료]
  검증된 프롬프트를 API로 호출
    -> OpenRouter 무료 엔드포인트 또는 Google AI Studio
    -> Pillow로 텍스트/브랜딩 합성 (한글 정확)
    -> 완성된 섬네일 출력

[Stage 3: 프로덕션 - 추후]
  로컬 Stable Diffusion으로 이관
    -> 검증된 프롬프트 재사용
    -> 템플릿 기반 대량 자동화
    -> 동일 Pillow 합성 파이프라인
```

#### API 접근 경로

**OpenRouter 무료 엔드포인트 (추천):**

```python
import requests, base64
from PIL import Image
from io import BytesIO

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "google/gemini-2.5-flash-image-preview:free",
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
        "image_config": {"aspect_ratio": "16:9"}
    }
)

result = response.json()
image_url = result["choices"][0]["message"]["images"][0]["image_url"]["url"]
b64_data = image_url.split(",")[1]
image = Image.open(BytesIO(base64.b64decode(b64_data)))
```

**Google AI Studio 직접:**

```python
from google import genai
from google.genai import types

client = genai.Client()  # GOOGLE_API_KEY 환경변수

response = client.models.generate_content(
    model="gemini-2.5-flash-image",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(aspect_ratio="16:9")
    )
)

for part in response.parts:
    if part.inline_data:
        part.as_image().save("thumbnail_bg.png")
```

#### 프롬프트 전략: 배경만 생성 + Pillow 합성

```
[Bad] "유튜브 섬네일 만들어줘, 텍스트 '충격 반전!' 포함"
  -> 한글 텍스트 깨짐, 레이아웃 제어 불가

[Good] "Dramatic dark blue background with neon orange glow,
        cinematic lighting, empty right side for text placement,
        16:9 aspect ratio, 1280x720, no text, no letters"
  -> 깔끔한 배경 이미지만 생성
```

텍스트/브랜딩은 Pillow로 정확하게 합성:

```python
from PIL import Image, ImageDraw, ImageFont

bg = Image.open("thumbnail_bg.png").resize((1280, 720))
overlay = Image.new("RGBA", bg.size, (0, 0, 0, 100))  # 반투명 오버레이
bg = Image.alpha_composite(bg.convert("RGBA"), overlay)

draw = ImageDraw.Draw(bg)
font = ImageFont.truetype("NotoSansKR-Black.ttf", 80)
draw.text((640, 360), "충격 반전!", font=font, fill="#FFD700",
          anchor="mm", stroke_width=4, stroke_fill="#000")

bg.convert("RGB").save("thumbnail_final.jpg", quality=90)
```

#### 참고: 기타 AI 이미지 생성 도구

| 도구 | 유형 | 비고 |
| --- | --- | --- |
| DALL-E / GPT-4o | 유료 API | 텍스트 렌더링 정확하나 유료 |
| Midjourney | 유료 SaaS | 고품질 아트 스타일 |
| Canva Magic Media | Freemium SaaS | 비개발자용 간편 도구 |

### 3.3 YouTube API & 자동화

| 도구 | 유형 | 설명 |
| --- | --- | --- |
| **YouTube Data API v3** | API | 영상 메타데이터 조회, 섬네일 업로드 (`thumbnails.set`, 50 units/call) |
| **YouTube Analytics API** | API | CTR, 노출수, Watch Time 등 성과 데이터 수집 |

### 3.4 A/B 테스트 도구

| 도구 | 유형 | 설명 |
| --- | --- | --- |
| **YouTube Test & Compare** | Native | 최대 3개 변형 네이티브 A/B 테스트 (무료) |
| **ThumbnailTest** | SaaS | 외부 A/B 테스트, 상세 분석 |
| **TubeBuddy** | Extension | 섬네일 로테이션, 키워드, 성과 분석 |

### 3.5 권장 자동화 파이프라인 스택

```
[입력] 영상 제목/키워드/스크립트

[Stage 1: 프롬프트 검증]
  AntiGravity IDE + 나노바나나
    -> 배경 이미지 프롬프트 실험 (무료, 수동)
    -> 검증된 프롬프트 저장

[Stage 2: 자동화 파이프라인]
  나노바나나 API (OpenRouter 무료 또는 Google AI Studio)
    -> 배경 이미지 생성 (텍스트 없이)
    -> Pillow 합성 (텍스트 오버레이 + 브랜딩 + 인물 사진)
    -> 1280x720, <2MB JPEG 출력
    -> YouTube Data API v3 thumbnails.set 업로드

[Stage 3: 성과 분석]
  YouTube Analytics API
    -> videoThumbnailImpressions, CTR 수집
    -> A/B 테스트 (YouTube Test & Compare)
    -> 성과 기반 프롬프트/템플릿 개선

[Stage 4: 프로덕션 확장 (추후)]
  로컬 Stable Diffusion
    -> 검증된 프롬프트로 대량 생성
    -> 동일 Pillow 합성 파이프라인 재사용
```

**출처:**

- [thumbnail-generator GitHub Topics](https://github.com/topics/thumbnail-generator)
- [YouTube Thumbnail Generator with AI](https://github.com/jordicor/youtube_thumbnail_generator_with_AIs)
- [10 Best AI YouTube Thumbnail Generators In 2026](https://juma.ai/blog/ai-youtube-thumbnail-generators)
- [8 best AI tools for YouTube automation in 2026](https://shotstack.io/learn/best-ai-tools-for-youtube-automation/)
- [How to Generate YouTube Thumbnails with Python](https://jacobnarayan.com/blogs/how-to-generate-youtube-thumbnails-easily-with-python)
- [Google AntiGravity + NanoBanana Pro](https://cloud.google.com/blog/topics/developers-practitioners/agent-factory-recap-antigravity-and-nano-banana-pro-with-remik)
- [OpenRouter NanoBanana Free](https://openrouter.ai/google/gemini-2.5-flash-image-preview:free)
- [Gemini API Image Generation](https://ai.google.dev/gemini-api/docs/image-generation)
- [Free image generation with OpenRouter and Gemini Nano-banana](https://generativeai.pub/free-image-generation-with-openrouter-and-gemini-nano-banana-14837c69a7a7)

---

## 4. 데이터 모델

> YouTube Data API v3, YouTube Analytics API 공식 스키마 + thumbnail-maker 오픈소스 프로젝트 구조를 기반으로 보강한 모델입니다.

### 4.1 YouTube API 공식 스키마 매핑

#### Thumbnails Resource (YouTube Data API v3)

```json
// GET youtube/v3/videos?part=snippet → snippet.thumbnails
{
  "default":  { "url": "string", "width": 120, "height": 90 },
  "medium":   { "url": "string", "width": 320, "height": 180 },
  "high":     { "url": "string", "width": 480, "height": 360 },
  "standard": { "url": "string", "width": 640, "height": 480 },
  "maxres":   { "url": "string", "width": 1280, "height": 720 }
}
```

#### thumbnails.set (업로드 API)

```
POST https://www.googleapis.com/upload/youtube/v3/thumbnails/set
  ?videoId={VIDEO_ID}

Request Body: image binary (JPEG/PNG, max 2MB)
Quota Cost: 50 units/call (일일 한도 10,000 중)

Response:
{
  "kind": "youtube#thumbnailSetResponse",
  "etag": "string",
  "items": [ thumbnails_resource ]
}
```

#### Video Resource 핵심 필드

```json
{
  "snippet": {
    "title": "string",
    "description": "string",
    "tags": ["string"],
    "categoryId": "string",
    "thumbnails": { /* 위 Thumbnails Resource */ }
  },
  "contentDetails": {
    "duration": "string (ISO 8601, e.g. PT15M33S)",
    "hasCustomThumbnail": "boolean"  // 맞춤 섬네일 여부
  },
  "statistics": {
    "viewCount": "unsigned long",
    "likeCount": "unsigned long",
    "commentCount": "unsigned long"
  }
}
```

#### YouTube Analytics API 섬네일 관련 메트릭

| 메트릭명 | 타입 | 설명 |
| --- | --- | --- |
| `videoThumbnailImpressions` | numeric | 섬네일 노출수 (1초 이상 표시 + 50% 이상 가시) |
| `videoThumbnailImpressionsClickRate` | percentage | 섬네일 CTR (clicks / impressions) |
| `views` | numeric | 조회수 |
| `engagedViews` | numeric | 초기 몇 초 이후까지 시청한 조회수 |
| `estimatedMinutesWatched` | numeric | 총 시청 시간 (분) |
| `averageViewDuration` | numeric | 평균 시청 시간 (초) |
| `averageViewPercentage` | percentage | 평균 시청 비율 (%) |

### 4.2 자동화 파이프라인 데이터 모델

YouTube API 스키마 + 자동화 도구 구조를 결합한 통합 모델:

```
Channel (채널 브랜딩 설정)
  - channel_id: string          # YouTube channel ID (PK)
  - name: string
  - brand_colors: string[]      # HEX codes (e.g. ["#FF0000", "#FFFFFF"])
  - brand_fonts: string[]       # Google Fonts 이름 (e.g. ["Montserrat"])
  - default_template_id: FK -> Template
  - youtube_auth: JSON          # OAuth 2.0 credentials (encrypted)
  - api_quota_used_today: int   # 일일 쿼터 사용량 추적 (max 10,000)

Video (영상 메타데이터 - YouTube API 동기화)
  - video_id: string            # YouTube video ID (PK)
  - channel_id: FK -> Channel
  - title: string
  - description: string
  - tags: string[]
  - category_id: string         # YouTube 카테고리 ID
  - duration: string            # ISO 8601 (e.g. "PT15M33S")
  - has_custom_thumbnail: bool  # contentDetails.hasCustomThumbnail
  - upload_date: datetime
  - synced_at: datetime         # 마지막 API 동기화 시점

Template (레이아웃 템플릿 - thumbnail-maker 패턴)
  - template_id: string (PK)
  - name: string
  - channel_id: FK -> Channel
  - layers: JSON                # 레이어 구성 (3-layer 구조)
    [
      { "type": "background", "source": "unsplash|upload|ai", "config": {} },
      { "type": "overlay", "opacity": 0.4, "color": "#000000" },
      { "type": "content", "elements": [
          { "type": "text", "position": {x,y}, "font": "...", "size": 72, "color": "#FFF", "max_words": 5 },
          { "type": "face", "position": {x,y}, "size": {w,h}, "border": true },
          { "type": "logo", "position": {x,y}, "size": {w,h} }
        ]
      }
    ]
  - canvas: { width: 1280, height: 720 }
  - safe_zone: { top: 40, right: 40, bottom: 80, left: 40 }  # 하단 타임스탬프 고려
  - created_at: datetime
  - updated_at: datetime

Thumbnail (생성된 섬네일 인스턴스)
  - thumbnail_id: string (PK)
  - video_id: FK -> Video
  - template_id: FK -> Template
  - variant_label: string       # "A" | "B" | "C"
  - file_path: string           # 로컬 경로 (e.g. "output/{videoId}_{variant}.jpg")
  - file_url: string            # CDN/Storage URL
  - file_size: int              # bytes (max 2,097,152 = 2MB)
  - mime_type: string           # "image/jpeg" | "image/png"
  - resolution: { width: 1280, height: 720 }
  - text_overlay: string        # 렌더링된 텍스트 내용
  - background_source: JSON     # { type: "unsplash|upload|ai", url: "...", prompt?: "..." }
  - face_image_url: string?     # 인물 이미지 (optional)
  - emotion: string?            # "surprised" | "excited" | "curious" | "shocked"
  - generated_by: enum          # "manual" | "ai" | "template" | "hybrid"
  - ai_prompt: string?          # AI 생성 시 사용된 프롬프트
  - youtube_upload_status: enum # "pending" | "uploaded" | "failed"
  - youtube_etag: string?       # thumbnails.set 응답의 etag
  - youtube_urls: JSON?         # API 반환 5단계 URL (default~maxres)
  - created_at: datetime
  - uploaded_at: datetime?

ABTest (A/B 테스트 관리)
  - test_id: string (PK)
  - video_id: FK -> Video
  - variants: FK[] -> Thumbnail # 최대 3개 (YouTube 제한)
  - start_date: datetime
  - end_date: datetime?
  - duration_days: int          # 최소 7일 권장
  - status: enum                # "running" | "completed" | "cancelled"
  - winner_thumbnail_id: FK -> Thumbnail?
  - winner_criteria: enum       # "ctr" | "watch_time" | "engaged_views"
  - min_impressions_per_variant: int  # 기본값 1,000

Performance (성과 데이터 - YouTube Analytics API 동기화)
  - performance_id: string (PK)
  - thumbnail_id: FK -> Thumbnail
  - date: date                  # 일별 집계
  - impressions: int            # videoThumbnailImpressions
  - clicks: int                 # 계산: impressions * ctr
  - ctr: float                  # videoThumbnailImpressionsClickRate
  - views: int                  # views 메트릭
  - engaged_views: int          # engagedViews 메트릭
  - estimated_minutes_watched: float  # estimatedMinutesWatched
  - avg_view_duration_sec: float      # averageViewDuration (초)
  - avg_view_percentage: float        # averageViewPercentage (%)
  - synced_at: datetime         # Analytics API 동기화 시점
```

### 4.3 엔티티 관계

```
Channel 1 ──── * Video
Channel 1 ──── * Template
Video   1 ──── * Thumbnail
Template 1 ──── * Thumbnail
Video   1 ──── * ABTest
ABTest  1 ──── * Thumbnail (variants, max 3)
Thumbnail 1 ──── * Performance (daily)
```

### 4.4 thumbnail-maker 참조: 3-Layer 합성 구조

```
Layer 1: Background (배경)
  - Unsplash API에서 키워드 기반 자동 가져오기
  - 또는 로컬 이미지 업로드
  - 또는 AI 생성 (DALL-E / Stable Diffusion)

Layer 2: Overlay (오버레이)
  - 반투명 색상 레이어 (텍스트 가독성 향상)
  - opacity: 0.3~0.5 (어두운 배경) 또는 그라데이션

Layer 3: Content (콘텐츠)
  - Text: Bold Sans-serif, 5단어 이하, high contrast
  - Face: 인물 사진 (감정 표현, 배경 제거)
  - Logo: 채널 로고 (선택적)
  - Icon/Emoji: 보조 시각 요소 (선택적)
```

**출처:**

- [Thumbnails Resource - YouTube Data API](https://developers.google.com/youtube/v3/docs/thumbnails)
- [thumbnails.set - YouTube Data API](https://developers.google.com/youtube/v3/docs/thumbnails/set)
- [Videos Resource - YouTube Data API](https://developers.google.com/youtube/v3/docs/videos)
- [Metrics - YouTube Analytics API](https://developers.google.com/youtube/analytics/metrics)
- [thumbnail-maker - GitHub](https://github.com/nailtonvital/thumbnail-maker)
- [Automate YouTube Thumbnails](https://primetime.media/blog-posts-advanced/advanced-automation-and-data-driven-thumbnail-systems-for-scaling-youtube-metada-advanced)

---

## 5. 리스크 & 주의사항

### 5.1 YouTube 정책 위반 리스크

| 리스크 | 심각도 | 설명 | 대응 |
| --- | --- | --- | --- |
| **클릭베이트 정책 위반** | HIGH | 제목/섬네일이 영상 내용과 불일치 시 삭제 및 경고 | 영상 내용과 섬네일 일치 검증 로직 필수 |
| **성적 암시 섬네일** | HIGH | 성적 자극 목적의 이미지는 즉시 제거 | AI 생성 이미지 콘텐츠 필터링 |
| **3 Strike 규칙** | HIGH | 90일 내 3회 위반 시 채널 종료 | 자동화 시 정책 준수 검증 레이어 필수 |
| **저작권 침해** | MEDIUM | 타인 이미지/얼굴 무단 사용 | 라이선스 확인, 자체 에셋 사용 권장 |

### 5.2 기술적 리스크

| 리스크 | 심각도 | 설명 | 대응 |
| --- | --- | --- | --- |
| **API 할당량 초과** | MEDIUM | YouTube Data API 일일 쿼터 제한 (10,000 units) | 쿼터 모니터링, 배치 처리 |
| **AI 생성 품질 불안정** | MEDIUM | AI 이미지가 항상 고품질은 아님 | 품질 검증 단계 + 수동 검토 옵션 |
| **파일 크기 초과** | LOW | 2MB 제한 초과 | 자동 압축/리사이즈 파이프라인 |
| **폰트 라이선스** | LOW | 상용 폰트 무단 사용 | 오픈소스 폰트 사용 (Google Fonts) |

### 5.3 운영 리스크

| 리스크 | 심각도 | 설명 | 대응 |
| --- | --- | --- | --- |
| **브랜드 일관성 훼손** | MEDIUM | 자동화로 인한 채널 정체성 약화 | 브랜드 템플릿 강제 적용 |
| **A/B 테스트 오남용** | LOW | 빈번한 변경이 알고리즘에 부정적 영향 가능 | 테스트 주기 최소 7일 유지 |
| **과도한 자동화** | MEDIUM | 인간 창의성 배제 시 차별화 실패 | approval_required로 핵심 결정에 인간 검토 |

**출처:**

- [YouTube Thumbnails Policy](https://support.google.com/youtube/answer/9229980?hl=en)
- [Strengthening enforcement against egregious clickbait](https://blog.google/intl/en-in/products/platforms/strengthening-enforcement-against-egregious-clickbait-on-youtube/)
- [YouTube Spam, deceptive practices & scams policies](https://support.google.com/youtube/answer/2801973?hl=en)

---

## 조사 요약

| 카테고리 | 품질 | 주요 발견 | 신뢰도 |
| --- | --- | --- | --- |
| 핵심 용어 | 양호 | CTR, Custom Thumbnail, A/B Test 등 핵심 용어 정의 완료 | 높음 |
| 워크플로우 | 우수 | 7단계 표준 프로세스 (기획-&gt;디자인-&gt;브랜딩-&gt;모바일 최적화-&gt;A/B 테스트-&gt;반복) | 높음 |
| 기술 스택 | 양호 | Pillow/Sharp + AI(DALL-E/SD) + YouTube API 조합. 상용/오픈소스 비교 완료 | 높음 |
| 데이터 모델 | 우수 | YouTube API 공식 스키마 + Analytics 메트릭 + thumbnail-maker 3-Layer 구조 기반. 6개 엔티티 | 높음 |
| 리스크 | 우수 | YouTube 클릭베이트 정책 강화(2025\~), 3 Strike 규칙, API 쿼터 제한 | 높음 |
