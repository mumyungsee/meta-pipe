# Module-2: Phase A (Consult) — Plan

> Phase A 레퍼런스 파일(`references/consult.md`) 구현 계획

## 목표

사용자의 목표, 제약 조건, 기대 결과물을 대화형으로 수집하여 `consult.json`으로 구조화

## Design 문서 기준 (4.1 + 8.3)

### 구현할 것

1. **인터뷰 질문 시나리오** (최대 3라운드, 한 번에 2개 이하)
   - 기술 스택/도구 제약
   - 코딩 역량 수준 (beginner/intermediate/advanced)
   - 결과물 형태 (코드/문서/자동화 등)
2. **"모르겠어" 대응 기본값 테이블**
   - 각 질문별 합리적 기본값 정의
3. **consult.json 출력 규칙**
   - 스키마 준수 (goal, goal_refined, constraints, deliverable, search_keywords)
   - search_keywords 자동 생성 로직 (goal + constraints 기반)
4. **수집 정보 정리 → 사용자 확인 단계**

### 완료 기준 (Design 7.2 T-01)

- `consult.json`에 goal, constraints, deliverable 3요소 모두 포함
- 인터뷰 3라운드 이내 완료
- "모르겠어" 입력 시 기본값 제안 동작

### 테스트 방법

- 실제로 `/meta-pipe` 실행 → Phase A만 동작 확인
- 테스트 입력: "bkit 플러그인 만들고 싶어"
- 검증: 생성된 consult.json이 스키마와 일치하는지 확인

## 산출물

- `skills/meta-pipe/references/consult.md`
