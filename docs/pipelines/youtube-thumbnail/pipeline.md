# Phase B: Design Pipeline - 유튜브 섬네일 자동화 파이프라인

> **도메인**: 유튜브 섬네일 자동화
> **설계 일자**: 2026-03-25
> **기반**: Phase A 도메인 조사 결과
> **복잡도**: 일반 (score 10) -> 7단계

---

## 파이프라인 개요

```
[Step 1] 채널 브랜드 & 용어 정의           ← approval_required
    |
[Step 2] 프롬프트 엔지니어링 & 검증         ← approval_required (핵심)
    |
[Step 3] 이미지 합성 파이프라인 구축
    |
[Step 4] 템플릿 시스템 구현
    |
[Step 5] YouTube API 연동 & 업로드
    |
[Step 6] 정책 준수 & 품질 검증 레이어       ← approval_required
    |
[Step 7] 통합 테스트 & A/B 최적화
```

---

## Step 1: 채널 브랜드 & 용어 정의

**목적**: 섬네일 자동화의 기준이 되는 채널 브랜드 가이드와 도메인 용어를 확정한다.

**할 일**:
- 대상 채널 정보 정의 (채널명, 카테고리, 타겟 시청자)
- 브랜드 컬러 2-3개 확정 (HEX 코드)
- 브랜드 폰트 1-2개 확정 (Google Fonts 중 한글 지원 폰트)
- 섬네일 레이아웃 방향 결정 (인물 중심 / 텍스트 중심 / 오브젝트 중심)
- 도메인 용어 사전 작성 (Phase A 핵심 용어 기반)

**산출물**:
- `docs/steps/step-1-brand-definition.md` - 채널 브랜드 가이드
- `config/brand.json` - 브랜드 설정 (컬러, 폰트, 레이아웃 타입)

**완료 기준**:
- 브랜드 컬러 HEX 코드 2-3개 확정
- 한글 지원 폰트 최소 1개 선정 및 테스트
- 레이아웃 방향 1가지 이상 확정

**도메인 특화 주의사항**:
- 폰트는 반드시 한글 지원 + 오픈소스 라이선스 확인 (Noto Sans KR, Pretendard 등)
- 브랜드 컬러는 YouTube 다크 피드에서 눈에 띄는 고대비 색상 권장
- 모바일에서 가독성 확보를 위해 복잡한 레이아웃 지양

**approval_required**: **true**
> 이유: 브랜드 가이드는 이후 모든 섬네일의 기준이 되는 아키텍처 결정. 변경 시 전체 템플릿 수정 필요.

---

## Step 2: 프롬프트 엔지니어링 & 검증

**목적**: AntiGravity IDE에서 나노바나나용 프롬프트를 실험하고, 재사용 가능한 프롬프트 템플릿을 확정한다.

**할 일**:
- AntiGravity IDE에서 나노바나나 이미지 생성 실험
- 배경 이미지 프롬프트 패턴 3-5개 개발 (텍스트 없이, 16:9)
- 프롬프트에 Step 1 브랜드 톤 반영 (색감, 분위기)
- 채널 카테고리별 프롬프트 변형 테스트 (예: 리뷰, 브이로그, 교육)
- 검증된 프롬프트를 템플릿으로 저장

**산출물**:
- `docs/steps/step-2-prompt-engineering.md` - 프롬프트 엔지니어링 결과 보고서
- `config/prompts/` - 검증된 프롬프트 템플릿 파일들
- `examples/prompt-results/` - AntiGravity에서 생성한 샘플 이미지

**완료 기준**:
- 최소 3개 프롬프트 패턴이 일관된 품질의 배경 이미지를 생성
- 생성된 이미지가 1280x720 16:9에서 텍스트 배치 공간을 확보
- 한글 텍스트를 포함하지 않는 깔끔한 배경 출력 확인

**도메인 특화 주의사항**:
- 프롬프트에 반드시 "no text, no letters, no words" 포함 (AI의 한글 텍스트 렌더링 방지)
- "empty space for text on [left/right/bottom]" 으로 텍스트 배치 영역 확보
- YouTube 모바일 피드에서 눈에 띄려면 고대비, 밝은 색감 프롬프트 필요
- 성적 암시나 폭력적 이미지가 생성되지 않도록 프롬프트에 안전장치 포함

**approval_required**: **true**
> 이유: 프롬프트 품질이 최종 섬네일 품질을 직접 결정. 콘텐츠 품질의 핵심이며 YouTube 정책 위반 리스크 방지 필요.

---

## Step 3: 이미지 합성 파이프라인 구축

**목적**: 나노바나나 배경 + Pillow 텍스트/브랜딩 합성 자동화 파이프라인을 구현한다.

**할 일**:
- OpenRouter 무료 API 또는 Google AI Studio 연동 코드 작성
- Pillow 기반 레이어 합성 구현 (3-Layer: 배경 -> 오버레이 -> 콘텐츠)
- 텍스트 렌더링 모듈 구현 (한글 폰트, Bold, 외곽선, 그림자)
- 인물 사진 합성 모듈 구현 (선택적, 배경 제거 후 배치)
- 최종 이미지 출력 (1280x720, JPEG <2MB, 자동 품질 조정)

