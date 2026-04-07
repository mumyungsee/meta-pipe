# meta-pipe v2 Plan

> **Version**: 0.1 **Created**: 2026-04-01 **Status**: Draft **선행 문서**: `docs/00-ideation/2026-04-01-v2-redesign.md`

---

## 1. 개요

### 1.1 목적

사용자가 "X를 만들고 싶어"라고 말하면, AI가:

1. 사용자를 **컨설팅**하여 목표/환경/역량/평가 기준을 수립하고
2. 해당 도메인을 **조사**하여 전문가 수준의 지식을 확보하고
3. 도메인에 최적화된 **파이프라인을 설계**하고
4. 필요한 **도구를 세팅**하고
5. 파이프라인을 **실행**하고
6. 결과물을 **검수/개선**하는 루프를 돌린다

### 1.2 v1에서 배운 것

| 한계 | v2 해결 |
| --- | --- |
| 사용자 맥락 부재 | Phase A(Consult) 추가 |
| 도구 세팅 생략 | Phase D(Setup) 추가 |
| 결과 검수 없음 | Phase F(Evaluate) 추가 |
| 단일 컨텍스트 실행 | 서브에이전트 분산 실행 (Design에서 구체화) |
| 고정 실행 주체 | Step별 실행 모드 태깅 (auto/assist/manual) |

### 1.3 선행 리써치 (v1에서 수행)

- 도메인 적응형 파이프라인 도구: 현재 시장에 없음
- 유사 프로젝트: AWS AI-DLC (적응형 워크플로우, 도메인 조사 없음), DataFlow Agent (동적 파이프라인, 데이터 전용)
- 차별점: "도메인 조사 -&gt; 도메인 맞춤 파이프라인 동적 생성"의 조합은 유일

---

## 2. 전체 아키텍처

```
입력: "X를 만들고 싶어"
  |
  v
Phase A: Consult (컨설팅) ─────────────────────────┐
  A1. 요구사항 수집 (목표, 자동화 수준, 사용 주체)        │
  A2. 사용자 프로필 파악 (도구, 역량, 의지)              │
  A3. Feasibility Research (AI 단독 조사)             │
  A4. 선택지 제안 (경로별 트레이드오프) ←─ 재조사 루프    │
  A5. 조율 확정 (평가 기준 + 실행 모드 사전 결정)        │
  |                                                 │
  v                                                 │
Phase B: Discover (도메인 조사)                       │
  B1. 5카테고리 WebSearch 조사                        │
  B2. 품질 평가 + 보완 조사                            │
  B3. 조사 결과 구조화                                │
  |                                                 │
  v                                                 │
Phase C: Design Pipeline (파이프라인 설계)             │
  C1. Step 도출 (도메인 맞춤)                         │
  C2. Step별 실행 모드 태깅 (auto/assist/manual)       │
  C3. 도구 매핑 + 에이전트 분리 설계                    │
  C4. 세팅 필요 항목 정리                              │
  |                                                 │
  v                                                 │
Phase D: Setup (도구 세팅) — 레벨에 따라 생략 가능       │
  D1. 도구 설치/설정 안내 또는 자동 실행                  │
  |                                                 │
  v                                                 │
Phase E: Execute (실행)                              │
  E1. 파이프라인 실행 (서브에이전트 분산)                 │
  E2. Step별 산출물 생성                              │
  |                                                 │
  v                                                 │
Phase F: Evaluate & Improve (검수/개선) <─────────────┘
  F1. 평가 기준 대비 검수                         (A4 참조)
  F2. 기준 미달 시 개선 루프
```

---

## 3. Phase별 스코프

### 3.1 Phase A: Consult (컨설팅)

**목적**: 사용자의 요구사항과 역량을 파악하고, AI가 현실적 경로를 조사/제안하여, 사용자가 충분한 정보를 바탕으로 결정할 수 있도록 컨설팅한다.

**v1과의 차이**: v1에는 이 단계가 없었다. 사용자 맥락 없이 바로 도메인 조사로 진입하여 "실행 불가능한 파이프라인"이 생성되는 문제가 있었다.

**핵심 원칙**: 단순 인터뷰가 아닌 컨설팅. AI가 능동적으로 조사하고, 사용자의 요구사항과 역량을 교차 분석하여 현실적 선택지를 제안한다. 사용자는 충분한 정보를 바탕으로 경로를 선택한다.

