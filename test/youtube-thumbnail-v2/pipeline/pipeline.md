# Phase C: Design Pipeline - 유튜브 섬네일 자동화 (v2)

> **도메인**: 유튜브 섬네일 자동화
> **설계 일자**: 2026-04-04
> **복잡도**: Standard
> **파이프라인 단계 수**: 8
> **Adaptive Depth**: Full 기준 적용 (워크플로우 6개 + required_tools 4개 + quality high → 최고 레벨 8단계)

---

## 파이프라인 설계

| Step | 이름 | 실행 모드 | 필요 도구 | 완료 기준 |
|------|------|:---------:|----------|----------|
| step-1 | API 환경 설정 확인 | manual | huggingface_hub, google-auth-oauthlib | HF token + Google OAuth credentials.json 준비 완료 |
| step-2 | 영상 메타데이터 수집 | assist | google-api-python-client | video_id, 제목, 설명 구조화 완료 |
| step-3 | SDXL 프롬프트 생성 | assist | - | 긍정/부정 프롬프트 사용자 승인 완료 |
| step-4 | 섬네일 이미지 생성 | auto | diffusers, torch, safetensors | 1280×720 이상 PNG/JPEG 파일 생성 완료 |
| step-5 | 텍스트 오버레이 합성 | auto | Pillow | Safe Zone 준수 텍스트 합성 이미지 완료 |
| step-6 | 품질 자동 검증 | auto | Pillow, opencv-python | ValidationResult.overall_pass == true |
| step-7 | 사용자 최종 승인 | manual | - | 정성 품질(디자인, CTR 느낌) 사용자 승인 |
| step-8 | YouTube API 업로드 | auto | google-api-python-client, google-auth-oauthlib | YouTube 영상에 섬네일 업로드 성공 확인 |

---

## Step 상세

### Step 1: API 환경 설정 확인
- **목적**: HuggingFace 및 Google OAuth 인증 설정 확인
- **실행 모드**: manual (도구 세팅 단계 — Phase D에서 처리)
- **필요 도구**: huggingface_hub, google-auth-oauthlib
- **작업 항목**:
  - HuggingFace API token 발급 및 환경변수 설정
  - Google Cloud Console OAuth 2.0 credentials.json 다운로드
  - Python 라이브러리 설치 (diffusers, torch, Pillow, google-api-python-client 등)
- **완료 기준**: HF token 인증 성공 + Google OAuth flow 완료
- **주의사항**: credentials.json 파일 보안 관리 (절대 커밋 금지)

### Step 2: 영상 메타데이터 수집
- **목적**: 섬네일 생성에 필요한 영상 컨텍스트 확보
- **실행 모드**: assist (AI가 메타데이터 파싱 + 사용자 검수)
- **필요 도구**: google-api-python-client (선택적 — 직접 입력도 가능)
- **작업 항목**:
  - 영상 ID 입력 또는 YouTube API에서 메타데이터 조회
  - 제목, 설명, 핵심 키워드 추출
- **완료 기준**: metadata.json 생성 (video_id, title, description, keywords)
- **주의사항**: API 없이 직접 입력 가능 (YouTube API quota 절약)

### Step 3: SDXL 프롬프트 생성
- **목적**: 섬네일 스타일에 최적화된 SDXL 프롬프트 작성
- **실행 모드**: assist (AI 초안 + 사용자 승인 — 품질 high이므로 검수 필수)
- **필요 도구**: -
- **작업 항목**:
  - 영상 메타데이터에서 시각적 키워드 추출
  - 긍정 프롬프트: 주제, 분위기, 스타일, LoRA 트리거 워드
  - 부정 프롬프트: 저품질 요소 제거
- **완료 기준**: prompt.json 생성 (positive_prompt, negative_prompt) + 사용자 승인
- **주의사항**: `youtube thumbnail, ytb` 등 LoRA trigger word 포함 필수

