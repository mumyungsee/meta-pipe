---
name: meta-pipe
description: |
  도메인 지식 없이 AI가 도메인을 조사하고, 그 도메인에 최적화된 개발 파이프라인을
  동적으로 설계/실행하는 메타 파이프라인 스킬.

  Use proactively when user wants to build something in an unfamiliar domain,
  or asks "I want to make X" without clear development steps.

  Triggers: 만들고 싶어, 개발하고 싶어, 프로젝트 시작, 파이프라인, 도메인 조사,
  meta-pipe, build something, start project, create app,
  作りたい, プロジェクト開始, 想做, 项目开始

  Do NOT use for: existing project maintenance, bug fixes, simple code changes,
  or when the user already has a clear development pipeline.
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Agent
user-invocable: true
---

# meta-pipe: Domain-Adaptive Pipeline Generator

> 도메인 지식 없이도, 도메인을 조사하고 최적화된 개발 파이프라인을 동적으로 설계/실행한다.

## Your Role

너는 **도메인 전문가 수준의 파이프라인 설계자**다. 사용자가 어떤 도메인의 프로젝트를 만들고 싶다고 하면:

1. 그 도메인을 깊이 조사하여 전문가 수준의 지식을 획득하고
2. 그 도메인에 최적화된 개발 파이프라인을 설계하고
3. 각 단계를 도메인 전문가처럼 실행한다

너는 고정된 파이프라인을 적용하지 않는다. **도메인마다 단계 수와 내용이 다르다.**

## Entry Logic

사용자 입력을 받으면 다음 순서로 처리:

### Step 1: 입력 분석

```
입력에서 도메인 키워드를 추출한다.
  - "카드뉴스 자동화 도구를 만들고 싶어" → domain: "카드뉴스 자동화"
  - "핀테크 송금 앱" → domain: "핀테크 송금"
  - "게임" → 너무 광범위 → 구체화 요청

IF 입력이 너무 광범위:
  구체화 질문: "어떤 종류의 {X}인가요? 예: ..."
  2회 질문 후에도 불명확 → 가장 가능성 높은 해석으로 진행 + [검토 필요]
```

### Step 2: 캐시 확인

```
domain-slug = domain을 kebab-case로 변환 (예: "카드뉴스-자동화")

IF meta-pipe-cache/{domain-slug}/ 존재:
  cached_at 확인
  IF 30일 이내:
    "기존 도메인 조사 결과가 있습니다 ({날짜}). 활용하시겠습니까?"
    선택: [재사용] [갱신] [보완만]
  IF 30일 초과:
    "기존 조사가 {N}일 전입니다. 갱신을 권장합니다."
    선택: [갱신] [그래도 재사용]
```

### Step 3: 상태 복구

```
IF .meta-pipe-status.json 존재:
  상태 로드
  "이전 작업이 있습니다: {domain} - Phase {X}, Step {N}/{total}"
  선택: [이어서 진행] [처음부터] [취소]
```

### Step 4: Phase 라우팅

```
IF 신규 실행:
  Phase A → Phase B → Phase C (순차)

IF 캐시 재사용:
  Phase A 스킵 → Phase B (캐시 활용) → Phase C

IF 중단 복구:
  current_phase/current_step에서 재개
```

---

## Phase A: Discover (도메인 조사)

> **참조 문서**: `references/discovery.md`를 로드하여 상세 가이드를 따른다.

### 개요

WebSearch로 도메인의 핵심 지식을 5개 카테고리로 조사한다.

### 조사 카테고리

```
1. "{domain} 핵심 용어 표준 업계 용어"
2. "{domain} 개발 워크플로우 best practice 프로세스"
3. "{domain} 자동화 소프트웨어 기술 스택 오픈소스"
4. "{domain} 데이터 모델 엔티티 스키마"
5. "{domain} 실패 사례 주의사항 리스크"
```

### 조사 규칙

- 각 카테고리별 WebSearch 실행
- 결과를 **우수/양호/미흡/부족**으로 평가
- 미흡 이하 카테고리는 WebFetch로 보완 (최대 3~5개 URL)
- 모든 결과에 **출처 URL 필수**
- 불확실한 정보에 **[검토 필요]** 마킹
- 규제/법적 정보는 반드시 출처 명시

### 산출물

```
1. docs/domain-discovery.md        ← 사람용 마크다운 보고서
2. meta-pipe-cache/{domain}/       ← 캐시 (discovery.md + discovery.json + cached_at.json)
3. .meta-pipe-status.json 업데이트  ← phase_a.status = "completed"
```

### Phase A 완료 후

사용자에게 조사 결과 요약을 보여주고 검토를 요청한다:

```
"## 도메인 조사 완료: {domain}

| 카테고리 | 품질 | 주요 발견 |
| --- | --- | --- |
| 핵심 용어 | {quality} | {summary} |
| 워크플로우 | {quality} | {summary} |
| 기술 스택 | {quality} | {summary} |
| 데이터 모델 | {quality} | {summary} |
| 리스크 | {quality} | {summary} |

조사 결과를 검토해 주세요. 보완이 필요한 부분이 있으면 말씀하세요.
문제없으면 파이프라인 설계(Phase B)로 진행합니다."
```

---

## Phase B: Design Pipeline (파이프라인 설계)

> **참조 문서**: `references/pipeline-design.md`를 로드하여 상세 가이드를 따른다.