**산출물**:
- `src/generator/api_client.py` - 나노바나나 API 클라이언트
- `src/generator/compositor.py` - Pillow 레이어 합성 엔진
- `src/generator/text_renderer.py` - 텍스트 렌더링 모듈
- `docs/steps/step-3-image-pipeline.md` - 파이프라인 구현 문서

**완료 기준**:
- 영상 제목 입력 -> 완성된 섬네일 이미지 자동 출력
- 한글 텍스트가 깨짐 없이 정확하게 렌더링
- 출력 이미지가 YouTube 업로드 규격 충족 (1280x720, <2MB, JPEG/PNG)

**도메인 특화 주의사항**:
- 나노바나나 API rate limit 대응: 실패 시 재시도 + 백오프 로직
- 파일 크기 2MB 초과 시 자동 JPEG 품질 단계적 하향 (95 -> 90 -> 85 -> ...)
- 텍스트는 5단어 이하로 자동 트리밍하는 옵션 고려

**approval_required**: false
> 이유: Step 1(브랜드)과 Step 2(프롬프트)에서 범위가 확정된 구현 단계.

---

## Step 4: 템플릿 시스템 구현

**목적**: 반복 사용 가능한 섬네일 템플릿 시스템을 구축하여 브랜드 일관성을 보장한다.

**할 일**:
- Template 엔티티 기반 JSON 템플릿 포맷 정의
- 기본 템플릿 3종 구현 (텍스트 중심 / 인물+텍스트 / 오브젝트 중심)
- 템플릿 변수 시스템 (제목, 배경 프롬프트, 컬러 오버라이드)
- 템플릿 선택 로직 (영상 카테고리 -> 적합한 템플릿 자동 매칭)
- CLI 인터페이스: `generate --template "review" --title "..." --output ./`

**산출물**:
- `src/templates/template_engine.py` - 템플릿 엔진
- `templates/` - 기본 템플릿 3종 (JSON)
- `docs/steps/step-4-template-system.md` - 템플릿 시스템 문서

**완료 기준**:
- 템플릿 JSON만 교체하면 다른 스타일의 섬네일 생성 가능
- CLI로 `--template`, `--title` 옵션만으로 섬네일 1장 생성
- Step 1 브랜드 가이드(컬러, 폰트)가 모든 템플릿에 자동 적용

**도메인 특화 주의사항**:
- Safe Zone 반영: 우하단에 YouTube 타임스탬프 영역 피하기
- 모바일 프리뷰에서도 텍스트가 읽히는지 축소 테스트
- 인물 사진은 optional - 없으면 텍스트+배경만으로 생성

**approval_required**: false
> 이유: Step 3의 합성 파이프라인을 템플릿으로 구조화하는 구현 단계.

---

## Step 5: YouTube API 연동 & 업로드

**목적**: 생성된 섬네일을 YouTube Data API v3로 자동 업로드하고, 영상 메타데이터를 연동한다.

**할 일**:
- YouTube Data API v3 OAuth 2.0 인증 구현
- `thumbnails.set` 엔드포인트 연동 (섬네일 업로드)
- 영상 목록 조회 & 메타데이터(제목, 태그) 가져오기
- 업로드 결과 확인 & 에러 핸들링
- API 쿼터 사용량 추적 (50 units/upload, 일일 10,000 한도)

**산출물**:
- `src/youtube/auth.py` - OAuth 2.0 인증 모듈
- `src/youtube/uploader.py` - 섬네일 업로드 모듈
- `src/youtube/metadata.py` - 영상 메타데이터 조회 모듈
- `docs/steps/step-5-youtube-api.md` - API 연동 문서

**완료 기준**:
- CLI로 `upload --video-id "xxx" --thumbnail "./thumbnail.jpg"` 실행 시 업로드 성공
- API 쿼터 사용량이 콘솔에 표시
- 인증 토큰 자동 갱신

**도메인 특화 주의사항**:
- OAuth 2.0 credentials는 `.env`에 저장, 절대 커밋 금지
- 쿼터 초과 방지: 업로드 전 남은 쿼터 확인 로직
- `thumbnails.set`은 50 units 소모 -> 일일 최대 200회 업로드 가능

**approval_required**: false
> 이유: YouTube API 연동은 공식 문서 기반의 표준 구현. 기술적 판단만 필요.

---

## Step 6: 정책 준수 & 품질 검증 레이어

**목적**: YouTube 정책 위반 방지 및 섬네일 품질 자동 검증 시스템을 구축한다.

**할 일**:
- 클릭베이트 검증: 섬네일 텍스트와 영상 제목의 일치도 검사
- 콘텐츠 안전 검증: AI 생성 이미지의 성적/폭력적 콘텐츠 필터링
- 기술 규격 검증: 해상도, 파일 크기, 포맷 자동 체크
- 브랜드 일관성 검증: 템플릿 컬러/폰트가 브랜드 가이드와 일치하는지 확인
- 검증 실패 시 업로드 차단 + 경고 메시지

