# Phase A: Consult (상담)

> 사용자의 목표, 제약 조건, 기대 결과물을 대화형으로 수집하여 consult.json으로 구조화

---

## 목차

- [1. 목적](#1-목적)
- [2. 인터뷰 흐름](#2-인터뷰-흐름)
- [3. 기본값 테이블](#3-기본값-테이블)
- [4. search_keywords 생성 규칙](#4-search_keywords-생성-규칙)
- [5. consult.json 출력 규칙](#5-consultjson-출력-규칙)
- [6. 에러 대응](#6-에러-대응)

---

## 1. 목적

Phase A는 후속 Phase(B: Search, C: Adapt, E: Execute)에서 사용할 **구조화된 컨텍스트**를 만드는 단계입니다.

수집 대상 3요소:
- **goal**: 사용자가 만들고 싶은 것
- **constraints**: 기술 스택, 도구, 역량, 제외 항목
- **deliverable**: 기대하는 결과물 형태

---

## 2. 인터뷰 흐름

### 2.1 Round 구조

인터뷰는 **최대 3라운드**, 한 라운드에 **질문 2개 이하**로 진행합니다.

```
Round 0 (SKILL.md에서 처리):
  → "무엇을 만들고 싶으세요?" → 사용자 답변 수신

Round 1:
  Q1. "사용할 수 있는 기술 스택이나 도구가 있나요? (예: Python, Node.js, 특정 API 등)"
  Q2. "본인의 코딩 역량은 어느 정도인가요? (beginner / intermediate / advanced)"

Round 2:
  Q1. "결과물은 어떤 형태를 원하시나요? (예: 실행 가능한 코드, 자동화 스크립트, 문서/가이드 등)"
  Q2. "절대 쓰고 싶지 않은 기술이나 방법이 있나요?"

Round 3 (필요 시에만):
  → Round 1~2 답변에서 불명확한 부분이 있을 때만 추가 질문
  → 불명확한 부분이 없으면 Round 3 생략
```

### 2.2 질문 규칙

- 모든 질문은 AskUserQuestion 도구로 수행
- 한 번에 2개를 초과하는 질문 금지
- 사용자 답변이 충분히 명확하면 남은 라운드 생략 가능
- 각 질문에는 괄호로 예시를 포함하여 사용자가 답변하기 쉽게 함

### 2.3 "모르겠어" 처리

사용자가 "모르겠어", "잘 모르겠어", "아무거나", "상관없어" 등으로 답변하면:
1. 해당 항목의 기본값(3절 참조)을 제안
2. "이렇게 설정해도 될까요?"로 확인
3. 사용자가 수락하면 기본값 적용

---

## 3. 기본값 테이블

| 항목 | 기본값 | 근거 |
|------|--------|------|
| `constraints.stack` | `["Python"]` | 가장 범용적, 사례 풍부 |
| `constraints.tools` | `["Claude Code"]` | 현재 실행 환경 |
| `constraints.capabilities` | `"beginner"` | 안전한 기본값, 단순한 사례 우선 |
| `constraints.budget` | `null` (제한 없음) | 무료 도구 우선 검색 |
| `constraints.excluded` | `[]` (없음) | 제외 항목 없이 검색 범위 최대화 |
| `deliverable` | `"실행 가능한 코드"` | 가장 구체적인 결과물 형태 |

---

## 4. search_keywords 생성 규칙

인터뷰 완료 후, Phase B 검색에 사용할 키워드를 자동 생성합니다.

**생성 로직**:
1. `goal_refined`에서 핵심 명사/동사 추출 (2~3개)
2. `constraints.stack`의 주요 기술명 추가 (1~2개)
3. 총 3~5개 키워드로 구성

**예시**:
- goal: "유튜브 영상 자동 편집 도구" + stack: ["Python", "FFmpeg"]
- → `search_keywords`: `["youtube automation", "video editing", "Python FFmpeg"]`

**규칙**:
- 영어 키워드 우선 (검색 범위 확대)
- 한국어 고유명사는 그대로 유지
- `excluded` 항목의 키워드는 포함하지 않음

---

## 5. consult.json 출력 규칙

### 5.1 출력 전 사용자 확인

JSON 저장 전, 수집된 정보를 아래 형식으로 정리하여 사용자에게 보여줍니다:

```
정리된 내용을 확인해주세요:

- 목표: {goal_refined}
- 기술 스택: {constraints.stack}
- 사용 도구: {constraints.tools}
- 역량 수준: {constraints.capabilities}
- 제외 항목: {constraints.excluded}
- 결과물 형태: {deliverable}
- 검색 키워드: {search_keywords}

이대로 진행할까요?
```

사용자가 수정을 요청하면 해당 항목만 수정 후 다시 확인합니다.

### 5.2 스키마

```json
{
  "goal": "사용자 원문 그대로",
  "goal_refined": "AI가 한 줄로 정리한 목표",
  "constraints": {
    "stack": ["기술 스택 배열"],
    "tools": ["도구 배열"],
    "capabilities": "beginner|intermediate|advanced",
    "budget": "예산/시간 제약 문자열 또는 null",
    "excluded": ["제외 항목 배열"]
  },
  "deliverable": "결과물 형태 문자열",
  "search_keywords": ["키워드 배열 (3~5개)"]
}
```

### 5.3 저장

- 경로: `test/{slug}/pipeline/consult.json`
- Write 도구로 저장
- 저장 후 사용자에게 "consult.json이 저장되었습니다" 알림

---

## 6. 에러 대응

| 상황 | 대응 |
|------|------|
| 사용자가 목표를 명확히 말하지 못함 | 예시 3개 제시하여 선택 유도: "예를 들면, (1) 업무 자동화 도구, (2) 데이터 수집/분석, (3) 콘텐츠 제작 도구 중 가까운 게 있나요?" |
| 모든 질문에 "모르겠어" | 기본값 전체 적용 제안 + 확인 |
| 사용자가 중간에 목표를 바꿈 | 변경된 목표로 goal/goal_refined 재설정, 이전 답변 중 유효한 것은 유지 |
| 3라운드 후에도 정보 부족 | 부족한 항목에 기본값 적용하고 "부족한 부분은 기본값으로 설정했습니다" 안내 후 진행 |
