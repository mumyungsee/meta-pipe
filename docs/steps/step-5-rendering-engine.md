# Step 5: 렌더링 엔진 구현

> **파이프라인**: 카드뉴스 자동화 도구
> **목적**: 데이터 모델 + 템플릿 + 콘텐츠를 결합하여 실제 이미지를 생성하는 엔진을 설계한다.
> **approval_required**: false (앞 단계에서 범위 확정된 구현 세부사항)

---

## 1. 렌더링 방식

**선택: HTML/CSS → Puppeteer 스크린샷**

| 대안 | 장점 | 단점 | 선택 이유 |
| --- | --- | --- | --- |
| **HTML/CSS + Puppeteer** | 웹 기술 그대로, 픽셀 퍼펙트, 폰트 렌더링 우수 | Headless Chrome 의존 | **채택** - 업계 검증, 가장 유연 |
| Canvas API (node-canvas) | 경량, 서버 의존 낮음 | 텍스트 레이아웃 복잡, CSS 미지원 | 미채택 |
| Sharp 합성 | 고성능 | 텍스트 렌더링 한계 | 후처리용으로만 사용 |

---

## 2. 렌더링 파이프라인

```
Slide (데이터)
  │
  ▼
[1] HTML 생성
  - Template의 layout_slots → HTML 구조
  - Element 데이터 → HTML 요소
  - StyleGuide → CSS 변수
  │
  ▼
[2] CSS 적용
  - 스타일 변수 시스템 (--primary, --font-title 등)
  - 슬롯 위치 → absolute positioning
  - 반응형 처리 (% → px 변환)
  │
  ▼
[3] 폰트 로딩
  - @font-face 선언
  - 로컬 폰트 파일 참조 (fonts/ 디렉토리)
  - 한글 폰트: 나눔스퀘어, 프리텐다드, Noto Sans KR
  │
  ▼
[4] Puppeteer 렌더링
  - page.setViewport({ width, height, deviceScaleFactor: 2 })
  - page.setContent(html)
  - page.screenshot({ type: 'png', fullPage: true })
  │
  ▼
[5] 후처리 (Sharp)
  - 포맷 변환 (PNG → JPG/WebP)
  - 품질 최적화
  - 파일 용량 확인 (플랫폼 제한)
  │
  ▼
출력: 이미지 파일 (PNG/JPG/WebP)
```

---

## 3. HTML 템플릿 생성

```html
<!-- 슬라이드 HTML 구조 예시 -->
<div class="slide" style="
  width: ${canvas.width}px;
  height: ${canvas.height}px;
  position: relative;
  overflow: hidden;
  background: ${background.value};
">
  <!-- 배경 이미지 (있을 경우) -->
  <img class="bg-image" src="${background.image_url}"
       style="position:absolute; width:100%; height:100%; object-fit:cover;" />

  <!-- 반투명 오버레이 (텍스트 가독성) -->
  <div class="overlay" style="
    position:absolute; width:100%; height:100%;
    background: rgba(0,0,0,${overlay_opacity});
  "></div>

  <!-- 요소들 (z_index 순서) -->
  ${elements.map(el => renderElement(el)).join('')}
</div>
```

---

## 4. 폰트 관리

### 기본 제공 폰트 (OFL 라이선스)

| 폰트 | 용도 | 파일 |
| --- | --- | --- |
| Pretendard | 범용 본문/제목 | fonts/Pretendard-*.woff2 |
| NanumSquare | 굵은 제목 | fonts/NanumSquare-*.woff2 |
| Noto Sans KR | 범용 대체 | fonts/NotoSansKR-*.woff2 |

### 폰트 로딩

```css
@font-face {
  font-family: 'Pretendard';
  src: url('./fonts/Pretendard-Regular.woff2') format('woff2');
  font-weight: 400;
}
@font-face {
  font-family: 'Pretendard';
  src: url('./fonts/Pretendard-Bold.woff2') format('woff2');
  font-weight: 700;
}
```

### 한글 렌더링 주의사항

- Puppeteer `--font-render-hinting=none` 플래그로 힌팅 비활성화 (깔끔한 렌더링)
- `font-feature-settings: "kern"` 한글 자간 최적화
- 행간(line-height) = 폰트크기 x 1.618 고정 (CSS와 디자인 도구 차이 보정)

---

## 5. 품질 기준

| 항목 | 기준 |
| --- | --- |
| 해상도 | 1080px 기준, 2x DPI (deviceScaleFactor: 2) |
| 렌더링 시간 | 슬라이드 1장당 3초 이내 |
| 한글 폰트 | 자간, 행간, 장평 정상 렌더링 |
| 이미지 위 텍스트 | 반투명 오버레이로 가독성 보장 |
| 파일 용량 | PNG < 5MB, JPG < 2MB (슬라이드당) |
