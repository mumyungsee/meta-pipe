# meta-pipe

> 도메인 지식이 없어도 AI가 컨설팅하고, 적절한 도구를 찾고, 실행 가능한 파이프라인을 설계하고, 결과를 검수/개선하는 루프까지 돌려주는 메타 파이프라인 프로젝트

## 프로젝트 상태

- 현재 버전: v2 (v1은 `archive/v1/`에 보존)
- 현재 단계: v2 Do(구현) 진행 중 — module-1, module-2 완료
- 아이데이션 기록: `docs/00-ideation/2026-04-01-v2-redesign.md`
- Design 미결 사항 결정: `docs/00-ideation/2026-04-01-v2-design-decisions.md`
- Plan 문서: `docs/01-plan/v2-plan.md`
- Design 문서: `docs/02-design/v2-design.md`
- GitHub Issues: 27개 생성 완료 (8개 Milestone)

## v2 핵심 개념

```text
입력: "X를 만들고 싶어"
  -> Phase A: Consult (컨설팅 — 목표, 환경, 역량, 평가 기준 수립)
  -> Phase B: Discover (도메인 조사 — 컨설팅 결과 반영)
  -> Phase C: Design Pipeline (파이프라인 설계 — step별 실행 모드 태깅)
  -> Phase D: Setup (도구 세팅 — 레벨에 따라 생략 가능)
  -> Phase E: Execute (실행)
  -> Phase F: Evaluate & Improve (검수/개선 루프)

Step별 실행 모드:
  - auto: AI가 자동 실행
  - assist: AI 초안 + 사람 검수
  - manual: 사람 실행, AI 가이드

복잡도 레벨:
  - Light: 도구 세팅 불필요
  - Standard: 일부 세팅 필요
  - Full: 인프라 구축 수준
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
- `archive/v1/`
  - v1의 docs/, skills/ 보존. v1에서 배운 것은 `archive/v1/README.md` 참조.

## 현재 파일 구조

```text
meta-pipe/
├── CLAUDE.md
├── .meta-pipe-status.json
├── archive/
│   └── v1/
│       ├── docs/
│       ├── skills/
│       └── README.md
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
├── test/
│   ├── card-news/
│   │   ├── pipeline/
│   │   └── docs/
│   └── youtube-thumbnail/
│       ├── pipeline/
│       └── docs/
└── runtime/
    ├── cache/
    └── logs/
```

## 문서 운영 규칙

- `meta-pipe` 본체 문서는 `docs/`에만 둔다.
- 테스트 파이프라인 계획/설계/검증/보고는 각 `test/{slug}/docs/`에서 따로 관리한다.
- 테스트 산출물은 `test/{slug}/pipeline/` 밖으로 섞지 않는다.
- 상태 추적:
  - 테스트별 상태: `test/{slug}/docs/status.json`
  - 실행 런타임 상태: `.meta-pipe-status.json`
  - 캐시: `runtime/cache/`
  - 실행 로그: `runtime/logs/`

## 결정 사항

- 스코프: Phase A~F 전체 재설계 (설계는 전체, 구현은 Phase A부터 순차)
- Phase 순서: Consult(A) -> Discover(B) -> Design Pipeline(C) -> Setup(D) -> Execute(E) -> Evaluate(F)
- 테스트 도메인: Plan 단계에서 결정

## 구현 진행 상황

| Module | Scope | 상태 | 산출물 |
|--------|-------|------|--------|
| module-1 | SKILL.md 기본 구조 | 완료 | `skills/meta-pipe/SKILL.md` |
| module-2 | Phase A (Consult) | 완료 | `skills/meta-pipe/references/consult.md` |
| module-3 | Phase B (Discover) | 완료 | `references/discovery.md` |
| module-4 | Phase C (Design Pipeline) | 대기 | `references/pipeline-design.md` |
| module-5 | Phase D+E (Setup+Execute) | 대기 | `references/setup.md`, `execution.md` |
| module-6 | Phase F (Evaluate) | 대기 | `references/evaluation.md` |
| module-7 | 테스트 + 개선 | 대기 | end-to-end 검증 |

## 다음 작업

- 우선순위 1: `/pdca do v2-design --scope module-3` — Phase B (Discover) 구현
- 우선순위 2: GitHub Project 보드 셋업 (권한 추가 필요: `gh auth refresh -s read:project -s project`)
