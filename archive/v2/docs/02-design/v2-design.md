# meta-pipe v2 Design Document

> **Summary**: 도메인 지식 없이 AI가 컨설팅 -> 조사 -> 파이프라인 설계 -> 세팅 -> 실행 -> 검수/개선까지 돌리는 메타 파이프라인
>
> **Project**: meta-pipe
> **Version**: 2.0
> **Author**: mumusee00
> **Date**: 2026-04-03
> **Status**: Draft
> **Planning Doc**: [v2-plan.md](../01-plan/v2-plan.md)
> **Design Decisions**: [v2-design-decisions.md](../00-ideation/2026-04-01-v2-design-decisions.md)

---

## Context Anchor

> Plan 1절, 11절에서 합성. Design -> Do 핸드오프 시 전략적 맥락 유지.

| Key | Value |
|-----|-------|
| **WHY** | v1은 사용자 맥락 부재, 도구 세팅 생략, 결과 검수 없음으로 "실행 불가능한 파이프라인"을 생성. 6단계 구조로 현실적 실행 + 품질 루프 확보 |
| **WHO** | 도메인 전문 지식이 없는 일반 사용자. AI가 컨설팅 + 조사를 대행 |
| **RISK** | 컨텍스트 윈도우 초과(높음), 컨설팅 과잉으로 사용자 이탈(높음), 서브에이전트 간 컨텍스트 손실(중간) |
| **SUCCESS** | (1) v1 대비 파이프라인 실행 성공률 향상 (2) Phase F 검수 통과율 70%+ (3) 2개 이상 도메인에서 end-to-end 완주 |
| **SCOPE** | Phase A~F 전체 설계. 구현은 Phase A부터 순차. 테스트 도메인 2개(유튜브 섬네일 + Light 레벨 1개) |

---

## 1. Overview

### 1.1 Design Goals

1. **컨텍스트 효율성**: Phase당 ~3000 토큰 예산으로 6단계를 안정적으로 실행
2. **도메인 적응성**: 고정 스키마 없이 어떤 도메인이든 파이프라인 생성 가능
3. **단계적 강등**: 실패 시 중단이 아닌 auto -> assist -> manual 강등으로 항상 진행
4. **세션 복원**: 중단된 파이프라인을 정확한 지점에서 재개
5. **bkit 통합**: 기존 PDCA, gap-detector, pdca-iterator 인프라 재활용

### 1.2 Design Principles

- **Phase 격리**: 각 Phase는 자기 reference만 로드. 이전 Phase는 summary로만 참조
- **summary 체인**: 모든 산출물에 summary 필드 의무화. 다음 Phase의 최소 컨텍스트
- **Adaptive Depth**: 도메인 복잡도에 따라 파이프라인 step 수 3~12단계 자동 조절 (아래 기준표 참조)
- **최소 필수 필드**: strict JSON Schema 대신 필수 필드 존재 여부만 검증

### 1.3 Adaptive Depth 결정 기준

Phase C에서 파이프라인 step 수를 결정할 때 다음 4가지 요인을 종합한다:

| 요인 | 3~5단계 (Light) | 6~8단계 (Standard) | 9~12단계 (Full) |
|------|:-:|:-:|:-:|
| 도메인 워크플로우 수 (B의 workflows) | 1~2개 | 3~5개 | 6개+ |
| required_tools 종류 수 | 0~1개 | 2~3개 | 4개+ |
| execution_mode 혼합도 | 전부 동일 | 2종 혼합 | 3종 혼합 |
| quality_expectation (A의 consult-result) | low/medium | medium/high | high |

요인이 서로 다른 레벨을 가리킬 경우, **가장 높은 레벨을 채택**한다. 예: 워크플로우 2개(Light)이지만 required_tools 4개(Full)이면 Full 기준으로 9~12단계.

---

## 2. Architecture

### 2.0 Architecture Selection

**Selected**: Option C (단일 SKILL + Phase별 references) — 결정 1에서 확정

**Rationale**: bkit의 development-pipeline과 동일 패턴. SKILL.md가 오케스트레이터, 각 Phase 로직은 references/에 위임하여 지연 로딩. Phase당 1개 reference만 로드하여 컨텍스트 예산 준수.

| Criteria | Option A: Monolithic | Option B: Phase 분리 | **Option C: SKILL + refs** |
|----------|:-:|:-:|:-:|
| **Approach** | 단일 SKILL.md | Phase별 별도 SKILL | SKILL 오케스트레이터 + refs |
| **파일 수** | 1 | 6+ | 8 |
| **컨텍스트** | ~12000 토큰 전체 로드 | 최소 (Phase별) | ~3000/Phase |
| **Phase 간 연결** | 내부 분기 | 외부 상태 전달 필요 | SKILL.md가 관리 |
| **유지보수** | 단일 파일 비대화 | 분산으로 추적 어려움 | Phase별 독립 수정 가능 |
| **Recommendation** | 프로토타입용 | 과도한 분리 | **Default choice** |

### 2.1 System Diagram

