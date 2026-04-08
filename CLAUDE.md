# meta-pipe

> 도메인 지식이 없어도 AI가 검증된 사례를 찾아서 사용자 상황에 맞게 적용하고, PDCA 사이클로 검증/개선하는 메타 파이프라인 프로젝트. bkit 플러그인으로 통합 목표.

## 프로젝트 상태

- 현재 버전: v3 (v1, v2는 `archive/`에 보존)
- 현재 단계: **module-2 테스트 완료 (T-01 Pass), module-3 구현 대기**
- 핵심 변경: "처음부터 생성" → "검증된 사례 검색 + 적용"
- Plan 문서: `docs/01-plan/features/meta-pipe-v3.plan.md`
- Design 문서: `docs/02-design/features/meta-pipe-v3.design.md`

## 버전 히스토리 참조

| 버전 | 핵심 교훈 | 참조 문서 |
|------|----------|----------|
| v1 | 사용자 맥락 없이 파이프라인 생성 → 실행 불가 | `archive/v1/README.md` |
| v2 | Phase별 테스트 없이 전체 구현 → Phase A 결함이 전체 흔들림 | `archive/v2/docs/00-ideation/` |
| v2→v3 | 왜 v3인지, 무엇을 carry over했는지 | `docs/00-ideation/2026-04-07-v3-kickoff.md` |
| v3 피봇 | "처음부터 생성" → "사례 기반 검색+적용"으로 전환 | `docs/00-ideation/2026-04-08-v3-pivot-to-case-based.md` |

## v3 핵심 가설

> 검증된 사례를 잘 찾아서 사용자 상황에 맞게 적용하면, 도메인 모르는 사용자도 결과를 예측하고 납득한 뒤 실행할 수 있는가

## v3 핵심 개념

```text
입력: "X를 만들고 싶어"
  -> Phase A: Consult  (목표 + 제약 조건 + 결과물 형태 수집)
  -> Phase B: Search   (지정 사이트에서 검증된 사례 검색 + 결과 예시 제시)
  -> Phase C: Adapt    (선택한 사례를 내 상황에 맞게 수정/파이프라인화)
  -> Phase E: Execute  (실행)

검색 소스 (site: 연산자):
  - github.com    → 실행 가능한 코드/오픈소스 레포
  - threads.net   → 실제 사용 후기/팁
  - gpters.org    → 검증된 사례 + 실행 결과

Step별 실행 모드:
  - auto:   AI가 자동 실행
  - assist: AI 초안 + 사람 검수
  - manual: 사람 실행, AI 가이드
```

## 구조 원칙

- `docs/`
  - `meta-pipe` 자체를 개선하는 문서만 둔다.
  - `00-ideation` 아이데이션/회의록, `01-plan` 전체 기획, `02-design` 전체 설계를 관리한다.
  - `03-do` 구현 추적 — **모듈별 폴더**에서 자체 mini-PDCA 사이클을 돌린다.
  - `04-check`, `05-act`는 프로젝트 전체 레벨 회고용.
