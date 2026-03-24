# Phase B: Design Pipeline - 상세 가이드

> 이 문서는 SKILL.md의 Phase B 실행 시 로드된다.
> 도메인 맞춤 파이프라인 설계의 구체적인 알고리즘, 판단 기준, 출력 규칙을 정의한다.

---

## 1. 파이프라인 단계 도출 알고리즘

### 1.1 도메인 지식에서 단계 후보 추출

Phase A 조사 결과를 분석하여 파이프라인 단계 후보를 도출한다:

```
입력: discovery.json (Phase A 결과)

Step 1: 워크플로우에서 핵심 단계 추출
  workflow.standard_process → 각 프로세스 단계를 파이프라인 후보로

Step 2: 데이터 모델에서 설계 단계 추가
  data_model.entities → "데이터 모델 설계" 단계 추가
  복잡한 엔티티 관계 → "스키마 설계" 단계 추가

Step 3: 리스크에서 검증/준수 단계 추가
  risks.items (severity=high) → 대응 단계 추가
  법적/규제 리스크 → "컴플라이언스/법적 준수" 단계 추가
  보안 리스크 → "보안 설계" 단계 추가

Step 4: 기술 스택에서 구현 단계 추가
  tech_stack.recommended_approach → 핵심 기술 구현 단계 추가

Step 5: 공통 단계 추가
  항상 포함: "용어/요구사항 정의" (첫 단계), "통합 테스트" (마지막 단계)
```

### 1.2 bkit 9단계와 비교 차별화

반드시 bkit 9단계와 비교하여 도메인 맞춤화를 검증한다:

```
bkit 9단계:
  1. Schema/Terminology
  2. Coding Convention
  3. Mockup Development
  4. API Design/Implementation
  5. Design System
  6. UI Implementation
  7. SEO/Security
  8. Review
  9. Deployment

비교 절차:
  FOR each bkit_step:
    IF 이 도메인에 불필요:
      제거하고 이유 기록
      예: "카드뉴스 → Mockup 불필요 (시각 결과물이 곧 제품)"
    IF 이 도메인에 필요하지만 내용이 다름:
      도메인에 맞게 변형
      예: "핀테크 → SEO/Security를 '보안 아키텍처 설계'로 격상"

  FOR each pipeline_step:
    IF bkit에 없는 도메인 고유 단계:
      "도메인 고유" 라벨 부여
      예: "카드뉴스 → 템플릿 엔진 설계 (도메인 고유)"
```

### 1.3 단계 정렬

```
정렬 원칙:
  1. 정의/설계 단계가 앞 (용어, 데이터 모델, 아키텍처)
  2. 구현 단계가 중간
  3. 검증/배포 단계가 뒤
  4. depends_on 관계 반영 (선행 단계가 앞)

의존성 규칙:
  - "데이터 모델" → "구현" 단계들의 선행
  - "법적 준수" → "데이터 모델" 이후 (엔티티에 법적 필드 추가 필요)
  - "통합 테스트" → 모든 구현 단계 이후
```

---

## 2. Adaptive Depth (단계 수 결정)

### 2.1 복잡도 평가

```
도메인 복잡도 요소:
  1. 규제 수준: 높음(핀테크, 의료) / 중간(이커머스) / 낮음(CLI, 게임)
  2. 엔티티 수: 10개+ (높음) / 5-9개 (중간) / 1-4개 (낮음)
  3. 플랫폼 수: 3개+ (높음) / 1-2개 (중간) / 단일 (낮음)
  4. 기술 스택 다양성: 프론트+백+인프라 (높음) / 2개 (중간) / 1개 (낮음)
  5. 리스크 심각도: high 항목 3개+ (높음) / 1-2개 (중간) / 0개 (낮음)
```

### 2.2 단계 수 가이드

```
단순 (complexity_score <= 5):  3~5단계
  예: CLI 도구, 간단한 스크립트, 단일 목적 라이브러리

일반 (complexity_score 6~10): 6~8단계
  예: 카드뉴스 자동화, 이커머스, 교육 플랫폼

복잡 (complexity_score >= 11): 8~12단계
  예: 핀테크, 의료 시스템, 대규모 멀티플랫폼 서비스
```

---

## 3. approval_required 판단

### 3.1 TRUE 조건 (하나라도 해당 시)

