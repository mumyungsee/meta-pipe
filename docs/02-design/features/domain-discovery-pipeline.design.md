# meta-pipe 설계 문서

> **요약**: meta-pipe SKILL.md의 기술 설계. 3-Phase 실행 로직, 파일 구조, 데이터 스키마, 캐시/로그 시스템을 정의한다.
> **프로젝트**: meta-pipe **버전**: 0.1 **날짜**: 2026-03-24 **상태**: Draft
> **Plan 문서**: `docs/01-plan/features/domain-discovery-pipeline.plan.md` (v0.5)
> **PoC 결과**: `examples/card-news/` (Phase A/B 검증 완료)

---

## 1. 아키텍처 개요

### 1.1 전체 구조

```
사용자 입력: "X를 만들고 싶어"
     │
     ▼
┌─────────────────────────────────────────────┐
│  SKILL.md (컨트롤러)                          │
│  - 트리거 감지 + Phase 라우팅                  │
│  - 캐시 존재 여부 확인                         │
│  - 진행 상태 파일 로드/복구                     │
├─────────────────────────────────────────────┤
│  references/ (지연 로딩)                       │
│  ├── discovery.md       ← Phase A 실행 시 로드 │
│  ├── pipeline-design.md ← Phase B 실행 시 로드 │
│  └── execution.md       ← Phase C 실행 시 로드 │
├─────────────────────────────────────────────┤
│  런타임 산출물                                  │
│  ├── cache/{domain}/    ← 도메인 지식 캐시      │
│  ├── logs/              ← 실행 로그             │
│  └── {project}/         ← 파이프라인 + 산출물    │
└─────────────────────────────────────────────┘
```

### 1.2 AI-DLC 패턴 적용

| 패턴 | AI-DLC 원본 | meta-pipe 적용 |
| --- | --- | --- |
| 2-tier 규칙 | core-workflow + rule-details/ | SKILL.md + references/ |
| 지연 로딩 | "Load from X" 지시 | Phase 진입 시 참조 문서 로드 |
| Execute IF / Skip IF | 마크다운 조건문 | 캐시 유무, 도메인 복잡도 기반 분기 |
| Adaptive Depth | Minimal/Standard/Comprehensive | 도메인 복잡도에 따라 단계 수/깊이 조절 |
| State + Audit | aidlc-state.md + audit.md | .meta-pipe-status.json + logs/ |

---

## 2. 파일 구조

### 2.1 스킬 파일 구조

```
skills/meta-pipe/
├── SKILL.md                    # 메인 스킬 (엔트리포인트)
└── references/
    ├── discovery.md            # Phase A 상세 가이드
    ├── pipeline-design.md      # Phase B 상세 가이드
    └── execution.md            # Phase C 상세 가이드
```

### 2.2 런타임 산출물 구조

```
{working-directory}/
├── .meta-pipe-status.json      # 진행 상태 (중단/재개용)
├── meta-pipe-cache/
│   └── {domain-slug}/          # 도메인별 캐시
│       ├── discovery.md        # Phase A 조사 결과
│       ├── discovery.json      # Phase A 구조화 데이터
│       └── cached_at.json      # 캐시 메타데이터
├── meta-pipe-logs/
│   └── {timestamp}.json        # 실행 로그
└── docs/                       # 파이프라인 산출물
    ├── domain-discovery.md     # Phase A 보고서
    ├── pipeline.md             # Phase B 파이프라인 정의 (마크다운)
    ├── pipeline.json           # Phase B 파이프라인 정의 (JSON)
    └── steps/                  # Phase C 각 단계 산출물
        ├── step-1-{name}.md
        ├── step-2-{name}.md
        └── ...
```

---

## 3. SKILL.md 설계

### 3.1 frontmatter

```yaml
---
name: meta-pipe
description: 도메인 지식 없이 AI가 도메인을 조사하고 최적화된 개발 파이프라인을 동적으로 설계/실행
version: 1.0.0
triggers:
  - "만들고 싶어"
  - "프로젝트 시작"
  - "개발하고 싶어"
  - "파이프라인"
  - "도메인 조사"
  - "meta-pipe"
tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Glob
  - Grep
---
```

