# Step 4: 콘텐츠 파이프라인 설계

> **파이프라인**: 카드뉴스 자동화 도구
> **목적**: 원시 텍스트/주제에서 카드뉴스 콘텐츠(카피, 이미지 키워드, 슬라이드 구성)를 자동 생성하는 파이프라인을 설계한다.
> **approval_required**: true (콘텐츠 품질이 최종 결과물의 핵심)

---

## 1. 입력 형식

### 1.1 지원 입력 유형

| 유형 | 예시 | 처리 방식 |
| --- | --- | --- |
| **주제어** | "재택근무 생산성 팁" | LLM이 주제 기반 콘텐츠 생성 |
| **원문 텍스트** | 블로그 글 본문 붙여넣기 | 텍스트 요약 → 슬라이드 분할 |
| **URL** | https://blog.example.com/article | WebFetch로 본문 추출 → 요약 → 분할 |

### 1.2 공통 옵션

```json
{
  "input": "재택근무 생산성 팁",
  "input_type": "topic",
  "options": {
    "slide_count": 7,           // 원하는 슬라이드 수 (null = 자동)
    "tone": "friendly",         // friendly | professional | playful
    "target_audience": "직장인",
    "language": "ko"
  }
}
```

---

## 2. 콘텐츠 생성 파이프라인

```
입력 (주제/텍스트/URL)
  │
  ▼
[Stage 1] 콘텐츠 분석 & 아웃라인
  - 핵심 메시지 추출
  - 슬라이드 수 결정 (5~10장)
  - 슬라이드별 핵심 메시지 1개씩 배정
  │
  ▼
[Stage 2] 슬라이드별 카피라이팅
  - 표지: 호기심 유발 제목 (15자 이내)
  - 본문: 핵심 메시지 (제목 15자 + 본문 50자 이내)
  - 마지막 장: CTA 문구
  │
  ▼
[Stage 3] 이미지 키워드 생성
  - 각 슬라이드 텍스트와 의미적으로 일치하는 키워드
  - 스톡 이미지 검색용 영어 키워드 3~5개
  │
  ▼
[Stage 4] 스토리라인 검증
  - 슬라이드 간 논리적 흐름 확인
  - 반복/중복 제거
  - 표지(호기심) → 본문(정보 전달) → 마지막(행동 유도) 패턴 확인
  │
  ▼
출력: ContentPlan (아래 스키마)
```

---

## 3. LLM 프롬프트 설계

### 3.1 아웃라인 생성 프롬프트

```
당신은 카드뉴스 콘텐츠 전문가입니다.

주제: {input}
대상: {target_audience}
톤: {tone}
슬라이드 수: {slide_count || "5~10장 사이에서 적절히 결정"}

다음 규칙을 따라 카드뉴스 아웃라인을 작성하세요:

1. 첫 슬라이드(표지): 호기심을 유발하는 질문이나 강렬한 문장
2. 본문 슬라이드: 각 슬라이드에 핵심 메시지 1개만
3. 마지막 슬라이드: 구체적인 행동 유도(CTA)
4. 전체 흐름이 자연스러운 스토리라인 형성

출력 형식:
slide_1 (cover): [제목]
slide_2 (body): [핵심 메시지]
...
slide_N (closing): [CTA]
```

### 3.2 카피라이팅 프롬프트

```
당신은 SNS 카피라이터입니다.

아래 아웃라인의 각 슬라이드를 카드뉴스 텍스트로 작성하세요.

규칙:
- 제목: 15자 이내, 굵고 임팩트 있게
- 본문: 50자 이내, 핵심만 간결하게
- 한 슬라이드에 메시지 1개만
- 숫자/데이터 활용 권장 (구체성)
- 이모지 최소 사용 (클린한 톤)

아웃라인:
{outline}

출력 형식 (JSON):
[
  { "slide_type": "cover", "title": "...", "subtitle": "..." },
  { "slide_type": "body", "title": "...", "body": "..." },
  ...
  { "slide_type": "closing", "cta": "...", "subtitle": "..." }
]
```

### 3.3 이미지 키워드 프롬프트

```
아래 카드뉴스 슬라이드 텍스트에 어울리는 배경 이미지 검색 키워드를 생성하세요.

규칙:
- 영어 키워드 3~5개
- 텍스트 내용과 의미적으로 일치
- 추상적이지 않고 구체적인 시각 이미지
- 스톡 이미지 사이트(Pexels, Unsplash)에서 검색 가능한 키워드

슬라이드:
{slides}

출력 형식 (JSON):
[
  { "slide_index": 0, "keywords": ["keyword1", "keyword2", "keyword3"] },
  ...
]
```

---

## 4. ContentPlan 스키마

```typescript
interface ContentPlan {
  topic: string;
  input_type: "topic" | "text" | "url";
  tone: "friendly" | "professional" | "playful";
  total_slides: number;
  slides: ContentSlide[];
  storyline_summary: string;     // 전체 스토리 한줄 요약
}

interface ContentSlide {
  slide_index: number;
  slide_type: "cover" | "body" | "closing";
  title: string;                  // 15자 이내
  body: string | null;            // 50자 이내 (body 타입만)
  subtitle: string | null;
  cta: string | null;             // closing 타입만
  image_keywords: string[];       // 영어 키워드 3~5개
  key_message: string;            // 핵심 메시지 1줄 요약
}
```

---

## 5. 스토리라인 검증 규칙

```
검증 체크리스트:
  [ ] 표지가 호기심/관심을 유발하는가?
  [ ] 각 본문 슬라이드가 독립적인 핵심 메시지를 가지는가?
  [ ] 슬라이드 간 논리적 연결이 자연스러운가?
  [ ] 정보가 점진적으로 심화되는가? (얕은 → 깊은)
  [ ] 마지막 장에 명확한 CTA가 있는가?
  [ ] 중복 메시지가 없는가?
  [ ] 제목이 15자, 본문이 50자 이내인가?

자동 검증 가능:
  - 글자 수 제한 (자동)
  - 중복 키워드 감지 (자동)
  - cover → body → closing 순서 (자동)

수동 검증 필요:
  - 스토리 흐름의 자연스러움
  - 톤 일관성
  - 메시지의 설득력
```

---

## 주의사항

- 카드당 텍스트량 엄격 제한: 제목 15자, 본문 50자 권장
- 표지는 "질문형" 또는 "숫자형" 제목이 효과적 (예: "3가지 방법", "왜 실패할까?")
- 이미지 키워드는 텍스트 내용과 **의미적 일치** 필요 (시각적 비유 아닌 직접 연관)
- LLM 프롬프트 품질은 실제 테스트로 반복 검증 필요 [검토 필요]