```
사용자 입력: "X를 만들고 싶어"
       |
       v
┌──────────────────────────────────────────────────────┐
│  SKILL.md (오케스트레이터, ~500 토큰)                    │
│  - Phase 전환 로직                                     │
│  - .meta-pipe-status.json 관리                        │
│  - 컨텍스트 로드 로직 (summary + reference)              │
│  - 세션 재개 로직                                      │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Phase A ──> Phase B ──> Phase C ──> Phase D ──> Phase E ──> Phase F
│  consult.md  discovery.md  pipeline-   setup.md  execution.md  evaluation.md
│                            design.md                              │
│                                                      │
│  각 Phase 실행 시:                                     │
│   1. references/{phase}.md 로드 (~2000 토큰)           │
│   2. 직전 산출물의 summary 로드 (~500 토큰)              │
│   3. 원본 입력 로드 (~200 토큰)                         │
│   = Phase당 ~3000 토큰                                │
└──────────────────────────────────────────────────────┘
       |
       v
산출물: test/{domain-slug}/pipeline/
상태: .meta-pipe-status.json
캐시: runtime/cache/{domain-slug}/
프로필: runtime/user-profile.json
로그: runtime/logs/
```

### 2.2 Data Flow

```
A (Consult)
  -> consult-result.json
     |-> B (Discover)     [goal, user_profile -> 조사 방향]
     |-> C (Design)       [available_tools, user_profile -> 도구/역량 제약]
     |-> F (Evaluate)     [eval_criteria -> 평가 기준]

B (Discover)
  -> discovery.json + discovery.md
     |-> C (Design)       [domain_knowledge -> step 도출]
     |-> E (Execute)      [summary + domain_warnings -> 에이전트 프롬프트]

C (Design Pipeline)
  -> pipeline.json + pipeline.md
     |-> D (Setup)        [setup_requirements -> 세팅 목록]
     |-> E (Execute)      [steps, execution -> 실행 계획]

D (Setup)
  -> setup-result.json
     |-> E (Execute)      [completed/skipped/failed -> 도구 사용 가능 여부]

E (Execute)
  -> step 산출물 + .meta-pipe-status.json
     |-> F (Evaluate)     [결과물]

F (Evaluate)
  -> evaluation-result.json
     |-> E (Execute)      [미달 step 재실행 지시]
```

### 2.3 Dependencies

| Component | Depends On | Purpose |
|-----------|-----------|---------|
| SKILL.md | .meta-pipe-status.json | 세션 재개 위치 판단 |
| SKILL.md | runtime/user-profile.json | 반복 인터뷰 최소화 |
| Phase B | runtime/cache/ | 캐시 히트 시 조사 건너뛰기 |
| Phase E | pipeline.json | step별 실행 계획 |
| Phase F | eval_criteria (from A) | 평가 기준 참조 |
| Phase F | bkit gap-detector, pdca-iterator | 기존 인프라 재활용 |

---

## 3. Phase 간 인터페이스 JSON (Data Model)

> 결정 5: 최소 필수 필드 + 확장 허용. strict JSON Schema 대신 필수 필드 존재 여부만 체크.

### 3.0 공통 헤더

모든 산출물 JSON은 다음 공통 필드를 포함한다:

