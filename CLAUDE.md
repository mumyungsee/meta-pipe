# meta-pipe

> 도메인 지식이 없어도 AI가 컨설팅하고, 적절한 도구를 찾고, 실행 가능한 파이프라인을 설계하고, 결과를 검수/개선하는 루프까지 돌려주는 메타 파이프라인 프로젝트

## 프로젝트 상태

- 현재 버전: v3 (v1, v2는 `archive/`에 보존)
- 현재 단계: v3 설계 시작
- Plan 문서: `docs/01-plan/` (작성 예정)
- Design 문서: `docs/02-design/` (작성 예정)

## v3 핵심 가설

> 인터뷰를 제대로 하면, 도메인 모르는 사용자가 납득하고 선택할 수 있는 파이프라인이 나오는가

## v3 핵심 개념

```text
입력: "X를 만들고 싶어"
  -> Phase A: Consult  (목표 + 결과물 형태 수집 + 결과물 예시 포함한 경로 제안)
  -> Phase B: Discover (도메인 조사 — 컨설팅 결과 반영)
  -> Phase C: Design   (파이프라인 설계 — step별 실행 모드 태깅)
  -> Phase E: Execute  (실행)

Step별 실행 모드:
  - auto:   AI가 자동 실행
  - assist: AI 초안 + 사람 검수
  - manual: 사람 실행, AI 가이드
```

## 구조 원칙

- `docs/`
  - `meta-pipe` 자체를 개선하는 문서만 둔다.
  - `00-ideation` 아이데이션/회의록, `01-plan` 기획, `02-design` 설계, `03-do` 구현 추적, `04-check` 갭 분석, `05-act` 회고/다음 사이클을 관리한다.
- `skills/meta-pipe/`
  - 실제 실행되는 `SKILL.md`와 `references/` 정본 위치다.
- `test/{slug}/pipeline/`
  - `meta-pipe`가 생성한 테스트 파이프라인 raw output을 둔다.
- `test/{slug}/docs/`
  - 각 테스트 파이프라인을 별도 PDCA 사이클로 관리한다.
- `archive/v1/`, `archive/v2/`
  - 이전 버전 보존. 각 버전 README 참조.

## 현재 파일 구조

```text
meta-pipe/
├── CLAUDE.md
├── archive/
│   ├── v1/
│   └── v2/
├── docs/
│   ├── 00-ideation/
│   ├── 01-plan/
│   ├── 02-design/
│   ├── 03-do/
│   ├── 04-check/
│   └── 05-act/
├── skills/
│   └── meta-pipe/
│       └── references/
└── test/
```

## 문서 운영 규칙

- `meta-pipe` 본체 문서는 `docs/`에만 둔다.
- 테스트 파이프라인 계획/설계/검증/보고는 각 `test/{slug}/docs/`에서 따로 관리한다.
- 테스트 산출물은 `test/{slug}/pipeline/` 밖으로 섞지 않는다.
- 상태 추적:
  - 테스트별 상태: `test/{slug}/docs/status.json`
  - 실행 런타임 상태: `.meta-pipe-status.json`

## 결정 사항

- 스코프: Phase A, B, C, E (Phase D, F는 가설 검증 후 추가)
- Phase 순서: Consult(A) -> Discover(B) -> Design(C) -> Execute(E)
- v3 제외 항목: 사용자 프로필, 캐시, 세션 재개, 강등/업그레이드, 복잡도 레벨 분기

## 구현 진행 상황

| Module | Scope | 상태 | 산출물 |
|--------|-------|------|--------|
| module-1 | SKILL.md 기본 구조 | 대기 | `skills/meta-pipe/SKILL.md` |
| module-2 | Phase A (Consult) | 대기 | `references/consult.md` |
| module-3 | Phase B (Discover) | 대기 | `references/discovery.md` |
| module-4 | Phase C (Design) | 대기 | `references/pipeline-design.md` |
| module-5 | Phase E (Execute) | 대기 | `references/execution.md` |
| module-6 | 테스트 + 개선 | 대기 | end-to-end 검증 |

## 다음 작업

- 우선순위 1: v3 Plan 문서 작성 (`docs/01-plan/`)
- 우선순위 2: v3 Design 문서 작성 (`docs/02-design/`)
