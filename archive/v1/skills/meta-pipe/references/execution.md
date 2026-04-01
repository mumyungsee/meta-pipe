# Phase C: Execute - 상세 가이드

> 이 문서는 SKILL.md의 Phase C 실행 시 로드된다.
> 파이프라인 각 단계의 실행 프로토콜, 승인 처리, 상태 관리, 산출물 생성 규칙을 정의한다.

---

## 1. 단계 실행 프로토콜

### 1.1 단계 진입

각 단계 시작 시 다음 형식으로 안내한다:

```markdown
---

## Step {N}/{total}: {name}

**목적**: {purpose}

**할 일**:
1. {task_1}
2. {task_2}
3. ...

**주의사항**:
- {domain_warning_1}
- {domain_warning_2}

**산출물**: {output_files}

---
```

### 1.2 산출물 생성 규칙

```
1. Phase A 조사 결과를 맥락으로 활용
   - test/{domain-slug}/pipeline/domain-discovery.md 또는 캐시에서 관련 정보 참조
   - 도메인 용어 사전의 용어 사용

2. domain_warnings를 산출물에 반영
   - 각 경고를 산출물의 관련 섹션에 녹여넣기
   - 경고 사항을 무시하지 않았음을 확인

3. 불확실한 부분 처리
   - [검토 필요] 마킹
   - 대안 제시 (가능한 경우)
   - 판단 근거 기록

4. 출처 포함
   - Phase A에서 수집된 출처 URL 활용
   - 추가 조사 시 새 출처 추가
```

### 1.3 산출물 파일 저장

```
저장 경로: test/{domain-slug}/pipeline/steps/step-{N}-{slug}.md
  예: test/{domain-slug}/pipeline/steps/step-1-glossary-requirements.md
      test/{domain-slug}/pipeline/steps/step-2-data-model.md

slug 생성: 단계 name_en을 kebab-case로
  "Domain Glossary & Requirements" → "glossary-requirements"
  "Data Model Design" → "data-model"

추가 산출물 (단계에 따라):
  - JSON Schema → schemas/{name}.schema.json
  - 코드 → src/{module}/
  - 설정 → config/{name}.json
```

---

## 2. approval_required 처리

### 2.1 사용자 모드 (Human)

```
approval_required = true:
  1. 산출물 초안 생성
  2. 사용자에게 보여주기:
     "### Step {N} 결과 검토

     (산출물 요약 또는 핵심 결정 사항)

     이 단계의 결과를 검토해 주세요.
     - 수정이 필요하면 말씀하세요
     - 문제없으면 '확인' 또는 다음 단계로 진행합니다"

  3. 사용자 피드백 반영
     - 수정 요청 → 반영 후 재검토
     - 승인 → 다음 단계로

approval_required = false:
  1. 산출물 생성
  2. done_criteria 자체 검증
  3. 간단 요약 후 자동으로 다음 단계 안내:
     "Step {N} 완료. 산출물: {files}. Step {N+1}로 진행합니다."
```

### 2.2 에이전트 모드 (Autonomous Agent)

```
approval_required = true:
  1. 산출물 생성
  2. 승인 요청 파일 생성:
     test/{domain-slug}/pipeline/steps/.approval-needed-step-{N}.md
     내용: 결정 사항 요약, 대안, 판단 근거
  3. 상태를 "awaiting_approval"로 설정
  4. 다음 단계로 진행하지 않음

approval_required = false:
  1. 산출물 생성
  2. done_criteria 자체 검증
  3. 자동으로 다음 단계 연속 실행
```

### 2.3 에이전트 모드 감지

```
에이전트 모드 판단:
  - 입력이 JSON 형식 → 에이전트
  - pipeline.json을 직접 참조하여 호출 → 에이전트
  - 자연어 대화 → 사용자

명시적 지정도 가능:
  .meta-pipe-status.json의 "mode": "human" | "agent"
```

---

## 3. 도메인 전문가 수준 유지

### 3.1 전문가 수준 체크리스트

각 단계 실행 시 자체 점검:

```
[ ] 이 산출물이 도메인 전문가가 작성한 것처럼 보이는가?
[ ] 도메인 고유 용어를 정확히 사용하고 있는가?
[ ] 일반적인 소프트웨어 개발 가이드가 아닌 도메인 특화 가이드인가?
[ ] domain_warnings의 모든 항목이 반영되었는가?
[ ] 해당 도메인에서 일반적인 실수/안티패턴을 방지하고 있는가?
```

### 3.2 도메인 지식 활용 패턴

```
용어 사전 활용:
  - 산출물에서 도메인 용어 사용 시 Phase A 용어 참조
  - 한/영 매핑 일관성 유지

워크플로우 활용:
  - 각 단계의 산출물이 도메인 표준 워크플로우를 반영
  - 업계 best practice 패턴 적용

기술 스택 활용:
  - 구현 단계에서 Phase A 추천 기술 스택 참조
  - 도메인에서 검증된 도구/라이브러리 우선 추천

리스크 활용:
  - 관련 리스크가 있는 단계에서 명시적 대응
  - 법적 리스크 → 산출물에 준수 사항 포함
```

---

## 4. 상태 관리

### 4.1 상태 파일 업데이트 시점