### 3.2 SKILL.md 본문 구조

```
1. 역할 정의
   - "너는 도메인 전문가 수준의 파이프라인 설계자"
   - 이중 사용자 대응 (사람/에이전트)

2. 진입 로직
   - 입력 분석: 도메인 추출 + 구체화 요청 판단
   - 캐시 확인: meta-pipe-cache/{domain-slug}/ 존재 여부
   - 상태 복구: .meta-pipe-status.json 존재 시 이어서 진행

3. Phase 라우팅
   - 신규: Phase A → B → C 순차
   - 캐시 있음: Phase A 스킵, B에서 캐시 활용
   - 중단 복구: 상태 파일의 current_phase/current_step에서 재개

4. Phase A 실행 지시
   - "Load references/discovery.md"
   - WebSearch 쿼리 패턴, WebFetch 보완, 캐시 저장

5. Phase B 실행 지시
   - "Load references/pipeline-design.md"
   - 파이프라인 설계, approval_required 판단, 이중 형식 출력

6. Phase C 실행 지시
   - "Load references/execution.md"
   - 단계별 순차 실행, 승인 요청, 산출물 생성

7. 출력 규칙
   - 이중 형식: 마크다운 + JSON 동시 출력
   - 출처 URL 필수, 불확실 정보에 [검토 필요]
   - 실행 로그 기록
```

---

## 4. Phase A: Discover (도메인 조사)

### 4.1 입력 → 출력

```
입력: 사용자 프로젝트 아이디어 (자유 텍스트)
출력:
  - docs/domain-discovery.md (마크다운 보고서)
  - meta-pipe-cache/{domain}/discovery.json (구조화 데이터)
```

### 4.2 WebSearch 쿼리 패턴

5개 카테고리 병렬 조사 (PoC에서 검증됨):

```
1. "{domain} 핵심 용어 표준 업계 용어"
2. "{domain} 개발 워크플로우 best practice 프로세스"
3. "{domain} 자동화 소프트웨어 기술 스택 오픈소스"
4. "{domain} 데이터 모델 엔티티 스키마"
5. "{domain} 실패 사례 주의사항 리스크"
```

### 4.3 WebFetch 보완 전략

WebSearch 결과 중 심층 분석이 필요한 URL을 선별하여 WebFetch:

```
보완 기준:
  - 학술 논문 / 기술 문서 → 데이터 모델, 아키텍처 보완
  - API 문서 → 기술 스택 구체화
  - 튜토리얼 / 구현 가이드 → 구현 패턴 보완

보완 수: 최대 3~5개 URL (컨텍스트 비용 고려)
```

### 4.4 조사 결과 구조화 스키마

```json
{
  "domain": "string",
  "investigated_at": "ISO8601",
  "categories": {
    "terminology": {
      "quality": "excellent|good|fair|poor",
      "terms": [
        { "term": "string", "term_en": "string", "description": "string" }
      ],
      "sources": ["url"]
    },
    "workflow": {
      "quality": "excellent|good|fair|poor",
      "standard_process": ["step description"],
      "sources": ["url"]
    },
    "tech_stack": {
      "quality": "excellent|good|fair|poor",
      "tools": [
        { "name": "string", "type": "SaaS|library|framework", "description": "string" }
      ],
      "recommended_approach": "string",
      "sources": ["url"]
    },
    "data_model": {
      "quality": "excellent|good|fair|poor",
      "entities": [
        { "name": "string", "fields": ["string"], "relationships": ["string"] }
      ],
      "derived": "boolean",
      "sources": ["url"]
    },
    "risks": {
      "quality": "excellent|good|fair|poor",
      "items": [
        { "risk": "string", "severity": "high|medium|low", "mitigation": "string" }
      ],
      "sources": ["url"]
    }
  },
  "webfetch_supplements": [
    { "url": "string", "reason": "string", "priority": "high|medium|low" }
  ]
}
```