```
1. 법적/규제 리스크
   - 해당 단계의 결정이 법적 책임에 영향
   - 규제 요구사항 충족 여부 판단 필요
   예: 접근성/법적 준수, 컴플라이언스 검증

2. 아키텍처 결정
   - 전체 시스템 구조에 영향을 미치는 설계
   - 변경 시 다수의 후속 단계에 영향
   예: 데이터 모델, 용어 정의

3. 되돌리기 어려운 결정
   - 이 단계 이후에 변경하면 비용이 크게 증가
   예: 기술 스택 선정, 데이터 스키마

4. 콘텐츠 품질 핵심
   - 최종 결과물의 품질이 이 단계에 크게 의존
   예: 프롬프트 설계, 콘텐츠 생성 로직
```

### 3.2 FALSE 조건

```
1. 앞 단계에서 범위가 확정된 구현 세부사항
2. 테스트/검증 단계 (결과만 리포트)
3. 기술적 최적화 (성능, 포맷 등)
4. 배포/패키징 (설정 기반)
```

### 3.3 목표 비율

```
전체 단계의 30~50%가 approval_required=true
  - 50% 초과: 승인 피로도 → 일부를 false로 조정
  - 30% 미만: 자율 실행 비율 과다 → 리스크 재점검
```

---

## 4. 이중 형식 출력

### 4.1 pipeline.md (마크다운)

```markdown
# Phase B: Design Pipeline - {domain} 파이프라인

> **도메인**: {domain}
> **설계 일자**: {date}
> **기반**: Phase A 도메인 조사 결과

---

## 파이프라인 개요

(ASCII 플로우차트)

---

## Step 1: {name}

**목적**: {purpose}

**할 일**:
- {task 1}
- {task 2}

**산출물**:
- `{file_path}` - {description}

**완료 기준**:
- {criterion 1}
- {criterion 2}

**도메인 특화 주의사항**:
- {warning 1}
- {warning 2}

**approval_required**: {true/false}
> 이유: {reason}

---

(반복)

---

## 파이프라인 요약표

| Step | 이름 | 핵심 산출물 | approval_required |
|------|------|------------|-------------------|
| 1 | {name} | {output} | **true**/false |

**approval_required 비율**: {M}/{N} ({percent}%)
```

### 4.2 pipeline.json (구조화 데이터)

Design 문서(섹션 5.4)에 정의된 JSON 스키마를 따른다:

```
필수 필드:
  meta: domain, version, created_at, generated_by, input_prompt
  pipeline: name, description, total_steps, approval_required_count, steps[]
  domain_knowledge: key_entities, recommended_tech_stack, legal_risks

각 step 필수 필드:
  id, name, name_en, purpose, tasks[], outputs[], done_criteria[],
  domain_warnings[], approval_required, depends_on[]

선택 필드:
  approval_reason (approval_required=true인 경우만)
```

---

## 5. bkit 연동 판단

Phase A 조사 후 도메인이 "웹앱 개발"에 해당하는 경우:

```
웹앱 판단 기준:
  - 워크플로우에 "프론트엔드", "백엔드", "API", "UI" 키워드 포함
  - 기술 스택에 React, Next.js, Vue 등 웹 프레임워크 포함
  - 데이터 모델이 CRUD 중심

웹앱으로 판단 시:
  "이 프로젝트는 웹앱 개발에 해당합니다.
  bkit의 9단계 파이프라인을 사용하시겠습니까?
  아니면 meta-pipe로 도메인 맞춤 파이프라인을 설계하시겠습니까?"

  [bkit 사용] → bkit 파이프라인 추천 + Phase A 도메인 지식을 Phase 1에 주입
  [meta-pipe 사용] → 도메인 맞춤 파이프라인 설계 계속
```

---

## 6. 설계 검증 체크리스트

파이프라인 설계 완료 시 자체 검증:

```
[ ] 도메인 고유 단계가 최소 1개 이상 존재하는가?
[ ] bkit 9단계와 완전히 동일하지 않은가?
[ ] approval_required 비율이 30~50% 범위인가?
[ ] 첫 단계가 "정의/설계"이고 마지막이 "검증/테스트"인가?
[ ] depends_on 관계에 순환 의존성이 없는가?
[ ] 모든 단계에 산출물이 정의되어 있는가?
[ ] domain_warnings가 Phase A 리스크를 반영하는가?
[ ] pipeline.md와 pipeline.json의 내용이 일치하는가?
```
