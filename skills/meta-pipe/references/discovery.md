# Phase B: Discover (도메인 조사)

> 목표 도메인의 전문가 수준 지식을 확보한다. Phase A(Consult)의 산출물을 반영하여 조사 방향이 구체화된다.

<!-- Design Ref: §3.2 discovery.json, §5 캐시 시스템, §7.1 Phase B 컨텍스트 로드 -->
<!-- Plan SC: 2개 이상 도메인에서 end-to-end 완주 — Phase B가 도메인 지식 확보 담당 -->

---

## 입력 컨텍스트

Phase B 시작 시 SKILL.md가 로드해주는 데이터:

| 항목 | 출처 | 용도 |
|------|------|------|
| A.summary | consult-result.json의 `.summary` | 조사 방향 결정 (목표, 선택 경로, 복잡도) |
| 원본 입력 | `.meta-pipe-status.json`의 `input_prompt` | 도메인 키워드 추출 |
| domain_slug | `.meta-pipe-status.json`의 `domain_slug` | 산출물/캐시 경로 |
| consult_path_id | consult-result.json의 `selected_path.id` | 캐시 히트 판단 |

---

## 0. 캐시 체크

Phase B 실행 전 캐시를 확인한다. SKILL.md의 `--refresh` 플래그가 있으면 이 단계를 건너뛴다.

```
runtime/cache/{domain-slug}/ 존재?
  |
  ├─ No  → 캐시 미스 → B1~B3 정상 실행
  |
  └─ Yes → cached_at.json 읽기
           → consult_path_id 비교 (A에서 선택한 경로 ID와)
             |
             ├─ 일치 → 캐시 히트!
             |         사용자에게 확인:
             |         "이전에 동일 경로로 조사한 결과가 있습니다. 재사용할까요?"
             |           → Yes: Phase B 건너뛰기 (SKILL.md에 "skipped" 보고)
             |           → No:  B1~B3 재실행 → 캐시 덮어쓰기
             |
             └─ 불일치 → "조사 방향이 달라졌으므로 재조사합니다."
                         B1~B3 재실행 → 캐시 덮어쓰기
```

---

## B1. 5카테고리 WebSearch 조사

A.summary에서 목표와 선택 경로를 읽고, 원본 입력에서 도메인 키워드를 추출한다.

### 1.1 도메인 키워드 추출

```
원본 입력: "유튜브 섬네일 전자동으로 만들고 싶어"
  → domain: "유튜브 섬네일"
  → domain_en: "youtube thumbnail"

A.summary: "... DALL-E + YouTube API 경로 선택. Standard 레벨."
  → 조사에 반영: DALL-E, YouTube API 관련 도구/워크플로우 중점 조사
```

### 1.2 5카테고리 쿼리 템플릿

도메인 키워드를 추출한 후, 아래 5개 카테고리로 WebSearch를 실행한다.

```
카테고리 1: 핵심 용어
  한국어: "{domain} 핵심 용어 표준 업계 용어 정의"
  영어:   "{domain_en} key terminology standard glossary"

카테고리 2: 워크플로우
  한국어: "{domain} 워크플로우 best practice 프로세스 단계"
  영어:   "{domain_en} workflow best practice process steps"

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

### 1.3 A.summary 반영 쿼리 보강

A에서 선택한 경로의 도구/방법이 있으면 쿼리에 추가한다:

```
예: selected_path에 "DALL-E" 포함 시
  기술 스택 쿼리 → "{domain} DALL-E 3 API integration workflow pricing"
  리스크 쿼리   → "{domain} DALL-E content policy rate limit"
```

이렇게 하면 v1과 달리 A의 컨설팅 결과가 조사 방향을 구체화한다.

### 1.4 쿼리 전략

- **한국어 + 영어 동시 검색**: 한국어 결과가 부족한 카테고리는 영어로 보완
- **도메인별 키워드 추가**: 관련 전문 키워드를 추가
  - 핀테크 → "KYC AML PCI-DSS"
  - 게임 → "game loop ECS sprite"
  - 의료 → "HIPAA HL7 FHIR"
- **연도 한정**: 최신 트렌드가 중요한 도메인은 "2025 2026" 추가

### 1.5 검색 순서

```
1. 5개 카테고리 한국어 WebSearch (병렬 가능)
2. 결과 품질 평가 (B2)
3. 미흡/부족 카테고리 → 영어 WebSearch
4. 여전히 미흡 → WebFetch 보완 대상 선정
```

---

## B2. 품질 평가 + 보완 조사

### 2.1 카테고리별 품질 등급

| 등급 | 기준 |
|------|------|
| **우수** (excellent) | 실무에 바로 적용 가능한 구체적 정보. 다수의 신뢰할 수 있는 출처 |
| **양호** (good) | 유용한 정보가 있으나 일부 보완 필요. 출처 2개 이상 |
| **미흡** (fair) | 직접적 정보 부족. 간접적 정보에서 유추 필요 |
| **부족** (poor) | 해당 카테고리 정보를 거의 찾지 못함 |

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
  부족 = 직접 설계 필요 (일반적 — 도메인 특화 스키마 자료는 드묾)

리스크:
  우수 = 법적/기술적 리스크 목록 + 대응방안
  양호 = 주요 리스크 파악, 대응방안 일부
  미흡 = 일반적 주의사항만
  부족 = 리스크 정보 없음
```