### 4.5 도메인 캐시

```
meta-pipe-cache/{domain-slug}/
├── discovery.md          # 마크다운 보고서
├── discovery.json        # 구조화 데이터 (위 스키마)
└── cached_at.json        # { "cached_at": "ISO8601", "version": "1.0" }
```

캐시 활용 로직:

```
IF cache/{domain}/ 존재:
  - 캐시 날짜 확인
  - 30일 이내: "기존 조사 결과를 활용합니다. 보완이 필요하면 말씀하세요."
  - 30일 초과: "기존 조사가 {N}일 전입니다. 갱신하시겠습니까?"
  - 사용자 선택: 재사용 / 갱신 / 보완만
ELSE:
  - Phase A 전체 실행
```

---

## 5. Phase B: Design Pipeline (파이프라인 설계)

### 5.1 입력 → 출력

```
입력: Phase A 도메인 지식 보고서
출력:
  - docs/pipeline.md (마크다운)
  - docs/pipeline.json (구조화 JSON)
```

### 5.2 파이프라인 설계 로직

```
1. 도메인 지식에서 필수 단계 도출
   - 워크플로우 → 단계 후보 목록
   - 리스크 → 검증/준수 단계 추가
   - 데이터 모델 → 설계 단계 추가

2. bkit 9단계와 비교하여 차별화
   - 불필요한 단계 제거 (도메인에 맞지 않으면)
   - 도메인 고유 단계 추가

3. 단계 수 결정 (Adaptive Depth)
   - 단순 도메인 (CLI 도구 등): 3~5단계
   - 일반 도메인 (카드뉴스 등): 6~8단계
   - 복잡 도메인 (핀테크 등): 8~12단계

4. 각 단계에 상세 정보 부여
   - 목적, 할 일, 산출물, 완료 기준, 도메인 주의사항
   - approval_required 자동 판단 (5.3 참조)
   - 의존성 정의 (depends_on)
```

### 5.3 approval_required 자동 판단 휴리스틱

```
TRUE로 설정하는 조건 (하나라도 해당 시):
  - 법적/규제 리스크가 있는 단계
  - 전체 아키텍처에 영향을 미치는 설계 결정 (데이터 모델, 용어 정의)
  - 비용이 높은 되돌리기 어려운 결정
  - 콘텐츠 품질이 최종 결과물의 핵심인 경우

FALSE로 설정하는 조건:
  - 앞 단계에서 범위가 확정된 구현 세부사항
  - 테스트/검증 단계
  - 기술적 최적화 단계
```

### 5.4 파이프라인 JSON 스키마

```json
{
  "meta": {
    "domain": "string",
    "version": "semver",
    "created_at": "ISO8601",
    "generated_by": "meta-pipe Phase A+B",
    "input_prompt": "string"
  },
  "pipeline": {
    "name": "slug",
    "description": "string",
    "total_steps": "number",
    "approval_required_count": "number",
    "steps": [
      {
        "id": "step-{N}",
        "name": "string",
        "name_en": "string",
        "purpose": "string",
        "tasks": ["string"],
        "outputs": [
          { "file": "path", "format": "string", "description": "string" }
        ],
        "done_criteria": ["string"],
        "domain_warnings": ["string"],
        "approval_required": "boolean",
        "approval_reason": "string (nullable)",
        "depends_on": ["step-id"]
      }
    ]
  },
  "domain_knowledge": {
    "key_entities": ["string"],
    "supported_platforms": [{ "name": "string", "aspect_ratio": "string", "size": "string" }],
    "recommended_tech_stack": { "key": "value" },
    "legal_risks": ["string"],
    "safe_resources": { "key": ["string"] }
  }
}
```

---

## 6. Phase C: Execute (단계별 실행)

### 6.1 입력 → 출력

