# Step 2: 프롬프트 엔지니어링 & 검증

> **모델**: NanoBanana Pro (Gemini 2.5 Pro Image)
> **작성일**: 2026-03-27
> **의존**: Step 1 (브랜드 가이드)

---

## 1. 프롬프트 설계 원칙

| 원칙 | 설명 |
| --- | --- |
| **텍스트 없는 배경** | AI는 배경만 생성. 한글 텍스트는 Pillow로 합성 |
| **Safety Suffix** | 모든 프롬프트 끝에 `no text, no letters, no words, no watermarks, safe for all audiences` |
| **브랜드 컬러 명시** | HEX 코드를 프롬프트에 직접 포함하여 일관성 확보 |
| **텍스트 공간 확보** | `empty space for text overlay` 또는 `clean empty space` 지시 |
| **16:9 비율 명시** | `16:9 aspect ratio, high resolution` 항상 포함 |

---

## 2. 프롬프트 패턴 (5개)

### 2.1 테크 그라디언트 (`tech-gradient`)

- **레이아웃**: full_bg_center_text
- **용도**: 일반 AI 팁, 도구 소개, 리스트형 콘텐츠
- **텍스트 위치**: 중앙

```
Abstract technology gradient background, deep navy blue (#0D1B2A) to
electric blue (#2D7FF9) smooth gradient, subtle glowing particles and
light rays, clean and modern, bright energetic mood, empty center area
for overlay, 16:9 aspect ratio, high resolution, no text, no letters,
no words, no watermarks, safe for all audiences
```

### 2.2 스크린 글로우 (`screen-glow`)

- **레이아웃**: screen_demo
- **용도**: AI 도구 시연, 화면 튜토리얼, 소프트웨어 리뷰
- **텍스트 위치**: 우측 40%

```
Photorealistic glowing laptop screen on left side of frame, electric
blue (#2D7FF9) light emanating from screen, dark navy (#0D1B2A)
background, right 40% of image is clean dark space for text overlay,
bright tech atmosphere, soft bokeh lights, 16:9 aspect ratio, high
resolution, no text, no letters, no words, no watermarks, safe for
all audiences
```

### 2.3 AI 뉴럴 네트워크 (`ai-neural`)

- **레이아웃**: full_bg_center_text
- **용도**: AI 개념 설명, GPT/LLM 관련, AI 뉴스
- **텍스트 위치**: 중앙

```
Abstract neural network visualization, glowing blue (#2D7FF9) nodes
and connections on dark navy (#0D1B2A) background, flowing data streams
with yellow (#FFD600) accent highlights, futuristic and clean, empty
space in center for text overlay, bright energetic atmosphere, 16:9
aspect ratio, high resolution, no text, no letters, no words, no
watermarks, safe for all audiences
```

### 2.4 워크스페이스 데스크 (`workspace-desk`)

- **레이아웃**: screen_demo
- **용도**: 생산성 도구, 워크플로우 가이드, 세팅/설정 영상
- **텍스트 위치**: 우측 40%

```
Clean modern tech workspace from above angle, monitor and keyboard on
left side, blue (#2D7FF9) LED ambient lighting, dark desk surface,
right 40% of frame is clean empty space, minimal and organized, bright
professional atmosphere, 16:9 aspect ratio, high resolution, no text,
no letters, no words, no watermarks, safe for all audiences
```

### 2.5 미래형 UI 대시보드 (`futuristic-ui`)

- **레이아웃**: full_bg_center_text
- **용도**: 시리즈 시작, 특별 영상, AI 미래 전망
- **텍스트 위치**: 중앙

```
Futuristic holographic UI dashboard elements floating in space, electric
blue (#2D7FF9) and vivid yellow (#FFD600) glowing interface panels, dark
navy (#0D1B2A) deep background, large empty center area for text,
cinematic lighting, high contrast, bright and energetic sci-fi mood,
16:9 aspect ratio, high resolution, no text, no letters, no words,
no watermarks, safe for all audiences
```

---

## 3. 레이아웃별 매핑

| 레이아웃 | 프롬프트 패턴 | 텍스트 영역 |
| --- | --- | --- |
| `screen_demo` | screen-glow, workspace-desk | 우측 40% (x:780, w:480) |
| `full_bg_center_text` | tech-gradient, ai-neural, futuristic-ui | 중앙 (x:200, w:880) |

---

## 4. 사용 플랫폼

| 플랫폼 | 비용 | 용도 |
| --- | --- | --- |
| **AntiGravity IDE** | 무료/무제한 | 프롬프트 실험, 초안 생성 |
| **OpenRouter** | 유료 | `google/gemini-2.5-pro-image` 자동화 |
| **Google AI Studio** | 무료 티어 | 대안 API |

---

## 5. 검증 체크리스트

- [ ] 5개 패턴 모두 AntiGravity IDE에서 테스트
- [ ] 생성 이미지가 1280x720 16:9에서 텍스트 배치 공간 확보됨
- [ ] 한글 텍스트를 포함하지 않는 깔끔한 배경 출력 확인
- [ ] 브랜드 컬러(Blue #2D7FF9, Yellow #FFD600, Navy #0D1B2A)가 반영됨
- [ ] 성적/폭력적 이미지 없음 확인

---

## 6. 변형 가이드

각 패턴의 `variables`를 조정하여 변형 가능:

```
예시: screen-glow 패턴에서 device 변경
- "laptop screen" → "dual monitor setup"
- "laptop screen" → "tablet screen"

예시: tech-gradient 패턴에서 mood 변경
- "bright energetic" → "calm professional"
- "bright energetic" → "dynamic and exciting"
```

---

> **[승인 필요]** 이 프롬프트 패턴들을 AntiGravity IDE에서 테스트 후 결과를 검토해 주세요.
> 패턴 수정/추가/삭제가 필요하면 말씀하세요.
