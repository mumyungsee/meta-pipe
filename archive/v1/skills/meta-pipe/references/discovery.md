# Phase A: Discover - 상세 가이드

> 이 문서는 SKILL.md의 Phase A 실행 시 로드된다.
> 도메인 조사의 구체적인 절차, 쿼리 패턴, 평가 기준, 구조화 규칙을 정의한다.

---

## 1. WebSearch 쿼리 생성

### 1.1 5개 카테고리 쿼리 템플릿

도메인 키워드를 추출한 후, 아래 5개 카테고리로 WebSearch를 실행한다.

```
카테고리 1: 핵심 용어
  한국어: "{domain} 핵심 용어 표준 업계 용어 정의"
  영어:   "{domain_en} key terminology standard glossary"

카테고리 2: 워크플로우
  한국어: "{domain} 개발 워크플로우 best practice 프로세스 단계"
  영어:   "{domain_en} development workflow best practice process steps"

카테고리 3: 기술 스택
  한국어: "{domain} 자동화 소프트웨어 기술 스택 오픈소스 라이브러리"
  영어:   "{domain_en} automation software tech stack open source library"

카테고리 4: 데이터 모델
  한국어: "{domain} 데이터 모델 엔티티 스키마 ERD"
  영어:   "{domain_en} data model entity schema ERD database"

카테고리 5: 리스크
  한국어: "{domain} 실패 사례 주의사항 리스크 규제"
  영어:   "{domain_en} failure cases pitfalls risks regulations compliance"
```

### 1.2 쿼리 전략

- **한국어 + 영어 동시 검색**: 한국어 결과가 부족한 카테고리는 영어로 보완
- **구체적 키워드 추가**: 도메인에 따라 관련 키워드를 추가
  - 핀테크 → "KYC AML PCI-DSS"
  - 게임 → "game loop ECS sprite"
  - 의료 → "HIPAA HL7 FHIR"
- **연도 한정**: 최신 트렌드가 중요한 도메인은 "2025 2026" 추가

### 1.3 검색 순서

```
1. 5개 카테고리 한국어 WebSearch (병렬 가능)
2. 결과 품질 평가
3. 미흡/부족 카테고리 → 영어 WebSearch
4. 여전히 미흡 → WebFetch 보완 대상 선정
```

---

## 2. 결과 평가 기준

### 2.1 카테고리별 품질 등급

| 등급 | 기준 |
| --- | --- |
| **우수** (excellent) | 실무에 바로 적용 가능한 구체적 정보. 다수의 신뢰할 수 있는 출처 |
| **양호** (good) | 유용한 정보가 있으나 일부 보완 필요. 출처가 2개 이상 |
| **미흡** (fair) | 직접적 정보가 부족. 간접적 정보에서 유추 필요 |
| **부족** (poor) | 해당 카테고리 정보를 거의 찾지 못함. 직접 도출 필요 |

### 2.2 판단 가이드

```
핵심 용어:
  우수 = 업계 표준 용어 10개+ 확인, 정의와 관계까지 파악
  양호 = 주요 용어 5개+ 확인, 일부 정의 부족
  미흡 = 용어 3개 미만, 비공식 출처만
  부족 = 거의 못 찾음

워크플로우:
  우수 = 표준 프로세스 전체 파악, 단계별 상세 설명
  양호 = 대략적 프로세스 파악, 일부 단계 상세 부족
  미흡 = 단편적 정보만, 전체 흐름 불완전
  부족 = 해당 도메인 워크플로우 정보 없음

기술 스택:
  우수 = 실무 도구/라이브러리 비교 가능, 장단점 파악
  양호 = 주요 도구 목록 확인, 비교는 제한적
  미흡 = 도구 1~2개만 확인
  부족 = 기술 정보 없음

데이터 모델:
  우수 = 도메인 특화 스키마/ERD 존재
  양호 = 주요 엔티티 파악 가능, 관계는 유추 필요
  미흡 = 간접적으로 엔티티 유추 가능
  부족 = 직접 설계 필요 (일반적임 - 도메인 특화 스키마 자료는 드묾)

리스크:
  우수 = 법적/기술적 리스크 목록 + 대응방안
  양호 = 주요 리스크 파악, 대응방안 일부
  미흡 = 일반적 주의사항만
  부족 = 리스크 정보 없음
```

---

## 3. WebFetch 보완

### 3.1 보완 대상 선정

WebSearch 결과 중 심층 분석이 필요한 URL을 선별:

```
우선순위 높음:
  - 학술 논문 (데이터 모델, 아키텍처 보완)
  - 공식 API/SDK 문서 (기술 스택 구체화)
  - 규제 가이드라인 (법적 리스크 정확도)

우선순위 중간:
  - 상세 튜토리얼/구현 가이드
  - 도구 비교 리뷰

우선순위 낮음:
  - 일반 블로그 포스트
  - 뉴스 기사
```

### 3.2 보완 규칙

- **최대 3~5개 URL** (컨텍스트 비용 고려)
- WebFetch 결과가 길면 핵심 부분만 추출
- 보완 후 해당 카테고리 품질 등급 재평가

---

## 4. 조사 결과 구조화

### 4.1 마크다운 보고서 (domain-discovery.md)

```markdown
# Phase A: Discover - {domain} 도메인 조사

> **도메인**: {domain}
> **조사 일자**: {date}
> **상태**: Complete

---

## 1. {domain} 핵심 용어 표준
### 1.1 {subtopic}
(내용)

**출처:**
- [제목 - 사이트](URL)

---

## 2. {domain} 워크플로우 Best Practice
(내용)

---

## 3. {domain} 기술 스택
(내용)

---

## 4. {domain} 데이터 모델
> [검토 필요] (직접 도출 시)
(내용)

---

## 5. {domain} 리스크 & 주의사항
(내용)

---

## 조사 요약

| 카테고리 | 주요 발견 | 신뢰도 |
| --- | --- | --- |
| 핵심 용어 | {summary} | {높음/중간/낮음} |
| 워크플로우 | {summary} | {높음/중간/낮음} |
| 기술 스택 | {summary} | {높음/중간/낮음} |
| 데이터 모델 | {summary} | {높음/중간/낮음} |
| 리스크 | {summary} | {높음/중간/낮음} |
```

### 4.2 구조화 데이터 (discovery.json)

```json
{
  "domain": "string",
  "investigated_at": "ISO8601",
  "categories": {
    "terminology": {
      "quality": "excellent|good|fair|poor",
      "terms": [
        { "term": "용어", "term_en": "Term", "description": "설명" }
      ],
      "sources": ["url"]
    },
    "workflow": {
      "quality": "excellent|good|fair|poor",
      "standard_process": ["단계 설명"],
      "sources": ["url"]
    },
    "tech_stack": {
      "quality": "excellent|good|fair|poor",
      "tools": [
        { "name": "도구명", "type": "SaaS|library|framework", "description": "설명" }
      ],
      "recommended_approach": "권장 접근법",
      "sources": ["url"]
    },
    "data_model": {
      "quality": "excellent|good|fair|poor",
      "entities": [
        { "name": "엔티티", "fields": ["필드"], "relationships": ["관계"] }
      ],
      "derived": true,
      "sources": ["url"]
    },
    "risks": {
      "quality": "excellent|good|fair|poor",
      "items": [
        { "risk": "리스크", "severity": "high|medium|low", "mitigation": "대응" }
      ],
      "sources": ["url"]
    }
  },
  "webfetch_supplements": [
    { "url": "string", "reason": "string", "priority": "high|medium|low" }
  ]
}
```

---

## 5. 캐시 저장

### 5.1 캐시 구조

```
runtime/cache/{domain-slug}/
├── discovery.md          # 마크다운 보고서 복사
├── discovery.json        # 구조화 데이터
└── cached_at.json        # 캐시 메타데이터
```

### 5.2 cached_at.json

```json
{
  "cached_at": "2026-03-24T15:30:00Z",
  "domain": "카드뉴스 자동화",
  "domain_slug": "card-news-automation",
  "version": "1.0",
  "categories_quality": {
    "terminology": "excellent",
    "workflow": "excellent",
    "tech_stack": "good",
    "data_model": "fair",
    "risks": "good"
  }
}
```

### 5.3 domain-slug 생성 규칙

```
한국어 도메인 → 영어 번역 → kebab-case
  "카드뉴스 자동화" → "card-news-automation"
  "핀테크 송금" → "fintech-remittance"
  "2D 인디 게임" → "2d-indie-game"
```

---

## 6. 데이터 모델 직접 도출

데이터 모델 카테고리가 미흡/부족인 경우 (일반적):

```
1. 다른 카테고리 결과에서 엔티티 후보 추출
   - 핵심 용어 → 주요 명사 = 엔티티 후보
   - 워크플로우 → 각 단계의 입출력 = 엔티티 후보
   - 기술 스택 → 도구가 다루는 데이터 = 엔티티 후보

2. 엔티티 정제
   - 중복 제거, 관계 정의
   - 필수 필드 도출 (도메인 지식 기반)

3. [검토 필요] 마킹
   - "WebSearch에서 직접 확인되지 않은 직접 도출 모델"임을 명시
```