```
입력: pipeline.json (또는 pipeline.md)
출력: docs/steps/step-{N}-{name}.md (각 단계 산출물)
```

### 6.2 실행 플로우

```
FOR each step in pipeline.steps (순서대로):
  1. 현재 단계 안내
     - "## Step {N}: {name}"
     - 목적, 할 일, 산출물 목록 표시
     - domain_warnings 표시

  2. approval_required 확인
     IF true AND 사용자 모드:
       - 산출물 초안 생성
       - "이 단계의 결과를 검토해 주세요. 수정이 필요하면 말씀하세요."
       - 사용자 승인 대기
     IF true AND 에이전트 모드:
       - 산출물 생성
       - 승인 요청 파일 생성 (.approval-needed.md)
       - 다음 단계로 진행하지 않음
     IF false:
       - 산출물 생성
       - done_criteria 자체 검증
       - 자동으로 다음 단계 진행

  3. 산출물 저장
     - docs/steps/step-{N}-{name}.md
     - 상태 파일 업데이트

  4. 진행 상태 업데이트
     - .meta-pipe-status.json 갱신
     - 실행 로그 기록
```

### 6.3 도메인 전문가 수준 가이드

각 단계 실행 시 references/execution.md의 지침:

```
1. Phase A 조사 결과를 해당 단계에 맥락으로 활용
2. domain_warnings를 반드시 반영
3. 산출물에 도메인 용어 사용 (Phase A 용어 사전 참조)
4. 불확실한 부분에 [검토 필요] 마킹
5. 출처 URL 포함 (Phase A에서 수집된 출처)
```

---

## 7. 진행 상태 관리

### 7.1 상태 파일 스키마

```json
// .meta-pipe-status.json
{
  "project_id": "uuid",
  "domain": "string",
  "input_prompt": "string",
  "started_at": "ISO8601",
  "updated_at": "ISO8601",
  "current_phase": "A|B|C",
  "phase_a": {
    "status": "pending|in_progress|completed|skipped",
    "cache_used": "boolean",
    "completed_at": "ISO8601 (nullable)"
  },
  "phase_b": {
    "status": "pending|in_progress|completed",
    "total_steps": "number (nullable)",
    "completed_at": "ISO8601 (nullable)"
  },
  "phase_c": {
    "status": "pending|in_progress|completed",
    "current_step": "number",
    "total_steps": "number",
    "steps": [
      {
        "id": "step-{N}",
        "name": "string",
        "status": "pending|in_progress|completed|awaiting_approval",
        "approval_required": "boolean",
        "completed_at": "ISO8601 (nullable)"
      }
    ]
  }
}
```

### 7.2 중단/재개 로직

```
세션 시작 시:
  IF .meta-pipe-status.json 존재:
    - 상태 로드
    - "이전 작업이 있습니다: {domain} - Phase {X}, Step {N}"
    - "이어서 진행하시겠습니까?"
    - 선택: 이어서 / 처음부터 / 취소
```

---

## 8. 실행 로그

### 8.1 로그 파일 구조

```json
// meta-pipe-logs/{timestamp}.json
{
  "session_id": "uuid",
  "domain": "string",
  "input_prompt": "string",
  "started_at": "ISO8601",
  "completed_at": "ISO8601 (nullable)",
  "phases": {
    "A": {
      "duration_seconds": "number",
      "queries_count": "number",
      "webfetch_count": "number",
      "cache_hit": "boolean",
      "categories_quality": {
        "terminology": "excellent|good|fair|poor",
        "workflow": "excellent|good|fair|poor",
        "tech_stack": "excellent|good|fair|poor",
        "data_model": "excellent|good|fair|poor",
        "risks": "excellent|good|fair|poor"
      }
    },
    "B": {
      "duration_seconds": "number",
      "total_steps": "number",
      "approval_required_count": "number",
      "domain_unique_steps": ["string"],
      "removed_generic_steps": ["string"]
    },
    "C": {
      "duration_seconds": "number",
      "steps_completed": "number",
      "steps_total": "number",
      "approvals_requested": "number",
      "approvals_given": "number"
    }
  },
  "evaluation": {
    "websearch_quality": "number (1-5)",
    "pipeline_domain_fit": "number (1-5)",
    "expert_level": "number (1-5)"
  }
}
```

