# meta-pipe v3 Design Document

> **Summary**: 검증된 사례를 검색하여 사용자 상황에 맞게 적용하는 사례 기반 메타 파이프라인 — bkit Skill 설계
>
> **Project**: meta-pipe
> **Version**: v3.0
> **Author**: mumyungsee
> **Date**: 2026-04-08
> **Status**: Draft
> **Planning Doc**: [meta-pipe-v3.plan.md](../../01-plan/features/meta-pipe-v3.plan.md)

---

## 목차

- [Executive Summary](#executive-summary)
- [1. Overview](#1-overview)
- [2. Architecture](#2-architecture)
- [3. Data Model](#3-data-model)
- [4. Phase 상세 설계](#4-phase-상세-설계)
- [5. User Flow](#5-user-flow)
- [6. Error Handling](#6-error-handling)
- [7. Test Plan](#7-test-plan)
- [8. Implementation Guide](#8-implementation-guide)
- [Version History](#version-history)

---

## Executive Summary

| Perspective | Content |
|-------------|---------|
| **Problem** | 도메인 지식 없는 사용자가 자동화 파이프라인을 만들려 할 때, 뭘 골라야 할지 모르고 결과를 예측할 수 없어 선택 자체가 어려움 |
| **Solution** | 검증된 사례(GitHub, Threads, 지피터스)를 AI가 검색·요약하여 결과 예시와 함께 제시, 사용자는 선택만 하면 내 상황에 맞게 자동 적용 |
| **Function/UX Effect** | `/meta-pipe` 한 번 실행 → Consult(상담) → Search(검색) → Adapt(적용) → Execute(실행) 4단계 자동 흐름. 각 단계에서 사용자 확인 후 진행 |
| **Core Value** | 도메인 모르는 사용자도 결과를 예측하고 납득한 뒤 실행할 수 있는 의사결정 지원. 전 과정 문서화로 개인 지식베이스 축적 |

---

## 1. Overview

### 1.1 Design Goals

1. **프롬프트 기반 구현**: 코드 없이 SKILL.md + references/ 구조로 전체 파이프라인 동작
2. **Phase 간 데이터 계약**: 각 Phase의 입출력을 JSON 스키마로 명확히 정의
3. **사용자 주도 흐름**: 매 Phase 전환 시 사용자 확인 필수 (자동 진행 없음)
4. **산출물 문서화**: 모든 결과를 `test/{slug}/pipeline/`에 파일로 저장

### 1.2 Design Principles

- **Phase 독립성**: 각 Phase는 입력 JSON만 있으면 독립 실행 가능
- **투명성 우선**: AI의 검색/판단 과정을 사용자에게 항상 보여줌
- **최소 구현**: v3 스코프에 없는 기능(캐시, 프로필, 세션 등)은 설계하지 않음

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────┐
│  /meta-pipe (SKILL.md — Orchestrator)               │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────┐ │
│  │ Phase A  │→ │ Phase B  │→ │ Phase C  │→ │Ph. E│ │
│  │ Consult  │  │ Search   │  │ Adapt    │  │Exec │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────┘ │
│       ↓              ↓             ↓           ↓    │
│  consult.json  search-results  pipeline.json  log   │
│                    .json       pipeline.md    .json  │
└─────────────────────────────────────────────────────┘
         │                │
         ▼                ▼
  ┌─────────────┐  ┌──────────────┐
  │ AskUser     │  │ WebSearch    │
  │ Question    │  │ WebFetch     │
  │ (사용자입력)│  │ (검색/수집)  │
  └─────────────┘  └──────────────┘
```

### 2.2 파일 구조

```
skills/meta-pipe/
├── SKILL.md                    # 오케스트레이터 (Phase 흐름 제어)
└── references/
    ├── consult.md              # Phase A 상세 프롬프트
    ├── search.md               # Phase B 상세 프롬프트
    ├── adapt.md                # Phase C 상세 프롬프트
    └── execute.md              # Phase E 상세 프롬프트

test/{slug}/
├── pipeline/                   # Phase 산출물 저장
│   ├── consult.json
│   ├── search-results.json
│   ├── pipeline.json
│   ├── pipeline.md
│   ├── execution-log.json
│   └── result.md
└── docs/                       # 테스트별 PDCA 관리
```

### 2.3 Dependencies

| Component | Depends On | Purpose |
|-----------|-----------|---------|
| SKILL.md | references/*.md | 각 Phase 프롬프트 참조 |
| Phase A | AskUserQuestion | 대화형 인터뷰 |
| Phase B | WebSearch, WebFetch | 사례 검색 + 상세 수집 |
| Phase C | Phase B 출력 (search-results.json) | 선택 사례 기반 적용 |
| Phase E | Phase C 출력 (pipeline.json) | 파이프라인 실행 |

### 2.4 Tool 사용 매핑

| Phase | Claude Code Tool | 용도 |
|-------|-----------------|------|
| A (Consult) | AskUserQuestion | 목표/제약/결과물 인터뷰 |
| B (Search) | WebSearch | `site:` 검색 실행 |
| B (Search) | WebFetch | 유망 결과 상세 수집 |
| B (Search) | AskUserQuestion | 사례 선택 확인 |
| C (Adapt) | AskUserQuestion | 수정 방향 확인 |
| E (Execute) | Bash, Write, Read | 파이프라인 step 실행 |
| 공통 | Write | 산출물 JSON/MD 저장 |

---

## 3. Data Model

### 3.1 Phase A 출력: `consult.json`

```json
{
  "goal": "무엇을 만들고 싶은지 (사용자 원문)",
  "goal_refined": "AI가 정리한 목표 한 줄",
  "constraints": {
    "stack": ["사용 가능한 기술 스택"],
    "tools": ["사용 가능한 도구"],
    "capabilities": "사용자 역량 수준 (beginner|intermediate|advanced)",
    "budget": "예산/시간 제약 (선택)",
    "excluded": ["절대 쓰지 않을 것"]
  },
  "deliverable": "기대하는 결과물 형태",
  "search_keywords": ["키워드1", "키워드2", "키워드3"]
}
```

### 3.2 Phase B 출력: `search-results.json`

```json
{
  "queries": [
    {
      "site": "github.com",
      "query": "실행한 검색 쿼리",
      "results_count": 5
    }
  ],
  "results": [
    {
      "id": 1,
      "source": "github.com",
      "url": "https://...",
      "title": "제목",
      "summary": "AI 요약 (2-3줄)",
      "relevance": "high|medium|low",
      "match_reason": "왜 이 사례가 적합한지"
    }
  ],
  "selected": {
    "id": 1,
    "url": "https://...",
    "reason": "사용자가 선택한 이유",
    "feasibility": "실행 가능성 판단 (Phase B→C 게이트)"
  }
}
```

### 3.3 Phase C 출력: `pipeline.json` + `pipeline.md`

```json
{
  "original": {
    "source_url": "원본 사례 URL",
    "summary": "원본 사례 요약"
  },
  "adaptations": [
    {
      "what": "변경 사항",
      "why": "변경 이유 (내 제약 조건과의 차이)"
    }
  ],
  "steps": [
    {
      "order": 1,
      "name": "Step 이름",
      "mode": "auto|assist|manual",
      "instruction": "실행 지시사항",
      "expected_output": "기대 결과",
      "tools_needed": ["필요한 도구"]
    }
  ]
}
```

### 3.4 Phase E 출력: `execution-log.json` + `result.md`

```json
{
  "steps_completed": [
    {
      "step": 1,
      "name": "Step 이름",
      "status": "success|skipped|failed",
      "output": "실행 결과 요약",
      "files_created": ["생성된 파일 경로"]
    }
  ],
  "final_result": "최종 결과 요약",
  "next_actions": ["후속 작업 제안"]
}
```

---

## 4. Phase 상세 설계

### 4.1 Phase A — Consult (상담)

**목적**: 사용자의 목표, 제약 조건, 기대 결과물을 구조화

**흐름**:
```
1. 인사 + "무엇을 만들고 싶으세요?" 질문
2. 답변 → 후속 질문 (최대 3회):
   - 기술 스택/도구 제약이 있나요?
   - 본인의 코딩 역량은? (beginner/intermediate/advanced)
   - 결과물 형태는? (코드/문서/자동화 등)
3. 수집 정보 정리 → 사용자 확인
4. consult.json 저장
5. search_keywords 자동 생성 (goal + constraints 기반)
```

**프롬프트 설계 핵심** (`references/consult.md`):
- 질문은 최대 3라운드, 한 번에 2개 이하
- 사용자가 "모르겠어"라고 하면 AI가 합리적 기본값 제안
- 제약 조건 중 `excluded`는 반드시 확인 (사례 검색 시 필터링 핵심)

**완료 기준**: `consult.json` 생성 + goal, constraints, deliverable 3요소 모두 포함

### 4.2 Phase B — Search (검색)

**목적**: 검증된 사례를 검색하고 사용자가 하나를 선택

**흐름**:
```
1. consult.json의 search_keywords + constraints로 검색 쿼리 생성
2. 3개 사이트 순차 검색:
   a. site:github.com {keywords} → 실행 가능한 코드/레포
   b. site:threads.net {keywords} → 실제 사용 후기/팁
   c. site:gpters.org {keywords} → 검증된 사례 + 실행 결과
3. 각 사이트 상위 3개씩 수집 (최대 9개)
4. 유망 결과 2~3개 WebFetch로 상세 수집
5. 결과 테이블 제시:
   | # | 소스 | 제목 | 요약 | 적합도 |
6. 사용자 선택 요청 (AskUserQuestion)
7. 선택 사례 실행 가능성 판단 (B→C 게이트):
   - "내 constraints에서 실행 가능한가?"
   - 불가능 시 → 이유 설명 + 다른 사례 추천
8. search-results.json 저장
```

**검색 쿼리 생성 규칙**:
- 기본: `site:{site} {goal_refined} {stack keywords}`
- `excluded` 항목은 `-{keyword}`로 제외
- 한국어 목표 → 영어 + 한국어 쿼리 각 1회

**B→C 게이트 판단 기준**:
| 판단 항목 | 통과 기준 |
|----------|----------|
| 기술 스택 호환성 | 사용자 stack에 포함되거나 쉽게 대체 가능 |
| 역량 요구 수준 | 사용자 capabilities 이하 |
| 도구 가용성 | 사용자 tools에 포함되거나 무료 |

**완료 기준**: 검색 결과 제시 + 사용자 사례 선택 + 실행 가능성 통과

### 4.3 Phase C — Adapt (적용)

**목적**: 선택 사례를 내 환경에 맞게 수정하고 실행 가능한 파이프라인으로 변환

**흐름**:
```
1. 선택 사례 원본 분석 (WebFetch로 상세 읽기)
2. 원본 vs 내 환경 차이점 도출:
   - 스택 차이 → 대체 방법
   - 도구 차이 → 대체 도구
   - 역량 차이 → 단순화 or 자동화
3. 수정 사항 목록 사용자 확인 (AskUserQuestion)
4. Step 분할:
   - 각 step에 mode(auto/assist/manual) 할당
   - step별 expected_output 정의
5. pipeline.json + pipeline.md 저장
```

**mode 할당 기준**:
| Mode | 조건 | 예시 |
|------|------|------|
| auto | AI가 100% 실행 가능 (파일 생성, 코드 작성 등) | `Write`, `Bash` 명령 |
| assist | AI 초안 + 사람 검수 필요 | 설정 파일, 환경 변수 |
| manual | 사람만 실행 가능 (외부 서비스 가입, 결제 등) | API 키 발급, 서비스 가입 |

**pipeline.md 형식**:
```markdown
# {goal_refined} 파이프라인

원본 사례: {source_url}

## Steps

### Step 1: {name} [auto]
{instruction}
> 기대 결과: {expected_output}

### Step 2: {name} [assist]
...
```

**완료 기준**: pipeline.json 생성 + 최소 1개 step 포함 + 사용자 확인

### 4.4 Phase E — Execute (실행)

**목적**: 파이프라인 step을 순차 실행하고 결과 기록

**흐름**:
```
1. pipeline.json 로드
2. step별 순차 실행:
   - auto: AI 직접 실행 → 결과 기록
   - assist: AI 초안 제시 → 사용자 확인 후 적용
   - manual: 실행 가이드 제시 → 사용자 완료 확인
3. 각 step 결과를 execution-log.json에 기록
4. 실패 시:
   - 실패 원인 분석
   - 대안 제시 (skip / retry / modify)
   - 사용자 선택에 따라 진행
5. 전체 완료 후 result.md 생성
6. 후속 작업 제안
```

**실패 처리 전략**:
| 실패 유형 | 대응 |
|----------|------|
| 도구 오류 (명령 실패) | 오류 메시지 분석 → 수정 후 재시도 |
| 권한 부족 (API 키 등) | manual step으로 전환 → 사용자 가이드 |
| 스택 비호환 | Phase C로 돌아가서 해당 step 수정 제안 |

**완료 기준**: 모든 step 완료(success/skipped) + execution-log.json + result.md 저장

---

## 5. User Flow

### 5.1 전체 흐름

```
사용자: /meta-pipe
  │
  ├─ Phase A ─────────────────────────────────────────────
  │  AI: "무엇을 만들고 싶으세요?"
  │  사용자: "유튜브 자동화 도구를 만들고 싶어"
  │  AI: (후속 질문 2-3회)
  │  AI: "정리하면 이렇습니다: [요약]. 맞나요?"
  │  사용자: "네"
  │  → consult.json 저장
  │  AI: "사례를 검색하겠습니다. 진행할까요?"
  │
  ├─ Phase B ─────────────────────────────────────────────
  │  AI: (3개 사이트 검색 실행)
  │  AI: "검색 결과입니다:"
  │  | # | 소스 | 제목 | 요약 | 적합도 |
  │  AI: "어떤 사례를 적용할까요?"
  │  사용자: "2번"
  │  AI: "이 사례는 내 환경에서 실행 가능합니다. 적용 단계로 넘어갈까요?"
  │  → search-results.json 저장
  │
  ├─ Phase C ─────────────────────────────────────────────
  │  AI: "원본과 내 환경 차이점:"
  │  AI: [수정 사항 목록]
  │  AI: "이렇게 수정할까요?"
  │  사용자: "네"
  │  AI: "파이프라인 (N steps):"
  │  | Step | 이름 | 모드 | 설명 |
  │  → pipeline.json + pipeline.md 저장
  │
  └─ Phase E ─────────────────────────────────────────────
     AI: "Step 1 실행 중... ✅ 완료"
     AI: "Step 2는 assist 모드입니다. 초안: [...]  적용할까요?"
     사용자: "네"
     AI: "Step 3은 manual입니다. [가이드] 완료되면 알려주세요."
     사용자: "완료"
     AI: "모든 Step 완료! 결과 요약: [...]"
     → execution-log.json + result.md 저장
```

### 5.2 Phase 전환 확인

모든 Phase 전환 시 반드시 AskUserQuestion으로 사용자 확인:
- "Phase B(검색)로 넘어갈까요?"
- "Phase C(적용)로 넘어갈까요?"
- "Phase E(실행)로 넘어갈까요?"

사용자가 "아니오" 시: 현재 Phase 결과 수정 또는 중단 선택지 제시.

---

## 6. Error Handling

### 6.1 Phase별 에러 시나리오

| Phase | 에러 | 대응 |
|-------|------|------|
| A | 사용자가 목표를 명확히 말 못 함 | AI가 예시 3개 제시 → 선택 유도 |
| B | 검색 결과 0건 | 키워드 변경 제안 → 재검색 |
| B | WebSearch 도구 실패 | 에러 알림 + 수동 검색 URL 제공 |
| B | WebFetch 차단/실패 | 검색 요약만으로 진행 (상세 수집 skip) |
| B→C | 실행 가능성 탈락 | 이유 설명 + 다른 사례 선택 유도 |
| C | 수정 불가능한 차이 | 해당 부분 manual step으로 전환 |
| E | step 실행 실패 | skip/retry/modify 선택지 |
| E | 연쇄 실패 (3회) | 파이프라인 중단 + 지금까지 결과 저장 |

### 6.2 중단 시 복구

중단된 파이프라인은 `test/{slug}/pipeline/` 산출물로 남아 있으므로:
- 다음 세션에서 `/meta-pipe` 재실행 시, 기존 산출물 감지 → "이어서 진행할까요?" 질문
- v3에서는 자동 세션 복구 미구현 (Out of Scope), 수동 판단

---

## 7. Test Plan

### 7.1 Test Scope

| Type | Target | Method |
|------|--------|--------|
| Phase 단위 테스트 | 각 Phase 독립 실행 | 실제 도메인으로 `/meta-pipe` 실행, 해당 Phase만 검증 |
| 통합 테스트 | A→B→C→E 전체 흐름 | 테스트 도메인 end-to-end 실행 |
| 산출물 검증 | JSON 스키마 준수 | 생성된 파일이 3.1~3.4 스키마와 일치하는지 확인 |

### 7.2 Test Cases

| ID | Phase | 시나리오 | 완료 기준 |
|----|-------|---------|----------|
| T-01 | A | "bkit 플러그인 만들고 싶어" 입력 | consult.json에 goal/constraints/deliverable 포함 |
| T-02 | B | consult.json 기반 검색 실행 | 3개 사이트 검색 + 사례 요약 테이블 출력 |
| T-03 | B→C | 선택 사례 실행 가능성 판단 | feasibility 판단 결과 출력 |
| T-04 | C | 선택 사례 적용 | pipeline.json에 steps 1개 이상 |
| T-05 | E | 파이프라인 실행 | execution-log.json + result.md 생성 |
| T-06 | 통합 | 테스트 도메인 end-to-end | 전체 4 Phase 완주 + 모든 산출물 존재 |

### 7.3 첫 번째 테스트 도메인

- **입력**: "bkit 플러그인으로 사례 기반 파이프라인 도구를 만들고 싶어"
- **기대**: 관련 오픈소스/사례를 찾아서 적용 방법을 제시
- **저장**: `test/meta-pipe-self/pipeline/`

---

## 8. Implementation Guide

### 8.1 Implementation Order

| 순서 | Module | 산출물 | 의존성 | 테스트 |
|------|--------|--------|--------|--------|
| 1 | SKILL.md 기본 구조 | `skills/meta-pipe/SKILL.md` | 없음 | `/meta-pipe` 실행 시 Phase A 호출 확인 |
| 2 | Phase A (Consult) | `references/consult.md` | module-1 | T-01 통과 |
| 3 | Phase B (Search) | `references/search.md` | module-2 | T-02, T-03 통과 |
| 4 | Phase C (Adapt) | `references/adapt.md` | module-3 | T-04 통과 |
| 5 | Phase E (Execute) | `references/execute.md` | module-4 | T-05 통과 |
| 6 | 통합 테스트 | end-to-end 검증 | module-5 | T-06 통과 |

### 8.2 SKILL.md 오케스트레이터 설계

```markdown
# SKILL.md 핵심 구조 (pseudo)

1. slug 생성 (goal에서 kebab-case)
2. test/{slug}/pipeline/ 디렉토리 생성
3. Phase A 실행 (references/consult.md 참조)
   → consult.json 저장
   → 사용자 확인
4. Phase B 실행 (references/search.md 참조)
   → search-results.json 저장
   → 사용자 확인
5. Phase C 실행 (references/adapt.md 참조)
   → pipeline.json + pipeline.md 저장
   → 사용자 확인
6. Phase E 실행 (references/execute.md 참조)
   → execution-log.json + result.md 저장
7. 완료 요약 출력
```

### 8.3 Module별 핵심 구현 포인트

**Module 1 (SKILL.md)**:
- frontmatter: name, description, trigger keyword
- Phase 흐름 제어 로직 (순차 실행 + 전환 확인)
- slug 생성 + 디렉토리 구조 자동 생성

**Module 2 (consult.md)**:
- 인터뷰 질문 시나리오 (최대 3라운드)
- "모르겠어" 대응 기본값 테이블
- consult.json 스키마 출력 규칙

**Module 3 (search.md)**:
- 검색 쿼리 생성 알고리즘 (goal + constraints → query)
- 3사이트 × 상위 3개 = 최대 9개 수집
- 유망 2~3개 WebFetch 상세 수집
- B→C 게이트 판단 로직

**Module 4 (adapt.md)**:
- 원본 vs 내 환경 diff 생성
- step 분할 + mode 할당
- pipeline.json + pipeline.md 동시 생성

**Module 5 (execute.md)**:
- mode별 실행 전략 (auto/assist/manual)
- step별 결과 기록
- 실패 처리 (skip/retry/modify)
- result.md 요약 생성

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 0.1 | 2026-04-08 | Initial draft — Plan 기반 상세 설계 | mumyungsee |
