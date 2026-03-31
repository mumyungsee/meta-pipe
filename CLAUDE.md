# meta-pipe

> 도메인 지식이 없어도 AI가 도메인을 조사하고, 그 도메인에 맞는 개발 파이프라인을 설계하고 실행하는 메타 파이프라인 프로젝트

## 프로젝트 상태

- 현재 단계: `meta-pipe` v1 문서/스킬 구현 완료, 테스트 파이프라인 2건 보관
- 최상위 PDCA: `docs/`
- 실제 스킬 정본: `skills/meta-pipe/`
- 테스트 파이프라인: `test/card-news/`, `test/youtube-thumbnail/`

## 구조 원칙

- `docs/`
  - `meta-pipe` 자체를 개선하는 문서만 둔다.
  - `01-plan` 기획, `02-design` 설계, `03-do` 구현 추적, `04-check` 갭 분석, `05-act` 회고/다음 사이클을 관리한다.
- `skills/meta-pipe/`
  - 실제 실행되는 `SKILL.md`와 `references/` 정본 위치다.
- `test/{slug}/pipeline/`
  - `meta-pipe`가 생성한 테스트 파이프라인 raw output을 둔다.
  - `domain-discovery.md`, `pipeline.md`, `pipeline.json`, `steps/`, `output/`를 포함한다.
- `test/{slug}/docs/`
  - 각 테스트 파이프라인을 별도 PDCA 사이클로 관리한다.

## 핵심 개념

```text
입력: "X를 만들고 싶어"
  -> Phase A: Discover
  -> Phase B: Design Pipeline
  -> Phase C: Execute

산출물:
  - meta-pipe 자체 개선 문서: docs/
  - 테스트 파이프라인 raw output: test/{slug}/pipeline/
  - 테스트 파이프라인 개선 문서: test/{slug}/docs/
```

## 현재 파일 구조

```text
meta-pipe/
├── CLAUDE.md
├── .meta-pipe-status.json
├── meta-pipe-cache/
├── meta-pipe-logs/
├── skills/
│   └── meta-pipe/
│       ├── SKILL.md
│       └── references/
├── docs/
│   ├── 01-plan/
│   ├── 02-design/
│   ├── 03-do/
│   ├── 04-check/
│   ├── 05-act/
│   └── status.json
└── test/
    ├── card-news/
    │   ├── pipeline/
    │   └── docs/
    └── youtube-thumbnail/
        ├── pipeline/
        └── docs/
```

## 문서 운영 규칙

- `meta-pipe` 본체 문서는 `docs/`에만 둔다.
- 테스트 파이프라인 계획/설계/검증/보고는 각 `test/{slug}/docs/`에서 따로 관리한다.
- 테스트 산출물은 `test/{slug}/pipeline/` 밖으로 섞지 않는다.
- 상태 추적:
  - 최상위 프로젝트: `docs/status.json`
  - 테스트별 상태: `test/{slug}/docs/status.json`
  - 실행 런타임 상태: `.meta-pipe-status.json`

## 다음 작업

- Harness 패턴 통합은 `docs/05-act/next-cycle/harness-integration.plan.md`에서 이어간다.
- 새 테스트 파이프라인은 항상 `test/{domain-slug}/pipeline/`에 만들고, 검증 문서는 `test/{domain-slug}/docs/`에 쌓는다.