```json
{
  "version": "2.0",
  "phase": "A",
  "created_at": "2026-04-01T10:00:00Z",
  "summary": "...(300자 이내, 다음 Phase가 최소한으로 알아야 할 것)",
  "domain_specific": {}
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| version | string | O | "2.0" 고정 |
| phase | string | O | "A"~"F" |
| created_at | ISO 8601 | O | 생성 시각 |
| summary | string | O | 300자 이내 요약. 다음 Phase의 최소 컨텍스트 (결정 7) |
| domain_specific | object | X | 도메인별 확장 필드 |

**검증**: Phase 전환 시 SKILL.md에서 필수 필드 존재 여부만 체크. 값의 형식은 검증하지 않음.

### 3.1 consult-result.json (Phase A 산출물)

**경로**: `test/{domain-slug}/pipeline/consult-result.json`

```json
{
  "version": "2.0",
  "phase": "A",
  "created_at": "2026-04-01T10:00:00Z",
  "summary": "유튜브 섬네일 전자동 생성. DALL-E + YouTube API 경로 선택. Standard 레벨.",

  "requirements": {
    "goal": "유튜브 섬네일 전자동 생성",
    "automation_level": "full",
    "target_user": "human",
    "quality_expectation": "high"
  },
  "user_profile": {
    "tools": ["dalle_api_key", "youtube_api_key"],
    "capabilities": "API 키 발급 경험 있음, Docker 모름",
    "willingness": "high",
    "budget": "월 $10~15"
  },
  "selected_path": {
    "id": "path-1-dalle-youtube-api",
    "description": "DALL-E API + YouTube API 세팅으로 전자동 고품질 섬네일 생성",
    "tradeoffs": "월 ~$15 비용 발생, API 키 2개 세팅 필요"
  },
  "eval_criteria": [
    { "type": "quantitative", "criterion": "텍스트 영역 30% 이상", "auto_checkable": true },
    { "type": "qualitative", "criterion": "밝고 클릭 유도하는 느낌", "auto_checkable": false }
  ],
  "complexity": "Standard"
}
```

**필수 필드**: requirements, user_profile, selected_path, eval_criteria, complexity

### 3.2 discovery.json (Phase B 산출물)

**경로**: `test/{domain-slug}/pipeline/discovery.json`

```json
{
  "version": "2.0",
  "phase": "B",
  "created_at": "2026-04-01T11:00:00Z",
  "summary": "유튜브 섬네일 5카테고리 조사 완료. DALL-E 3 + YouTube Data API v3 조합. 해상도 1280x720 필수.",

  "domain_knowledge": {
    "glossary": [
      { "term": "CTR", "definition": "Click-Through Rate, 썸네일 클릭률" }
    ],
    "workflows": [
      { "name": "표준 섬네일 제작", "steps": ["키워드 분석", "디자인 컨셉", "이미지 생성", "텍스트 오버레이", "업로드"] }
    ],
    "tech_stack": [
      { "tool": "DALL-E 3", "purpose": "이미지 생성", "cost": "$0.04/image" }
    ],
    "data_model": [
      { "entity": "Thumbnail", "fields": ["title", "image_url", "resolution", "channel_id"] }
    ],
    "risks": [
      { "risk": "YouTube 커뮤니티 가이드라인 위반", "severity": "high", "mitigation": "정책 준수 체크 step 추가" }
    ]
  }
}
```

**필수 필드**: domain_knowledge (하위 5카테고리: glossary, workflows, tech_stack, data_model, risks)

**참고**: `discovery.md`도 동시 생성 (사람용 마크다운 보고서). JSON과 동일 내용.

### 3.3 pipeline.json (Phase C 산출물)

**경로**: `test/{domain-slug}/pipeline/pipeline.json`

```json
{
  "version": "2.0",
  "phase": "C",
  "created_at": "2026-04-01T12:00:00Z",
  "summary": "6단계 파이프라인 설계. step 1~2 assist, 3~4 auto, 5 assist, 6 auto.",

  "meta": {
    "domain": "유튜브 섬네일 자동화",
    "domain_slug": "youtube-thumbnail",
    "total_steps": 6,
    "complexity": "Standard"
  },
  "steps": [
    {
      "id": "step-1",
      "name": "채널 브랜드 & 용어 정의",
      "purpose": "채널 고유 스타일과 용어 확립",
      "tasks": ["채널 분석", "브랜드 키워드 정의", "톤앤매너 결정"],
      "done_criteria": "브랜드 가이드 문서 생성",
      "execution_mode": "assist",
      "required_tools": [],
      "domain_warnings": ["채널이 없으면 신규 생성 필요"],
      "approval_required": true,
      "depends_on": [],
      "execution": {
        "pattern": "pipeline",
        "agent_type": "conversational",
        "delegation": "Task"
      }
    }
  ],
  "setup_requirements": [
    {
      "tool": "dalle_api_key",
      "reason": "이미지 생성용",
      "setup_guide": "https://platform.openai.com/api-keys 에서 발급"
    }
  ]
}
```

**필수 필드**: meta, steps[] (각 step: id, name, execution_mode, required_tools), setup_requirements[]

**Optional 필드**: steps[].execution — Phase C가 에이전트 할당을 확정할 수 있으면 포함. 없으면 Phase E의 references/execution.md가 런타임에 결정 (fallback).

| execution 필드 | 설명 | 값 예시 |
|---------------|------|--------|
| pattern | Harness 6패턴 중 하나 | pipeline, fan-out, expert-pool, producer-reviewer, supervisor, hierarchical |
| agent_type | 에이전트 유형 | tool-caller, conversational, researcher |
| delegation | bkit 호출 방식 | Task (bkit Task()), Agent (Claude Agent()) |

### 3.4 setup-result.json (Phase D 산출물)

**경로**: `test/{domain-slug}/pipeline/setup-result.json`

```json
{
  "version": "2.0",
  "phase": "D",
  "created_at": "2026-04-01T13:00:00Z",
  "summary": "DALL-E API 키 세팅 완료. YouTube API MCP 설정 완료. 전체 도구 사용 가능.",

  "completed": [
    { "tool": "dalle_api_key", "method": "manual", "verified": true }
  ],
  "skipped": [],
  "failed": []
}
```

**필수 필드**: completed[], skipped[], failed[]

**참고**: complexity가 Light이면 Phase D 자체가 생략되며, 이 파일은 생성되지 않는다. Phase E는 setup-result.json 부재 시 "모든 도구 사용 가능"으로 간주.

### 3.5 evaluation-result.json (Phase F 산출물)

**경로**: `test/{domain-slug}/pipeline/evaluation-result.json`

```json
{
  "version": "2.0",
  "phase": "F",
  "created_at": "2026-04-01T15:00:00Z",
  "summary": "5/6 기준 통과. '텍스트 영역' 기준 미달로 step-3 1회 재실행 후 통과.",

  "criteria_results": [
    {
      "criterion": "텍스트 영역 30% 이상",
      "type": "quantitative",
      "result": "pass",
      "score": 35,
      "note": "1차 25% -> 재실행 후 35%"
    }
  ],
  "overall_pass": true,
  "improvement_log": [
    {
      "iteration": 1,
      "step_id": "step-3",
      "change": "텍스트 영역 비율 증가 프롬프트 조정",
      "result": "25% -> 35%"
    }
  ]
}
```

**필수 필드**: criteria_results[], overall_pass, improvement_log[]

---

## 4. 상태 관리

> 결정 2: Phase E만 step 단위 재개, 나머지(A~D, F)는 Phase 단위 재개.

### 4.1 .meta-pipe-status.json 스키마

```json
{
  "session_id": "yt-thumb-2026-03-25",
  "domain": "유튜브 섬네일 자동화",
  "domain_slug": "youtube-thumbnail",
  "input_prompt": "유튜브 섬네일 자동화 워크플로우를 만들고 싶어",
  "complexity": "Standard",
  "current_phase": "E",
  "started_at": "2026-03-25T10:00:00Z",
  "updated_at": "2026-03-27T15:00:00Z",
  "phases": {
    "A": { "status": "completed", "completed_at": "2026-03-25T10:30:00Z" },
    "B": { "status": "completed", "completed_at": "2026-03-25T11:00:00Z" },
    "C": { "status": "completed", "completed_at": "2026-03-25T12:00:00Z" },
    "D": { "status": "skipped", "reason": "Standard 레벨 - 사용자가 직접 완료" },
    "E": {
      "status": "in_progress",
      "current_step": "step-3",
      "steps": [
        { "id": "step-1", "status": "completed", "execution_mode": "assist", "completed_at": "..." },
        { "id": "step-2", "status": "completed", "execution_mode": "assist", "completed_at": "..." },
        { "id": "step-3", "status": "in_progress", "execution_mode": "auto" }
      ]
    },
    "F": { "status": "pending" }
  }
}
```

### 4.2 세션 재개 로직

```
세션 시작
  |
  v
