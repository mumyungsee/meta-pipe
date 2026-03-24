# Step 3: 템플릿 엔진 설계

> **파이프라인**: 카드뉴스 자동화 도구
> **목적**: 재사용 가능한 카드뉴스 템플릿을 정의하고 관리하는 시스템을 설계한다.
> **approval_required**: false (데이터 모델 확정 후 구현 세부사항)

---

## 1. 템플릿 구조: 슬롯 시스템

각 템플릿은 **슬롯(Slot)**의 집합으로 정의된다. 슬롯은 요소가 배치될 수 있는 영역.

```
Template = SlotDefinition[]

SlotDefinition:
  - slot_id: "title" | "subtitle" | "body_text" | "image" | "cta" | "logo"
  - position: { x, y, width, height } (% 단위, 반응형)
  - default_style: 기본 폰트/색상/정렬
  - required: boolean
```

### 슬롯 좌표 시스템

```
(0,0) ─────────────────── (100,0)
│                                │
│   [title slot]                 │
│                                │
│   [body_text slot]             │
│                                │
│   [image slot]                 │
│                                │
(0,100) ─────────────────(100,100)

좌표: % 단위 (0-100)
  → 판형이 바뀌어도 비율 유지
  → 실제 px = slot.position * canvas_size / 100
```

---

## 2. 기본 레이아웃 유형 (6개)

### Cover 템플릿 (2개)

**cover-center**: 중앙 정렬 제목
```
┌──────────────────┐
│                  │
│   [title]        │
│   [subtitle]     │
│                  │
│          [logo]  │
└──────────────────┘
slots:
  title:     { x:10, y:30, w:80, h:20, required:true }
  subtitle:  { x:15, y:52, w:70, h:10, required:false }
  logo:      { x:70, y:85, w:20, h:10, required:false }
```

**cover-left**: 좌측 정렬 + 이미지
```
┌──────────────────┐
│ [title]  │       │
│ [sub]    │ [img] │
│          │       │
│  [logo]  │       │
└──────────────────┘
slots:
  title:     { x:5, y:20, w:45, h:25, required:true }
  subtitle:  { x:5, y:48, w:45, h:10, required:false }
  image:     { x:55, y:5, w:40, h:90, required:false }
  logo:      { x:5, y:85, w:15, h:10, required:false }
```

### Body 템플릿 (2개)

**body-text-top**: 텍스트 상단 + 이미지 하단
```
┌──────────────────┐
│ [title]          │
│ [body_text]      │
│                  │
│ [image]          │
└──────────────────┘
slots:
  title:     { x:10, y:8, w:80, h:12, required:true }
  body_text: { x:10, y:22, w:80, h:25, required:true }
  image:     { x:10, y:52, w:80, h:42, required:false }
```

**body-split**: 좌우 분할
```
┌──────────────────┐
│ [title]          │
│ [img]  │ [text]  │
│        │         │
└──────────────────┘
slots:
  title:     { x:10, y:5, w:80, h:12, required:true }
  image:     { x:5, y:22, w:43, h:70, required:false }
  body_text: { x:52, y:22, w:43, h:70, required:true }
```

### Closing 템플릿 (2개)

**closing-cta**: CTA 중심
```
┌──────────────────┐
│                  │
│   [cta]          │
│   [subtitle]     │
│                  │
│   [logo]         │
└──────────────────┘
slots:
  cta:       { x:10, y:30, w:80, h:20, required:true }
  subtitle:  { x:15, y:55, w:70, h:10, required:false }
  logo:      { x:35, y:80, w:30, h:12, required:false }
```

**closing-info**: 정보 나열
```
┌──────────────────┐
│ [title]          │
│ [body_text]      │
│ [logo]           │
│ [cta]            │
└──────────────────┘
slots:
  title:     { x:10, y:10, w:80, h:15, required:false }
  body_text: { x:10, y:30, w:80, h:30, required:false }
  logo:      { x:35, y:62, w:30, h:12, required:false }
  cta:       { x:15, y:80, w:70, h:12, required:true }
```

---

## 3. 스타일 변수 시스템

```json
{
  "theme_variables": {
    "colors": {
      "--primary": "#2563EB",
      "--secondary": "#F59E0B",
      "--bg": "#FFFFFF",
      "--text": "#1F2937",
      "--text-light": "#6B7280"
    },
    "fonts": {
      "--font-title": "Pretendard",
      "--font-body": "Pretendard",
      "--font-weight-title": 700,
      "--font-weight-body": 400
    },
    "spacing": {
      "--margin": "40px",
      "--padding": "24px",
      "--line-height": 1.618
    }
  }
}
```

스타일 변수만 교체하면 같은 레이아웃에서 다른 분위기 생성:

```
"Corporate" → primary:#1E3A5F, font:Pretendard, weight:700
"Playful"   → primary:#FF6B6B, font:NanumSquare, weight:800
"Minimal"   → primary:#333333, font:NotoSansKR, weight:300
```

---

## 4. 자동 폰트 크기 조정

```
텍스트 길이에 따른 자동 조정:
  IF text.length <= 10: font_size = max (48pt)
  IF text.length <= 20: font_size = 36pt
  IF text.length <= 40: font_size = 28pt
  IF text.length <= 60: font_size = 24pt
  IF text.length >  60: font_size = min (20pt) + overflow 처리

overflow 처리:
  1. 줄바꿈으로 분리
  2. 여전히 넘치면 폰트 축소 (min 16pt까지)
  3. 그래도 넘치면 텍스트 잘림 + "..." (경고 로그)
```

---

## 5. 이미지 자동 fit 전략

```
이미지 비율 vs 슬롯 비율:
  비율 일치:     fit = "cover" (꽉 채움)
  가로가 더 넓:  fit = "cover" + 상하 중앙 crop
  세로가 더 넓:  fit = "cover" + 좌우 중앙 crop
  비율 큰 차이:  fit = "contain" + 배경색 여백

플랫폼별 판형 흡수:
  Template의 슬롯 좌표가 % 단위이므로
  canvas_size만 변경하면 판형 자동 대응
```
