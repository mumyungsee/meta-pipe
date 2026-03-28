# Plan: 유튜브 섬네일 자동화

> **Feature**: youtube-thumbnail-automation
> **Version**: 1.0
> **Created**: 2026-03-25
> **Updated**: 2026-03-27
> **Status**: Completed
> **PDCA Phase**: Plan → Do 완료

---

## 1. 개요

### 1.1 문제 정의

유튜브 채널 운영 시 매 영상마다 섬네일을 수동 제작하는 것은 시간 소모적이고, 브랜드 일관성 유지가 어렵다. AI 이미지 생성 모델을 활용하여 영상 제목만 입력하면 브랜드 가이드에 맞는 완성 섬네일을 자동 생성하고, YouTube에 업로드하며, 성과를 추적하는 파이프라인이 필요하다.

### 1.2 목표

- 영상 제목 → 완성 섬네일 이미지 원샷 자동 생성
- YouTube API로 자동 업로드
- 정책 준수 자동 검증 (3 Strike 방지)
- A/B 테스트 변형 생성 및 CTR 성과 추적

### 1.3 대상 채널

- **카테고리**: AI 활용법 / 테크 튜토리얼
- **타겟**: AI 활용에 관심 있는 일반인~중급자 (20-40대)
- **톤**: 밝고 활기찬 (Bright & Energetic)
- **비주얼**: AI 시연 화면 위주 → 추후 웹캠/캐릭터 추가

---

## 2. 도메인 조사 결과 (meta-pipe Phase A)

상세: `docs/domain-discovery-youtube-thumbnail.md`

### 2.1 핵심 용어

Thumbnail, CTR, Impression, A/B Test, Clickbait, Safe Zone, Text Overlay, Brand Template 등 10개 용어 정의.

### 2.2 워크플로우 Best Practice

7단계 프로세스: 브랜드 정의 → 템플릿 제작 → 이미지 생성 → 텍스트 합성 → 품질 검증 → 업로드 → 성과 분석

### 2.3 기술 스택

- **이미지 생성**: NanoBanana Pro (Gemini 2.5 Pro Image) - 텍스트 포함 원샷 생성
- **YouTube 연동**: YouTube Data API v3 (OAuth 2.0, thumbnails.set)
- **성과 추적**: YouTube Analytics API (CTR, 노출수)

### 2.4 주요 리스크

- YouTube 클릭베이트 정책 강화 (2025~)
- 3 Strike 규칙: 90일 내 3회 위반 → 채널 종료
- API 쿼터: thumbnails.set 50 units/회, 일일 10,000 (최대 200회/일)

---

## 3. 파이프라인 설계 (meta-pipe Phase B)

상세: `docs/pipeline-youtube-thumbnail.json`

### 3.1 6단계 파이프라인

| # | 단계 | Approval | 산출물 |
|---|------|----------|--------|
| 1 | 채널 브랜드 & 용어 정의 | Yes | brand.json, step-1 문서 |
| 2 | 프롬프트 엔지니어링 & 검증 | Yes | prompt-patterns.json, step-2 문서 |
| 3 | 섬네일 생성 자동화 | No | src/generator/, step-3 문서 |
| 4 | YouTube API 연동 & 업로드 | No | src/youtube/, step-4 문서 |
| 5 | 정책 준수 & 품질 검증 | Yes | src/validator/, step-5 문서 |
| 6 | 통합 테스트 & A/B 최적화 | No | src/testing/, src/analytics/, step-6 문서 |

### 3.2 핵심 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| 이미지 생성 방식 | NanoBanana Pro 원샷 | Pillow 합성 대비 단순하고 빠름 |
| 텍스트 렌더링 | AI가 직접 생성 | 한글 포함 완성 이미지를 한번에 |
| 인증 | OAuth 2.0 | thumbnails.set에 필수 |
| 비용 | Google AI Studio API | AntiGravity IDE 무료 + API 유료 병행 |

---

## 4. 범위

### 4.1 포함 (In Scope)

- 프롬프트 기반 섬네일 이미지 생성
- YouTube API 섬네일 업로드
- 정책/품질 자동 검증
- A/B 변형 생성
- CTR 성과 수집

### 4.2 제외 (Out of Scope)

- 웹 UI / 대시보드
- 로컬 Stable Diffusion 연동 (추후)
- 캐릭터/웹캠 합성 (추후)
- 자동 스케줄링

---

## 5. 의존성

- Python 3.11+
- google-genai (NanoBanana Pro API)
- google-api-python-client (YouTube API)
- Pillow (품질 검증용 이미지 메타 읽기)
- Google Cloud OAuth 2.0 클라이언트