**산출물**:
- `src/validator/policy_checker.py` - 정책 준수 검증 모듈
- `src/validator/quality_checker.py` - 품질 검증 모듈
- `docs/steps/step-6-policy-validation.md` - 정책 검증 규칙 문서

**완료 기준**:
- 정책 위반 가능성이 있는 섬네일에 경고 플래그 표시
- 기술 규격 미달 시 자동 보정 (리사이즈, 압축) 또는 차단
- 검증 통과율 리포트 출력

**도메인 특화 주의사항**:
- YouTube 3 Strike 규칙: 90일 내 3회 위반 시 채널 종료 -> 검증 레이어 필수
- 클릭베이트 판단은 완벽하지 않으므로 `approval_required`로 사람 검토 병행
- AI 생성 이미지에 SynthID 워터마크 포함 (Google 기본 적용)

**approval_required**: **true**
> 이유: 정책 위반은 채널 종료까지 이어질 수 있는 고위험 영역. 검증 규칙 자체를 사람이 승인해야 함.

---

## Step 7: 통합 테스트 & A/B 최적화

**목적**: 전체 파이프라인 E2E 테스트 및 A/B 테스트 기반 성과 최적화 워크플로우를 구축한다.

**할 일**:
- E2E 테스트: 제목 입력 -> 섬네일 생성 -> 검증 -> 업로드 전체 흐름
- A/B 테스트 워크플로우: 동일 영상에 2-3개 변형 생성 -> YouTube Test & Compare 연동
- 성과 수집: YouTube Analytics API로 CTR, 노출수 데이터 수집
- 성과 리포트: 섬네일별 CTR 비교 대시보드 (콘솔 또는 간단한 HTML)
- 프롬프트 피드백 루프: 고성과 섬네일의 프롬프트 패턴 분석 & 저장

**산출물**:
- `src/testing/e2e_test.py` - E2E 테스트 스크립트
- `src/analytics/performance_tracker.py` - 성과 추적 모듈
- `docs/steps/step-7-testing-optimization.md` - 테스트 & 최적화 가이드

**완료 기준**:
- E2E: 제목 1개 입력 -> 60초 이내 섬네일 생성 & 검증 통과
- A/B: 동일 영상에 대해 2개 이상 변형 생성 가능
- 성과: CTR 데이터를 최소 일별 단위로 수집 & 표시

**도메인 특화 주의사항**:
- A/B 테스트는 최소 7일, 변형당 1,000 노출 이상 후 판단
- YouTube는 Watch Time 기준으로 최적화 -> CTR만이 아닌 Watch Time도 추적
- 빈번한 섬네일 변경은 알고리즘에 부정적 -> 테스트 주기 관리 필요

**approval_required**: false
> 이유: 테스트/검증 단계로 결과를 리포트하는 역할. 이전 단계에서 품질이 확정됨.

---

## 파이프라인 요약표

| Step | 이름 | 핵심 산출물 | approval_required |
| --- | --- | --- | --- |
| 1 | 채널 브랜드 & 용어 정의 | `config/brand.json` | **true** |
| 2 | 프롬프트 엔지니어링 & 검증 | `config/prompts/` | **true** |
| 3 | 이미지 합성 파이프라인 구축 | `src/generator/` | false |
| 4 | 템플릿 시스템 구현 | `templates/`, `src/templates/` | false |
| 5 | YouTube API 연동 & 업로드 | `src/youtube/` | false |
| 6 | 정책 준수 & 품질 검증 레이어 | `src/validator/` | **true** |
| 7 | 통합 테스트 & A/B 최적화 | `src/testing/`, `src/analytics/` | false |

**approval_required 비율**: 3/7 (43%)

## bkit 대비 차별화

| bkit 9단계 | 이 파이프라인 | 판단 |
| --- | --- | --- |
| 1. Schema/Terminology | Step 1 채널 브랜드 & 용어 | 변형: 브랜드 가이드 추가 |
| 2. Coding Convention | - | 제거: 자동화 도구 특성상 불필요 |
| 3. Mockup | - | 제거: 섬네일 자체가 시각 산출물 |
| 4. API Design | Step 5 YouTube API 연동 | 변형: 외부 API 연동 |
| 5. Design System | Step 4 템플릿 시스템 | 변형: 디자인 시스템 -> 섬네일 템플릿 |
| 6. UI Implementation | Step 3 이미지 합성 파이프라인 | 변형: UI -> 이미지 합성 |
| 7. SEO/Security | Step 6 정책 준수 & 품질 검증 | 변형: SEO -> YouTube 정책 |
| 8. Review | Step 7 통합 테스트 | 유지 |
| 9. Deployment | - | 제거: CLI 도구, 별도 배포 불필요 |
| - | **Step 2 프롬프트 엔지니어링** | **도메인 고유**: AI 이미지 생성 핵심 |

**도메인 고유 단계**: Step 2 프롬프트 엔지니어링 & 검증