#### Sub-steps

| Step | 이름 | 설명 | 비고 |
| --- | --- | --- | --- |
| A1 | 요구사항 수집 | 목표, 자동화 수준(전자동/반자동/가이드), 사용 주체(사람/AI), 품질 기대치 | 입력이 모호하면 구체화 질문 (최대 2회) |
| A2 | 사용자 프로필 파악 | 보유 도구, 세팅 역량, 추가 세팅 의지, 비용 지불 가능 여부 | 프로필 있으면 변경분만 갱신 |
| A3 | Feasibility Research | AI가 A1+A2를 교차 분석하여 도구/방법 조사. "이 역량으로 이 목표를 달성하려면?" 경로 후보 도출 | AI 단독 조사 (WebSearch) |
| A4 | 선택지 제안 (Options) | 경로별 결과물 수준, 필요 세팅, 비용, 사용자 공수 제시. 요구사항 충족도 명시 | 사용자 선택. 재조사 요청 시 A3 복귀 |
| A5 | 조율 확정 (Calibration) | 선택된 경로 기반 평가 기준 구체화 + 실행 모드 사전 결정 + 프로필 갱신 | Phase F에서 참조 |

#### A3→A4 경로 예시

```
요구사항: "유튜브 섬네일 전자동으로 만들고 싶어" (자동화: 전자동, 품질: 높음)
역량: API 키 발급 경험 있음, Docker 모름, 월 $10 정도 가능

AI 조사 결과 → 3가지 경로 제안:
  경로1 [전자동, 고품질]: DALL-E API + YouTube API 세팅
    - 결과: 전자동 가능, 고품질
    - 필요: API 키 2개 발급, MCP 설정 (세팅 2시간)
    - 비용: 월 ~$15
    - 요구사항 충족도: 100%

  경로2 [반자동, 고품질]: AI 프롬프트 생성 + 사용자가 Canva에서 실행
    - 결과: 반자동 (프롬프트+가이드만), 품질은 사용자 실행에 따라 다름
    - 필요: 세팅 없음
    - 비용: 무료
    - 요구사항 충족도: 60% (전자동 아님)

  경로3 [전자동, 중품질]: 무료 오픈소스 이미지 생성 + 자동화
    - 결과: 전자동 가능, 품질은 경로1보다 낮음
    - 필요: Docker 설치 + 로컬 모델 세팅 (세팅 4시간)
    - 비용: 무료 (GPU 필요)
    - 요구사항 충족도: 80% (품질 타협)

  → AI 추천: 경로1 (역량 충분, 비용 범위 내, 요구사항 100% 충족)
```

#### 산출물

```
consult-result.json:
  requirements:
    goal:             사용자 목표 (구체화된)
    automation_level: full / semi / guide
    target_user:      human / ai_agent
    quality_expectation: high / medium / low
  user_profile:
    tools:            보유 도구 목록
    capabilities:     세팅 역량 수준
    willingness:      추가 세팅/학습 의지
    budget:           비용 범위
  selected_path:
    id:               선택된 경로
    description:      경로 설명
    tradeoffs:        타협한 부분 명시
  eval_criteria:      평가 기준 (선택 경로 기반, 정량 + 정성)
  complexity:         Light / Standard / Full
```

### 3.2 Phase B: Discover (도메인 조사)

**목적**: 목표 도메인의 전문가 수준 지식을 확보한다.

**v1과의 차이**: v1의 Phase A와 동일한 5카테고리 조사이나, 컨설팅 결과(A의 산출물)를 반영하여 조사 방향이 구체화된다.

#### Sub-steps

| Step | 이름 | 설명 |
| --- | --- | --- |
| B1 | 5카테고리 조사 | 핵심 용어, 워크플로우, 기술 스택, 데이터 모델, 리스크 |
| B2 | 품질 평가 + 보완 | 각 카테고리 우수/양호/미흡/부족 평가. 미흡 이하는 WebFetch로 보완 |
| B3 | 결과 구조화 | 이중 형식 출력 (마크다운 + JSON) |

#### 산출물

```
discovery.md:     사람용 마크다운 보고서
discovery.json:   에이전트용 구조화 데이터
  domain_knowledge:
    glossary:     용어 사전
    workflows:    업계 표준 워크플로우
    tech_stack:   기술 스택 옵션
    data_model:   핵심 엔티티/스키마
    risks:        리스크/주의사항
```

