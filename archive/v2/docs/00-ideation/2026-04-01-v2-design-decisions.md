# meta-pipe v2 Design 미결 사항 결정 기록

> 일시: 2026-04-01
> 목적: v2 Plan 9절의 미결 사항을 Design 문서 작성 전에 결정
> 선행 문서: `docs/01-plan/v2-plan.md`, `docs/00-ideation/2026-04-01-v2-redesign.md`

---

## 배경

v2 Plan 9절에서 "Design에서 결정할 사항" 7가지를 명시했다. Design 문서 작성 전에 이 미결 사항들을 먼저 결정하여 Design의 방향을 확정한다.

---

## 결정 1: 서브에이전트 실행 방식 — bkit 방식 단일 채택

### 논의 과정

bkit과 Harness 두 프로젝트를 비교 분석했다.

**분석 결과 — 두 프로젝트의 본질적 차이:**

| | bkit | Harness |
|---|---|---|
| 정체 | 플러그인 시스템 (37 스킬 + 32 에이전트가 이미 존재) | 메타 스킬 (에이전트 팀 + 스킬을 매번 새로 생성) |
| 핵심 가치 | 프로세스 프레임워크 (PDCA, 파이프라인, 품질 루프) | 에이전트 오케스트레이션 (도메인별 에이전트 구성 자동화) |
| 에이전트 실행 | Task(에이전트명) 또는 에이전트 팀 | TeamCreate + SendMessage 또는 Agent() |
| 데이터 전달 | 파일 체인 (docs/) + 상태 파일 + Context Anchor | 메시지 + 태스크 + 파일(_workspace/) 3종 조합 |
| 적용 대상 | 웹앱 개발 (고정 도메인, 사전 정의된 에이전트) | 아무 도메인 (매번 다른 에이전트를 동적 생성) |

**핵심 인사이트**: 둘 다 Claude Code의 동일한 에이전트 팀/서브에이전트 기능을 사용한다. 차이는 실행 메커니즘이 아니라 "에이전트가 사전 정의됨(bkit) vs 매번 생성(Harness)"이다.

**meta-pipe에 대입한 결과:**
- meta-pipe의 Phase A~F는 고정된 프로세스 → bkit의 Phase 1~9과 동일한 성격
- meta-pipe가 Phase C에서 도메인별 에이전트를 설계하는 것 자체가 Harness와 같은 역할
- Harness를 별도로 가져올 필요 없이, meta-pipe의 Phase C가 Harness의 역할을 흡수하면 됨
- bkit이 이미 설치되어 있으므로 PDCA, gap-detector 등을 재활용할 수 있음

### 결정

**bkit 방식 단일 채택. Harness의 설계 지식(6가지 아키텍처 패턴)은 references에 포함.**

구체적으로:
1. meta-pipe = bkit의 새 파이프라인 (development-pipeline 옆에 meta-pipeline 추가)
2. Phase A~F = bkit의 Phase 1~9과 동일 구조 (스킬 + references, 지연 로딩)
3. Phase F(Evaluate) = bkit의 PDCA Check-Act 재활용 (gap-detector, pdca-iterator)
4. Phase E의 에이전트 실행 = bkit이 쓰는 Task(에이전트명) 또는 Agent() 도구
5. Phase C에서 도메인별 에이전트 설계 시 Harness의 6가지 패턴(Pipeline, Fan-out, Expert Pool, Producer-Reviewer, Supervisor, Hierarchical)을 **설계 지식으로 참조** (references/pipeline-design.md에 포함)
6. Harness를 시스템/코드로 가져오지 않음

### 영향

- Phase C의 references/pipeline-design.md에 Harness 6가지 아키텍처 패턴 지식 포함
- Phase E의 references/execution.md에 bkit 패턴의 에이전트 실행 방식 적용
- Phase F는 bkit의 기존 에이전트(gap-detector, pdca-iterator, report-generator) 연동 설계 필요
- pipeline.json에 execution 섹션 추가 (agent, required_tools 매핑)

---

## 결정 2: 상태 관리

### 논의 과정

v1의 `.meta-pipe-status.json`이 이미 step 단위 추적을 하고 있었다. Phase E가 6개 step 파이프라인을 실행하는데, Phase 단위로만 재개하면 완료된 step까지 버리게 된다.

한편 Phase A~D는 대화형/단발성이라 중간 재개의 의미가 없고, Phase F도 평가 기준이 전체에 적용되므로 통째로 재실행이 자연스럽다.

### 결정

**Phase E만 step 단위 재개, 나머지(A~D, F)는 Phase 단위 재개.**

