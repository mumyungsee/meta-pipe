# meta-pipe v3 Gap Analysis

> **Feature**: meta-pipe-v3
> **Date**: 2026-04-08
> **Phase**: Check (Gap Analysis)
> **Design Doc**: [meta-pipe-v3.design.md](../02-design/features/meta-pipe-v3.design.md)
> **Match Rate**: **33%** (8/24 항목 완료)

---

## 목차

- [Executive Summary](#executive-summary)
- [1. File Structure Gap](#1-file-structure-gap)
- [2. Functional Requirements Gap](#2-functional-requirements-gap)
- [3. Data Model Gap](#3-data-model-gap)
- [4. Phase Detail Gap](#4-phase-detail-gap)
- [5. Test Plan Gap](#5-test-plan-gap)
- [6. Unplanned Items](#6-unplanned-items)
- [7. Summary](#7-summary)

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Feature** | meta-pipe v3 — 사례 기반 메타 파이프라인 |
| **Analysis Date** | 2026-04-08 |
| **Match Rate** | **33%** (8/24) |
| **Status** | module-1, module-2 완료 / module-3~6 미착수 |

| Category | Total | Match | Gap | Rate |
|----------|-------|-------|-----|------|
| File Structure | 5 | 2 | 3 | 40% |
| Functional Requirements | 11 | 3 | 8 | 27% |
| Data Model | 4 | 1 | 3 | 25% |
| Phase Detail (Phase A) | 4 | 4 | 0 | 100% |
| Test Plan | 6 | 1 | 5 | 17% |
| **Total** | **24** | **8** | **16** | **33%** |

> **참고**: 이 Match Rate는 전체 설계 대비 현재 구현 상태를 반영합니다. module-2까지만 구현한 상태이므로 낮은 비율은 예상된 결과입니다. Phase A 단독으로는 100% 매칭됩니다.

---

## 1. File Structure Gap

Design 문서 Section 2.2에서 정의한 파일 구조 대비:

| File | Design | Implementation | Status |
|------|--------|---------------|--------|
| `skills/meta-pipe/SKILL.md` | 오케스트레이터 | ✅ 존재, 전체 Phase 흐름 정의 | ✅ Match |
| `skills/meta-pipe/references/consult.md` | Phase A 프롬프트 | ✅ 존재, 인터뷰 흐름 구현 | ✅ Match |
| `skills/meta-pipe/references/search.md` | Phase B 프롬프트 | ❌ 미존재 | ❌ Gap |
| `skills/meta-pipe/references/adapt.md` | Phase C 프롬프트 | ❌ 미존재 | ❌ Gap |
| `skills/meta-pipe/references/execute.md` | Phase E 프롬프트 | ❌ 미존재 | ❌ Gap |

**Gap 파일 3개**: search.md, adapt.md, execute.md (module-3, 4, 5에 해당)

---

## 2. Functional Requirements Gap

Plan 문서 Section 3.1에서 정의한 기능 요구사항 대비:

| ID | Requirement | Status | Notes |
|----|-------------|--------|-------|
| FR-01 | Phase A: 대화형 인터뷰 → consult.json | ✅ Match | T-01 테스트 통과 |
| FR-02 | Phase A: 제약 조건으로 검색 범위 필터링 | ✅ Match | consult.json의 excluded 필드 |
| FR-03 | Phase B: 3개 사이트 검색 | ❌ Gap | search.md 미구현 |
| FR-04 | Phase B: WebFetch 상세 수집 + 요약 | ❌ Gap | search.md 미구현 |
| FR-05 | Phase B: 사용자 사례 선택 | ❌ Gap | search.md 미구현 |
| FR-06 | Phase B→C: 실행 가능성 판단 | ❌ Gap | search.md 미구현 |
| FR-07 | Phase C: 사례 적용/수정 | ❌ Gap | adapt.md 미구현 |
| FR-08 | Phase C: 파이프라인화 | ❌ Gap | adapt.md 미구현 |
| FR-09 | Phase E: 파이프라인 실행 | ❌ Gap | execute.md 미구현 |
| FR-10 | 각 Phase 산출물 문서 저장 | 🔶 Partial | Phase A만 저장 동작 확인 |
| FR-11 | SKILL.md 오케스트레이터 | ✅ Match | Phase 전체 흐름 정의됨 |

**Match: 3/11 (27%)** — FR-01, FR-02, FR-11 완료. FR-10 부분 완료.

---

## 3. Data Model Gap

Design 문서 Section 3에서 정의한 데이터 모델 대비:

| Schema | Design | Implementation | Status |
|--------|--------|---------------|--------|
| `consult.json` (3.1) | goal, goal_refined, constraints, deliverable, search_keywords | ✅ T-01 출력이 스키마와 일치 | ✅ Match |
| `search-results.json` (3.2) | queries, results, selected | ❌ Phase B 미구현 | ❌ Gap |
| `pipeline.json` (3.3) | original, adaptations, steps | ❌ Phase C 미구현 | ❌ Gap |
| `execution-log.json` (3.4) | steps_completed, final_result | ❌ Phase E 미구현 | ❌ Gap |

**Match: 1/4 (25%)**

### consult.json 스키마 검증

T-01 테스트에서 생성된 `test/lecture-wiki-automation/pipeline/consult.json` 검증:

| Field | Design Schema | Actual Output | Match |
|-------|--------------|---------------|-------|
| `goal` | string (사용자 원문) | ✅ 사용자 원문 포함 | ✅ |
| `goal_refined` | string (AI 정리) | ✅ AI 정리 한 줄 | ✅ |
| `constraints.stack` | string[] | ✅ 배열 형태 | ✅ |
| `constraints.tools` | string[] | ✅ 배열 형태 | ✅ |
| `constraints.capabilities` | enum | ✅ "beginner" | ✅ |
| `constraints.budget` | string \| null | ✅ "무료 도구만" | ✅ |
| `constraints.excluded` | string[] | ✅ ["유료 API"] | ✅ |
| `deliverable` | string | ✅ 존재 | ✅ |
| `search_keywords` | string[] (3~5개) | ✅ 3개 | ✅ |

**consult.json 스키마 일치율: 100%**

---

## 4. Phase Detail Gap

### 4.1 Phase A — Consult (✅ 100%)

Design Section 4.1에서 정의한 Phase A 상세 대비:

| Item | Design | Implementation | Status |
|------|--------|---------------|--------|
| 인터뷰 흐름 (최대 3라운드, 2개/라운드) | ✅ consult.md에 정의 | T-01에서 2라운드 + 확인으로 동작 | ✅ Match |
| "모르겠어" 기본값 처리 | ✅ 기본값 테이블 정의 | consult.md Section 3 | ✅ Match |
| 사용자 확인 후 저장 | ✅ 확인 → 수정 → 재확인 | T-01에서 수정 1회 후 확인 동작 | ✅ Match |
| search_keywords 자동 생성 | ✅ 생성 규칙 정의 | T-01에서 3개 키워드 생성 | ✅ Match |

### 4.2 Phase B — Search (❌ 0%)

search.md 미구현. 설계 항목 전체 Gap.

### 4.3 Phase C — Adapt (❌ 0%)

adapt.md 미구현. 설계 항목 전체 Gap.

### 4.4 Phase E — Execute (❌ 0%)

execute.md 미구현. 설계 항목 전체 Gap.

---

## 5. Test Plan Gap

Design 문서 Section 7.2에서 정의한 테스트 케이스 대비:

| ID | Phase | Scenario | Status | Notes |
|----|-------|----------|--------|-------|
| T-01 | A | "bkit 플러그인 만들고 싶어" 입력 | ✅ Pass | 다른 도메인("강의 위키 자동화")으로 실행, consult.json 3요소 포함 확인 |
| T-02 | B | consult.json 기반 검색 실행 | ❌ Not Tested | search.md 미구현 |
| T-03 | B→C | 선택 사례 실행 가능성 판단 | ❌ Not Tested | search.md 미구현 |
| T-04 | C | 선택 사례 적용 | ❌ Not Tested | adapt.md 미구현 |
| T-05 | E | 파이프라인 실행 | ❌ Not Tested | execute.md 미구현 |
| T-06 | 통합 | end-to-end | ❌ Not Tested | module-3~5 미구현 |

**Pass: 1/6 (17%)**

### T-01 상세 결과

- **테스트 도메인**: "주제를 입력하면 강의록을 위키로 만들어주는 자동화" (Design의 테스트 도메인과 다름, 더 현실적)
- **인터뷰**: 2라운드 진행 (Round 1: 스택+역량, Round 2: 결과물+제외)
- **수정 루프**: 1회 발생 (사용자가 "Karpathy 오픈소스 활용 강조" 수정 요청 → 반영 → 재확인)
- **산출물**: `test/lecture-wiki-automation/pipeline/consult.json` 저장됨
- **스키마 일치**: 100%
- **Phase 전환 확인**: "Phase B로 넘어갈까요?" → 사용자가 "Phase A만 테스트하고 중단" 선택 → 정상 중단

---

## 6. Unplanned Items

Design에 없지만 구현 과정에서 추가된 항목:

| Item | Description | Impact |
|------|-------------|--------|
| `.claude/skills/meta-pipe/SKILL.md` | CC 스킬 등록용 wrapper (frontmatter 포함) | Design에 미반영. CC 스킬 시스템 연동에 필수. Design 업데이트 필요 |

### 권장 Design 업데이트

Design Section 2.2 파일 구조에 다음 추가 필요:

```
.claude/skills/meta-pipe/
└── SKILL.md          # CC 스킬 등록 (frontmatter + 오케스트레이터 참조)
```

---

## 7. Summary

### Match Rate: 33% (8/24)

```
구현 진행도:

[module-1] SKILL.md 오케스트레이터  ████████████████████ 100% ✅
[module-2] Phase A (Consult)       ████████████████████ 100% ✅
[module-3] Phase B (Search)        ░░░░░░░░░░░░░░░░░░░░   0% ❌
[module-4] Phase C (Adapt)         ░░░░░░░░░░░░░░░░░░░░   0% ❌
[module-5] Phase E (Execute)       ░░░░░░░░░░░░░░░░░░░░   0% ❌
[module-6] 통합 테스트              ░░░░░░░░░░░░░░░░░░░░   0% ❌

전체: ██████░░░░░░░░░░░░░░ 33%
```

### Gap 우선순위 (다음 작업)

| Priority | Gap | Action |
|----------|-----|--------|
| 1 | search.md 미구현 (module-3) | Phase B 레퍼런스 작성 |
| 2 | adapt.md 미구현 (module-4) | Phase C 레퍼런스 작성 |
| 3 | execute.md 미구현 (module-5) | Phase E 레퍼런스 작성 |
| 4 | T-02~T-06 미테스트 | module-3~5 구현 후 순차 테스트 |
| 5 | Design 업데이트 | CC 스킬 등록 파일 반영 |

### Phase A 품질 평가

| 항목 | 평가 |
|------|------|
| consult.md 설계 충실도 | ✅ Design과 100% 일치 |
| consult.json 스키마 준수 | ✅ 9/9 필드 일치 |
| 인터뷰 UX | ✅ 자연스러운 대화형 흐름, 수정 루프 동작 |
| Phase 전환 확인 | ✅ AskUserQuestion으로 확인 후 진행/중단 |
| 에러 대응 | 🔶 미테스트 ("모르겠어" 시나리오 별도 테스트 필요) |

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-08 | Initial gap analysis — module-1,2 완료 기준 | Claude (gap-detector) |