### 3.3 Phase C: Design Pipeline (파이프라인 설계)

**목적**: 도메인에 최적화된 N단계 파이프라인을 설계한다.

**v1과의 차이**: Step별 실행 모드 태깅 추가, 도구 매핑 + 에이전트 분리 설계 추가, 세팅 필요 항목 정리 추가.

#### Sub-steps

| Step | 이름 | 설명 |
| --- | --- | --- |
| C1 | Step 도출 | 도메인 조사(B) + 목표(A1) 기반으로 단계 설계. Adaptive Depth: 3\~12단계 |
| C2 | 실행 모드 태깅 | 각 step에 auto/assist/manual 결정. 기준: 자동화 가능성, 도구 세팅 여부, 사용자 역량 |
| C3 | 도구 매핑 + 실행 설계 | 각 step에 필요한 도구, 에이전트 분리 기준 결정. 구현 방식은 Design 단계에서 확정 |
| C4 | 세팅 항목 정리 | Phase D에서 처리할 도구 세팅 목록 도출 |

#### 산출물

```
pipeline.md:      사람용 파이프라인 문서
pipeline.json:    에이전트용 구조화 파이프라인
  meta:           domain, version, complexity
  steps[]:
    id, name, purpose, tasks, done_criteria,
    execution_mode (auto/assist/manual),
    required_tools[], domain_warnings[],
    approval_required, depends_on[]
  setup_requirements[]:
    tool, reason, setup_guide
```

### 3.4 Phase D: Setup (도구 세팅)

**목적**: 파이프라인 실행에 필요한 도구를 세팅한다.

**v1과의 차이**: v1에는 이 단계가 없었다. 도구 세팅이 파이프라인 밖에서 암묵적으로 이루어져야 했다.

#### 복잡도별 동작

| 레벨 | 동작 |
| --- | --- |
| Light | Phase D 생략. 기존 도구로 충분 |
| Standard | 일부 도구 세팅 안내. API 키 등록, MCP 설정 등 |
| Full | 인프라 구축 수준. Docker, CI/CD 등 |

#### Sub-steps

| Step | 이름 | 설명 |
| --- | --- | --- |
| D1 | 세팅 실행 | setup_requirements\[\]를 순회하며 안내 또는 자동 실행 |

#### 산출물

```
setup-result.json:
  completed[]:    세팅 완료된 도구
  skipped[]:      생략된 도구 (사유 포함)
  failed[]:       실패한 도구 (에러 + 수동 가이드)
```

### 3.5 Phase E: Execute (실행)

**목적**: 설계된 파이프라인을 실행하여 산출물을 생성한다.

**v1과의 차이**: 단일 컨텍스트 순차 실행에서 서브에이전트 분산 실행으로 전환. 구현 방식(Harness 파일 기반 전달 vs bkit Agent 도구 활용 등)은 Design에서 확정.

#### Sub-steps

| Step | 이름 | 설명 |
| --- | --- | --- |
| E1 | 파이프라인 실행 | pipeline.json의 steps를 순서대로 실행. 실행 모드에 따라 자동/반자동/수동 |
| E2 | 산출물 관리 | 각 step의 산출물을 workspace에 저장. 상태 추적 |

#### 실행 모드별 동작

```
auto:    AI가 자동 실행. 산출물 생성 후 다음 step으로
assist:  AI가 초안 생성 -> 사용자 검수 -> 승인 후 다음 step
manual:  사용자가 직접 실행. AI는 가이드만 제공. 완료 확인 후 다음 step
```

#### 산출물

```
test/{domain-slug}/pipeline/steps/   각 step 산출물
test/{domain-slug}/pipeline/output/  최종 결과물
.meta-pipe-status.json               실행 상태 (중단/재개용)
runtime/logs/{timestamp}.json        실행 로그
```

### 3.6 Phase F: Evaluate & Improve (검수/개선)

**목적**: 평가 기준(A4)에 따라 결과물을 검수하고, 기준 미달 시 개선 루프를 돌린다.

**v1과의 차이**: v1에는 이 단계가 없었다. 파이프라인 실행으로 끝났다.

#### Sub-steps

