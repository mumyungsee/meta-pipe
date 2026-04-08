# meta-pipe

> 검증된 사례를 검색하여 사용자 상황에 맞게 적용하는 사례 기반 메타 파이프라인

---

## 목차

- [Overview](#overview)
- [Phase A: Consult](#phase-a-consult)
- [Phase B: Search](#phase-b-search)
- [Phase C: Adapt](#phase-c-adapt)
- [Phase E: Execute](#phase-e-execute)
- [Error Handling](#error-handling)

---

## Overview

이 스킬은 도메인 지식이 없는 사용자가 자동화 파이프라인을 만들 수 있도록,
검증된 사례를 검색하고 사용자 상황에 맞게 적용하는 4단계 파이프라인입니다.

**흐름**: Consult(상담) → Search(검색) → Adapt(적용) → Execute(실행)

**핵심 원칙**:
- 매 Phase 전환 시 사용자 확인 필수 (자동 진행 없음)
- AI의 검색/판단 과정을 항상 사용자에게 보여줌
- 모든 결과를 `test/{slug}/pipeline/`에 파일로 저장

---

## Execution Flow

사용자가 `/meta-pipe`를 실행하면 아래 순서로 진행합니다.

### Step 0: 초기화

1. 사용자에게 인사하고 "무엇을 만들고 싶으세요?"를 AskUserQuestion으로 질문
2. 답변에서 slug 생성 (goal을 kebab-case로 변환, 예: "유튜브 자동화" → `youtube-automation`)
3. 디렉토리 생성: `test/{slug}/pipeline/`
4. Phase A로 진입

### Step 1: Phase A — Consult (상담)

**목적**: 사용자의 목표, 제약 조건, 기대 결과물을 구조화

**참조**: `references/consult.md`

**실행 절차**:
1. 사용자 답변(Step 0)을 기반으로 후속 질문 (최대 3라운드, 한 번에 2개 이하):
   - 기술 스택/도구 제약이 있나요?
   - 본인의 코딩 역량은? (beginner/intermediate/advanced)
   - 결과물 형태는? (코드/문서/자동화 등)
2. "모르겠어"라고 하면 AI가 합리적 기본값 제안
3. 수집 정보를 정리하여 사용자에게 확인 요청
4. 확인 후 `test/{slug}/pipeline/consult.json` 저장

**consult.json 스키마**:
```json
{
  "goal": "사용자 원문",
  "goal_refined": "AI가 정리한 목표 한 줄",
  "constraints": {
    "stack": ["사용 가능한 기술 스택"],
    "tools": ["사용 가능한 도구"],
    "capabilities": "beginner|intermediate|advanced",
    "budget": "예산/시간 제약 (선택)",
    "excluded": ["절대 쓰지 않을 것"]
  },
  "deliverable": "기대하는 결과물 형태",
  "search_keywords": ["키워드1", "키워드2", "키워드3"]
}
```

**완료 기준**: consult.json 생성 + goal, constraints, deliverable 3요소 모두 포함

**Phase 전환**: "사례를 검색하겠습니다. Phase B(검색)로 넘어갈까요?" → AskUserQuestion

---

### Step 2: Phase B — Search (검색)

**목적**: 검증된 사례를 검색하고 사용자가 하나를 선택

**참조**: `references/search.md`

**실행 절차**:
1. consult.json의 search_keywords + constraints로 검색 쿼리 생성
   - 기본: `site:{site} {goal_refined} {stack keywords}`
   - excluded 항목은 `-{keyword}`로 제외
   - 한국어 목표 → 영어 + 한국어 쿼리 각 1회
2. 3개 사이트 순차 검색 (WebSearch):
   - `site:github.com` → 실행 가능한 코드/레포
   - `site:threads.net` → 실제 사용 후기/팁
   - `site:gpters.org` → 검증된 사례 + 실행 결과
3. 각 사이트 상위 3개씩 수집 (최대 9개)
4. 유망 결과 2~3개 WebFetch로 상세 수집
5. 결과 테이블 제시:

   | # | 소스 | 제목 | 요약 | 적합도 |
   |---|------|------|------|--------|

6. 사용자에게 사례 선택 요청 (AskUserQuestion)
7. B→C 게이트 판단 (선택 사례의 실행 가능성):
   - 기술 스택 호환성: 사용자 stack에 포함되거나 쉽게 대체 가능
   - 역량 요구 수준: 사용자 capabilities 이하
   - 도구 가용성: 사용자 tools에 포함되거나 무료
   - 불가능 시 → 이유 설명 + 다른 사례 추천
8. `test/{slug}/pipeline/search-results.json` 저장

**완료 기준**: 검색 결과 제시 + 사용자 사례 선택 + 실행 가능성 통과

**Phase 전환**: "선택한 사례를 내 환경에 맞게 적용하겠습니다. Phase C(적용)로 넘어갈까요?" → AskUserQuestion

---

### Step 3: Phase C — Adapt (적용)

**목적**: 선택 사례를 내 환경에 맞게 수정하고 실행 가능한 파이프라인으로 변환

**참조**: `references/adapt.md`

**실행 절차**:
1. 선택 사례 원본 분석 (WebFetch로 상세 읽기)
2. 원본 vs 내 환경 차이점 도출:
   - 스택 차이 → 대체 방법
   - 도구 차이 → 대체 도구
   - 역량 차이 → 단순화 or 자동화
3. 수정 사항 목록을 사용자에게 확인 (AskUserQuestion)
4. Step 분할 + mode 할당:
   - **auto**: AI가 100% 실행 가능 (파일 생성, 코드 작성 등)
   - **assist**: AI 초안 + 사람 검수 필요 (설정 파일, 환경 변수)
   - **manual**: 사람만 실행 가능 (API 키 발급, 서비스 가입 등)
5. `test/{slug}/pipeline/pipeline.json` + `test/{slug}/pipeline/pipeline.md` 저장

**완료 기준**: pipeline.json 생성 + 최소 1개 step 포함 + 사용자 확인

**Phase 전환**: "파이프라인을 실행하겠습니다. Phase E(실행)로 넘어갈까요?" → AskUserQuestion

---

### Step 4: Phase E — Execute (실행)

**목적**: 파이프라인 step을 순차 실행하고 결과 기록

**참조**: `references/execute.md`

**실행 절차**:
1. pipeline.json 로드
2. step별 순차 실행:
   - **auto**: AI 직접 실행 (Bash, Write, Read 등) → 결과 기록
   - **assist**: AI 초안 제시 → AskUserQuestion으로 사용자 확인 후 적용
   - **manual**: 실행 가이드 제시 → AskUserQuestion으로 사용자 완료 확인
3. 각 step 결과를 execution-log.json에 기록
4. 실패 시:
   - 도구 오류 → 오류 메시지 분석 → 수정 후 재시도
   - 권한 부족 → manual step으로 전환 → 사용자 가이드
   - 스택 비호환 → Phase C로 돌아가서 해당 step 수정 제안
   - 연쇄 실패 (3회) → 파이프라인 중단 + 지금까지 결과 저장
5. 전체 완료 후:
   - `test/{slug}/pipeline/execution-log.json` 저장
   - `test/{slug}/pipeline/result.md` 생성 (최종 결과 요약 + 후속 작업 제안)

**완료 기준**: 모든 step 완료(success/skipped) + execution-log.json + result.md 저장

---

## Error Handling

| Phase | 에러 | 대응 |
|-------|------|------|
| A | 사용자가 목표를 명확히 말 못 함 | AI가 예시 3개 제시 → 선택 유도 |
| B | 검색 결과 0건 | 키워드 변경 제안 → 재검색 |
| B | WebSearch/WebFetch 실패 | 에러 알림 + 수동 검색 URL 제공 |
| B→C | 실행 가능성 탈락 | 이유 설명 + 다른 사례 선택 유도 |
| C | 수정 불가능한 차이 | 해당 부분 manual step으로 전환 |
| E | step 실행 실패 | skip/retry/modify 선택지 |
| E | 연쇄 실패 (3회) | 파이프라인 중단 + 지금까지 결과 저장 |

---

## Resume (중단 복구)

중단된 파이프라인은 `test/{slug}/pipeline/` 산출물로 남아 있습니다.
다음 세션에서 `/meta-pipe` 재실행 시:
1. 기존 산출물 감지
2. "이전에 중단된 파이프라인이 있습니다. 이어서 진행할까요?" 질문
3. 사용자 선택에 따라 이어서 진행 or 새로 시작

> v3에서는 자동 세션 복구 미구현. 사용자가 수동으로 판단합니다.
