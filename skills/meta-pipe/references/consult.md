# Phase A: Consult (컨설팅)

> 사용자의 요구사항과 역량을 파악하고, AI가 현실적 경로를 조사/제안하여, 사용자가 충분한 정보를 바탕으로 결정할 수 있도록 컨설팅한다.

<!-- Design Ref: §3.1 consult-result.json, §6 사용자 프로필, §9 인터랙션 포인트 -->
<!-- Plan SC: v1 대비 파이프라인 실행 성공률 향상 — Phase A가 사용자 맥락 확보 담당 -->

---

## A1. 요구사항 수집

사용자의 원본 입력에서 4가지 축을 파악한다.

| 축 | 파악할 것 | 기본값 (모호 시) |
|----|----------|:---------------:|
| **goal** | 무엇을 만들고 싶은지 (구체적 결과물) | — (필수, 기본값 없음) |
| **automation_level** | full / semi / guide | semi |
| **target_user** | 결과물 사용 주체 — human / ai_agent | human |
| **quality_expectation** | high / medium / low | medium |

### 수집 절차

1. 원본 입력 파싱: 위 4가지 축에 매핑 가능한 정보 추출
2. **모호한 축이 있으면** 구체화 질문 (최대 2회):
   - 1회차: 모호한 축만 묶어서 한 번에 질문
   - 2회차: 여전히 모호하면 한 번 더 질문
   - 그래도 모호하면: 기본값 적용 + "기본값으로 진행합니다" 알림
3. goal이 지나치게 추상적이면 (예: "좋은 거 만들고 싶어") 구체화를 반드시 요청한다. goal만은 기본값 없음.

### 질문 예시

```
입력이 모호할 때:
"'{goal}'을 만들고 싶으시군요. 몇 가지 확인할게요:
1. 자동화 수준: 전자동 / 반자동(AI 초안 + 검수) / 가이드만 — 어떤 걸 원하세요?
2. 품질 기대치: 높음(프로) / 보통 / 낮음(빠른 결과 우선) — 어느 정도를 원하세요?"
```

---

## A2. 사용자 프로필 파악

프로필을 축적하여 반복 인터뷰를 최소화한다.

### 프로필 경로

`runtime/user-profile.json`

### 프로필 로드/갱신 흐름

```
runtime/user-profile.json 존재?
  |
  ├─ No  → 전체 인터뷰 실행 (아래 질문 세트)
  |         → 프로필 생성 + 저장
  |
  └─ Yes → 프로필 로드 + 요약 표시
           "이전 프로필: {capabilities.description}, {tools.description}, {preferences.description}"
           "변경된 것 있나요?"
             |
             ├─ 변경 없음 → 그대로 사용
             └─ 변경 있음 → 변경분만 merge → updated_at 갱신
```

### 전체 인터뷰 질문 세트 (프로필 없을 때)

3가지 카테고리를 한 번에 질문한다:

```
"파이프라인 설계를 위해 몇 가지 확인합니다:

1. 역량: API 키 발급, Docker, CI/CD 중 할 수 있는 것은?
2. 보유 도구: 현재 사용 중인 API 키, 디자인 툴, 개발 환경 등이 있나요?
3. 선호도:
   - 실행 환경: 로컬 우선 / 클라우드 선호?
   - 비용: 무료만 / 소액(~$15/월) / 자유?
   - 자동화: 전자동 선호 / 검수 원함?"
```

### user-profile.json 스키마

```json
{
  "updated_at": "YYYY-MM-DD",
  "capabilities": {
    "api_setup": true,
    "docker": false,
    "ci_cd": false,
    "description": "자유 텍스트 — LLM이 역량을 이해할 수 있도록"
  },
  "tools": {
    "owned": ["tool_id_1"],
    "familiar": ["tool_id_2"],
    "description": "자유 텍스트"
  },
  "preferences": {
    "execution_preference": "local_first | cloud_first",
    "cost_tolerance": "free | low | flexible",
    "automation_preference": "full | semi | guide",
    "description": "자유 텍스트"
  },
  "execution_history": []
}
```

- `execution_history`는 Phase F 완료 후 기록된다 (references/evaluation.md에서 관리).
- 프로필 저장 시 `updated_at`을 현재 날짜로 갱신한다.

---

## A3. Feasibility Research

A1(요구사항) + A2(역량/도구)를 교차 분석하여 현실적 경로 후보를 도출한다.

### 조사 절차

1. **교차 분석 프레임**: "이 역량(A2)으로 이 목표(A1)를 달성하려면 어떤 도구/방법이 있는가?"
2. **WebSearch 조사**: 다음 3가지 관점으로 검색
   - 도구/API 옵션 (무료 vs 유료, 로컬 vs 클라우드)
   - 자동화 가능 범위 (어디까지 auto 가능한가)
   - 필요 세팅 수준 (API 키만? Docker? 인프라?)
3. **경로 후보 도출**: 최소 2개, 최대 4개 경로
   - 각 경로에 대해: 결과물 수준, 필요 세팅, 비용, 사용자 공수, 요구사항 충족도 정리

### AI 단독 작업

A3는 사용자 대화 없이 AI가 단독으로 수행한다. 진행 중 알림만 표시:

