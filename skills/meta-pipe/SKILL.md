# meta-pipe

> 도메인 지식 없이도 AI가 컨설팅하고, 도구를 찾고, 실행 가능한 파이프라인을 설계하고, 결과를 검수/개선하는 루프까지 돌려주는 메타 파이프라인.

## 인수

| 인수 | 설명 | 예시 |
|------|------|------|
| (없음) | 새 파이프라인 시작 또는 중단된 세션 재개 | `/meta-pipe` |
| `--refresh` | Phase B 캐시 무시하고 도메인 재조사 강제 실행 | `/meta-pipe --refresh` |
| `--status` | 현재 세션 상태만 출력 (실행 없음) | `/meta-pipe --status` |

---

## 실행 흐름

이 파일(SKILL.md)은 **오케스트레이터**다. 각 Phase의 실제 로직은 `references/` 하위 파일에 위임한다. Phase 실행 시 해당 reference 파일만 로드하여 컨텍스트를 ~3000 토큰 이내로 유지한다.

```
사용자 입력
    |
    v
[1] 세션 재개 체크        → .meta-pipe-status.json 확인
    |
    v
[2] --status 플래그?      → 상태만 출력하고 종료
    |
    v
[3] 중단된 세션 있음?     → 재개 여부 확인 (AskUserQuestion)
    |
    v
[4] Phase 전환 루프       → A → B → C → D → E → F
    |                        (Light: D 생략)
    v
[5] 완료                  → evaluation-result.json 생성 완료
```

---

## 1단계: 세션 재개 체크

### 1.1 .meta-pipe-status.json 읽기

세션 시작 시 프로젝트 루트의 `.meta-pipe-status.json`을 Read 도구로 읽는다.

**파일 없음** → 새 세션 시작. Phase A로 진입.

**파일 있음** → `current_phase` 확인:

| current_phase | 재개 위치 |
|---------------|-----------|
| A, B, C, D, F | 해당 Phase 처음부터 재실행 |
| E | `current_step` 읽어서 해당 step부터 재개 |

**재개 확인 메시지** (AskUserQuestion):
```
이전 세션 '{domain}'이 Phase {current_phase}에서 중단되었습니다.
이어서 진행할까요?
```
- 예 → 해당 Phase부터 재개
- 아니오 → 새 세션 시작 (Phase A, 기존 상태 덮어쓰기)

### 1.2 --status 플래그 처리

`--status` 인수가 있으면 `.meta-pipe-status.json` 내용을 사람이 읽기 좋게 출력하고 종료:

```
현재 세션: {domain} ({session_id})
진행 상황: Phase {current_phase} ({complexity})
시작: {started_at}
마지막 업데이트: {updated_at}

Phase 상태:
  A (Consult):         {phases.A.status}
  B (Discover):        {phases.B.status}
  C (Design Pipeline): {phases.C.status}
  D (Setup):           {phases.D.status}
  E (Execute):         {phases.E.status} — 현재 step: {phases.E.current_step}
  F (Evaluate):        {phases.F.status}
```

---

## 2단계: Phase 전환 루프

각 Phase를 순서대로 실행한다. Phase 실행 전 아래 순서를 따른다:

1. `.meta-pipe-status.json`의 해당 Phase `status`가 `"completed"` 또는 `"skipped"`이면 건너뜀
2. 상태를 `"in_progress"`로 업데이트
3. 해당 `references/{phase}.md` 파일을 Read 도구로 로드
4. 이전 Phase의 `summary`를 로드 (아래 컨텍스트 로드 전략 참조)
5. reference 파일의 지시에 따라 Phase 실행
6. 완료 시 상태를 `"completed"`로 업데이트, `completed_at` 기록

### 2.1 Phase 순서 및 진입 조건