.meta-pipe-status.json 존재?
  |
  ├─ No  -> 새 세션 시작 (Phase A부터)
  |
  ├─ Yes -> current_phase 읽기
  |          |
  |          ├─ Phase A~D, F -> 해당 Phase 처음부터 재실행
  |          |                   (대화형/단발성이므로 중간 재개 불필요)
  |          |
  |          └─ Phase E -> current_step 읽기
  |                        -> 해당 step부터 재개
  |                        -> 완료된 step은 건너뛰기
  |
  v
사용자에게 재개 여부 확인
  "이전 세션 '{domain}'이 {current_phase}에서 중단되었습니다. 이어서 진행할까요?"
```

### 4.3 상태 전이 규칙

| From | To | 조건 | 업데이트 |
|------|------|------|---------|
| pending | in_progress | Phase 시작 | current_phase, updated_at |
| in_progress | completed | Phase 완료 | phases.{X}.completed_at |
| in_progress | skipped | Phase D Light 레벨 | phases.D.reason |
| completed | - | 되돌리기 없음 | - |
| Phase F completed | (종료) | overall_pass == true | session 종료 |
| Phase F completed | Phase E | 재실행 지시 | 해당 step만 재개 |

---

## 5. 캐시 시스템

> 결정 3: TTL 없음, 명시적 무효화만. consult_path_id로 경로별 캐시 분리.

### 5.1 캐시 구조

```
runtime/cache/
  └── {domain-slug}/
      ├── cached_at.json      # 캐시 메타데이터
      ├── discovery.json      # Phase B 캐시된 결과
      └── discovery.md        # Phase B 캐시된 보고서
```

### 5.2 cached_at.json

```json
{
  "cached_at": "2026-03-25T11:00:00Z",
  "consult_path_id": "path-1-dalle-youtube-api",
  "domain": "유튜브 섬네일 자동화"
}
```

### 5.3 캐시 히트/미스 로직

```
Phase B 시작
  |
  v
runtime/cache/{domain-slug}/ 존재?
  |
  ├─ No  -> 캐시 미스 -> B1~B3 정상 실행 -> 캐시 저장
  |
  ├─ Yes -> cached_at.json 읽기
  |          |
  |          ├─ consult_path_id 일치? (Phase A에서 선택한 경로와 비교)
  |          |   |
  |          |   ├─ Yes -> 캐시 히트!
  |          |   |         "이전 조사 결과가 있습니다. 재사용할까요?"
  |          |   |         -> Yes: Phase B 건너뛰고 C로
  |          |   |         -> No:  B1~B3 재실행 -> 캐시 덮어쓰기
  |          |   |
  |          |   └─ No  -> 경로 변경 -> "조사 방향이 달라졌으므로 재조사합니다"
  |          |              B1~B3 재실행 -> 캐시 덮어쓰기
  |
  v
--refresh 플래그 사용 시: 캐시 무시하고 항상 재조사
```

### 5.4 캐시 대상

| 대상 | 캐시 여부 | 이유 |
|------|:---------:|------|
| Phase A (Consult) | X | 대화형. 매번 달라짐 |
| Phase B (Discover) | **O** | 도메인 지식은 재사용 가능 |
| Phase C~F | X | B 결과에 의존하므로 캐시 불가 |
| user-profile.json | (별도 관리) | 세션 간 영속. 캐시가 아닌 프로필 |

---

## 6. 사용자 프로필

> 결정 4: JSON 1파일 통합. description 필드로 LLM 친화성 확보.

### 6.1 runtime/user-profile.json 스키마

```json
{
  "updated_at": "2026-04-01",
  "capabilities": {
    "api_setup": true,
    "docker": false,
    "ci_cd": false,
    "description": "API 키 발급 경험 있음, 인프라 경험 없음"
  },
  "tools": {
    "owned": ["dalle_api_key", "youtube_api_key"],
    "familiar": ["canva", "figma"],
    "description": "이미지 생성 API 보유, 디자인 툴 사용 가능"
  },
  "preferences": {
    "execution_preference": "local_first",
    "cost_tolerance": "low",
    "automation_preference": "semi",
    "description": "로컬 우선, 비용 최소화, 반자동 선호"
  }
}
```

### 6.2 갱신 로직 (Phase A2)

```
Phase A2 시작
  |
  v
