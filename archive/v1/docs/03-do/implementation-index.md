# meta-pipe Implementation Index

## 목적

- 최상위 `docs/03-do/`는 `meta-pipe` 본체 구현 추적 문서만 관리한다.
- 실제 실행 정본은 계속 `skills/meta-pipe/`에 둔다.

## 정본 구현 경로

- `skills/meta-pipe/SKILL.md`
- `skills/meta-pipe/references/discovery.md`
- `skills/meta-pipe/references/pipeline-design.md`
- `skills/meta-pipe/references/execution.md`

## 구현 추적 규칙

- `meta-pipe` 본체 구조 변경은 먼저 `docs/01-plan`, `docs/02-design` 문서에 반영한다.
- 구현 완료 후 이 파일에 정본 경로와 변경 요약을 기록한다.
- 테스트 파이프라인 raw output은 여기서 관리하지 않는다.

## 현재 반영 상태

- Cycle 1
  - 계획 문서: `docs/01-plan/domain-discovery-pipeline.plan.md`
  - 설계 문서: `docs/02-design/domain-discovery-pipeline.design.md`
  - 정본 구현: `skills/meta-pipe/`
  - 테스트 출력 규약:
    - Phase A: `test/{domain-slug}/pipeline/domain-discovery.md`
    - Phase B: `test/{domain-slug}/pipeline/pipeline.md`, `test/{domain-slug}/pipeline/pipeline.json`
    - Phase C: `test/{domain-slug}/pipeline/steps/`, `test/{domain-slug}/pipeline/output/`

## 메모

- `meta-pipe` 자체 갭 분석 문서는 향후 `docs/04-check/`에 기록한다.
- 다음 사이클 계획은 `docs/05-act/next-cycle/`에서 관리한다.