### 2.3 보완 조사

미흡 이하 카테고리에 대해 보완 조사를 실행한다.

**영어 WebSearch**: 미흡/부족 카테고리를 영어 쿼리로 재검색.

**WebFetch 심층 분석**: WebSearch 결과 중 심층 분석이 필요한 URL을 선별:

```
우선순위 높음:
  - 공식 API/SDK 문서 (기술 스택 구체화)
  - 규제 가이드라인 (법적 리스크 정확도)
  - 학술 논문 (데이터 모델, 아키텍처 보완)

우선순위 중간:
  - 상세 튜토리얼/구현 가이드
  - 도구 비교 리뷰

우선순위 낮음:
  - 일반 블로그 포스트
  - 뉴스 기사
```

**규칙**:
- 최대 3~5개 URL (컨텍스트 비용 고려)
- WebFetch 결과가 길면 핵심 부분만 추출
- 보완 후 해당 카테고리 품질 등급 재평가

### 2.4 데이터 모델 직접 도출

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
   - "직접 도출 모델"임을 명시 (sources에 "derived" 표기)
```

---

## B3. 조사 결과 구조화

조사 완료 후 **이중 형식**으로 출력한다: 사람용 마크다운 + 에이전트용 JSON.

### 3.1 discovery.md (사람용 마크다운 보고서)

경로: `test/{domain-slug}/pipeline/discovery.md`

```markdown
# Phase B: Discover - {domain} 도메인 조사

> **도메인**: {domain}
> **조사 일자**: {date}
> **선택 경로**: {selected_path.description} (from Phase A)
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

| 카테고리 | 주요 발견 | 품질 등급 |
|----------|----------|:---------:|
| 핵심 용어 | {summary} | {excellent/good/fair/poor} |
| 워크플로우 | {summary} | {excellent/good/fair/poor} |
| 기술 스택 | {summary} | {excellent/good/fair/poor} |
| 데이터 모델 | {summary} | {excellent/good/fair/poor} |
| 리스크 | {summary} | {excellent/good/fair/poor} |
```

### 3.2 discovery.json (에이전트용 구조화 데이터)

경로: `test/{domain-slug}/pipeline/discovery.json`

v2 공통 헤더 + domain_knowledge 5카테고리:

```json
{
  "version": "2.0",
  "phase": "B",
  "created_at": "ISO 8601",
  "summary": "(300자 이내. 5카테고리 조사 핵심 + 선택 경로 관련 기술 스택 요약)",

  "domain_knowledge": {
    "glossary": [
      { "term": "용어", "definition": "정의" }
    ],
    "workflows": [
      {
        "name": "워크플로우 이름",
        "steps": ["단계1", "단계2"]
      }
    ],
    "tech_stack": [
      {
        "tool": "도구명",
        "purpose": "용도",
        "cost": "비용 (해당 시)"
      }
    ],
    "data_model": [
      {
        "entity": "엔티티명",
        "fields": ["필드1", "필드2"],
        "relationships": ["관계 설명"]
      }
    ],
    "risks": [
      {
        "risk": "리스크 설명",
        "severity": "high | medium | low",
        "mitigation": "대응방안"
      }
    ]
  },
  "quality_grades": {
    "glossary": "excellent | good | fair | poor",
    "workflows": "excellent | good | fair | poor",
    "tech_stack": "excellent | good | fair | poor",
    "data_model": "excellent | good | fair | poor",
    "risks": "excellent | good | fair | poor"
  }
}
```

**필수 필드**: domain_knowledge (하위 5카테고리: glossary, workflows, tech_stack, data_model, risks)

**summary 규칙**: 300자 이내. Phase C가 이것만 읽고도 파이프라인 step 수와 도구를 결정할 수 있어야 한다. 포함할 것: 핵심 워크플로우 단계 수, 주요 도구, 주의할 리스크.

---

## 캐시 저장

B1~B3 완료 후 결과를 캐시에 저장한다.

### 캐시 구조

```
runtime/cache/{domain-slug}/
├── cached_at.json      # 캐시 메타데이터
├── discovery.json      # B 산출물 복사
└── discovery.md        # B 보고서 복사
```

### cached_at.json

```json
{
  "cached_at": "ISO 8601",
  "consult_path_id": "{A에서 선택된 경로 ID}",
  "domain": "{domain}",
  "domain_slug": "{domain-slug}",
  "quality_grades": {
    "glossary": "excellent",
    "workflows": "good",
    "tech_stack": "good",
    "data_model": "fair",
    "risks": "good"
  }
}
```

consult_path_id를 저장하여 다음 실행 시 경로가 동일한지 판단한다.

---

## Phase B 완료 후

1. `.meta-pipe-status.json` 업데이트: `phases.B.status = "completed"`, `current_phase = "C"`
2. 사용자에게 요약 출력:
   ```
   Phase B 완료.
   - 5카테고리 조사 결과:
     용어: {grade}, 워크플로우: {grade}, 기술 스택: {grade},
     데이터 모델: {grade}, 리스크: {grade}
   - 보완 조사: {N}건 WebFetch 수행
   - 캐시 저장 완료: runtime/cache/{domain-slug}/

   Phase C(파이프라인 설계)로 진행합니다...
   ```
3. Phase C로 전환 (SKILL.md의 Phase 전환 루프가 처리)