```
"요구사항과 역량을 바탕으로 실현 가능한 경로를 조사 중입니다..."
```

---

## A4. 선택지 제안 (Options)

A3에서 도출한 경로 후보를 사용자에게 제안한다.

### 제안 형식

각 경로를 다음 표 형식으로 제시한다:

```
조사 결과, {N}가지 경로를 찾았습니다:

| | 경로 1: {이름} | 경로 2: {이름} | 경로 3: {이름} |
|---|---|---|---|
| **자동화** | full / semi / guide | ... | ... |
| **결과물 수준** | 높/중/낮 | ... | ... |
| **필요 세팅** | {세팅 항목} | ... | ... |
| **예상 비용** | {금액/월} | ... | ... |
| **사용자 공수** | 낮/중/높 | ... | ... |
| **요구사항 충족도** | {N}% | ... | ... |

→ AI 추천: 경로 {N} ({추천 이유})
```

### 사용자 선택

- 사용자가 경로를 선택한다.
- **재조사 요청 시**: A3로 돌아가 추가 조사 후 새 경로 제안. 재조사는 최대 2회.

---

## A5. 조율 확정 (Calibration)

선택된 경로를 기반으로 평가 기준과 실행 모드를 확정한다.

### 확정 항목

1. **eval_criteria** (Phase F에서 사용할 평가 기준):
   - 정량적 기준: 수치로 측정 가능 (예: "텍스트 영역 30% 이상"). `auto_checkable: true`
   - 정성적 기준: 사용자 판단 필요 (예: "밝고 클릭 유도하는 느낌"). `auto_checkable: false`
   - 각 기준에 type + criterion + auto_checkable 명시

2. **complexity** 결정:
   - Light: 기존 도구로 충분. API/인프라 불필요 → Phase D 생략
   - Standard: 일부 API 키, MCP 설정 필요 → Phase D 부분 실행
   - Full: Docker, CI/CD 등 인프라 구축 필요 → Phase D 전체 실행

3. **프로필 갱신**: A4에서 선택한 경로가 프로필에 영향을 주면 갱신
   - 예: 새로운 API 키를 발급받기로 했으면 tools.owned에 추가 예정 표시

### 확정 대화

```
"정리하겠습니다:
- 선택 경로: {경로 이름}
- 복잡도: {Light/Standard/Full}
- 평가 기준:
  1. [정량] {criterion} — 자동 검수 가능
  2. [정성] {criterion} — 사용자 검수 필요

이대로 진행할까요?"
```

사용자 승인 후 A5 완료.

---

## consult-result.json 출력

A1~A5 완료 후 결과를 `test/{domain-slug}/pipeline/consult-result.json`으로 출력한다.

### domain-slug 생성 규칙

사용자의 goal에서 kebab-case slug를 생성한다:
- 한글은 영어로 변환 (예: "유튜브 섬네일" → "youtube-thumbnail")
- 공백은 하이픈으로 치환
- 특수문자 제거
- 소문자

### 출력 스키마

```json
{
  "version": "2.0",
  "phase": "A",
  "created_at": "ISO 8601",
  "summary": "(300자 이내. 목표, 선택 경로, 복잡도를 한 줄로)",

  "requirements": {
    "goal": "구체화된 목표",
    "automation_level": "full | semi | guide",
    "target_user": "human | ai_agent",
    "quality_expectation": "high | medium | low"
  },
  "user_profile": {
    "tools": ["tool_id"],
    "capabilities": "역량 설명",
    "willingness": "high | medium | low",
    "budget": "비용 범위"
  },
  "selected_path": {
    "id": "path-{N}-{slug}",
    "description": "선택 경로 설명",
    "tradeoffs": "타협한 부분 명시"
  },
  "eval_criteria": [
    {
      "type": "quantitative | qualitative",
      "criterion": "평가 기준",
      "auto_checkable": true
    }
  ],
  "complexity": "Light | Standard | Full"
}
```

### 필수 필드 검증

출력 전 다음 필드 존재 여부를 확인한다:
- `requirements` (하위: goal, automation_level, target_user, quality_expectation)
- `user_profile` (하위: tools, capabilities, willingness, budget)
- `selected_path` (하위: id, description, tradeoffs)
- `eval_criteria` (1개 이상)
- `complexity`
- `summary` (300자 이내)

---

## 디렉토리 준비

Phase A 실행 전 다음 경로가 존재하는지 확인하고, 없으면 생성한다:
- `test/{domain-slug}/pipeline/` (consult-result.json 저장)
- `runtime/` (user-profile.json 저장)

---

## Phase A 완료 후

1. `.meta-pipe-status.json` 업데이트: `phases.A.status = "completed"`, `current_phase = "B"`
2. 사용자에게 요약 출력:
   ```
   Phase A 완료.
   - 목표: {goal}
   - 경로: {selected_path.description}
   - 복잡도: {complexity}
   - 평가 기준: {N}개 ({정량 N}개 자동 + {정성 N}개 수동)

   Phase B(도메인 조사)로 진행합니다...
   ```
3. Phase B로 전환 (SKILL.md의 Phase 전환 루프가 처리)