| Step | 이름 | 설명 |
| --- | --- | --- |
| F1 | 검수 | eval_criteria(A4)의 각 항목 대비 결과물 평가 |
| F2 | 개선 루프 | 기준 미달 항목에 대해 해당 step 재실행. 최대 3회 반복 |

#### 검수 방식

```
정량적 기준 (예: "텍스트 영역 30% 이상"):
  -> AI가 자동 검수 가능

정성적 기준 (예: "밝은 느낌"):
  -> 사용자 검수 필요 (assist 모드)
```

#### 산출물

```
evaluation-result.json:
  criteria_results[]:
    criterion, result (pass/fail), score, note
  overall_pass: boolean
  improvement_log[]:
    iteration, step_id, change, result
```

---

## 4. Phase 간 인터페이스

각 Phase가 다음 Phase에 넘기는 데이터를 명확히 정의한다. 이것이 v2 설계의 핵심이다.

```
A (Consult)
  ──> consult-result.json ──> B (Discover)
                           ──> C (Design Pipeline)  [goal, user_profile, available_tools]
                           ──> D (Setup)             [available_tools]
                           ──> F (Evaluate)          [eval_criteria]

B (Discover)
  ──> discovery.json ──> C (Design Pipeline)         [domain_knowledge]
                      ──> E (Execute)                [domain_knowledge - 에이전트 프롬프트에 포함]

C (Design Pipeline)
  ──> pipeline.json ──> D (Setup)                    [setup_requirements]
                     ──> E (Execute)                 [steps, execution config]

D (Setup)
  ──> setup-result.json ──> E (Execute)              [도구 사용 가능 여부 확인]

E (Execute)
  ──> step 산출물 + status ──> F (Evaluate)           [결과물]

F (Evaluate)
  ──> evaluation-result.json ──> E (Execute)          [개선 필요 step 재실행]
  ──> (최종 완료 시) 종료
```

### 데이터 흐름 요약

| From | To | 데이터 | 형식 |
| --- | --- | --- | --- |
| A -&gt; B | 조사 방향 | goal, user_profile | consult-result.json |
| A -&gt; C | 도구/역량 제약 | available_tools, user_profile | consult-result.json |
| A -&gt; F | 평가 기준 | eval_criteria | consult-result.json |
| B -&gt; C | 도메인 지식 | domain_knowledge | discovery.json |
| B -&gt; E | 도메인 맥락 | glossary, workflows | discovery.json (요약) |
| C -&gt; D | 세팅 목록 | setup_requirements | pipeline.json |
| C -&gt; E | 실행 계획 | steps, execution | pipeline.json |
| D -&gt; E | 도구 상태 | completed/skipped/failed | setup-result.json |
| E -&gt; F | 결과물 | step 산출물 | 파일 시스템 |
| F -&gt; E | 재실행 지시 | 미달 step ID + 피드백 | evaluation-result.json |

---

## 5. 복잡도 레벨

컨설팅(A) 과정에서 자동 결정된다.

| 레벨 | 기준 | Phase D | 예시 |
| --- | --- | --- | --- |
| **Light** | 기존 도구로 충분. API/인프라 불필요 | 생략 | 블로그 글쓰기, 마케팅 카피 |
| **Standard** | 일부 API 키, MCP 설정 필요 | 부분 실행 | 유튜브 섬네일, 카드뉴스 |
| **Full** | Docker, CI/CD 등 인프라 구축 필요 | 전체 실행 | 영상 편집 자동화, 데이터 파이프라인 |

---

## 6. 사용자 프로필

반복 인터뷰를 최소화하기 위해 프로필을 축적한다.

```
user-profile/
├── capabilities.md    # 역량 (API 세팅 가능, Docker 모름 등)
├── tools.md          # 보유 도구 (DALL-E API 키 있음 등)
└── preferences.md    # 선호도 (로컬 우선, 비용 최소화 등)
```

- 첫 실행 시: A2에서 전체 인터뷰
- 이후 실행 시: 변경된 부분만 갱신
- 프로필 저장 위치: `runtime/user-profile/` (gitignore)

---

## 7. 구현 순서

설계는 Phase A\~F 전체를 한번에 하지만, 구현은 Phase A부터 순차적으로 진행한다.