상태 스키마:

```json
{
  "session_id": "yt-thumb-2026-03-25",
  "domain": "유튜브 섬네일 자동화",
  "input_prompt": "유튜브 섬네일 자동화 워크플로우를 만들고 싶어",
  "complexity": "Standard",
  "current_phase": "E",
  "started_at": "2026-03-25T10:00:00Z",
  "updated_at": "2026-03-27T15:00:00Z",
  "phases": {
    "A": { "status": "completed", "completed_at": "..." },
    "B": { "status": "completed", "completed_at": "..." },
    "C": { "status": "completed", "completed_at": "..." },
    "D": { "status": "skipped", "reason": "Standard 레벨 - 사용자가 직접 완료" },
    "E": {
      "status": "in_progress",
      "current_step": "step-3",
      "steps": [
        { "id": "step-1", "status": "completed", "execution_mode": "assist" },
        { "id": "step-2", "status": "completed", "execution_mode": "assist" },
        { "id": "step-3", "status": "in_progress", "execution_mode": "auto" }
      ]
    },
    "F": { "status": "pending" }
  }
}
```

재개 로직: 세션 시작 시 `.meta-pipe-status.json`을 읽고, `current_phase` + `current_step`(E인 경우)에서 재개.

### 영향

- `.meta-pipe-status.json` 스키마에 `complexity`, `started_at`, `updated_at` 필드 추가
- Phase E의 `steps[]`에 `execution_mode` 필드 추가 (강등 추적용, 결정 6과 연동)
- SKILL.md 세션 재개 로직에서 이 스키마를 파싱

---

## 결정 3: 캐시

### 논의 과정

TTL 7일을 검토했으나, 도메인마다 지식의 유효 기간이 다르다. "YouTube API 스펙"은 6개월이 지나도 유효하고, "카드뉴스 디자인 트렌드"는 1주일이면 바뀔 수 있다. 일률적 TTL은 적합하지 않다.

또한 같은 도메인이라도 컨설팅에서 다른 경로를 선택하면 조사 방향이 달라지므로, 경로(path)별 캐시 분리가 필요하다.

### 결정

**TTL 없음. 명시적 무효화만. `consult_path_id`로 경로별 캐시 분리.**

구체적으로:
1. **캐시 대상**: Phase B(Discover) 결과만 (A는 대화형이라 캐시 불가, C~F는 B 결과에 의존)
2. **무효화 조건**: (1) 사용자가 `--refresh` 요청, (2) Phase A에서 선택 경로가 이전과 다를 때 SKILL.md가 재조사 권유
3. **저장 위치**: `runtime/cache/{domain-slug}/` (현재 구조 유지)
4. **저장 형식**: `discovery.json` + `discovery.md` + `cached_at.json` (현재와 동일)
5. `cached_at.json`에 `consult_path_id` 추가 — 같은 도메인이라도 경로가 다르면 캐시 미스

```json
// runtime/cache/{domain-slug}/cached_at.json
{
  "cached_at": "2026-03-25T11:00:00Z",
  "consult_path_id": "path-1-dalle-youtube-api",
  "domain": "유튜브 섬네일 자동화"
}
```

### 영향

- Phase B 시작 시 캐시 체크 로직: domain-slug 매칭 + consult_path_id 매칭
- `--refresh` 플래그를 SKILL.md 인터페이스에 추가
- 캐시 히트 시 Phase B를 건너뛰고 바로 Phase C로 진행

---

## 결정 4: 사용자 프로필

### 논의 과정

Plan 6절에서 마크다운 3파일 구조(capabilities.md, tools.md, preferences.md)를 제안했다. 그러나 Phase A2에서 프로그래머틱하게 읽고/갱신해야 하므로 마크다운보다 JSON이 적합하다. 또한 3파일 분리는 항상 3개를 다 읽어야 하므로 오버헤드만 추가된다.

LLM이 자연어로 프로필을 판단할 수 있도록 각 섹션에 `description` 필드를 둔다.

### 결정

**마크다운 3파일 → JSON 1파일 통합. `description` 필드로 LLM 친화성 확보.**

