# meta-pipe Gap Analysis

## 목적

- `meta-pipe` 본체 PDCA와 테스트 파이프라인 산출물이 서로 섞여 관리되던 문제를 정리한다.
- 현재 저장소 구조가 `meta-pipe` 개선 사이클과 테스트별 개선 사이클을 분리했는지 확인한다.

## 비교 기준

- Plan: `docs/01-plan/domain-discovery-pipeline.plan.md`
- Design: `docs/02-design/domain-discovery-pipeline.design.md`
- Implementation root: `skills/meta-pipe/`

## 확인된 문제

1. 기존 `docs/` 아래에 `meta-pipe` 본체 문서와 테스트 파이프라인 raw output이 함께 저장되어 PDCA 대상이 섞였다.
2. 테스트 파이프라인 자체를 개선하는 문서와 raw 산출물이 같은 위치에 놓여 테스트별 PDCA 사이클이 분리되지 않았다.
3. 보조 문서와 명령어 설명 일부가 기존 `docs/...` 경로를 계속 참조하고 있었다.

## 반영 결과

1. `meta-pipe` 본체 문서는 최상위 `docs/`로 분리했다.
2. 실제 실행 정본은 `skills/meta-pipe/`에 유지했다.
3. 테스트 파이프라인 raw output은 `test/{slug}/pipeline/`로 이동했다.
4. 테스트 파이프라인 개선 문서는 `test/{slug}/docs/`로 분리했다.
5. 경로 계약 문서를 새 구조에 맞게 수정했다.
   - `CLAUDE.md`
   - `skills/meta-pipe/SKILL.md`
   - `skills/meta-pipe/references/execution.md`
   - `.claude/commands/status.md`
   - `.claude/commands/test-domain.md`

## 남은 갭

1. `card-news` 테스트는 legacy 산출물 이관 상태라 `docs/`와 별개로 테스트용 `docs/01-plan`, `02-design`, `03-do` 문서가 아직 비어 있다.
2. 다음 사이클에서는 `docs/05-act/next-cycle/harness-integration.plan.md`를 기준으로 meta-pipe 본체를 확장해야 한다.

## 판단

- 구조 분리 목표는 달성됐다.
- 최상위 `docs/`는 `meta-pipe` 본체 개선 기록만 관리한다.
- 테스트 파이프라인은 `test/{slug}/pipeline/`와 `test/{slug}/docs/`로 분리되어 독립 PDCA 운용이 가능하다.