### Step 4: 섬네일 이미지 생성
- **목적**: SDXL LoRA로 고품질 배경 이미지 생성
- **실행 모드**: auto
- **필요 도구**: diffusers, torch, safetensors
- **작업 항목**:
  - `itzzdeep/youtube-thumbnails-sdxl-lora-v3` 로드
  - AutoPipelineForText2Image로 이미지 생성 (1024×1024 → 1280×720 리사이즈)
  - HF Inference API fallback 처리 (로컬 GPU 없을 경우)
- **완료 기준**: raw_image.png 생성 (1280×720 이상)
- **주의사항**: HF rate limit 있음 (무료 tier). CPU 실행 시 ~10분 소요.

### Step 5: 텍스트 오버레이 합성
- **목적**: 제목 텍스트를 Safe Zone 내 합성
- **실행 모드**: auto
- **필요 도구**: Pillow
- **작업 항목**:
  - Google Fonts에서 무료 폰트 사용 (저작권 안전)
  - Safe Zone (중앙 1235×338 px) 내 텍스트 배치
  - WCAG AA 명암비 기준 아웃라인 적용
- **완료 기준**: thumbnail_with_text.png 생성
- **주의사항**: 하단 우측 시간 오버레이 영역 텍스트 배치 금지

### Step 6: 품질 자동 검증
- **목적**: YouTube 업로드 기준 및 평가 기준 충족 확인
- **실행 모드**: auto
- **필요 도구**: Pillow, opencv-python
- **작업 항목**:
  - 해상도 검증: 1280×720 이상
  - 파일 크기 검증: 2MB 이하 (초과 시 JPEG 압축)
  - 명암비 측정: WCAG AA 4.5:1 기준
  - 포맷 검증: JPEG 또는 PNG
- **완료 기준**: validation_result.json 생성 (overall_pass: true)
- **주의사항**: 검증 실패 시 step-5로 rollback

### Step 7: 사용자 최종 승인
- **목적**: 정성적 품질 검수 (AI 단독 CTR 하락 리스크 방지)
- **실행 모드**: manual (사용자 검수 필수)
- **필요 도구**: -
- **작업 항목**:
  - 섬네일 이미지 확인 (브랜드 일관성, 클릭 유도 느낌)
  - 모바일 미리보기 텍스트 가독성 확인
  - 승인 또는 재생성 요청
- **완료 기준**: 사용자 승인 완료
- **주의사항**: AI 단독 운영 시 3주 내 CTR 0.7~2.3p 하락 (31% 사례) — 이 단계 생략 금지

### Step 8: YouTube API 업로드
- **목적**: 완성된 섬네일을 YouTube 영상에 설정
- **실행 모드**: auto
- **필요 도구**: google-api-python-client, google-auth-oauthlib
- **작업 항목**:
  - OAuth 2.0 인증 (token.json 갱신)
  - thumbnails.set API 호출 (50 units 소비)
  - 업로드 결과 확인
- **완료 기준**: YouTube 영상 섬네일 업로드 성공 + upload_result.json 저장
- **주의사항**: 일 quota 10,000 units (썸네일 업로드 최대 200회/일)

---

## 세팅 필요 항목 (Phase D)

| 도구 | 사유 | 세팅 가이드 |
|------|------|------------|
| HuggingFace API token | Step 4 SDXL 이미지 생성 (Inference API 사용 시) | https://huggingface.co/settings/tokens |
| Google OAuth credentials | Step 2, 8 YouTube API 접근 | Google Cloud Console → OAuth 2.0 클라이언트 ID |
| Python packages | Step 4~6, 8 실행 | pip install diffusers torch Pillow opencv-python google-api-python-client google-auth-oauthlib |

---

## 설계 요약

- 총 8단계, auto 4개 / assist 2개 / manual 2개
- 업그레이드 제안: 없음 (첫 실행 — execution_history 없음)
- Phase D 필요 여부: **필요 — 3개 도구 세팅** (HF token, Google OAuth, Python packages)
