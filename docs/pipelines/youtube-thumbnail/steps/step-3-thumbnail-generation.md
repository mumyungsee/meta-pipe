# Step 3: 섬네일 생성 자동화

> **모델**: NanoBanana Pro (Gemini 2.5 Pro Image)
> **작성일**: 2026-03-27
> **의존**: Step 1 (브랜드), Step 2 (프롬프트)

---

## 1. 아키텍처

```
영상 제목 + 템플릿 ID
    ↓
prompt_builder.py  →  프롬프트 패턴 로드 + {{title}} 치환
    ↓
api_client.py      →  NanoBanana Pro API 호출 (Google GenAI SDK)
    ↓
output/*.png       →  완성 섬네일 (1280x720, 텍스트 포함)
```

**핵심**: Pillow 합성 없이 나노바나나 Pro가 이미지 + 한글 텍스트를 한번에 생성.

---

## 2. 파일 구조

```
src/generator/
├── __init__.py
├── api_client.py       # Google GenAI SDK 클라이언트
├── prompt_builder.py   # 프롬프트 템플릿 로드/치환
└── cli.py              # CLI 인터페이스
```

---

## 3. 사용법

### 템플릿 목록 확인

```bash
python -m src.generator.cli --list
```

### 섬네일 생성

```bash
# 환경변수 설정
export GOOGLE_API_KEY="your_key"

# 생성
python -m src.generator.cli \
  --template tech-gradient \
  --title "AI 자동화" \
  --output output/thumbnail.png
```

### 프롬프트 패턴 (5종)

| ID | 레이아웃 | 용도 |
| --- | --- | --- |
| `tech-gradient` | full_bg | 일반 AI 팁, 도구 소개 |
| `screen-glow` | screen_demo | AI 시연, 튜토리얼 |
| `ai-neural` | full_bg | AI 개념, GPT/LLM |
| `workspace-desk` | screen_demo | 생산성 도구, 설정 |
| `futuristic-ui` | full_bg | 시리즈 시작, 특별 영상 |

---

## 4. API 설정

| 플랫폼 | 설정 |
| --- | --- |
| **Google AI Studio** | `GOOGLE_API_KEY` 환경변수. [키 발급](https://aistudio.google.com/apikey) |
| **모델** | `gemini-2.5-pro-preview-06-05` (기본값, `--model`로 변경 가능) |

---

## 5. 완료 기준 체크

- [ ] `--list` 명령으로 5개 템플릿 표시
- [ ] `--template --title`로 섬네일 이미지 생성
- [ ] 생성 이미지가 YouTube 규격 충족 (1280x720 권장, <2MB)
- [ ] 한글 텍스트가 이미지에 포함되어 생성됨
