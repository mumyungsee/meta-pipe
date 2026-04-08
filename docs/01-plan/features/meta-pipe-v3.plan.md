# meta-pipe v3 Planning Document

> **Summary**: 검증된 사례를 검색하여 사용자 상황에 맞게 적용하는 사례 기반 메타 파이프라인
>
> **Project**: meta-pipe
> **Version**: v3.0
> **Author**: mumyungsee
> **Date**: 2026-04-08
> **Status**: Draft

---

## 목차

- [Executive Summary](#executive-summary)
- [1. Overview](#1-overview)
- [2. Scope](#2-scope)
- [3. Requirements](#3-requirements)
- [4. Success Criteria](#4-success-criteria)
- [5. Risks and Mitigation](#5-risks-and-mitigation)
- [6. Architecture Considerations](#6-architecture-considerations)
- [7. Implementation Plan](#7-implementation-plan)
- [8. Next Steps](#8-next-steps)

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | 도메인 지식 없는 사용자가 자동화 파이프라인을 만들려 할 때, 뭘 골라야 할지 모르고 결과를 예측할 수 없어 선택 자체가 어려움 |
| **Solution** | 검증된 사례(GitHub, Threads, 지피터스)를 AI가 검색·요약하여 결과 예시와 함께 제시, 사용자는 선택만 하면 내 상황에 맞게 자동 적용 |
| **Function/UX Effect** | "뭘 만들지 상담 → 사례 검색·비교 → 내 환경에 맞게 적용 → 실행"의 4단계 플로우. 사용자는 결과를 미리 보고 납득한 뒤 실행 |
| **Core Value** | 도메인 모르는 사용자도 결과를 예측하고 납득한 뒤 실행할 수 있는 의사결정 지원. 전 과정 문서화로 개인 지식베이스 축적 |

---

## 1. Overview

### 1.1 Purpose

도메인 지식이 없는 사용자가 자동화 도구/파이프라인을 만들 때:
- **무엇을 골라야 할지** 선택이 어려움 (도메인 없으니까)
- **결과를 사전에 예측할 수 없음** (같은 사례를 보지 않는 한)
- **직접 만들면 완성도 부족** → 버려둠 → 남이 만든 것 사용 패턴 반복

이 문제를 "검증된 사례 검색 + 적용" 방식으로 해결한다.

### 1.2 Background

- **v1 교훈**: 사용자 맥락 없이 파이프라인 생성 → 실행 불가
- **v2 교훈**: Phase별 테스트 없이 전체 구현 → Phase A 결함이 전체를 흔듦
- **v3 피봇 (B안)**: "처음부터 생성" → "검증된 사례 검색 + 적용"으로 전환
- 사용자의 실제 행동 패턴("찾아서 커스터마이징")과 설계를 일치시킴

### 1.3 Related Documents

- 킥오프: [2026-04-07-v3-kickoff.md](../../00-ideation/2026-04-07-v3-kickoff.md)
- 피봇 결정: [2026-04-08-v3-pivot-to-case-based.md](../../00-ideation/2026-04-08-v3-pivot-to-case-based.md)
- v1/v2 아카이브: `archive/v1/`, `archive/v2/`

### 1.4 핵심 가설

> 검증된 사례를 잘 찾아서 사용자 상황에 맞게 적용하면, 도메인 모르는 사용자도 결과를 예측하고 납득한 뒤 실행할 수 있는가

---

## 2. Scope

### 2.1 In Scope

- [ ] **Phase A (Consult)**: 목표 + 제약 조건(스택/도구/역량) + 결과물 형태 수집
- [ ] **Phase B (Search)**: 지정 사이트에서 사례 검색 + 결과 예시 제시
- [ ] **Phase C (Adapt)**: 선택한 사례를 내 상황에 맞게 수정/파이프라인화
- [ ] **Phase E (Execute)**: 파이프라인 실행
- [ ] **SKILL.md 오케스트레이터**: Phase A→B→C→E 흐름 제어
- [ ] **산출물 문서화**: 각 Phase 결과를 JSON/MD로 저장

### 2.2 Out of Scope (v3 이후)

- 사용자 프로필/선호 저장
- 사례 캐시/로컬 DB
- 세션 재개
- 복잡도 레벨 분기 (auto/assist/manual 외)
- 다중 사용자 지원 (v3 사용자 = 나 한 명)
- bkit 플러그인 스토어 등록
- 앰버서더/스터디 연계

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-01 | Phase A: 대화형 인터뷰로 목표/제약/결과물 수집 → `consult.json` 출력 | High | Pending |
| FR-02 | Phase A: 제약 조건(스택/도구/역량)으로 검색 범위 사전 필터링 | High | Pending |
| FR-03 | Phase B: `site:github.com`, `site:threads.net`, `site:gpters.org` 검색 | High | Pending |
| FR-04 | Phase B: 유망 결과 상세 수집(WebFetch) + 사례별 요약 제시 | High | Pending |
| FR-05 | Phase B: 사용자 선택 → 선택 사례 데이터 저장 | High | Pending |
| FR-06 | Phase B→C 판단: 선택 사례가 내 환경에서 실행 가능한지 검증 | Medium | Pending |
| FR-07 | Phase C: 선택 사례를 내 요구사항에 맞게 수정 | High | Pending |
| FR-08 | Phase C: 파이프라인화 (실행 가능한 step 구조로 변환) | High | Pending |
| FR-09 | Phase E: 파이프라인 실행 (auto/assist/manual 모드) | High | Pending |
| FR-10 | 각 Phase 산출물을 문서(JSON/MD)로 저장 | High | Pending |
| FR-11 | SKILL.md 오케스트레이터: Phase 간 흐름 제어 | High | Pending |

### 3.2 Non-Functional Requirements

| Category | Criteria | Measurement Method |
|----------|----------|-------------------|
| 사용성 | Phase 전환 시 사용자 확인 필수 | 수동 테스트 |
| 투명성 | 각 Phase 결과를 사용자에게 보여주고 확인받기 | 수동 테스트 |
| 문서화 | 전 과정 로컬 파일로 남기기 | 파일 존재 확인 |

---

## 4. Success Criteria

### 4.1 Phase별 완료 기준 + 테스트 방법

| Phase | 완료 기준 | 테스트 방법 |
|-------|----------|------------|
| A (Consult) | `consult.json` 생성됨 + 목표/제약/결과물 3가지 모두 포함 | 실제 도메인으로 `/meta-pipe` 실행, JSON 출력 확인 |
| B (Search) | 3개 사이트 검색 결과 + 사례별 요약 제시 + 사용자 선택 완료 | 검색 결과가 제약 조건에 부합하는지 사람이 판단 |
| C (Adapt) | 선택 사례가 내 환경 기준으로 수정됨 + 실행 가능한 step 구조 | 수정된 파이프라인이 실행 가능한 형태인지 사람이 판단 |
| E (Execute) | 파이프라인 실행 완료 + 결과 문서 저장 | 실행 결과 확인 |

### 4.2 MVP 완료 기준 (전체)

- [ ] `/meta-pipe` 한 번 실행으로 Phase A→B→C→E 전체 흐름 동작
- [ ] 테스트 도메인 1개로 end-to-end 성공
- [ ] 각 Phase 산출물 파일이 `test/{slug}/pipeline/`에 저장됨

### 4.3 테스트 도메인

**첫 번째 테스트**: meta-pipe 자체를 만드는 과정
- 입력: "bkit 플러그인으로 사례 기반 파이프라인 도구를 만들고 싶어"
- 기대: 관련 오픈소스/사례를 찾아서 적용 방법을 제시

---

## 5. Risks and Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **반복 패턴**: 완성도 부족 → 버림 | High | High | "사용 가능한 최소 버전" 먼저 정의 + 첫 테스트 빨리 실행 |
| **Phase B→C 갭**: 사례가 내 환경에서 안 돌아감 | Medium | Medium | FR-06: 실행 가능성 판단 단계 추가 |
| **검색 품질**: site: 검색 결과가 부실함 | Medium | Medium | 검색 키워드 품질을 Phase A 제약 조건으로 보강 |
| **스코프 확장**: v3에 불필요한 기능 추가 | High | Medium | 사용자=나 한 명, Out of Scope 엄수 |
| **4시간 타임라인 초과** | Low | Medium | Phase별 구현+테스트로 잘라서 진행, 미완성이면 다음 세션 |

---

## 6. Architecture Considerations

### 6.1 Project Level

**bkit Skill (Claude Code Plugin)** — 웹앱/서버 아님. bkit 스킬로 구현.

| 구성 요소 | 역할 | 파일 |
|----------|------|------|
| SKILL.md | 오케스트레이터 (Phase 흐름 제어) | `skills/meta-pipe/SKILL.md` |
| consult.md | Phase A 스킬 레퍼런스 | `skills/meta-pipe/references/consult.md` |
| search.md | Phase B 스킬 레퍼런스 | `skills/meta-pipe/references/search.md` |
| adapt.md | Phase C 스킬 레퍼런스 | `skills/meta-pipe/references/adapt.md` |
| execute.md | Phase E 스킬 레퍼런스 | `skills/meta-pipe/references/execute.md` |

### 6.2 Key Decisions

| 결정 | 선택 | 이유 |
|------|------|------|
| 구현 형태 | bkit Skill (SKILL.md + references/) | bkit 플러그인 통합 목표, 코드 없이 프롬프트 기반 |
| 검색 방식 | WebSearch + site: 연산자 | AI가 검색~요약, 사용자는 선택만 |
| 상세 수집 | WebFetch | 검색 결과 URL에서 상세 정보 추출 |
| 산출물 형식 | JSON (구조화) + MD (가독성) | 기계 처리 + 사람 읽기 모두 지원 |
| 실행 모드 | auto / assist / manual | 사용자 역량에 따라 선택 |
| 테스트 데이터 저장 | `test/{slug}/pipeline/` | 프로젝트 본체와 분리 |

### 6.3 Phase 간 데이터 흐름

```
Phase A (Consult)
  출력: consult.json
  ├── goal: "무엇을 만들고 싶은지"
  ├── constraints: { stack, tools, capabilities }
  ├── deliverable: "결과물 형태"
  └── search_keywords: ["키워드1", "키워드2"]

      ↓ (consult.json을 입력으로)

Phase B (Search)
  출력: search-results.json
  ├── queries: [실행한 검색 쿼리들]
  ├── results: [{ source, url, title, summary, relevance }]
  └── selected: { url, reason }

      ↓ (selected 사례를 입력으로)

  [판단: 내 환경에서 실행 가능한가?]

      ↓

Phase C (Adapt)
  출력: pipeline.json + pipeline.md
  ├── original: "원본 사례 요약"
  ├── adaptations: ["변경 사항 목록"]
  └── steps: [{ name, mode, instruction, expected_output }]

      ↓ (pipeline을 입력으로)

Phase E (Execute)
  출력: execution-log.json + result.md
  ├── steps_completed: [{ step, status, output }]
  └── final_result: "최종 결과 요약"
```

---

## 7. Implementation Plan

### 7.1 모듈 구현 순서 (Phase별 PDCA)

| Module | Scope | 산출물 | 완료 기준 |
|--------|-------|--------|----------|
| module-1 | SKILL.md 기본 구조 (오케스트레이터) | `skills/meta-pipe/SKILL.md` | `/meta-pipe` 실행 시 Phase A 호출 |
| module-2 | Phase A (Consult) | `references/consult.md` | consult.json 생성 + 3요소 포함 |
| module-3 | Phase B (Search) | `references/search.md` | 3사이트 검색 + 사례 요약 + 선택 |
| module-4 | Phase C (Adapt) | `references/adapt.md` | 선택 사례 수정 + pipeline 구조 생성 |
| module-5 | Phase E (Execute) | `references/execute.md` | 파이프라인 실행 + 결과 저장 |
| module-6 | 통합 테스트 | end-to-end 검증 | 테스트 도메인 1회 완주 |

### 7.2 4시간 MVP 타임라인

| 시간 | 할 일 | 산출물 |
|------|-------|--------|
| 0:00~0:30 | ✅ Plan 작성 (지금) | 이 문서 |
| 0:30~1:30 | module-1 + module-2 (SKILL.md + Phase A) | 오케스트레이터 + consult.md |
| 1:30~2:30 | module-3 (Phase B: Search) | search.md |
| 2:30~3:30 | module-4 (Phase C: Adapt) | adapt.md |
| 3:30~4:00 | module-5 + module-6 (Execute + 통합 테스트) | execute.md + 1회 테스트 |

### 7.3 개발 방법론

- **Phase별 PDCA**: 각 module 구현 후 테스트 통과해야 다음 module 시작
- **테스트 방법**: 실제 도메인으로 `/meta-pipe` 직접 실행 + 사람이 결과 판단
- **작은 단위**: 바이브코딩은 단위를 작게 잘라서 구현 + 테스트 반복

---

## 8. Next Steps

1. [ ] Design 문서 작성 (`/pdca design meta-pipe-v3`)
2. [ ] module-1부터 순차 구현 시작
3. [ ] 첫 테스트: meta-pipe 자체를 만드는 과정이 첫 번째 테스트 케이스

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-08 | Initial draft — B안(사례 기반) 피봇 기준 | mumyungsee |