```
Phase A (Consult)
  └─ 항상 실행
  └─ 로드: references/consult.md + 원본 입력
  └─ 산출물: test/{domain-slug}/pipeline/consult-result.json

Phase B (Discover)
  └─ --refresh 있으면: 캐시 무시 → B 실행
  └─ 캐시 히트 시:
       runtime/cache/{domain-slug}/cached_at.json 읽기
       consult_path_id 일치? → 사용자에게 재사용 여부 확인
         Yes → Phase B 건너뛰기 (status: "skipped")
         No  → B 실행
  └─ 로드: references/discovery.md + A.summary
  └─ 산출물: test/{domain-slug}/pipeline/discovery.json + discovery.md
             runtime/cache/{domain-slug}/ (캐시 저장)

Phase C (Design Pipeline)
  └─ 항상 실행
  └─ 로드: references/pipeline-design.md + B.summary + A.summary(목표/역량)
  └─ 산출물: test/{domain-slug}/pipeline/pipeline.json + pipeline.md

Phase D (Setup)
  └─ complexity == "Light" → 건너뜀 (status: "skipped", reason: "Light 레벨 — Phase D 불필요")
  └─ 그 외 → 실행
  └─ 로드: references/setup.md + C.setup_requirements
  └─ 산출물: test/{domain-slug}/pipeline/setup-result.json

Phase E (Execute)
  └─ 항상 실행
  └─ step 단위 재개 지원 (아래 3단계 참조)
  └─ 로드: references/execution.md (Phase 시작 시 1회)
           + 각 step 실행 시: pipeline.json의 해당 step JSON + B.domain_warnings
  └─ 산출물: test/{domain-slug}/pipeline/steps/ + output/

Phase F (Evaluate)
  └─ 항상 실행
  └─ 로드: references/evaluation.md + A.eval_criteria + E 결과물 경로
  └─ 산출물: test/{domain-slug}/pipeline/evaluation-result.json
  └─ overall_pass == false → E로 돌아가 미달 step 재실행 (최대 3회)
```

### 2.2 복잡도(complexity) 결정

Phase A 완료 후 `consult-result.json`의 `complexity` 필드로 결정된다:

| complexity | Phase D | 예시 도메인 |
|------------|---------|------------|
| Light | 생략 | 블로그 글쓰기, 마케팅 카피 |
| Standard | 부분 실행 | 유튜브 섬네일, 카드뉴스 |
| Full | 전체 실행 | 영상 편집 자동화, 데이터 파이프라인 |

---

## 3단계: Phase E step 단위 재개

Phase E는 step이 여러 개이고 각각 오래 걸리므로 step 단위로 재개한다.

```
Phase E 시작
  |
  v
.meta-pipe-status.json의 phases.E.steps[] 확인
  |
  ├─ steps[] 없음 또는 비어있음
  |   → pipeline.json에서 steps[] 읽기
  |   → 첫 번째 step부터 실행
  |
  └─ steps[] 있음
      → current_step 찾기 (status: "in_progress")
      → 해당 step부터 재개
      → 이전 completed step들은 건너뜀
```

### 3.1 step 실행 순서

각 step 실행 시:

1. `.meta-pipe-status.json`의 `phases.E.steps`에서 해당 step status를 `"in_progress"`로 업데이트
2. `phases.E.current_step`을 현재 step ID로 업데이트
3. `references/execution.md`의 지시 + pipeline.json의 해당 step 블록으로 실행
4. 완료 시:
   - step status를 `"completed"`로 업데이트
   - `final_mode` 기록 (강등이 발생했다면 강등된 모드)
   - `completed_at` 기록
5. 다음 step으로 이동

---

## 4단계: 컨텍스트 로드 전략

Phase당 ~3000 토큰 예산을 지키기 위해 최소한의 컨텍스트만 로드한다.

### 4.1 Phase별 로드 대상

| Phase | 로드 대상 | 예상 토큰 |
|-------|----------|:---------:|
| A | references/consult.md + 원본 입력 | ~2200 |
| B | references/discovery.md + A.summary | ~2500 |
| C | references/pipeline-design.md + B.summary + A.summary(목표/역량) | ~3000 |
| D | references/setup.md + C.setup_requirements | ~2500 |
| E (Phase 시작) | references/execution.md | ~1500 |
| E (step 실행) | 해당 step JSON + B.domain_warnings + 원본 입력 | ~1000 |
| F | references/evaluation.md + A.eval_criteria + E 결과물 경로 | ~2800 |

### 4.2 summary 로드 방법

각 Phase의 `summary`는 해당 산출물 JSON의 최상위 `summary` 필드에서 읽는다:

```
A.summary → test/{domain-slug}/pipeline/consult-result.json의 .summary
B.summary → test/{domain-slug}/pipeline/discovery.json의 .summary
C.summary → test/{domain-slug}/pipeline/pipeline.json의 .summary
D.summary → test/{domain-slug}/pipeline/setup-result.json의 .summary
```

**원칙**: 이전 Phase의 JSON 전체를 로드하지 않는다. `summary` 필드(300자 이내)만 읽는다.

---

## 5단계: 상태 관리

### 5.1 .meta-pipe-status.json 스키마