| 순서 | 작업 | 산출물 | 의존성 |
| --- | --- | --- | --- |
| 0 | Design 문서 작성 | `docs/02-design/v2-design.md` | 이 Plan |
| 1 | Phase A 구현 | `skills/meta-pipe/` + `references/consult.md` | Design |
| 2 | Phase B 구현 | `references/discovery.md` 업데이트 | Phase A |
| 3 | Phase C 구현 | `references/pipeline-design.md` 업데이트 | Phase B |
| 4 | Phase D 구현 | `references/setup.md` 신규 | Phase C |
| 5 | Phase E 구현 | `references/execution.md` 업데이트 | Phase D |
| 6 | Phase F 구현 | `references/evaluation.md` 신규 | Phase E |
| 7 | 통합 테스트 | 테스트 도메인으로 end-to-end | 전체 |
| 8 | SKILL.md 완성 | 전체 Phase 통합 | 통합 테스트 |

---

## 8. 테스트 도메인

### 8.1 선정 기준

- Phase A(Consult)의 가치를 검증할 수 있는 도메인
- v1 테스트와 비교 가능하면 좋음
- Light/Standard/Full 중 최소 2개 레벨 커버

### 8.2 후보

| 도메인 | 레벨 | v1 비교 | Consult 검증 |
| --- | --- | --- | --- |
| 유튜브 섬네일 (재실행) | Standard | v1 결과와 직접 비교 가능 | 중 |
| 블로그 글쓰기 파이프라인 | Light | 신규 | 높 (간단해서 컨설팅 효과 명확) |
| 팟캐스트 제작 파이프라인 | Standard | 신규 | 높 (도구 선택 다양) |
| 데이터 대시보드 | Full | 신규 | 높 (인프라 세팅 필요) |

### 8.3 결정

Plan 작성 시점에서는 미정. Design 완료 후 첫 구현 테스트 시 결정한다. **추천**: 유튜브 섬네일(v1 비교) + 블로그 글쓰기(Light 레벨 검증) 2개 도메인.

---

## 9. Design에서 결정할 사항

Plan에서는 "무엇을 할지"를 정했고, Design에서는 "어떻게 할지"를 결정한다:

| 항목 | Plan에서 정한 것 | Design에서 결정할 것 |
| --- | --- | --- |
| 서브에이전트 실행 | "Phase E는 분산 실행" | Harness 파일 기반 vs bkit Agent 도구 vs 하이브리드 |
| 상태 관리 | ".meta-pipe-status.json으로 추적" | 스키마 상세, 중단/재개 로직 |
| 캐시 | "runtime/cache/에 저장" | 캐시 무효화 정책, TTL |
| 프로필 | "user-profile/에 축적" | 스키마 상세, 갱신 로직 |
| 인터페이스 JSON | "Phase간 JSON으로 전달" | 각 JSON의 상세 스키마 (JSON Schema) |
| 에러 처리 | "실패 시 재시도/보고" | 재시도 정책, fallback 전략 |
| 컨텍스트 관리 | "Phase별로 분리" | references 로드 전략, 컨텍스트 예산 |

---

## 10. 작업 분해표

GitHub Issue로 전환할 단위. 각 항목은 독립적으로 완료 가능한 단위이다.

### Milestone 0: 설계 (Design)

| ID | 작업 | 설명 |
| --- | --- | --- |
| D-1 | v2 Design 문서 작성 | Phase A\~F 상세 기술 설계. 9절의 미결 사항 포함 |
| D-2 | Phase 간 인터페이스 JSON Schema 정의 | consult-result, discovery, pipeline, setup-result, evaluation-result |

### Milestone 1: Phase A - Consult

| ID | 작업 | 설명 |
| --- | --- | --- |
| A-1 | 요구사항 수집 로직 구현 | 목표 파싱, 자동화 수준/사용 주체/품질 기대치 수집 |
| A-2 | 사용자 프로필 시스템 구현 | 보유 도구, 세팅 역량, 세팅 의지, 비용 범위. 프로필 CRUD/갱신 |
| A-3 | Feasibility Research 구현 | 요구사항+역량 교차 분석, 도구/방법 조사, 경로 후보 도출 |
| A-4 | 선택지 제안 로직 구현 | 경로별 트레이드오프 제시, 추천 경로, 재조사 루프 |
| A-5 | 조율 확정 로직 구현 | 선택 경로 기반 평가 기준 구체화, 실행 모드 사전 결정 |
| A-6 | consult-result.json 출력 검증 | 스키마 준수 확인 (requirements, user_profile, selected_path, eval_criteria) |