```
Phase C 진입 시:
  phase_c.status = "in_progress"
  phase_c.current_step = 1

각 단계 시작 시:
  phase_c.steps[N].status = "in_progress"
  phase_c.current_step = N

각 단계 완료 시:
  phase_c.steps[N].status = "completed"
  phase_c.steps[N].completed_at = now()
  phase_c.current_step = N + 1

승인 대기 시:
  phase_c.steps[N].status = "awaiting_approval"

전체 완료 시:
  phase_c.status = "completed"
  updated_at = now()
```

### 4.2 상태 파일 스키마

```json
{
  "project_id": "uuid-v4",
  "domain": "카드뉴스 자동화",
  "input_prompt": "카드뉴스 자동화 도구를 만들고 싶어",
  "mode": "human",
  "started_at": "2026-03-24T10:00:00Z",
  "updated_at": "2026-03-24T12:30:00Z",
  "current_phase": "C",
  "phase_a": {
    "status": "completed",
    "cache_used": false,
    "completed_at": "2026-03-24T10:30:00Z"
  },
  "phase_b": {
    "status": "completed",
    "total_steps": 8,
    "completed_at": "2026-03-24T11:00:00Z"
  },
  "phase_c": {
    "status": "in_progress",
    "current_step": 3,
    "total_steps": 8,
    "steps": [
      {
        "id": "step-1",
        "name": "도메인 용어 & 요구사항 정의",
        "status": "completed",
        "approval_required": true,
        "completed_at": "2026-03-24T11:30:00Z"
      },
      {
        "id": "step-2",
        "name": "데이터 모델 설계",
        "status": "completed",
        "approval_required": true,
        "completed_at": "2026-03-24T12:00:00Z"
      },
      {
        "id": "step-3",
        "name": "템플릿 엔진 설계",
        "status": "in_progress",
        "approval_required": false,
        "completed_at": null
      }
    ]
  }
}
```

---

## 5. 실행 로그 기록

### 5.1 로그 기록 시점

```
Phase A 완료 시: phases.A 섹션 기록
Phase B 완료 시: phases.B 섹션 기록
Phase C 각 단계 완료 시: phases.C 업데이트
전체 완료 시: completed_at + evaluation 기록
```

### 5.2 로그 파일

```
runtime/logs/{timestamp}.json
  timestamp 형식: YYYYMMDD-HHmmss
  예: runtime/logs/20260324-150000.json
```

### 5.3 로그 스키마

```json
{
  "session_id": "uuid-v4",
  "domain": "카드뉴스 자동화",
  "input_prompt": "카드뉴스 자동화 도구를 만들고 싶어",
  "started_at": "ISO8601",
  "completed_at": "ISO8601 | null",
  "phases": {
    "A": {
      "duration_seconds": 300,
      "queries_count": 10,
      "webfetch_count": 2,
      "cache_hit": false,
      "categories_quality": {
        "terminology": "excellent",
        "workflow": "excellent",
        "tech_stack": "good",
        "data_model": "fair",
        "risks": "good"
      }
    },
    "B": {
      "duration_seconds": 120,
      "total_steps": 8,
      "approval_required_count": 4,
      "domain_unique_steps": ["템플릿 엔진", "콘텐츠 파이프라인", "접근성/법적 준수"],
      "removed_generic_steps": ["목업", "API 설계", "UI 구현"]
    },
    "C": {
      "duration_seconds": 1800,
      "steps_completed": 8,
      "steps_total": 8,
      "approvals_requested": 4,
      "approvals_given": 4
    }
  },
  "evaluation": {
    "websearch_quality": 4,
    "pipeline_domain_fit": 5,
    "expert_level": 4
  }
}
```

---

## 6. 단계 간 전환

### 6.1 자연스러운 전환

```
approval_required=false 단계 연속 시:
  "Step {N} 완료. → Step {N+1}: {name}으로 진행합니다."
  (자동 전환, 사용자 대기 없음)

approval_required=true → false 전환:
  사용자 승인 후 "→ Step {N+1}: {name}. 이 단계는 자율 진행됩니다."

approval_required=false → true 전환:
  "Step {N} 완료. → Step {N+1}: {name}은 검토가 필요한 단계입니다."
```

### 6.2 의존성 확인

```
다음 단계 시작 전:
  IF next_step.depends_on 에 미완료 단계가 있으면:
    "Step {X}가 먼저 완료되어야 합니다."
    (병렬 실행 불가 단계 식별)
```

---

## 7. 완료 처리

### 7.1 전체 파이프라인 완료 시

```
"## 파이프라인 실행 완료: {domain}

### 산출물 요약
| Step | 산출물 | 상태 |
| --- | --- | --- |
| 1 | test/{domain-slug}/pipeline/steps/step-1-{slug}.md | 완료 |
| ... | ... | ... |

### 다음 추천 작업
- 산출물을 기반으로 실제 구현 시작
- [검토 필요] 항목 확인 및 보완
- 필요시 특정 단계 재실행 가능"
```

### 7.2 실행 로그 최종 기록

```
completed_at 기록
evaluation 자체 평가 (1-5점)
runtime/logs/ 에 저장
```

### 7.3 상태 파일 정리

```
.meta-pipe-status.json 유지 (재실행 참조용)
phase_c.status = "completed"
```