```json
// runtime/user-profile.json (단일 파일)
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

갱신 로직: Phase A2에서 기존 프로필 있으면 "변경된 것 있나요?" 한 번 물어보고, 변경분만 merge.

### 영향

- Plan 6절의 `runtime/user-profile/` 디렉토리 → `runtime/user-profile.json` 단일 파일로 변경
- Phase A2에서 프로필 CRUD 로직: 파일 존재 여부 체크 → 있으면 로드 + 변경분 질문 → merge 저장
- `.gitignore`에 `runtime/user-profile.json` 추가 (개인 정보)

---

## 결정 5: Phase 간 인터페이스 JSON Schema

### 논의 과정

Plan 4절에서 데이터 흐름을 상세히 정의했다. 그러나 도메인마다 산출물 내용이 다르다. "유튜브 섬네일"의 consult-result와 "블로그 글쓰기"의 consult-result는 `selected_path.tradeoffs` 내용이 완전히 다르다. strict한 JSON Schema로 가면 도메인마다 스키마를 확장해야 한다.

meta-pipe의 핵심은 "도메인 적응형"이므로, 스키마도 적응형이어야 한다.

### 결정

**최소 필수 필드 + 확장 허용. strict JSON Schema 검증 대신 필수 필드 존재 여부만 체크.**

각 산출물 JSON의 공통 구조:

```json
{
  "version": "2.0",
  "phase": "A",
  "created_at": "2026-04-01T10:00:00Z",
  "summary": "...(300자 이내, 다음 Phase가 최소한으로 알아야 할 것)",
  
  // Phase별 필수 필드 (Plan 3절에서 정의한 것 그대로)
  // 예: consult-result.json → requirements, user_profile, selected_path, eval_criteria, complexity
  // 예: discovery.json → domain_knowledge (glossary, workflows, tech_stack, data_model, risks)
  
  // 도메인별 확장 필드 허용
  "domain_specific": { }
}
```

검증 방식: SKILL.md에서 다음 Phase 진입 전 필수 필드 존재 여부만 체크. 필드 값의 형식은 검증하지 않음.

`summary` 필드는 결정 7(컨텍스트 관리)과 연동 — 다음 Phase가 이전 Phase 전체 JSON 대신 summary만 로드.

### 영향

- 각 산출물 JSON에 `version`, `phase`, `created_at`, `summary` 공통 헤더 추가
- Phase 전환 시 필수 필드 체크 로직 추가 (SKILL.md에서 구현)
- JSON Schema 파일을 별도로 관리하지 않음 (SKILL.md references에 필수 필드 목록만 기술)

---

## 결정 6: 에러 처리

### 논의 과정

meta-pipe의 실행 모드 시스템(auto/assist/manual)을 에러 처리에도 활용하면 v2 설계 철학("현실적으로 실행 가능한 파이프라인")과 일관된다. auto에서 실패하면 assist로, assist에서도 안 되면 manual로 강등하는 체인.

### 결정

**핵심 원칙: auto → assist → manual 강등 체인. 파이프라인 중단은 Phase A~C 치명적 실패 시만.**

| Phase | 에러 유형 | 전략 |
|-------|-----------|------|
| A (Consult) | 사용자 응답 부족 | 최대 2회 재질문, 이후 기본값으로 진행 |
| B (Discover) | WebSearch 실패 | 재시도 1회 → 캐시 fallback → 사용자에게 직접 정보 요청 (manual 강등) |
| C (Design) | Step 설계 실패 | 발생 가능성 낮음 (LLM 작업). 실패 시 사용자에게 보고 |
| D (Setup) | 도구 세팅 실패 | 자동 → 수동 가이드 제공 (assist/manual 강등). 실패 도구는 `setup-result.json`에 기록 |
| E (Execute) | step 실패 | **auto**: 재시도 1회 → assist 강등. **assist**: 재시도 1회 → manual 강등. **manual**: 가이드 재제공 |
| F (Evaluate) | 개선 루프 한도 초과 | 3회 루프 후 미달 → 해당 step을 manual로 강등, 사용자 판단 위임 |

전체 파이프라인 중단 조건: Phase A~C에서 치명적 실패 시 (예: 도메인 조사 완전 불가). Phase D~F는 강등으로 우회 가능하므로 중단하지 않음.

강등 이력은 `.meta-pipe-status.json`의 `steps[].execution_mode`에 기록 (결정 2와 연동).

### 영향

- Phase E의 step 실행 로직에 강등 체인 구현
- 강등 발생 시 `.meta-pipe-status.json` 업데이트 (원래 모드 → 강등 모드)
- Phase F의 개선 루프 카운터 (최대 3회) 구현
- 사용자에게 강등 알림 메시지 출력

---

## 결정 7: 컨텍스트 관리

### 논의 과정

Plan 11절에서 "컨텍스트 윈도우 초과"를 높음 리스크로 잡았다. meta-pipe는 6개 Phase를 거치면서 references + 이전 Phase 산출물 + 현재 Phase 프롬프트가 동시에 필요한데, 무분별하게 로드하면 컨텍스트가 폭발한다.

수량 기반 제한("Phase당 references 최대 2개")보다 토큰 예산 기반이 실용적이다. references 1개 + 이전 산출물 요약이면 ~3000 토큰으로 관리 가능하다.

### 결정

**Phase별 컨텍스트 격리 + 산출물 `summary` 필드 의무화. Phase당 ~3000 토큰 예산.**

Phase 시작 시 로드하는 것:
1. 해당 Phase의 references (1개, 최대 ~2000 토큰)
2. 직전 Phase 산출물의 `summary` 필드 (~500 토큰)
3. 원본 입력 — 사용자의 최초 요구사항 (~200 토큰)

Phase 시작 시 로드하지 않는 것:
- 다른 Phase의 references
- 이전 Phase 산출물의 전체 JSON (필요 시 Read 도구로 참조)

Phase별 references 매핑:
```
Phase A → references/consult.md
Phase B → references/discovery.md
Phase C → references/pipeline-design.md (Harness 6패턴 포함)
Phase D → references/setup.md
Phase E → references/execution.md (+ pipeline.json에서 해당 step만 추출)
Phase F → references/evaluation.md
```

Phase E 특수 사항: 개별 step 실행 시 pipeline.json 전체가 아니라 해당 step의 JSON 블록만 추출하여 에이전트 프롬프트에 포함. discovery.json도 `summary` + 해당 step의 `domain_warnings[]`만 포함.

### 영향

- 결정 5(인터페이스)에서 의무화한 `summary` 필드가 컨텍스트 관리의 핵심 메커니즘
- SKILL.md의 Phase 전환 로직에서 "이전 산출물 summary 로드" 구현
- Phase E의 에이전트 프롬프트 생성 시 step 단위 JSON 추출 로직
- references 작성 시 ~2000 토큰 가이드라인 준수

---

## 결정 8: pipeline.json execution 섹션 — Optional + Fallback 구조

### 논의 과정

결정 1(bkit 방식 채택)에서 "pipeline.json에 execution 섹션 추가"를 언급했으나, 두 가지 접근이 가능했다:

- **Option A (pipeline.json에 명시)**: Phase C가 step마다 `execution: { pattern, agent_type, delegation }` 필드를 설계 시 포함. 재현성 높고 bkit 통합 시 구조 명확.
- **Option B (execution.md에서 런타임 결정)**: Phase E가 required_tools와 execution_mode를 보고 그 자리에서 에이전트 구성 결정. 유연하지만 디버깅 어려움.

**bkit 통합 목표** 관점에서 Option A가 유리하다 — pipeline.json만 보면 실행 방식까지 파악 가능. 단, 도메인마다 적절한 패턴이 달라 Phase C에서 항상 확정하기 어려우므로 **optional + fallback** 구조를 채택.

### 결정

**execution 섹션은 optional 필드. Phase C가 확정 가능하면 포함, 없으면 references/execution.md가 런타임에 결정 (fallback).**

```json
// step 내 optional execution 섹션
{
  "id": "step-3",
  "execution_mode": "auto",
  "required_tools": ["dalle_api"],
  "execution": {                    // optional
    "pattern": "pipeline",          // Harness 6패턴: pipeline/fan-out/expert-pool/producer-reviewer/supervisor/hierarchical
    "agent_type": "tool-caller",    // conversational / tool-caller / researcher
    "delegation": "Task"            // Task (bkit Task()) vs Agent (Claude Agent())
  }
}
```

### 영향

- Phase C의 references/pipeline-design.md에 "execution 섹션 작성 가이드" 포함
- Phase E의 references/execution.md에 "execution 섹션 없을 때 fallback 결정 로직" 포함
- bkit 통합 시 pipeline.json의 execution 섹션을 그대로 읽어 Task() 호출 가능

---

## 결정 9: Phase C Adaptive Depth 결정 기준

### 논의 과정

Plan 3.3절 C1에서 "Adaptive Depth: 3~12단계"라고 명시했으나, 구체적인 결정 기준이 없었다. "도메인 복잡도에 따라"라는 설명만으로는 Phase C 구현 시 기준이 불명확하다.

Discovery(Phase B) 산출물에서 추출 가능한 정량적 요인으로 기준을 수립한다.

### 결정

**4가지 요인으로 step 수 범위 결정. 요인이 서로 다른 레벨을 가리킬 경우 가장 높은 레벨 채택.**

| 요인 | 3~5단계 (Light) | 6~8단계 (Standard) | 9~12단계 (Full) |
|------|:-:|:-:|:-:|
| 도메인 워크플로우 수 (B의 workflows) | 1~2개 | 3~5개 | 6개+ |
| required_tools 종류 수 | 0~1개 | 2~3개 | 4개+ |
| execution_mode 혼합도 | 전부 동일 | 2종 혼합 | 3종 혼합 |
| quality_expectation (A의 consult-result) | low/medium | medium/high | high |

예: 워크플로우 2개(Light)이지만 required_tools 4개(Full) → Full 기준으로 9~12단계.

### 영향

- references/pipeline-design.md에 Adaptive Depth 결정 기준표 포함
- Phase C 구현 시 B의 discovery.json을 파싱하여 4가지 요인 추출 후 step 수 결정

---

## 결정 10: Phase F와 bkit 연동 범위 명확화

### 논의 과정

결정 1에서 "Phase F = bkit의 PDCA Check-Act 재활용 (gap-detector, pdca-iterator)"이라고 했으나, 이 표현이 모호했다.

**meta-pipe에는 두 가지 평가 대상이 존재한다:**

1. **meta-pipe 본체** (docs/ 하위): meta-pipe 스킬 자체의 품질 → bkit gap-detector로 "Design 문서 vs 구현 코드" 검증
2. **meta-pipe가 생성한 파이프라인** (test/ 하위): 도메인별 eval_criteria 대비 산출물 검수 → Phase F 자체 로직

도메인별 평가 기준(eval_criteria)은 bkit이 알 수 없으므로, Phase F가 bkit 도구를 직접 호출하는 것은 부적합하다.

### 결정

**Phase F는 자체 evaluation.md 로직으로 검수/개선 루프를 돈다. bkit 도구(gap-detector, pdca-iterator)는 meta-pipe 스킬 자체를 개선할 때만 사용한다.**

| 대상 | 도구 | 범위 |
|------|------|------|
| meta-pipe 본체 (docs/) | bkit gap-detector, pdca-iterator | Design vs 코드 검증. meta-pipe 자체의 PDCA |
| 생성된 파이프라인 (test/) | Phase F evaluation.md 자체 로직 | eval_criteria vs 산출물 검수 |

### 영향

- references/evaluation.md는 bkit 도구를 호출하지 않고 자체 평가 루프 구현
- meta-pipe 본체의 PDCA (docs/ 하위)는 별도로 bkit PDCA로 관리

---

## 결정 11: 실행 모드 업그레이드 메커니즘 (manual -> assist -> auto)

### 논의 과정

v2 Design에 강등(auto→manual) 체인은 설계되었으나, 반대 방향인 업그레이드(manual→auto)가 없었다. meta-pipe의 핵심 가치 중 하나가 "반복할수록 자동화 수준이 올라가는 것"이라면, 이 메커니즘이 필요하다.

사용자의 세팅 능력/기술이 발전하면 이전에 manual이었던 step을 assist, 나아가 auto로 올릴 수 있어야 한다.

### 결정

**Phase C에서 이전 실행 이력 + 프로필 변경을 종합하여 업그레이드를 "제안"한다. 사용자 확인 후 적용.**

| 항목 | 결정 |
|------|------|
| 업그레이드 단위 | step별 (강등과 동일 단위) |
| 트리거 시점 | Phase C (파이프라인 설계 시) |
| 업그레이드 근거 | 실행 이력 + 프로필 변경 둘 다 |
| 사용자 확인 | 확인 후 업그레이드 (강등은 알림, 업그레이드는 제안) |

**업그레이드 규칙:**
- `success: true` + 강등 없이 성공 → 한 단계 업그레이드 후보
- `success: true` + 강등 후 성공 → 업그레이드 안 함 (강등이 필요했으므로)
- 동일 도메인 2회 이상 성공 시에만 제안 (1회는 우연일 수 있음)

**execution_history 필드를 user-profile.json에 추가:**

```json
{
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

### 영향

- user-profile.json 스키마에 `execution_history[]` 추가 (결정 4 확장)
- Phase C의 references/pipeline-design.md에 "업그레이드 후보 검출 + 제안" 로직 포함
- Phase F 완료 시 execution_history 기록 (references/evaluation.md에서 처리)
- Module 4(Phase C)와 Module 6(Phase F) 구현 시 반영 필요

---

## 비교 분석 참조 자료

- bkit 레포: https://github.com/popup-studio-ai/bkit-claude-code
- Harness 레포: https://github.com/revfactory/harness
- v1 Harness 통합 Plan: `archive/v1/docs/05-act/next-cycle/harness-integration.plan.md`
