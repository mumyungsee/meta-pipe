# Phase C: Design Pipeline (파이프라인 설계)

> 도메인에 최적화된 N단계 파이프라인을 설계한다. Phase A(Consult)의 목표/역량 + Phase B(Discover)의 도메인 지식을 기반으로 실행 가능한 파이프라인을 생성한다.

<!-- Design Ref: §1.3 Adaptive Depth 결정 기준, §3.3 pipeline.json 스키마, §7.1 Phase C 컨텍스트 로드 -->
<!-- Design Ref: §8.6 실행 모드 업그레이드 — execution_history 참조 -->
<!-- Plan SC: v1 대비 파이프라인 실행 성공률 향상 — Phase C가 도메인 맞춤 설계 담당 -->

---

## 입력 컨텍스트

Phase C 시작 시 SKILL.md가 로드해주는 데이터:

| 항목 | 출처 | 용도 |
|------|------|------|
| B.summary | discovery.json의 `.summary` | 워크플로우 단계 수, 주요 도구, 리스크 파악 |
| A.summary | consult-result.json의 `.summary` | 목표, 자동화 수준, 선택 경로, 복잡도 |
| domain_slug | `.meta-pipe-status.json`의 `domain_slug` | 산출물 경로 |
| complexity | `.meta-pipe-status.json`의 `complexity` | Adaptive Depth 참고 |

**추가 로드** (업그레이드 판단 시):
- `runtime/user-profile.json`의 `execution_history` — 동일/유사 도메인 이전 실행 이력

---

## C1. Step 도출 (Adaptive Depth)

B.summary에서 도메인 워크플로우와 도구 정보를 읽고, A.summary에서 목표와 역량 제약을 읽어 파이프라인 step을 설계한다.

### 1.1 Step 도출 프로세스

```
B.summary에서 추출:
  → workflows 단계 수 (업계 표준 프로세스 몇 단계인가)
  → tech_stack 도구 수 (required_tools 후보)
  → risks (domain_warnings 후보)

A.summary에서 추출:
  → goal (최종 목표 — step의 마지막 산출물 정의)
  → automation_level (전자동/반자동/가이드 — 기본 실행 모드 결정)
  → quality_expectation (품질 기대 — step 세분화 수준)
  → selected_path (선택 경로 — 도구 구성)

Step 설계 원칙:
  1. B의 workflows를 기본 골격으로 사용
  2. 각 workflow step을 "하나의 산출물 = 하나의 step" 기준으로 분리
  3. 도구가 다른 작업은 별도 step으로 분리 (에이전트 분리 용이)
  4. quality_expectation이 high이면 검수 step 추가 고려
```

### 1.2 Adaptive Depth 결정

4가지 요인을 종합하여 파이프라인 step 수를 결정한다:

| 요인 | 3~5단계 (Light) | 6~8단계 (Standard) | 9~12단계 (Full) |
|------|:-:|:-:|:-:|
| 도메인 워크플로우 수 (B의 workflows) | 1~2개 | 3~5개 | 6개+ |
| required_tools 종류 수 | 0~1개 | 2~3개 | 4개+ |
| execution_mode 혼합도 | 전부 동일 | 2종 혼합 | 3종 혼합 |
| quality_expectation (A의 consult-result) | low/medium | medium/high | high |

**결정 규칙**: 요인이 서로 다른 레벨을 가리킬 경우, **가장 높은 레벨을 채택**한다.

```
예: 워크플로우 2개(Light) + required_tools 4개(Full)
  → Full 기준: 9~12단계

예: 워크플로우 3개(Standard) + quality low(Light) + tools 2개(Standard)
  → Standard 기준: 6~8단계
```

### 1.3 Step 정의 필수 항목

각 step에 다음 항목을 정의한다:

| 항목 | 설명 | 예시 |
|------|------|------|
| id | step-{N} | step-1 |
| name | 간결한 step 이름 | "채널 브랜드 & 용어 정의" |
| purpose | 이 step이 왜 필요한가 | "채널 고유 스타일과 용어 확립" |
| tasks | 구체적 실행 항목 목록 | ["채널 분석", "브랜드 키워드 정의"] |
| done_criteria | 완료 판단 기준 | "브랜드 가이드 문서 생성" |
| depends_on | 의존 step ID 목록 | ["step-1"] |
| domain_warnings | B의 risks에서 관련 항목 | ["채널이 없으면 신규 생성 필요"] |

---

## C2. 실행 모드 태깅

각 step에 execution_mode를 할당한다: `auto`, `assist`, `manual`.

### 2.1 기본 태깅 규칙