runtime/user-profile.json 존재?
  |
  ├─ No  -> 전체 인터뷰 (역량, 도구, 선호도)
  |         -> 프로필 생성 + 저장
  |
  ├─ Yes -> 프로필 로드 + 요약 표시
  |         "이전 프로필: {description들}. 변경된 것 있나요?"
  |         |
  |         ├─ 변경 없음 -> 그대로 사용
  |         └─ 변경 있음 -> 변경분만 merge -> updated_at 갱신
  |
  v
consult-result.json의 user_profile에 반영
```

### 6.3 gitignore 처리

`runtime/user-profile.json`은 개인 정보이므로 `.gitignore`에 추가:

```
runtime/user-profile.json
runtime/logs/
```

---

## 7. 컨텍스트 관리

> 결정 7: Phase별 격리 + summary 체인. Phase당 ~3000 토큰 예산.

### 7.1 Phase별 컨텍스트 로드 전략

| Phase | 로드 대상 | 예상 토큰 |
|-------|----------|:---------:|
| A | references/consult.md + 원본 입력 | ~2200 |
| B | references/discovery.md + A의 summary | ~2500 |
| C | references/pipeline-design.md + B의 summary + A의 summary (목표/역량) | ~3000 |
| D | references/setup.md + C의 setup_requirements | ~2500 |
| E | references/execution.md + C의 해당 step JSON + B의 domain_warnings | ~2500 |
| F | references/evaluation.md + A의 eval_criteria + E의 결과물 경로 | ~2800 |

### 7.2 references 매핑

```
Phase A -> references/consult.md          (~2000 토큰)
Phase B -> references/discovery.md        (~2000 토큰)
Phase C -> references/pipeline-design.md  (~2000 토큰, Harness 6패턴 포함)
Phase D -> references/setup.md            (~1500 토큰)
Phase E -> references/execution.md        (~1500 토큰)
Phase F -> references/evaluation.md       (~1500 토큰)
```

### 7.3 summary 체인 메커니즘

```
Phase A 실행
  -> consult-result.json.summary 생성
     "유튜브 섬네일 전자동 생성. DALL-E + YouTube API. Standard 레벨."

Phase B 시작 시 로드:
  [references/discovery.md] + [A.summary] + [원본 입력]

Phase B 실행
  -> discovery.json.summary 생성
     "유튜브 섬네일 5카테고리 조사 완료. DALL-E 3 + YouTube Data API v3."

Phase C 시작 시 로드:
  [references/pipeline-design.md] + [B.summary] + [A.summary 중 목표/역량 부분]
  (A 전체 JSON이 아닌 summary만 로드하여 토큰 절약)
```

### 7.4 Phase E 특수 사항

Phase E는 step별로 에이전트를 실행하므로 추가 최적화:

- pipeline.json **전체**가 아니라 **해당 step의 JSON 블록만** 추출하여 프롬프트에 포함
- discovery.json의 **summary** + 해당 step의 **domain_warnings[]**만 포함
- 각 step 에이전트 프롬프트 = references/execution.md + step JSON + domain_warnings + 원본 입력

---

## 8. 에러 처리

> 결정 6: auto -> assist -> manual 강등 체인. 중단은 A~C 치명적 실패 시만.

### 8.1 Phase별 에러 전략

| Phase | 에러 유형 | 전략 |
|-------|-----------|------|
| A (Consult) | 사용자 응답 부족 | 최대 2회 재질문, 이후 기본값으로 진행 |
| B (Discover) | WebSearch 실패 | 재시도 1회 -> 캐시 fallback -> manual 강등 (사용자에게 직접 정보 요청) |
| C (Design) | Step 설계 실패 | 발생 가능성 낮음 (LLM 작업). 실패 시 사용자에게 보고 |
| D (Setup) | 도구 세팅 실패 | auto 세팅 시도 -> 실패 시 수동 가이드 (assist/manual 강등) |
| E (Execute) | step 실패 | **강등 체인**: auto -> assist -> manual (아래 상세) |
| F (Evaluate) | 개선 루프 한도 초과 | 3회 루프 후 미달 -> 해당 step을 manual로 강등, 사용자 판단 위임 |

### 8.2 Phase E 강등 체인 상세

```
step 실행 (execution_mode에 따라)
  |
  ├─ auto 모드:
  |    실행 -> 실패
  |    -> 재시도 1회
  |    -> 재실패 -> assist로 강등
  |       "자동 실행이 실패했습니다. AI가 초안을 만들고 검수해주시겠어요?"
  |
  ├─ assist 모드:
  |    초안 생성 -> 사용자 검수 -> 수정 요청
  |    -> 재시도 1회
  |    -> 재실패 -> manual로 강등
  |       "AI 초안도 부족합니다. 가이드를 제공하니 직접 실행해주세요."
  |
  └─ manual 모드:
       가이드 제공 -> 사용자 실행 -> 완료 확인
       -> 실패: 가이드 재제공 (최종 단계이므로 더 이상 강등 없음)
