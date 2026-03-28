# Step 2: 데이터 모델 설계

> **파이프라인**: 카드뉴스 자동화 도구
> **목적**: 카드뉴스의 모든 구성요소를 표현할 수 있는 데이터 구조를 설계한다.

---

## 1. 핵심 엔티티

### 1.1 Project (프로젝트)

카드뉴스 한 세트의 최상위 컨테이너.

```typescript
interface Project {
  id: string;                    // UUID
  name: string;                  // 프로젝트 이름
  description: string;           // 설명/메모
  target_platform: PlatformType; // 기본 타깃 플랫폼
  aspect_ratio: AspectRatio;     // 기본 판형
  canvas_size: { width: number; height: number }; // px
  style_guide: StyleGuide;       // 톤앤매너
  export_config: ExportConfig;   // 내보내기 설정
  slides: Slide[];               // 슬라이드 목록 (순서 보장)
  created_at: string;            // ISO8601
  updated_at: string;
}
```

### 1.2 Slide (슬라이드)

개별 카드 1장.

```typescript
interface Slide {
  id: string;
  project_id: string;
  order_index: number;            // 0-based 순서
  slide_type: "cover" | "body" | "closing";
  template_id: string | null;     // 템플릿 참조 (nullable = 커스텀)
  background: Background;
  elements: Element[];            // z-index 순서
  alt_text: string;               // 접근성: 슬라이드 설명
}

interface Background {
  type: "color" | "image" | "gradient";
  value: string;                  // hex color | image URL | gradient CSS
  opacity: number;                // 0-1
}
```

### 1.3 Element (요소)

슬라이드 위에 배치되는 개별 객체. 다형성 처리.

```typescript
// Base Element
interface BaseElement {
  id: string;
  slide_id: string;
  element_type: ElementType;
  position: { x: number; y: number; width: number; height: number };
  rotation: number;               // 0-360 degrees
  opacity: number;                // 0-1
  z_index: number;
}

type ElementType = "text" | "image" | "shape" | "icon" | "logo";

// Text Element
interface TextElement extends BaseElement {
  element_type: "text";
  content: string;
  font_family: string;
  font_size: number;              // pt
  font_weight: number;            // 100-900
  color: string;                  // hex
  alignment: "left" | "center" | "right";
  line_height: number;            // 배수 (1.618 권장)
  letter_spacing: number;         // px
  text_decoration: "none" | "underline" | "line-through";
}

// Image Element
interface ImageElement extends BaseElement {
  element_type: "image";
  src: string;                    // URL 또는 파일 경로
  alt_text: string;               // 접근성 필수
  fit: "cover" | "contain" | "fill";
  filter: string | null;          // CSS filter (optional)
  license_info: LicenseInfo;      // 라이선스 추적 필수
}

interface LicenseInfo {
  type: "cc0" | "free" | "commercial" | "unknown";
  source: string;                 // Pexels, Unsplash 등
  attribution: string | null;     // 저작자 표시 (필요 시)
  url: string;                    // 원본 URL
}

// Shape Element
interface ShapeElement extends BaseElement {
  element_type: "shape";
  shape_type: "rectangle" | "circle" | "line" | "arrow";
  fill_color: string;
  stroke_color: string;
  stroke_width: number;
}
```

### 1.4 Template (템플릿)

재사용 가능한 레이아웃 + 스타일 조합.

```typescript
interface Template {
  id: string;
  name: string;
  category: "minimal" | "bold" | "corporate" | "playful";
  aspect_ratio: AspectRatio;
  slide_type: "cover" | "body" | "closing";
  theme: {
    primary_color: string;
    secondary_color: string;
    bg_style: "solid" | "gradient" | "image";
  };
  font_set: {
    title_font: string;
    body_font: string;
  };
  layout_slots: SlotDefinition[];  // 요소 배치 위치 정의
  thumbnail_url: string | null;
}

interface SlotDefinition {
  slot_id: string;
  slot_type: "title" | "subtitle" | "body_text" | "image" | "cta" | "logo";
  position: { x: number; y: number; width: number; height: number };
  default_style: Record<string, unknown>;  // 기본 스타일 속성
  required: boolean;
}
```

### 1.5 StyleGuide (스타일 가이드)

프로젝트 전체의 톤앤매너.

```typescript
interface StyleGuide {
  id: string;
  project_id: string;
  color_palette: ColorEntry[];
  fonts: {
    title: FontSpec;
    body: FontSpec;
  };
  spacing: {
    margin: number;               // px
    padding: number;
    line_height_ratio: number;    // 1.618 기본
  };
  brand_assets: BrandAsset[];
}

interface ColorEntry {
  name: string;                   // "primary", "secondary", "accent"
  hex: string;
  usage: string;                  // "배경", "제목 텍스트" 등
}

interface FontSpec {
  family: string;
  weight: number;
  size_range: { min: number; max: number };  // pt
  license: LicenseInfo;
}

interface BrandAsset {
  type: "logo" | "watermark" | "icon";
  url: string;
  license: LicenseInfo;
}
```

### 1.6 ExportConfig (내보내기 설정)

```typescript
interface ExportConfig {
  format: "png" | "jpg" | "webp" | "pdf";
  quality: number;                // 1-100 (jpg/webp)
  dpi: number;                    // 기본 2x (216 DPI)
  platform_presets: PlatformPreset[];
  naming_pattern: string;         // "{project}_{index}_{type}.{ext}"
}

interface PlatformPreset {
  platform: PlatformType;
  aspect_ratio: AspectRatio;
  size: { width: number; height: number };
  max_file_size_mb: number;
}

type PlatformType = "instagram_feed" | "instagram_story" | "facebook" | "blog" | "kakaotalk";
type AspectRatio = "1:1" | "4:5" | "9:16" | "16:9";
```

---

## 2. 엔티티 관계도

```
Project
├── 1:1 StyleGuide
├── 1:1 ExportConfig
├── 1:N Slide (order_index로 정렬)
│   ├── N:1 Template (optional)
│   └── 1:N Element (z_index로 정렬)
│       ├── TextElement
│       ├── ImageElement (+ LicenseInfo)
│       └── ShapeElement
└── (Template은 프로젝트 독립 - 글로벌 리소스)
```

---

## 3. 슬라이드 타입별 필수 요소

| 타입 | 필수 요소 | 선택 요소 |
| --- | --- | --- |
| **cover** | title (TextElement), background (Image/Color) | subtitle, logo, 장식 shape |
| **body** | title (TextElement), body_text (TextElement) | image, shape, icon |
| **closing** | cta (TextElement) | logo, contact_info, source_credits |

---

## 4. 접근성 필수 필드

```
모든 Slide:
  - alt_text: 슬라이드 전체 설명 (시각장애인용)

모든 ImageElement:
  - alt_text: 이미지 설명

모든 이미지/폰트:
  - license_info: 라이선스 유형, 출처, 저작자
```

---

## 주의사항

- Element 다형성은 `element_type` discriminator로 처리
- 슬라이드 타입(cover/body/closing)별 필수 요소가 다름 - Template의 `required` 슬롯으로 강제
- `alt_text`는 모든 Slide와 ImageElement에 필수
- `license_info`는 모든 ImageElement와 FontSpec에 필수 - 저작권 위반 방지
- 마이그레이션: 스키마 버전을 Project에 포함 (`schema_version: "1.0"`)