```
step의 기본 execution_mode 결정:

1. A.automation_level 확인:
   full  → 기본 모드 auto (가능한 한 자동화)
   semi  → 기본 모드 assist
   guide → 기본 모드 manual

2. step별 override:
   → required_tools에 사용자가 소유하지 않은 도구 포함
     → setup 전: manual
     → setup 후: auto (도구 확보 시)

   → 정성적 판단 필요 (디자인 검수, 톤앤매너 결정 등)
     → assist (AI 초안 + 사용자 검수)

   → 외부 서비스 호출 비용 발생
     → assist (사용자 승인 후 실행)

3. approval_required 결정:
   auto   → false (기본)
   assist → true
   manual → true (완료 확인)
```

### 2.2 실행 모드 업그레이드 (execution_history 참조)

Phase C에서 파이프라인 설계 시, 이전 실행 이력이 있으면 자동화 수준을 올릴 수 있다.

```
runtime/user-profile.json의 execution_history 확인
  |
  ├─ 동일/유사 도메인 이력 없음 → 기본 태깅 규칙(2.1)만 적용
  |
  └─ 이력 있음 → step별 분석:
       |
       ├─ 이전 manual step이 강등 없이 성공 (success: true, degraded: false)?
       |   → 동일 도메인 2회 이상 성공?
       |     → Yes: assist 업그레이드 제안
       |        "이전에 '{step_name}'을 직접 성공하셨습니다. 반자동으로 해볼까요?"
       |     → No: 기본 모드 유지 (1회 성공은 우연일 수 있음)
       |
       ├─ 이전 assist step이 수정 없이 승인됨?
       |   → 동일 도메인 2회 이상?
       |     → Yes: auto 업그레이드 제안
       |        "이전에 '{step_name}' AI 초안을 그대로 승인하셨습니다. 자동으로 할까요?"
       |     → No: 기본 모드 유지
       |
       └─ user-profile.json capabilities 변경됨?
           → 관련 step 업그레이드 후보 추가
           예: docker: false → true → setup step을 manual → auto 제안

사용자 승인 → execution_mode 업그레이드 반영
사용자 거부 → 이전과 동일한 execution_mode 유지
```

**업그레이드 규칙 요약**:
- `success: true` + `degraded: false` (강등 없이 성공) → 한 단계 업그레이드 후보
- `success: true` + `degraded: true` (강등 후 성공) → 업그레이드하지 않음
- 동일 도메인 **2회 이상** 성공 시에만 제안

---

## C3. 도구 매핑 + 실행 설계

### 3.1 도구 매핑

각 step에 `required_tools`를 할당한다.

```
B의 tech_stack에서 도구 후보 추출
  → 각 step의 tasks와 매칭
  → 매칭되는 도구를 required_tools에 추가

A의 user_profile.tools에서 이미 보유한 도구 확인
  → 보유 도구는 setup_requirements에서 제외
  → 미보유 도구는 setup_requirements에 추가
```

### 3.2 Harness 6패턴 (에이전트 실행 설계)

step의 성격에 따라 실행 패턴을 결정한다. **이 정보는 optional** — Phase C가 확정할 수 있으면 pipeline.json에 포함하고, 아니면 Phase E가 런타임에 결정한다.

| 패턴 | 설명 | 적합한 step |
|------|------|------------|
| pipeline | 순차 실행 | 대부분의 일반 step |
| fan-out | 병렬 실행 후 결과 수집 | 독립적인 여러 변형 생성 (A/B 테스트용 등) |
| expert-pool | 전문가 에이전트 선택 | 도메인 특화 판단 필요 시 |
| producer-reviewer | 생성 + 검수 분리 | quality_expectation: high + assist 모드 step |
| supervisor | 감독 에이전트가 하위 관리 | 복잡한 multi-step 작업 |
| hierarchical | 계층적 위임 | Full 레벨 대규모 파이프라인 |

```
패턴 결정 기준:
  → execution_mode가 auto + 단일 도구 → pipeline
  → execution_mode가 assist + 검수 필요 → producer-reviewer
  → 병렬 가능한 독립 task → fan-out
  → 나머지 → pipeline (기본)
```

### 3.3 execution 블록 (optional)

pipeline.json의 step에 포함할 수 있는 optional 블록:

```json
"execution": {
  "pattern": "pipeline | fan-out | expert-pool | producer-reviewer | supervisor | hierarchical",
  "agent_type": "tool-caller | conversational | researcher",
  "delegation": "Task | Agent"
}
```

- Phase C에서 확정 가능하면 포함
- 확정 불가하면 생략 → Phase E의 references/execution.md가 런타임에 결정

---

## C4. 세팅 항목 정리

Phase D에서 처리할 도구 세팅 목록을 정리한다.