```

### 8.3 강등 이력 추적

강등 발생 시 `.meta-pipe-status.json`의 해당 step에 기록:

```json
{
  "id": "step-3",
  "status": "in_progress",
  "execution_mode": "assist",
  "original_mode": "auto",
  "degradation_reason": "DALL-E API rate limit exceeded"
}
```

### 8.4 전체 파이프라인 중단 조건

| Phase | 중단 여부 | 이유 |
|-------|:---------:|------|
| A~C | 중단 가능 | 치명적 실패 시 (예: 도메인 조사 완전 불가) |
| D | 중단 안 함 | 도구 세팅 실패 -> manual 가이드로 우회 |
| E | 중단 안 함 | 강등 체인으로 항상 진행 가능 |
| F | 중단 안 함 | 3회 루프 후 사용자 판단 위임 |

### 8.5 Phase F와 bkit 연동 범위

bkit 도구(gap-detector, pdca-iterator, report-generator)와 Phase F의 역할은 **명확히 구분**한다:

| 대상 | 도구 | 범위 |
|------|------|------|
| **meta-pipe 본체** (docs/ 하위) | bkit gap-detector, pdca-iterator | "Design 문서 vs 구현 코드" 검증. meta-pipe 자체의 PDCA |
| **meta-pipe가 생성한 파이프라인** (test/ 하위) | Phase F evaluation.md 자체 로직 | "eval_criteria vs 산출물" 검수. 도메인별 평가 기준은 bkit이 알 수 없음 |

Phase F는 자체 evaluation.md 로직으로 검수/개선 루프를 돌며, bkit 도구를 **직접 호출하지 않는다**. bkit 도구는 meta-pipe 스킬 자체를 개선할 때만 사용한다.

### 8.6 실행 모드 업그레이드 (manual -> assist -> auto)

> 강등(8.2절)이 실패 대응이라면, 업그레이드는 **사용자 성장 반영**이다. 반복할수록 자동화 수준이 올라간다.

#### 업그레이드 설계 원칙

| 항목 | 결정 |
|------|------|
| 업그레이드 단위 | **step별** (강등과 동일 단위) |
| 트리거 시점 | **Phase C** (파이프라인 설계 시 이전 실행 이력 참조) |
| 업그레이드 근거 | **실행 이력 + 프로필 변경** 둘 다 |
| 사용자 확인 | **확인 후 업그레이드** (강등은 알림, 업그레이드는 제안) |

#### 업그레이드 플로우

```
Phase C: 파이프라인 설계 시
  |
  v
동일/유사 도메인의 이전 실행 이력 존재?
  |
  ├─ No  -> 기본 execution_mode 결정 (기존 로직)
  |
  ├─ Yes -> 이전 실행의 step별 결과 분석
  |          |
  |          ├─ 이전 manual step이 성공 완료됨?
  |          |   -> assist 업그레이드 제안
  |          |      "이전에 '{step_name}'을 직접 성공하셨습니다. 반자동으로 해볼까요?"
  |          |
  |          ├─ 이전 assist step이 수정 없이 승인됨?
  |          |   -> auto 업그레이드 제안
  |          |      "이전에 '{step_name}' AI 초안을 그대로 승인하셨습니다. 자동으로 할까요?"
  |          |
  |          └─ user-profile.json capabilities 변경됨?
  |              -> 관련 step 업그레이드 후보 추가
  |              예: docker: false -> true → setup step을 manual -> auto 제안
  |
  v
