# Phase C: Adapt (적용)

> 선택한 사례를 내 환경에 맞게 수정하고, 실행 가능한 파이프라인(pipeline.json + pipeline.md)으로 변환

---

## 목차

- [1. 목적](#1-목적)
- [2. 입력](#2-입력)
- [3. 원본 사례 분석](#3-원본-사례-분석)
- [4. 차이점 도출](#4-차이점-도출)
- [5. 수정 사항 사용자 확인](#5-수정-사항-사용자-확인)
- [6. Step 분할 + mode 할당](#6-step-분할--mode-할당)
- [7. pipeline.json + pipeline.md 생성](#7-pipelinejson--pipelinemd-생성)
- [8. 에러 대응](#8-에러-대응)

---

## 1. 목적

Phase C는 Phase B에서 선택한 사례(search-results.json의 selected)를 기반으로:
- 원본 사례를 **상세 분석**하여 기술 스택, 설치 방법, 핵심 기능 파악
- 원본 vs 내 환경의 **차이점을 도출**하여 수정 사항 목록 생성
- 수정 사항을 **사용자 확인** 후 확정
- 실행 가능한 **Step으로 분할**하고 mode(auto/assist/manual) 할당
- **pipeline.json + pipeline.md**로 저장

---

## 2. 입력

Phase C는 두 파일을 읽어서 시작합니다:

### 2.1 consult.json

`test/{slug}/pipeline/consult.json`에서 사용하는 필드:
- `goal_refined` — 파이프라인 제목에 사용
- `constraints.stack` — 원본과의 스택 차이 비교
- `constraints.tools` — 원본과의 도구 차이 비교
- `constraints.capabilities` — 역량 차이 → 단순화/자동화 판단
- `constraints.budget` — 유료/무료 제약 확인
- `deliverable` — 기대 결과물 형태

### 2.2 search-results.json

`test/{slug}/pipeline/search-results.json`에서 사용하는 필드:
- `selected.url` — 원본 사례 URL (WebFetch 대상)
- `selected.reason` — 선택 이유 (adapt 방향 참고)
- `selected.feasibility` — 실행 가능성 판단 결과
- `results[selected.id]` — 해당 사례의 summary, match_reason

---

## 3. 원본 사례 분석

### 3.1 WebFetch로 상세 읽기

`selected.url`을 WebFetch로 읽어 아래 정보를 파악합니다:

| 수집 항목 | 설명 | 예시 |
|----------|------|------|
| 기술 스택 | 사용된 언어/프레임워크 | Go, Preact, Tailwind CSS |
| 설치 방법 | 설치/실행 절차 | 바이너리 다운로드, go build |
| 핵심 기능 | 주요 기능 목록 | wikilinks, 검색, 지식 그래프 |
| 필요 도구 | 실행에 필요한 외부 도구 | Go 컴파일러, npm |
| 난이도 | 설치/설정의 복잡도 | beginner/intermediate/advanced |

### 3.2 original 필드 생성

분석 결과를 pipeline.json의 `original` 필드로 기록:

```json
{
  "original": {
    "source_url": "selected.url 값",
    "summary": "원본 사례 요약 2-3줄 (기술 스택 + 핵심 기능 + 실행 방법)"
  }
}
```

### 3.3 WebFetch 실패 시

- WebFetch 차단/타임아웃 → search-results.json의 `summary`와 `match_reason`만으로 분석 진행
- `original.summary`에 "(검색 결과 기반 요약)" 표기

---

## 4. 차이점 도출

consult.json의 constraints와 원본 사례를 대조하여 차이점을 도출합니다.

### 4.1 비교 항목

| 비교 항목 | 비교 방법 | 적용 방향 |
|----------|----------|----------|
| 스택 차이 | 원본 기술 vs `constraints.stack` | 대체 기술 제안 or 원본 그대로 사용 |
| 도구 차이 | 원본 필요 도구 vs `constraints.tools` | 대체 도구 제안 or 설치 가이드 |
| 역량 차이 | 원본 난이도 vs `constraints.capabilities` | 단순화 or 자동화 (auto step으로 전환) |
| 예산 차이 | 원본 필요 비용 vs `constraints.budget` | 무료 대안 제안 or manual step으로 안내 |

### 4.2 adaptations 필드 생성

각 차이점을 `adaptations[]`에 기록합니다:

```json
{
  "adaptations": [
    {
      "what": "Go 바이너리 → 사전 빌드된 릴리스 바이너리 다운로드로 변경",
      "why": "사용자 stack에 Go 없음. beginner 역량이므로 직접 빌드 대신 릴리스 사용"
    },
    {
      "what": "마크다운 파일 수동 작성 → Claude Code로 자동 생성",
      "why": "사용자 도구에 Claude Code 포함. 강의록 변환 자동화가 핵심 목표"
    }
  ]
}
```

### 4.3 차이가 없는 경우

- 원본과 내 환경이 완전히 일치하면 adaptations는 빈 배열 `[]`
- 이 경우에도 사용자에게 "수정 없이 그대로 적용합니다" 확인

---

## 5. 수정 사항 사용자 확인

### 5.1 제시 형식

AskUserQuestion으로 수정 사항 목록을 제시합니다:

```
원본 사례와 내 환경의 차이점을 분석했습니다:

| # | 변경 사항 | 이유 |
|---|----------|------|
| 1 | {what} | {why} |
| 2 | {what} | {why} |
| ... | ... | ... |

이대로 진행할까요? (수정/추가 요청도 가능합니다)
```

### 5.2 사용자 응답 처리

- **확인** ("네", "좋아요", "진행") → Step 분할로 진행
- **수정 요청** ("1번을 ~로 변경해줘") → 해당 adaptation 수정 후 다시 확인
- **추가 요청** ("~도 추가해줘") → adaptations에 항목 추가 후 다시 확인
- **전면 재검토** ("다시 분석해줘") → Section 3부터 재실행

---

## 6. Step 분할 + mode 할당

### 6.1 Step 분할 원칙

사례를 실행 가능한 단위로 분할합니다:
- 하나의 step = **하나의 명확한 작업 단위**
- step 간 **의존 순서**를 order로 표현
- 너무 세밀하지도, 너무 거칠지도 않게 (3~8개가 적정)

### 6.2 mode 할당 기준

| Mode | 조건 | 예시 |
|------|------|------|
| **auto** | AI가 100% 실행 가능. 외부 접근 불필요 | 파일 생성, 코드 작성, 디렉토리 구조 생성 |
| **assist** | AI 초안 + 사람 검수 필요 | 설정 파일, 환경 변수, 콘텐츠 수정 |
| **manual** | 사람만 실행 가능. AI는 가이드만 제공 | 외부 서비스 가입, API 키 발급, 결제, 바이너리 다운로드 |

### 6.3 step 필드 구조

각 step은 아래 필드를 포함합니다:

```json
{
  "order": 1,
  "name": "Step 이름 (간결하게)",
  "mode": "auto|assist|manual",
  "instruction": "구체적 실행 지시사항. mode=auto면 AI가 실행할 명령, mode=manual이면 사용자 가이드",
  "expected_output": "이 step 완료 시 기대되는 결과 (파일, 상태 등)",
  "tools_needed": ["이 step에 필요한 도구 목록"]
}
```

### 6.4 capabilities에 따른 mode 조정

- **beginner**: 가능한 한 auto/assist를 늘림. 복잡한 설정은 AI가 대신 처리
- **intermediate**: auto/assist/manual 균형 배분
- **advanced**: manual 비율 높여도 됨. 세부 가이드 대신 핵심 포인트만 제공

---

## 7. pipeline.json + pipeline.md 생성

### 7.1 pipeline.json 스키마

Design Section 3.3 준수:

```json
{
  "original": {
    "source_url": "원본 사례 URL",
    "summary": "원본 사례 요약"
  },
  "adaptations": [
    {
      "what": "변경 사항",
      "why": "변경 이유"
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

### 7.2 pipeline.md 형식

사람이 읽기 쉬운 마크다운으로 동일 내용을 작성:

```markdown
# {goal_refined} 파이프라인

원본 사례: {source_url}

## 수정 사항

| # | 변경 | 이유 |
|---|------|------|
| 1 | {what} | {why} |

## Steps

### Step 1: {name} [auto]
{instruction}
> 기대 결과: {expected_output}
> 도구: {tools_needed}

### Step 2: {name} [assist]
{instruction}
> 기대 결과: {expected_output}
> 도구: {tools_needed}

### Step 3: {name} [manual]
{instruction}
> 기대 결과: {expected_output}
```

### 7.3 동시 생성 규칙

- pipeline.json과 pipeline.md는 **동시에** 생성하여 내용 불일치 방지
- pipeline.md의 Step 내용은 pipeline.json의 steps와 **1:1 대응**
- 저장 경로: `test/{slug}/pipeline/pipeline.json`, `test/{slug}/pipeline/pipeline.md`

### 7.4 저장 전 확인

Step 분할 결과를 사용자에게 보여주고 확인 받은 후 저장:

```
파이프라인을 생성했습니다:

| Step | 이름 | Mode | 설명 |
|------|------|------|------|
| 1 | {name} | auto | {instruction 요약} |
| 2 | {name} | assist | {instruction 요약} |
| ... | ... | ... | ... |

이대로 저장할까요?
```

- 확인 → pipeline.json + pipeline.md 저장
- 수정 요청 → 해당 step 수정 후 다시 확인
- 저장 후 사용자에게 "pipeline.json, pipeline.md가 저장되었습니다" 알림

---

## 8. 에러 대응

| 상황 | 대응 |
|------|------|
| WebFetch 실패 (원본 사례 접근 불가) | search-results.json의 summary만으로 분석 진행. original.summary에 "(검색 결과 기반 요약)" 표기 |
| 원본 사례가 너무 복잡 | 핵심 기능만 추출하여 단순화. "원본의 핵심 기능 N개 중 M개만 적용합니다" 안내 |
| 스택 차이가 너무 큼 (대체 불가) | 해당 부분을 manual step으로 전환. "이 부분은 직접 설정이 필요합니다" 가이드 제공 |
| step 분할 불확실 | 사용자에게 분할 방향 확인 후 진행. "이 부분을 한 step으로 할까요, 나눌까요?" |
| pipeline.json 스키마 위반 | Design Section 3.3과 대조하여 누락 필드 보완 |
| 사용자가 전면 재검토 요청 | Section 3(원본 분석)부터 재실행. 기존 분석 결과는 덮어씀 |
