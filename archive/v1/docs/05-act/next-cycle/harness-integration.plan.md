# Plan: Harness 패턴 통합 — Phase B/C 확장

> **Feature**: harness-integration **Version**: 0.1 **Created**: 2026-03-30 **Status**: Draft **관련 문서**: `domain-discovery-pipeline.plan.md` v0.3의 Phase B/C를 확장

---

## 1. 개요

### 1.1 문제 정의

meta-pipe Phase C(Execute)에서 파이프라인 각 단계를 **단일 컨텍스트에서 순차 실행**한다. 이로 인해:

1. **MCP 토큰 낭비**: 이미지 생성 등 외부 도구가 필요한 단계가 하나라도 있으면, 세션 전체에 해당 MCP가 로드됨
2. **컨텍스트 비대화**: Phase A 조사 + Phase B 설계 + Phase C 실행이 하나의 컨텍스트에 쌓임
3. **전문성 희석**: 리서치, 디자인, 코드 생성, 검증을 모두 하나의 프롬프트가 수행

### 1.2 해결 방향

[Harness](https://github.com/revfactory/harness) 프로젝트의 에이전트 분리 패턴을 차용하여:

- Phase B에서 \*\*"누가 실행할지"\*\*까지 설계 (에이전트 + 스킬 정의)
- Phase C를 **서브에이전트 기반 분산 실행**으로 재설계
- 외부 도구가 필요한 단계만 해당 MCP를 로드하는 **토큰 격리** 달성

### 1.3 meta-pipe vs Harness 위치

|  | meta-pipe (유지) | Harness에서 차용 |
| --- | --- | --- |
| 도메인 조사 (Phase A) | WebSearch 기반 5카테고리 | 없음 (Claude 사전지식 의존) |
| 파이프라인 설계 (Phase B) | Adaptive Depth 동적 설계 | 에이전트 분리 로직, 아키텍처 패턴 선택 |
| 실행 (Phase C) | 단일 컨텍스트 순차 | 서브에이전트 분산 실행, \_workspace/ 파일 전달 |

---

## 2. Phase B 확장: 실행 설계 (Step B-3)

### 2.1 현재 Phase B ���름

```
B-1. 단계 후보 추출 (discovery.json 기반)
B-2. 단계 정렬 + approval_required 판단
→ 산출물: pipeline.md, pipeline.json
```

### 2.2 확장된 Phase B 흐름

```
B-1. 단계 후보 추출 (기존)
B-2. 단계 정렬 + approval_required 판단 (기존)
B-3. 실행 설계 (신규)
    B-3.1 각 단계의 required_tools 판단
    B-3.2 에이전트 분리 결정
    B-3.3 아키텍처 패턴 선택
    B-3.4 pipeline.json에 실행 정보 추가
```

### 2.3 에이전트 분리 기준

```
FOR each step in pipeline.steps:
  IF step에 외부 도구/MCP 필요?
    → 독립 에이전트로 분리 (토큰 격리)

  ELSE IF step이 이전 단계에 강하게 의존?
    → 같은 에이전트가 순차 실행 (파일 전달)

  ELSE IF step이 다른 단계와 병렬 가능?
    → 별도 에이전트로 분리 (run_in_background)

  ELSE
    → 이전 에이전트에 병합
```

### 2.4 아키텍처 패턴 선택 (Harness 6패턴 중)

meta-pipe 맥락에서 주로 사용할 패턴:

| 패턴 | 사용 조건 | 예시 |
| --- | --- | --- |
| **파이프라인** | 대부분의 도메인 (순차 의존) | 기본값 |
| **파이프라인 + 팬아웃** | 병렬 가능 구간이 있을 때 | 리서치 3개 병렬 → 통합 |
| **생성-검증** | 품질 검증이 중요한 산출물 | 이미지 생성 → 품질 체크 → 재생성 |

### 2.5 pipeline.json 스키마 확장

기존 step 필드에 실행 정보를 추가:

```json
{
  "steps": [
    {
      "id": "step-1",
      "name": "도메인 용어 & 레퍼런스 분석",
      "agent": "researcher",
      "agent_type": "general-purpose",
      "required_tools": ["WebSearch", "WebFetch"],
      "parallel_group": null,
      "depends_on": [],
      "outputs": ["test/{domain-slug}/pipeline/steps/step-1-glossary.md"]
    },
    {
      "id": "step-4",
      "name": "이미지 생성",
      "agent": "image-creator",
      "agent_type": "general-purpose",
      "required_tools": ["image-generation-mcp"],
      "parallel_group": null,
      "depends_on": ["step-3"],
      "outputs": ["test/{domain-slug}/pipeline/output/thumbnails/"]
    }
  ],
  "execution": {
    "architecture": "pipeline",
    "agents": {
      "researcher": {
        "type": "general-purpose",
        "tools": ["WebSearch", "WebFetch"],
        "steps": ["step-1", "step-2"]
      },
      "image-creator": {
        "type": "general-purpose",
        "tools": ["image-generation-mcp"],
        "steps": ["step-4"]
      }
    },
    "data_transfer": "file-based",
    "workspace": "test/{domain-slug}/pipeline/"
  }
}
```

---

## 3. Phase C 재설계: 분산 실행

### 3.1 현재 Phase C

```
단일 컨텍스트에서:
  FOR each step in pipeline.steps:
    직접 실행 → 산출물 생성 → 다음 단계
```

### 3.2 재설계된 Phase C

```
오케스트레이터 (메인 컨텍스트):
  1. pipeline.json 로드 + execution 섹션 파싱
  2. 에이전트별 실행:

     [순차 구간]
       Agent(researcher, prompt="step-1,2 실행. 결과를 {workspace}/steps/에 저장")
       → 완료 대기
       Agent(designer, prompt="step-3 실행. {workspace}/steps/step-1,2 참조")
       → 완료 대기

     [병렬 구간] (parallel_group이 같은 단계들)
       Agent(agent-A, run_in_background=true, prompt="step-X 실행")
       Agent(agent-B, run_in_background=true, prompt="step-Y 실행")
       → 둘 다 완료 후 다음 진행

     [approval_required 단계]
       에이전트 결과를 사용자에게 보여주고 승인 대기

  3. 전체 완료 후 산출물 요약 보고
```

### 3.3 에이전트 프롬프트 구성

각 서브에이전트에 전달할 프롬프트:

```
당신은 {domain} 도메인의 {role} 전문가입니다.

## 작업
{step.tasks}

## 도메인 지식
{domain-discovery.md의 관련 섹션 또는 요약}

## 주의사항
{step.domain_warnings}

## 산출물
결과를 {workspace}/steps/step-{N}-{slug}.md에 저장하세요.

## 이전 단계 참조
{depends_on 단계의 산출물 경로}
```

### 3.4 데이터 전달: 파일 기반

```
test/{domain-slug}/pipeline/           ← workspace
├── domain-discovery.md             ← Phase A 결과 (모든 에이전트 참조)
├── pipeline.json                   ← 실행 계획 (오케스트레이터 참조)
├── steps/                          ← 각 단계 산출물 (에이전트 간 파일 전달)
│   ├── step-1-glossary.md          ← researcher가 생성
│   ├── step-2-data-model.md        ← researcher가 생성
│   └── step-3-design.md            ← designer가 생성 (step-1,2 Read)
└── output/                         ← 실제 코드/이미지
```

---

## 4. 구현 우선순위

| 순서 | 작업 | 효과 | 난이도 | 비고 |
| --- | --- | --- | --- | --- |
| **v1.1** | pipeline.json에 execution 섹션 추가 (Phase B) | 실행 설계 기반 마련 | 중 | pipeline-design.md 수정 |
| **v1.2** | Phase C를 서브에이전트 기반으로 변경 | MCP 토큰 격리 (핵심) | 중 | execution.md 재작성 |
| **v1.3** | parallel_group 지원 | 병렬 실행으로 속도 향상 | 낮 | run_in_background 활용 |
| **v2.0** | 에이전트 팀 모드 지원 | 복잡한 도메인에서 에이전트 간 실시간 협업 | 높 | TeamCreate 필요 |

---

## 5. 검증 계획

### 5.1 유튜브 썸네일 도메인 재테스트

기존 `test/youtube-thumbnail/pipeline/` 파이프라인을 새 실행 방식으로 재실행:

- Step 1-2 (리서치): researcher 에이전트 (WebSearch만)
- Step 3 (프롬프트 설계): designer 에이전트
- Step 4 (이미지 생성): image-creator 에이전트 (이미지 MCP만 로드)
- Step 5-6 (검증/최적화): validator 에이전트

**검증 기준**:

- 토큰 사용량 비교 (단일 vs 분산)
- 산출물 품질 비교 (동일 이상)
- MCP 로드 횟수 비교

### 5.2 새 도메인 테스트

Harness 통합 후 새 도메인 1개로 end-to-end 테스트:

- 후보: 핀테크, 게임, CLI 도구 (Plan 10.4)

---

## 6. 수정 대상 파일

| 파일 | 변경 내용 |
| --- | --- |
| `skills/meta-pipe/references/pipeline-design.md` | B-3 실행 설계 섹션 추가 |
| `skills/meta-pipe/references/execution.md` | 서브에이전트 실행 로직으로 재작성 |
| `skills/meta-pipe/SKILL.md` | Phase B/C 개요 업데이트 |

---

## 7. 리스크

| 리스크 | 대응 |
| --- | --- |
| 서브에이전트 컨텍스트에 도메인 지식이 부족 | 프롬프트에 domain-discovery.md 요약 포함 |
| 에이전트 간 산출물 형식 불일치 | pipeline.json에 output_format 필드 추가 |
| 서브에이전트 실패 시 복구 | 1회 재시도 후 실패 보고, 나머지 단계 계속 |
| approval_required 단계의 UX | 오케스트레이터가 중간 결과를 사용자에게 직접 보여줌 |