- `docs/03-do/{module명}/`
  - 각 모듈의 plan.md, analysis.md, report.md 등 문서를 관리한다.
  - 스킬 파일(SKILL.md, references/*.md)은 실행 위치(`skills/meta-pipe/`)에 두고, 문서만 여기에 넣는다.
  - 예: `docs/03-do/module-2-phase-a/plan.md`, `docs/03-do/module-2-phase-a/analysis.md`
- `skills/meta-pipe/`
  - 실제 실행되는 `SKILL.md`와 `references/` 정본 위치다.
- `.claude/skills/meta-pipe/`
  - CC 스킬 등록용 wrapper (frontmatter 포함). `skills/meta-pipe/SKILL.md`를 참조.
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
├── .claude/
│   └── skills/
│       └── meta-pipe/
│           └── SKILL.md          # CC 스킬 등록 (frontmatter)
├── archive/
│   ├── v1/
│   └── v2/
├── docs/
│   ├── 00-ideation/
│   ├── 01-plan/
│   │   └── features/
│   │       └── meta-pipe-v3.plan.md
│   ├── 02-design/
│   │   └── features/
│   │       └── meta-pipe-v3.design.md
│   ├── 03-do/                    # 모듈별 mini-PDCA
│   │   └── module-2-phase-a/
│   │       ├── plan.md
│   │       └── analysis.md
│   ├── 04-check/
│   └── 05-act/
├── skills/
│   └── meta-pipe/
│       ├── SKILL.md              # 오케스트레이터 (실행 정본)
│       └── references/
│           └── consult.md        # Phase A
├── test/
│   └── lecture-wiki-automation/  # T-01 테스트 산출물
│       └── pipeline/
│           └── consult.json
```

## 문서 운영 규칙

- `meta-pipe` 본체 문서는 `docs/`에만 둔다.
- 테스트 파이프라인 계획/설계/검증/보고는 각 `test/{slug}/docs/`에서 따로 관리한다.
- 테스트 산출물은 `test/{slug}/pipeline/` 밖으로 섞지 않는다.
- 상태 추적:
  - 테스트별 상태: `test/{slug}/docs/status.json`
  - 실행 런타임 상태: `.meta-pipe-status.json`

## 결정 사항

> 상세 근거: `docs/00-ideation/2026-04-08-v3-pivot-to-case-based.md` 섹션 11 참조

- **D1**: B안(사례 기반) 피봇 — 사용자 실제 행동 패턴과 일치
- **D2**: Phase B = Search (사례 검색) — Discover에서 변경
- **D3**: Phase C = Adapt (사례 적용) — Design에서 변경
- **D4**: Phase A에 제약 조건 수집 추가 — 사례 라이브러리 충돌 방지
- **D5**: v3 사용자 = 나 한 명 — 스코프 제한
- **D6**: 사이트 지정 AI 검색 채택 — site: 연산자 활용
- **D7**: 각 Phase 산출물은 반드시 문서(JSON/MD)로 남김 — 핵심 차별점
- v3 제외 항목: 사용자 프로필, 캐시, 세션 재개, 강등/업그레이드, 복잡도 레벨 분기

## 구현 진행 상황

| Module | Scope | 상태 | 산출물 |
|--------|-------|------|--------|
| module-1 | SKILL.md 기본 구조 | ✅ 완료 | `skills/meta-pipe/SKILL.md` |
| module-2 | Phase A (Consult) | ✅ 테스트 통과 (T-01) | `references/consult.md` |
| module-3 | Phase B (Search) | 대기 | `references/search.md` |
| module-4 | Phase C (Adapt) | 대기 | `references/adapt.md` |
| module-5 | Phase E (Execute) | 대기 | `references/execute.md` |
| module-6 | 테스트 + 개선 | 대기 | end-to-end 검증 |

## 개발 방법론 (v3부터 적용)

- **Phase별 PDCA**: 각 Phase 구현 후 테스트 통과해야 다음 Phase 시작
- **테스트 방법**: 실제 테스트 도메인으로 `/meta-pipe` 직접 실행 + 사람이 결과 판단
- **작은 단위**: 바이브코딩은 단위를 작게 잘라서 구현 + 테스트 반복
- **Plan에 테스트 기준 포함**: Phase마다 "완료 기준 + 테스트 방법" 명시

## 다음 작업

- ~~우선순위 1: v3 Plan 문서 작성~~ ✅ 완료 (`docs/01-plan/features/meta-pipe-v3.plan.md`)
- ~~우선순위 1: v3 Design 문서 작성~~ ✅ 완료 (`docs/02-design/features/meta-pipe-v3.design.md`)
- ~~module-1: SKILL.md 오케스트레이터~~ ✅ 완료
- ~~module-2: consult.md 구현~~ ✅ 완료
- ~~module-2 테스트 (T-01)~~ ✅ 통과 — Phase A 동작 확인, consult.json 스키마 100% 일치
- **우선순위 1: module-3 구현 (Phase B: Search)** — `docs/03-do/module-3-phase-b/` 에서 PDCA
- 우선순위 3: meta-pipe 자체를 만드는 과정이 첫 번째 테스트 케이스

## 주의 사항

- **반복 패턴 경고**: "만들어도 완성도 부족 → 버림 → 남이 만든 것 사용" 패턴 반복 위험
- **대응**: 최소 사용 가능 버전 먼저 정의, 첫 테스트를 빨리 실행
- **스코프 엄수**: v3 사용자는 "나" 한 명. 스터디/앰버서더/생태계는 v3 이후