### 8.2 로그 활용 (v1.0)

- v1.0에서는 **기록만**. 분석/개선은 v2.0 범위
- 미래 자율 AI 에이전트가 로그를 분석하여:
  - WebSearch 쿼리 패턴 개선
  - approval_required 판단 정확도 향상
  - 도메인별 파이프라인 패턴 학습

---

## 9. references/ 상세 설계

### 9.1 discovery.md (Phase A 가이드)

```
내용:
  1. WebSearch 쿼리 생성 규칙
     - 5개 카테고리별 쿼리 템플릿
     - 도메인 키워드 추출 방법
     - 검색 언어 전략 (한/영 동시)

  2. 결과 평가 기준
     - 카테고리별 "우수/양호/미흡/부족" 판단 기준
     - 미흡 시 WebFetch 보완 대상 선정

  3. 구조화 규칙
     - discovery.json 스키마 준수
     - 출처 URL 필수
     - [검토 필요] 마킹 기준

  4. 캐시 저장 규칙
     - 캐시 디렉토리 생성
     - cached_at.json 기록
```

### 9.2 pipeline-design.md (Phase B 가이드)

```
내용:
  1. 단계 도출 알고리즘
     - 도메인 워크플로우 → 핵심 단계 추출
     - 도메인 리스크 → 검증/준수 단계 추가
     - bkit 9단계 비교 → 불필요 제거, 고유 추가

  2. approval_required 판단 규칙
     - 휴리스틱 (섹션 5.3)
     - 목표 비율: 30~50% (전체의)

  3. 이중 형식 출력 규칙
     - pipeline.md: 사람이 읽는 마크다운
     - pipeline.json: 에이전트가 파싱하는 JSON
     - 둘 다 항상 동시 생성

  4. Adaptive Depth 기준
     - 입력 복잡도에 따라 단계 수 조절
     - 도메인 규제 수준에 따라 깊이 조절
```

### 9.3 execution.md (Phase C 가이드)

```
내용:
  1. 단계 실행 프로토콜
     - 현재 단계 안내 형식
     - 산출물 생성 규칙
     - approval_required 처리 플로우

  2. 도메인 전문가 수준 유지 규칙
     - Phase A 지식 활용
     - domain_warnings 반영
     - 도메인 용어 사용

  3. 상태 관리 규칙
     - .meta-pipe-status.json 갱신 시점
     - 실행 로그 기록 시점

  4. 에이전트 모드 처리
     - approval_required=true 시 파일 기반 승인 요청
     - 자율 실행 가능 단계 연속 진행
```

---

## 10. 자동 호출 (Trigger) 설계

### 10.1 트리거 패턴

```yaml
triggers:
  # 직접 호출
  - "meta-pipe"
  - "파이프라인"
  - "도메인 조사"

  # 의도 감지
  - "만들고 싶어"
  - "개발하고 싶어"
  - "프로젝트 시작"
```

### 10.2 bkit과의 공존

```
사용자 입력 → 트리거 감지
  │
  ├── bkit 트리거에 해당 → bkit 실행
  │   (웹앱, 프론트엔드, Next.js 등 명시적 웹 개발)
  │
  ├── meta-pipe 트리거에 해당 → meta-pipe 실행
  │   (도메인 불명확, "X를 만들고 싶어" 패턴)
  │
  └── 도메인 조사 후 웹앱으로 판단 → bkit 추천
      ("이 프로젝트는 웹앱입니다. bkit 파이프라인을 사용하시겠습니까?")
```

---

## 11. 에러 처리

### 11.1 WebSearch 실패