### Milestone 2: Phase B - Discover

| ID | 작업 | 설명 |
| --- | --- | --- |
| B-1 | 컨설팅 결과 반영 조사 로직 | A의 산출물을 조사 쿼리에 반영 |
| B-2 | v1 Discovery 로직 마이그레이션 | v1 references/discovery.md 기반 5카테고리 조사 |
| B-3 | 캐시 시스템 연동 | runtime/cache/ 활용, TTL 관리 |

### Milestone 3: Phase C - Design Pipeline

| ID | 작업 | 설명 |
| --- | --- | --- |
| C-1 | Step 도출 + Adaptive Depth 로직 | 도메인 복잡도에 따른 3\~12단계 설계 |
| C-2 | 실행 모드 태깅 로직 | auto/assist/manual 자동 결정 |
| C-3 | 도구 매핑 + 실행 설계 로직 | required_tools, 에이전트 분리 기준 |
| C-4 | pipeline.json 출력 검증 | 스키마 준수 + 이중 형식 출력 |

### Milestone 4: Phase D - Setup

| ID | 작업 | 설명 |
| --- | --- | --- |
| D-3 | 레벨별 Setup 분기 로직 | Light(생략)/Standard(부분)/Full(전체) |
| D-4 | 도구 세팅 안내/실행 로직 | MCP 설정, API 키 등록 등 |

### Milestone 5: Phase E - Execute

| ID | 작업 | 설명 |
| --- | --- | --- |
| E-1 | 실행 모드별 동작 구현 | auto/assist/manual 분기 |
| E-2 | 서브에이전트 분산 실행 구현 | Design에서 확정된 방식으로 |
| E-3 | 상태 추적 + 중단/재개 | .meta-pipe-status.json 관리 |
| E-4 | 실행 로그 기록 | runtime/logs/ 기록 |

### Milestone 6: Phase F - Evaluate & Improve

| ID | 작업 | 설명 |
| --- | --- | --- |
| F-1 | 평가 기준 대비 자동 검수 로직 | 정량적 기준 자동 평가 |
| F-2 | 개선 루프 구현 | 미달 step 재실행, 최대 3회 |
| F-3 | evaluation-result.json 출력 | 검수 결과 구조화 |

### Milestone 7: 통합 + 마무리

| ID | 작업 | 설명 |
| --- | --- | --- |
| I-1 | SKILL.md 통합 작성 | Phase A\~F 전체 흐름 통합 |
| I-2 | 테스트 도메인 1: end-to-end 실행 | 선정된 도메인으로 전체 파이프라인 검증 |
| I-3 | 테스트 도메인 2: end-to-end 실행 | 다른 레벨의 도메인으로 검증 |
| I-4 | Gap Analysis + 개선 | 설계 대비 구현 갭 분석 |

---

## 11. 리스크

| 리스크 | 영향 | 대응 |
| --- | --- | --- |
| 컨설팅(A)이 너무 길어져 사용자 이탈 | 높 | 프로필 축적으로 반복 최소화. 최소 질문 세트 정의 |
| 도구 세팅(D) 실패 | 중 | 수동 가이드 fallback. 세팅 없이 가능한 대안 제시 |
| 서브에이전트 간 컨텍스트 손실 | 중 | Design에서 데이터 전달 방식 신중히 설계 |
| 정량적 평가 기준 도출 어려움 | 중 | 정성적 기준은 assist 모드로 사람 검수 |
| 컨텍스트 윈도우 초과 | 높 | Phase별 컨텍스트 분리, references 필요 시만 로드 |

---

## 부록: v1 참조 자료

- v1 Plan: `archive/v1/docs/01-plan/domain-discovery-pipeline.plan.md`
- v1 SKILL.md: `archive/v1/skills/meta-pipe/SKILL.md`
- v1 Gap Analysis: `archive/v1/docs/04-check/meta-pipe-gap-analysis.md`
- Harness 통합 Plan: `archive/v1/docs/05-act/next-cycle/harness-integration.plan.md`
- v1 테스트: `test/youtube-thumbnail/`, `test/card-news/`