```json
{
  "session_id": "{domain-slug}-{YYYY-MM-DD}",
  "domain": "사용자가 입력한 도메인 명칭",
  "domain_slug": "kebab-case-slug",
  "input_prompt": "사용자의 원본 입력",
  "complexity": "Light | Standard | Full",
  "current_phase": "A | B | C | D | E | F",
  "started_at": "ISO 8601",
  "updated_at": "ISO 8601",
  "phases": {
    "A": { "status": "pending | in_progress | completed" },
    "B": { "status": "pending | in_progress | completed | skipped", "reason": "(skipped 시 사유)" },
    "C": { "status": "pending | in_progress | completed" },
    "D": { "status": "pending | in_progress | completed | skipped", "reason": "(skipped 시 사유)" },
    "E": {
      "status": "pending | in_progress | completed",
      "current_step": "step-N",
      "steps": [
        {
          "id": "step-1",
          "status": "pending | in_progress | completed",
          "execution_mode": "auto | assist | manual",
          "original_mode": "auto | assist | manual",
          "completed_at": "ISO 8601",
          "degradation_reason": "(강등 발생 시 사유)"
        }
      ]
    },
    "F": { "status": "pending | in_progress | completed" }
  }
}
```

### 5.2 상태 업데이트 시점

| 이벤트 | 업데이트 필드 |
|--------|-------------|
| Phase 시작 | `phases.{X}.status = "in_progress"`, `current_phase`, `updated_at` |
| Phase 완료 | `phases.{X}.status = "completed"`, `phases.{X}.completed_at`, `updated_at` |
| Phase 생략 | `phases.{X}.status = "skipped"`, `phases.{X}.reason`, `updated_at` |
| step 시작 (E) | `phases.E.steps[i].status = "in_progress"`, `phases.E.current_step`, `updated_at` |
| step 완료 (E) | `phases.E.steps[i].status = "completed"`, `final_mode`, `completed_at`, `updated_at` |
| step 강등 (E) | `phases.E.steps[i].execution_mode` (강등된 모드), `original_mode`, `degradation_reason` |

**업데이트 방법**: Write 도구로 `.meta-pipe-status.json` 전체를 덮어쓴다. 부분 업데이트 없음.

---

## 6단계: 캐시 처리 (--refresh)

```
--refresh 플래그 있음?
  |
  ├─ Yes → Phase B 실행 시 runtime/cache/{domain-slug}/ 무시
  |         조사 완료 후 캐시 덮어쓰기
  |
  └─ No  → 정상 캐시 히트/미스 체크 (2단계 Phase B 참조)
```

### 6.1 캐시 저장 (Phase B 완료 시)

```
Write: runtime/cache/{domain-slug}/cached_at.json
  {
    "cached_at": "ISO 8601",
    "consult_path_id": "{A에서 선택된 경로 ID}",
    "domain": "{domain}"
  }

Write: runtime/cache/{domain-slug}/discovery.json (B 산출물 복사)
Write: runtime/cache/{domain-slug}/discovery.md   (B 산출물 복사)
```

---

## 산출물 경로 요약

| 파일 | 경로 |
|------|------|
| 실행 상태 | `.meta-pipe-status.json` |
| 사용자 프로필 | `runtime/user-profile.json` |
| 캐시 메타 | `runtime/cache/{domain-slug}/cached_at.json` |
| 캐시 조사 결과 | `runtime/cache/{domain-slug}/discovery.json` + `.md` |
| 컨설팅 결과 | `test/{domain-slug}/pipeline/consult-result.json` |
| 도메인 조사 | `test/{domain-slug}/pipeline/discovery.json` + `.md` |
| 파이프라인 설계 | `test/{domain-slug}/pipeline/pipeline.json` + `.md` |
| 세팅 결과 | `test/{domain-slug}/pipeline/setup-result.json` |
| step 산출물 | `test/{domain-slug}/pipeline/steps/` |
| 최종 결과물 | `test/{domain-slug}/pipeline/output/` |
| 검수 결과 | `test/{domain-slug}/pipeline/evaluation-result.json` |

---

## Design References

- Design 문서: `docs/02-design/v2-design.md`
- 결정 사항: `docs/00-ideation/2026-04-01-v2-design-decisions.md`
- Plan: `docs/01-plan/v2-plan.md`

<!-- Design Ref: §2 Architecture — Option C (단일 SKILL + references 지연 로딩) -->
<!-- Design Ref: §4 상태 관리 — Phase E step 단위 재개, 나머지 Phase 단위 -->
<!-- Design Ref: §5 캐시 — consult_path_id 기반 경로별 캐시 분리, TTL 없음 -->
<!-- Design Ref: §7 컨텍스트 관리 — Phase당 ~3000 토큰, summary 체인 -->
<!-- Design Ref: §8.6 업그레이드 — Phase C에서 execution_history 참조 (references/pipeline-design.md에서 구현) -->