```
1. 전체 step의 required_tools에서 고유 도구 목록 추출
2. A의 user_profile.tools와 비교
   → 이미 보유: 제외
   → 미보유: setup_requirements에 추가
3. 각 세팅 항목에 정보 기록:
   → tool: 도구명
   → reason: 어떤 step에서 왜 필요한지
   → setup_guide: 세팅 방법 (B의 tech_stack에서 참조)
```

### complexity별 세팅 범위

| complexity | 세팅 범위 |
|------------|----------|
| Light | setup_requirements 비어있음 → Phase D 생략 |
| Standard | API 키, MCP 설정 등 → 부분 세팅 |
| Full | Docker, CI/CD 등 → 전체 세팅 |

---

## 산출물 생성

### pipeline.md (사람용 마크다운)

경로: `test/{domain-slug}/pipeline/pipeline.md`

```markdown
# Phase C: Design Pipeline - {domain}

> **도메인**: {domain}
> **설계 일자**: {date}
> **복잡도**: {complexity}
> **파이프라인 단계 수**: {total_steps}
> **Adaptive Depth**: {depth_level} (요인: {결정 근거})

---

## 파이프라인 설계

| Step | 이름 | 실행 모드 | 필요 도구 | 완료 기준 |
|------|------|:---------:|----------|----------|
| step-1 | {name} | {mode} | {tools} | {done_criteria} |
| ... | ... | ... | ... | ... |

---

## Step 상세

### Step 1: {name}
- **목적**: {purpose}
- **실행 모드**: {mode} ({mode 결정 근거})
- **필요 도구**: {tools}
- **작업 항목**: {tasks}
- **완료 기준**: {done_criteria}
- **주의사항**: {domain_warnings}

(반복)

---

## 세팅 필요 항목

| 도구 | 사유 | 세팅 가이드 |
|------|------|------------|
| {tool} | {reason} | {guide} |

---

## 설계 요약

- 총 {N}단계, auto {a}개 / assist {b}개 / manual {c}개
- 업그레이드 제안: {있으면 내용, 없으면 "없음 (첫 실행)"}
- Phase D 필요 여부: {Light이면 "불필요", 아니면 "필요 — N개 도구 세팅"}
```

### pipeline.json (에이전트용 구조화 데이터)

경로: `test/{domain-slug}/pipeline/pipeline.json`

v2 공통 헤더 + meta + steps + setup_requirements:

```json
{
  "version": "2.0",
  "phase": "C",
  "created_at": "ISO 8601",
  "summary": "(300자 이내. step 수, 주요 도구, 실행 모드 분포, 세팅 필요 여부)",

  "meta": {
    "domain": "{domain}",
    "domain_slug": "{domain-slug}",
    "total_steps": 6,
    "complexity": "Standard"
  },
  "steps": [
    {
      "id": "step-1",
      "name": "step 이름",
      "purpose": "이 step의 목적",
      "tasks": ["작업1", "작업2"],
      "done_criteria": "완료 판단 기준",
      "execution_mode": "auto | assist | manual",
      "required_tools": [],
      "domain_warnings": [],
      "approval_required": false,
      "depends_on": [],
      "execution": {
        "pattern": "pipeline",
        "agent_type": "tool-caller",
        "delegation": "Task"
      }
    }
  ],
  "setup_requirements": [
    {
      "tool": "도구명",
      "reason": "사유",
      "setup_guide": "세팅 방법 또는 URL"
    }
  ]
}
```

**필수 필드**: meta, steps[] (각 step: id, name, execution_mode, required_tools), setup_requirements[]

**Optional**: steps[].execution — 확정 가능하면 포함, 아니면 생략.

**summary 규칙**: 300자 이내. Phase D/E가 이것만 읽고도 세팅 범위와 실행 계획을 파악할 수 있어야 한다. 포함할 것: step 수, 실행 모드 분포 (auto N / assist M / manual K), 세팅 필요 도구 수.

---

## 사용자 인터랙션

Phase C 완료 후 사용자에게 설계 결과를 확인받는다:

```
Phase C 완료.
- {total_steps}단계 파이프라인 설계 (Adaptive Depth: {level})
- 실행 모드: auto {a}개, assist {b}개, manual {c}개
- 세팅 필요 도구: {N}개
- 업그레이드 적용: {있으면 내용}

파이프라인 설계가 괜찮으신가요? 수정할 부분이 있으면 말씀해주세요.
```

사용자 승인 후 Phase D (또는 Light이면 Phase E)로 진행한다.

---

## Phase C 완료 후

1. `.meta-pipe-status.json` 업데이트: `phases.C.status = "completed"`, `current_phase = "D"` (Light이면 `"E"`)
2. 사용자에게 요약 + 확인 출력 (위 인터랙션 참조)
3. Phase D로 전환 (SKILL.md의 Phase 전환 루프가 처리)
   - Light 레벨: Phase D 건너뛰고 Phase E로 (`phases.D.status = "skipped"`)