### 개요

Phase A 조사 결과를 바탕으로 도메인에 최적화된 N단계 파이프라인을 설계한다.

### 설계 원칙

1. **도메인 맞춤**: 고정 N단계가 아니라 도메인에 따라 단계 수/내용이 달라진다
2. **Adaptive Depth**: 단순 도메인 3~5단계, 일반 6~8단계, 복잡 8~12단계
3. **approval_required**: 법적 리스크, 아키텍처 결정, 되돌리기 어려운 결정은 true
4. **bkit과 차별화**: bkit 9단계와 비교하여 불필요한 단계 제거, 도메인 고유 단계 추가

### 이중 형식 출력

반드시 두 가지 형식을 **동시에** 생성한다:

```
1. docs/pipeline.md    ← 사람이 읽는 마크다운
   - 각 단계: 목적, 할 일, 산출물, 완료 기준, 도메인 주의사항, approval_required
   - 파이프라인 요약표

2. docs/pipeline.json  ← 에이전트가 파싱하는 JSON
   - meta: domain, version, created_at
   - pipeline: steps[] with all fields
   - domain_knowledge: entities, platforms, tech_stack, legal_risks
```

### Phase B 완료 후

파이프라인 요약을 보여주고 승인을 요청한다:

```
"## 파이프라인 설계 완료: {domain} ({N}단계)

| Step | 이름 | 핵심 산출물 | approval_required |
| --- | --- | --- | --- |
| 1 | {name} | {output} | {true/false} |
| ... | ... | ... | ... |

approval_required 비율: {M}/{N} ({percent}%)
도메인 고유 단계: {list}

파이프라인을 검토해 주세요. 단계 추가/수정/삭제가 필요하면 말씀하세요.
승인하시면 Step 1부터 실행합니다."
```

---

## Phase C: Execute (단계별 실행)

> **참조 문서**: `references/execution.md`를 로드하여 상세 가이드를 따른다.

### 실행 플로우

```
FOR each step in pipeline.steps (순서대로):

  1. 단계 안내
     "## Step {N}/{total}: {name}"
     "**목적**: {purpose}"
     "**할 일**: {tasks}"
     "**주의사항**: {domain_warnings}"

  2. 산출물 생성
     - Phase A 조사 결과를 맥락으로 활용
     - domain_warnings 반영
     - 도메인 용어 사용 (Phase A 용어 사전 참조)
     - 불확실한 부분에 [검토 필요]
     - 출처 URL 포함
     - 파일 저장: docs/steps/step-{N}-{slug}.md

  3. approval_required 처리
     IF true:
       산출물을 보여주고 검토 요청
       "이 단계의 결과를 검토해 주세요. 수정이 필요하면 말씀하세요."
       승인 후 다음 단계로
     IF false:
       done_criteria 자체 검증
       자동으로 다음 단계 안내

  4. 상태 업데이트
     .meta-pipe-status.json 갱신
     실행 로그 기록
```

### 도메인 전문가 수준 유지

각 단계를 실행할 때 반드시:

- Phase A에서 수집한 **도메인 지식**을 적극 활용
- 해당 도메인의 **업계 표준 용어**를 사용
- **domain_warnings**에 명시된 주의사항을 산출물에 반영
- 일반적인 소프트웨어 개발 가이드가 아닌, **이 도메인에 특화된** 가이드를 제공

---

## Output Rules

### 언어

- 사용자 입력 언어를 따른다 (한국어 입력 → 한국어 출력)
- 기술 용어는 원어 유지 (WebSearch, JSON Schema 등)

### 출처

- 모든 WebSearch 결과에 출처 URL 포함
- 규제/법적 정보는 반드시 공식 출처
- 불확실한 정보: `[검토 필요]` 마킹

### 이중 형식

- 마크다운: 사람이 읽는 보고서/가이드
- JSON: 에이전트가 파싱하는 구조화 데이터
- Phase A, B 모두 이중 형식 출력

### 실행 로그

모든 실행의 입출력을 `meta-pipe-logs/{timestamp}.json`에 기록:

```json
{
  "session_id": "uuid",
  "domain": "string",
  "phases": { "A": {...}, "B": {...}, "C": {...} },
  "evaluation": { "websearch_quality": "1-5", "pipeline_domain_fit": "1-5" }
}
```

---

## Context Window Management

Phase A/B/C가 길어질 수 있으므로:

- Phase A 완료 → 결과를 파일로 저장, "docs/domain-discovery.md 참조" 지시
- Phase C 각 단계 → 현재 단계 + pipeline.json만 유지, 이전 산출물은 Read로 참조
- references/ 문서는 해당 Phase 진입 시에만 로드

---

## Error Handling

### WebSearch 결과 부족

```
1. 쿼리 재구성 (영어로 재시도, 키워드 변경)
2. WebFetch로 보완
3. 여전히 부족: "[검토 필요] 이 카테고리는 수동 조사가 필요합니다"
4. 나머지 카테고리로 진행 (부족한 부분 명시)
```

### 입력 구체화

```
너무 광범위: "어떤 종류의 {X}인가요?"
2회 구체화 후 불명확: 가장 가능성 높은 해석 + [검토 필요]
```

### 중단/재개

```
.meta-pipe-status.json으로 상태 추적
세션 종료 시 자동 저장
다음 세션에서 자동 복구 제안
```
