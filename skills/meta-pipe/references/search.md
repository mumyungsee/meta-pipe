# Phase B: Search (검색)

> consult.json의 키워드와 제약 조건을 기반으로 검증된 사례를 검색하고, 사용자가 하나를 선택

---

## 목차

- [1. 목적](#1-목적)
- [2. 입력](#2-입력)
- [3. 검색 쿼리 생성](#3-검색-쿼리-생성)
- [4. 검색 실행](#4-검색-실행)
- [5. 상세 수집](#5-상세-수집)
- [6. 결과 제시 + 사용자 선택](#6-결과-제시--사용자-선택)
- [7. B→C 게이트 판단](#7-bc-게이트-판단)
- [8. search-results.json 출력 규칙](#8-search-resultsjson-출력-규칙)
- [9. 에러 대응](#9-에러-대응)

---

## 1. 목적

Phase B는 Phase A에서 수집한 사용자 맥락(consult.json)을 기반으로:
- 검증된 사례를 **3개 사이트**에서 검색
- 유망 결과를 **상세 수집**하여 요약
- 사용자에게 **비교 테이블**로 제시하여 **선택**을 받음
- 선택 사례의 **실행 가능성**을 판단 (B→C 게이트)

---

## 2. 입력

Phase B는 `test/{slug}/pipeline/consult.json`을 읽어서 시작합니다.

사용하는 필드:
- `goal_refined` — 검색 쿼리의 핵심 문장
- `search_keywords` — 검색에 직접 사용할 키워드 (3~5개)
- `constraints.stack` — 기술 스택 키워드 추가
- `constraints.excluded` — 제외 키워드 (`-{keyword}`)
- `constraints.capabilities` — B→C 게이트 판단에 사용
- `constraints.tools` — B→C 게이트 판단에 사용

---

## 3. 검색 쿼리 생성

### 3.1 쿼리 패턴

각 사이트별로 아래 패턴으로 쿼리를 생성합니다:

```
site:{site} {search_keywords 조합} {stack 키워드}
```

- `search_keywords`에서 2~3개 조합
- `constraints.stack`에서 주요 기술명 1~2개 추가
- `constraints.excluded` 항목은 `-{keyword}`로 제외

### 3.2 한국어/영어 쿼리

- `search_keywords`에 한국어가 포함된 경우: 영어 쿼리 + 한국어 쿼리 각 1회
- 영어만인 경우: 영어 쿼리 1회
- 사이트당 최대 2회 검색 (영어 1회 + 한국어 1회)

### 3.3 예시

consult.json:
```json
{
  "goal_refined": "Karpathy 오픈소스 위키로 강의록 위키 자동 생성",
  "search_keywords": ["Karpathy wiki github", "Andrej Karpathy open source wiki", "lecture wiki markdown automation"],
  "constraints": { "stack": ["Claude Code", "Node.js", "Python"], "excluded": ["유료 API"] }
}
```

생성 쿼리:
```
site:github.com Karpathy wiki open source markdown
site:github.com 카파시 위키 오픈소스
site:threads.net Karpathy wiki automation lecture
site:gpters.org Karpathy wiki 강의 자동화
```

---

## 4. 검색 실행

### 4.1 검색 순서

3개 사이트를 **순차적으로** WebSearch 도구로 검색합니다:

| 순서 | 사이트 | 목적 | 기대 결과 |
|------|--------|------|----------|
| 1 | `site:github.com` | 실행 가능한 코드/레포 | README, 스타 수, 기술 스택 |
| 2 | `site:threads.net` | 실제 사용 후기/팁 | 경험담, 장단점, 팁 |
| 3 | `site:gpters.org` | 검증된 사례 + 실행 결과 | 완성된 결과물 예시 |

### 4.2 수집 규칙

- 각 사이트 **상위 3개** 결과 수집 (최대 9개)
- 검색 결과가 0건인 사이트는 **skip** (에러가 아님)
- 수집 항목: URL, 제목, 검색 snippet

### 4.3 결과 필터링

수집된 결과에서 아래를 제외:
- `constraints.excluded`에 해당하는 기술이 포함된 결과
- 명백히 관련 없는 결과 (AI 판단)
- 접근 불가능한 URL (404, 비공개 등 — WebFetch 단계에서 확인)

---

## 5. 상세 수집

### 5.1 WebFetch 대상 선정

검색 결과 중 **유망 2~3개**를 선정하여 WebFetch로 상세 수집합니다.

선정 기준:
- `goal_refined`와의 관련성이 높은 것
- `constraints.stack`과 호환되는 것
- GitHub 레포는 README 내용이 충실한 것 우선

### 5.2 상세 수집 정보

WebFetch로 수집할 정보:
- **GitHub**: README 내용, 기술 스택, 설치 방법, 스타 수
- **Threads**: 작성자 경험, 사용한 도구, 결과물 설명
- **gpters.org**: 사례 설명, 실행 방법, 결과 스크린샷/설명

### 5.3 AI 요약 생성

각 결과에 대해 2-3줄 요약 생성:
- 1줄: 이 사례가 **무엇을 하는지**
- 2줄: **어떤 기술/도구**를 사용하는지
- 3줄: 사용자 목표와 **어떻게 연결**되는지

### 5.4 WebFetch 실패 시

- 차단/타임아웃 → 검색 snippet만으로 요약 생성
- 해당 결과의 `summary`에 "(검색 결과 기반 요약)" 표기

---

## 6. 결과 제시 + 사용자 선택

### 6.1 결과 테이블

수집된 결과를 아래 형식으로 사용자에게 보여줍니다:

```
검색 결과입니다:

| # | 소스 | 제목 | 요약 | 적합도 |
|---|------|------|------|--------|
| 1 | github.com | {제목} | {2-3줄 요약} | high |
| 2 | threads.net | {제목} | {2-3줄 요약} | medium |
| 3 | gpters.org | {제목} | {2-3줄 요약} | high |
| ... | ... | ... | ... | ... |
```

### 6.2 적합도 판단 기준

| 적합도 | 기준 |
|--------|------|
| **high** | goal과 직접 관련 + stack 호환 + 결과물이 명확 |
| **medium** | goal과 관련 있으나 stack 차이 or 부분적 관련 |
| **low** | 간접적 관련 or 상당한 수정 필요 |

### 6.3 사용자 선택

AskUserQuestion으로 사례 선택을 요청합니다:

```
어떤 사례를 적용할까요? (번호로 선택, 또는 "재검색"을 입력하면 키워드를 변경하여 다시 검색합니다)
```

- 사용자가 번호 선택 → 해당 사례로 진행
- "재검색" → 키워드 변경 제안 → Section 4부터 재실행
- "없음" or "마땅한 게 없어" → 키워드 변경 제안 or 파이프라인 중단 선택지 제시

---

## 7. B→C 게이트 판단

사용자가 사례를 선택한 후, 내 환경에서 실행 가능한지 판단합니다.

### 7.1 판단 항목

| 항목 | 통과 기준 | 검증 방법 |
|------|----------|----------|
| 기술 스택 호환성 | 사용자 `stack`에 포함되거나 쉽게 대체 가능 | 사례의 기술 vs constraints.stack 대조 |
| 역량 요구 수준 | 사용자 `capabilities` 이하 | 사례 난이도 vs capabilities 비교 |
| 도구 가용성 | 사용자 `tools`에 포함되거나 무료 | 사례 필요 도구 vs constraints.tools 대조 |

### 7.2 판단 결과 제시

**통과 시**:
```
이 사례는 내 환경에서 실행 가능합니다.
- 기술 스택: ✅ {호환 설명}
- 역량 수준: ✅ {적합 설명}
- 도구: ✅ {가용 설명}

Phase C(적용)로 넘어갈까요?
```

**불통과 시**:
```
이 사례는 내 환경에서 바로 실행하기 어렵습니다.
- 기술 스택: ❌ {불호환 사유}
- 역량 수준: ⚠️ {주의 사항}

다른 사례를 선택하시겠어요? 아니면 이 사례를 수정하여 적용할까요?
```

- "다른 사례" → Section 6 테이블로 돌아감
- "수정하여 적용" → Phase C에서 추가 수정 사항으로 반영

### 7.3 feasibility 값

search-results.json의 `selected.feasibility`에 판단 결과를 기록:
- `"pass"` — 3가지 모두 통과
- `"pass_with_modifications"` — 통과하지만 일부 수정 필요
- `"fail"` — 실행 불가 (다른 사례 선택 유도)

---

## 8. search-results.json 출력 규칙

### 8.1 출력 전 확인

사용자가 사례를 선택하고 B→C 게이트를 통과한 후 저장합니다.
별도의 사용자 확인 없이 자동 저장 (Phase 전환 확인이 곧 저장 확인).

### 8.2 스키마

```json
{
  "queries": [
    {
      "site": "github.com",
      "query": "실행한 검색 쿼리 문자열",
      "results_count": 3
    },
    {
      "site": "threads.net",
      "query": "실행한 검색 쿼리 문자열",
      "results_count": 2
    },
    {
      "site": "gpters.org",
      "query": "실행한 검색 쿼리 문자열",
      "results_count": 1
    }
  ],
  "results": [
    {
      "id": 1,
      "source": "github.com",
      "url": "https://...",
      "title": "결과 제목",
      "summary": "AI 요약 2-3줄",
      "relevance": "high",
      "match_reason": "왜 이 사례가 적합한지 한 줄 설명"
    }
  ],
  "selected": {
    "id": 1,
    "url": "https://...",
    "reason": "사용자가 선택한 이유 (사용자 답변 원문 또는 AI 정리)",
    "feasibility": "pass"
  }
}
```

### 8.3 저장

- 경로: `test/{slug}/pipeline/search-results.json`
- Write 도구로 저장
- 저장 후 사용자에게 "search-results.json이 저장되었습니다" 알림

---

## 9. 에러 대응

| 상황 | 대응 |
|------|------|
| 특정 사이트 검색 결과 0건 | 해당 사이트 skip, 나머지 사이트 결과로 진행. "github.com에서는 결과를 찾지 못했습니다" 안내 |
| 전체 검색 결과 0건 | 키워드 변경 제안: "검색 결과가 없습니다. 다른 키워드로 검색할까요?" + 키워드 3개 제안 |
| WebSearch 도구 실패 | "검색 도구에 문제가 발생했습니다. 직접 검색해볼 수 있는 URL입니다:" + 각 사이트 수동 검색 URL 제공 |
| WebFetch 차단/타임아웃 | 해당 결과는 검색 snippet만으로 요약 생성. summary에 "(검색 결과 기반 요약)" 표기 |
| 사용자가 "마땅한 게 없어" | "키워드를 변경하여 재검색할까요? 아니면 다른 방향으로 접근할까요?" 선택지 제시 |
| site: 연산자 미지원 시 | `site:` 없이 `{keywords} {site명}` 형태로 fallback 검색 |