사용자 승인 -> pipeline.json의 해당 step execution_mode 업그레이드
사용자 거부 -> 이전과 동일한 execution_mode 유지
```

#### execution_history (user-profile.json 확장)

업그레이드 판단을 위해 `user-profile.json`에 실행 이력을 축적한다:

```json
{
  "updated_at": "2026-04-01",
  "capabilities": { ... },
  "tools": { ... },
  "preferences": { ... },
  "execution_history": [
    {
      "domain_slug": "youtube-thumbnail",
      "completed_at": "2026-04-01",
      "steps": [
        { "id": "step-1", "original_mode": "manual", "final_mode": "manual", "success": true },
        { "id": "step-3", "original_mode": "auto", "final_mode": "assist", "success": true, "degraded": true }
      ]
    }
  ]
}
```

| 필드 | 설명 |
|------|------|
| original_mode | Phase C가 설계한 최초 실행 모드 |
| final_mode | 실제 실행된 모드 (강등 반영) |
| success | step 완료 여부 |
| degraded | 강등 발생 여부 |

**업그레이드 규칙**:
- `success: true` + `final_mode == original_mode` (강등 없이 성공) -> 한 단계 업그레이드 후보
- `success: true` + `degraded: true` (강등 후 성공) -> 업그레이드하지 않음 (강등이 필요했으므로)
- 동일 도메인 2회 이상 성공 시에만 업그레이드 제안 (1회 성공은 우연일 수 있음)

---

## 9. 사용자 인터랙션 포인트

> meta-pipe는 UI가 없으므로, 사용자와의 인터랙션은 CLI 대화로 이루어진다.

### 9.1 Phase별 인터랙션

| Phase | 인터랙션 | 모드 |
|-------|----------|------|
| A1 | 요구사항 질문 (최대 2회) | 대화 |
| A2 | 프로필 확인/갱신 | 대화 |
| A4 | 경로 선택지 제안 -> 사용자 선택 | 대화 |
| A5 | 평가 기준 확정 | 대화 |
| B | (auto) 진행 중 알림만 | 알림 |
| C | 파이프라인 설계 결과 확인 | 대화 |
| D | 세팅 가이드 / 완료 확인 | 대화 |
| E (assist) | AI 초안 -> 사용자 검수 -> 승인 | 대화 |
| E (manual) | 가이드 제공 -> 완료 확인 | 대화 |
| E (auto) | 진행 중 알림만 | 알림 |
| F (정량적) | (auto) 결과 보고 | 알림 |
| F (정성적) | 사용자 검수 요청 | 대화 |

### 9.2 승인 필요 포인트

pipeline.json의 `approval_required: true`인 step에서만 사용자 승인을 요구한다. 자동으로 결정되는 기준:

- `execution_mode: "assist"` -> approval_required: true
- `execution_mode: "manual"` -> approval_required: true (완료 확인)
- `execution_mode: "auto"` -> approval_required: false (기본)

---

## 10. 보안 고려사항

meta-pipe는 웹 서비스가 아니므로 일반적인 웹 보안(XSS, CSRF 등)은 해당 없음. 주요 고려사항:

- [ ] API 키 관리: `runtime/user-profile.json`에 API 키를 직접 저장하지 않음. 환경변수 또는 MCP 설정 참조만
- [ ] user-profile.json을 `.gitignore`에 추가하여 개인 정보 유출 방지
- [ ] runtime/logs/를 `.gitignore`에 추가
- [ ] Phase E에서 외부 API 호출 시 사용자 확인 (비용 발생 가능)

---

## 11. 테스트 계획

### 11.1 테스트 도메인

| 도메인 | 레벨 | 목적 | v1 비교 |
|--------|------|------|---------|
| 유튜브 섬네일 | Standard | Phase A~F 전체 검증 + v1 비교 | O |
| 블로그 글쓰기 | Light | Phase D 생략 검증 + Consult 효과 검증 | 신규 |

### 11.2 검증 시나리오

| # | 시나리오 | 검증 대상 | 성공 기준 |
|---|---------|----------|----------|
| 1 | 유튜브 섬네일 end-to-end | Phase A~F 전체 | F에서 overall_pass: true |
| 2 | 블로그 글쓰기 end-to-end | Light 레벨 + Phase D 생략 | Phase D 자동 건너뛰기 + F 통과 |
| 3 | 세션 중단 + 재개 | 상태 관리 | Phase E step-3에서 중단 후 재개 시 step-3부터 재실행 |
| 4 | 캐시 히트 | 캐시 시스템 | 동일 경로 재실행 시 Phase B 건너뛰기 |
| 5 | 캐시 미스 (경로 변경) | 캐시 무효화 | 다른 경로 선택 시 재조사 |
| 6 | 강등 체인 | 에러 처리 | auto -> assist 강등 후 정상 진행 |
| 7 | 프로필 갱신 | 사용자 프로필 | 2회차 실행 시 프로필 로드 + 변경분만 갱신 |
| 8 | 업그레이드 제안 | 실행 모드 업그레이드 | 2회차 실행 시 성공 이력 기반 upgrade 제안 |

### 11.3 Skill Evals 도입 (Module 7)

Module 7(테스트 + 개선) 단계에서 Claude Code의 **Skill Evals** 프레임워크를 도입하여 회귀 테스트를 자동화한다.

**도입 시기**: Module 1~6 구현 완료 후, end-to-end 테스트 시점

**평가 세트 구성**:

| Eval | 입력 | 기대 출력 | 검증 대상 |
|------|------|----------|----------|
| consult-basic | "유튜브 섬네일 만들고 싶어" | consult-result.json 필수 필드 존재 | Phase A |
| discovery-cache | 동일 도메인 2회차 실행 | Phase B 캐시 히트 + 건너뛰기 | Phase B + 캐시 |
| pipeline-adaptive | Light 도메인 입력 | steps 3~5개 + Phase D 생략 | Phase C Adaptive Depth |
| degradation-chain | auto step 강제 실패 | assist로 강등 + 정상 진행 | Phase E 에러 처리 |
| upgrade-suggest | 2회차 + 이전 manual 성공 이력 | assist 업그레이드 제안 | 실행 모드 업그레이드 |

**bkit 통합 시**: `evals/` 디렉토리에 meta-pipe 평가 세트를 등록하여 스킬 변경 시 자동 회귀 검증.

### 11.4 v1 vs v2 비교 포인트 (유튜브 섬네일)

| 항목 | v1 | v2 기대 |
|------|------|--------|
| 사용자 맥락 반영 | 없음 | Phase A에서 역량/예산 반영 |
| 도구 세팅 | 암묵적 (사용자 알아서) | Phase D에서 안내/실행 |
| 결과 검수 | 없음 | Phase F 자동/수동 검수 |
| 실행 실패 시 | 중단 | 강등 체인으로 계속 |
| 재실행 시 조사 | 매번 전체 조사 | 캐시 히트 시 건너뛰기 |

---

## 12. 파일 구조 + Implementation Guide

### 12.1 skills/meta-pipe/ 구조

```
skills/meta-pipe/
├── SKILL.md                        # 오케스트레이터 (~500 토큰)
│   - Phase 전환 로직
│   - 상태 관리 (.meta-pipe-status.json)
│   - 컨텍스트 로드 로직
│   - 세션 재개 로직
│   - --refresh 플래그 처리
│
└── references/
    ├── consult.md                  # Phase A 로직 + 인터뷰 가이드 (~2000 토큰)
    ├── discovery.md                # Phase B 로직 + 5카테고리 조사 방법 (~2000 토큰)
    ├── pipeline-design.md          # Phase C 로직 + Harness 6패턴 (~2000 토큰)
    ├── setup.md                    # Phase D 로직 + 도구별 세팅 가이드 (~1500 토큰)
    ├── execution.md                # Phase E 로직 + 에이전트 실행 가이드 (~1500 토큰)
    └── evaluation.md               # Phase F 로직 + 평가/개선 가이드 (~1500 토큰)