```
WebSearch 결과 부족 시:
  1. 쿼리 재구성 (영어로 재시도, 키워드 변경)
  2. WebFetch로 보완 시도
  3. 여전히 부족하면: "[검토 필요] 이 카테고리는 수동 조사가 필요합니다"
  4. 나머지 카테고리로 파이프라인 설계 진행 (부족한 부분 표시)
```

### 11.2 컨텍스트 윈도우 관리

```
Phase A 완료 후:
  - 조사 결과를 파일로 저장
  - SKILL.md에서 "Phase A 결과는 docs/domain-discovery.md 참조" 지시
  - 전체 조사 결과를 컨텍스트에 유지하지 않음

Phase C 각 단계:
  - 현재 단계 + pipeline.json만 컨텍스트에 유지
  - 이전 단계 산출물은 필요 시 Read로 참조
```

### 11.3 입력 구체화

```
입력이 너무 광범위한 경우:
  - "앱 만들어줘" → "어떤 종류의 앱인가요? (예: 핀테크, 게임, 교육 등)"
  - "서비스" → "어떤 문제를 해결하는 서비스인가요?"
  - 2회 구체화 요청 후에도 불명확: 가장 가능성 높은 해석으로 진행 + [검토 필요]
```

---

## 12. v2.0 확장 포인트

v1.0에서는 구현하지 않지만, 확장을 고려한 설계:

### 12.1 Hooks (v2.0)

```
hooks:
  SessionStart:
    - .meta-pipe-status.json 로드
    - 진행 상태 컨텍스트 주입
  PreToolUse (Write/Edit):
    - 현재 단계의 산출물 경로인지 검증
    - 파이프라인 외 파일 쓰기 경고
  PostToolUse (Write):
    - done_criteria 자동 체크
    - 다음 단계 안내 주입
  Stop:
    - approval_required 단계에서 승인 없이 종료 방지
    - 실행 로그 최종 기록
```

### 12.2 메타-학습 (v2.0)

```
자율 AI 에이전트가 meta-pipe-logs/ 분석:
  - 도메인별 WebSearch 쿼리 성공률 → 쿼리 패턴 개선
  - approval_required 판단 vs 실제 수정 비율 → 판단 정확도 향상
  - 파이프라인 단계 패턴 → 도메인 유형별 기본 템플릿 생성
  - SKILL.md/references 자동 업데이트 PR 생성
```

---

## 13. 검증 계획

### 13.1 구현 후 검증 항목

| 검증 항목 | 방법 | 성공 기준 |
| --- | --- | --- |
| Phase A 조사 품질 | 5개 도메인 테스트 | 각 도메인 4/5개 카테고리 양호 이상 |
| Phase B 도메인 적합성 | bkit 9단계와 비교 | 최소 2개 도메인 고유 단계 존재 |
| Phase C 산출물 품질 | 전문가 리뷰 | "납득 가능" 수준 |
| 캐시 재사용 | 같은 도메인 2회 실행 | 2회차에서 WebSearch 스킵 |
| 중단/재개 | 세션 중간 종료 후 재개 | 이전 상태에서 정확히 재개 |
| 이중 형식 | JSON 파싱 검증 | 유효한 JSON, 스키마 준수 |
| 자동 호출 | 트리거 문구 입력 | meta-pipe 자동 활성화 |

### 13.2 테스트 도메인 (Plan 5.1)

```
1. 카드뉴스 자동화  → PoC 완료. SKILL.md 구현 후 재검증
2. 핀테크 송금 앱   → 규제 중심 파이프라인 생성 검증
3. 2D 인디 게임    → 게임 개발 파이프라인 생성 검증
4. CLI 도구        → 간결한 파이프라인 (3~5단계) 검증
5. 의료 예약 시스템 → HIPAA 포함 파이프라인 검증
```

---

## 버전 이력

| 버전 | 날짜 | 변경사항 | 작성자 |
| --- | --- | --- | --- |
| 0.1 | 2026-03-24 | 초안: 전체 설계 (아키텍처, 3-Phase, 스키마, 캐시, 로그, 트리거) | - |
