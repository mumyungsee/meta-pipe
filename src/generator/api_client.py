"""NanoBanana Pro (Gemini 2.5 Pro Image) API 클라이언트."""

import os
import time
from pathlib import Path

from google import genai
from google.genai import types


def create_client(api_key: str | None = None) -> genai.Client:
    """Google GenAI 클라이언트 생성."""
    key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "GOOGLE_API_KEY 환경변수를 설정하거나 api_key 인자를 전달하세요."
        )
    return genai.Client(api_key=key)


def generate_thumbnail(
    client: genai.Client,
    prompt: str,
    output_path: str | Path,
    model: str = "gemini-2.5-pro-preview-06-05",
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> Path:
    """프롬프트로 섬네일 이미지를 생성하고 파일로 저장.

    Args:
        client: GenAI 클라이언트
        prompt: 완성된 이미지 생성 프롬프트
        output_path: 저장할 파일 경로 (.png)
        model: 사용할 모델 ID
        max_retries: 최대 재시도 횟수 (기본 3회)
        initial_delay: 초기 대기 시간(초). 재시도마다 2배 증가 (exponential backoff)

    Returns:
        저장된 파일의 Path
    """
    last_error: Exception | None = None
    delay = initial_delay

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                ),
            )
            break
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"생성 실패 (시도 {attempt}/{max_retries}): {e}. {delay:.1f}초 후 재시도...")
                time.sleep(delay)
                delay *= 2
            else:
                raise RuntimeError(
                    f"이미지 생성 실패: {max_retries}회 시도 모두 실패. 마지막 오류: {e}"
                ) from last_error

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image_bytes = part.inline_data.data
            output_path.write_bytes(image_bytes)

            size_mb = len(image_bytes) / (1024 * 1024)
            print(f"생성 완료: {output_path} ({size_mb:.2f}MB)")

            if size_mb > 2.0:
                print(f"경고: 파일 크기 {size_mb:.2f}MB > 2MB (YouTube 제한)")

            return output_path

    raise RuntimeError("이미지 생성 실패: 응답에 이미지 데이터가 없습니다.")