```

### 12.2 런타임 파일 구조

```
meta-pipe/
├── .meta-pipe-status.json          # 실행 상태 추적
├── runtime/
│   ├── user-profile.json           # 사용자 프로필 (gitignore)
│   ├── cache/
│   │   └── {domain-slug}/
│   │       ├── cached_at.json
│   │       ├── discovery.json
│   │       └── discovery.md
│   └── logs/
│       └── {timestamp}.json        # 실행 로그 (gitignore)
└── test/
    └── {domain-slug}/
        ├── pipeline/
        │   ├── consult-result.json
        │   ├── discovery.json
        │   ├── discovery.md
        │   ├── pipeline.json
        │   ├── pipeline.md
        │   ├── setup-result.json
        │   ├── evaluation-result.json
        │   ├── steps/              # 각 step 산출물
        │   └── output/             # 최종 결과물
        └── docs/                   # PDCA 문서 (테스트별)
```

### 12.3 구현 순서 (Plan 7절 기반)

| 순서 | 작업 | 산출물 | 의존성 |
|:----:|------|--------|--------|
| 1 | SKILL.md 기본 구조 | skills/meta-pipe/SKILL.md | 이 Design 문서 |
| 2 | Phase A 구현 | references/consult.md | SKILL.md |
| 3 | Phase B 구현 | references/discovery.md | Phase A |
| 4 | Phase C 구현 | references/pipeline-design.md | Phase B |
| 5 | Phase D 구현 | references/setup.md | Phase C |
| 6 | Phase E 구현 | references/execution.md | Phase D |
| 7 | Phase F 구현 | references/evaluation.md | Phase E |
| 8 | 테스트 도메인 1 (유튜브 섬네일) | end-to-end 검증 | 전체 |
| 9 | 테스트 도메인 2 (블로그 글쓰기) | Light 레벨 검증 | 전체 |
| 10 | Gap Analysis + 개선 | 설계 대비 갭 분석 | 테스트 |

### 12.4 Session Guide

> 구현 시 `/pdca do v2-design --scope module-N`으로 세션 분리 가능.

| Module | Scope Key | Description | Estimated Turns |
|--------|-----------|-------------|:---------------:|
| SKILL.md 기본 구조 | `module-1` | 오케스트레이터, 상태 관리, 세션 재개 | 30-40 |
| Phase A (Consult) | `module-2` | 요구사항 수집, 프로필, Feasibility Research, 경로 제안 | 40-50 |
| Phase B (Discover) | `module-3` | 5카테고리 조사, 캐시 연동, 품질 평가 | 30-40 |
| Phase C (Design Pipeline) | `module-4` | Step 도출, 실행 모드 태깅, 도구 매핑, **업그레이드 로직** | 30-40 |
| Phase D+E (Setup+Execute) | `module-5` | 도구 세팅, 에이전트 실행, 강등 체인 | 50-60 |
| Phase F (Evaluate) | `module-6` | 검수, 개선 루프, **execution_history 기록** | 30-40 |
| 테스트 + 개선 | `module-7` | 2개 도메인 end-to-end + Gap Analysis + **Skill Evals** | 40-50 |

#### Recommended Session Plan

| Session | Phase | Scope | Turns |
|---------|-------|-------|:-----:|
| Session 1 | Do | `--scope module-1` (SKILL.md 기본) | 30-40 |
| Session 2 | Do | `--scope module-2` (Phase A) | 40-50 |
| Session 3 | Do | `--scope module-3,module-4` (Phase B+C) | 50-60 |
| Session 4 | Do | `--scope module-5` (Phase D+E) | 50-60 |
| Session 5 | Do | `--scope module-6` (Phase F) | 30-40 |
| Session 6 | Check | `--scope module-7` (테스트 + 개선) | 40-50 |
| Session 7 | Report | 전체 | 20-30 |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-03 | Initial draft — 7개 결정 사항 반영 | mumusee00 |
| 0.2 | 2026-04-03 | pipeline.json execution optional 섹션, Adaptive Depth 기준, Phase F bkit 연동 범위, 실행 모드 업그레이드 메커니즘, Skill Evals 도입 명시 | mumusee00 |
