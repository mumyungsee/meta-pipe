# Step 6: 플랫폼 어댑터 & 내보내기

> **파이프라인**: 카드뉴스 자동화 도구
> **목적**: 생성된 카드뉴스를 각 SNS 플랫폼에 맞는 형식으로 변환하고 내보내는 시스템.
> **approval_required**: false (기술 구현 세부사항)

---

## 1. 플랫폼 어댑터 구조

```typescript
interface PlatformAdapter {
  platform: PlatformType;
  resize(slide: RenderedSlide, preset: PlatformPreset): Buffer;
  optimize(buffer: Buffer, config: ExportConfig): Buffer;
  validate(buffer: Buffer): ValidationResult;
}
```

### 어댑터별 변환 로직

| 플랫폼 | 사이즈 | 포맷 | 특수 처리 |
| --- | --- | --- | --- |
| instagram_feed (1:1) | 1080x1080 | PNG/JPG | 정방형 crop, 30MB 제한 |
| instagram_feed (4:5) | 1080x1350 | PNG/JPG | 세로 확장, 30MB 제한 |
| instagram_story (9:16) | 1080x1920 | PNG/JPG | 상하 여백 or 확장 |
| facebook (16:9) | 1920x1080 | JPG | 파일 용량 최적화 (10MB) |
| blog (16:9) | 1920x1080 | PNG | 고품질 유지 |
| kakaotalk (1:1) | 800x800 | JPG | 5MB 제한, 용량 최적화 |

---

## 2. 멀티 플랫폼 내보내기

```
입력: Project + RenderedSlides[]
  │
  ▼
FOR each platform in export_config.platform_presets:
  FOR each slide in slides:
    1. 리사이즈 (원본 → 플랫폼 사이즈)
    2. 포맷 변환 (PNG → 플랫폼 최적 포맷)
    3. 품질 최적화 (용량 제한 내)
    4. 파일 저장
  │
  ▼
출력 구조:
  output/
  ├── instagram-1x1/
  │   ├── 01_cover.png
  │   ├── 02_body.png
  │   └── ...
  ├── facebook-16x9/
  │   ├── 01_cover.jpg
  │   └── ...
  └── export-all.zip        ← ZIP 묶음
```

---

## 3. 파일 네이밍 컨벤션

```
패턴: {index}_{slide_type}.{ext}
  예: 01_cover.png, 02_body.png, 07_closing.png

플랫폼별 폴더: {platform}-{aspect_ratio}/
  예: instagram-1x1/, facebook-16x9/

ZIP 파일: {project_name}_{platform}_{date}.zip
  예: productivity-tips_instagram-1x1_20260324.zip
```

---

## 4. 이미지 포맷 최적화

```
텍스트 중심 슬라이드 → PNG (텍스트 선명도)
사진 중심 슬라이드  → JPG (파일 용량)
웹 최적화 필요 시   → WebP (최소 용량)

JPG 품질 설정:
  기본: 85 (용량/품질 균형)
  용량 초과 시: 75 → 65 단계적 축소
  최소: 60 (이하는 품질 저하 심각)

용량 검증:
  IF file_size > platform.max_file_size_mb:
    1. JPG 품질 단계적 축소
    2. 여전히 초과 → 해상도 축소 (90% → 80%)
    3. 경고 로그 기록
```

---

## 5. 플랫폼 사이즈 설정 파일

```json
// config/platforms.json
{
  "platforms": [
    {
      "id": "instagram_feed_1x1",
      "name": "인스타그램 피드 (정방형)",
      "aspect_ratio": "1:1",
      "width": 1080,
      "height": 1080,
      "max_file_size_mb": 30,
      "recommended_format": "png",
      "updated_at": "2026-03-24"
    }
  ]
}
```

하드코딩 금지 - 플랫폼 사양 변경 시 이 파일만 수정.

---

## 주의사항

- 플랫폼별 이미지 사이즈 제약이 수시로 변경됨 → `config/platforms.json`으로 관리
- 파일명에 슬라이드 순서 반드시 포함 (SNS 업로드 순서 보장)
- ZIP 묶음 내보내기 지원 (대량 업로드 편의)
- [검토 필요] 플랫폼 API 직접 게시는 v2.0 범위 (Instagram Graph API 등)
