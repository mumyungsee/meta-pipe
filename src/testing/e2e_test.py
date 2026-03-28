"""E2E 테스트: 제목 입력 → 생성 → 검증 → 업로드 전체 흐름.

사용법:
    python -m src.testing.e2e_test --title "AI 자동화" --template tech-gradient
    python -m src.testing.e2e_test --title "AI 자동화" --template tech-gradient --upload --video-id VIDEO_ID
"""

import argparse
import time
from pathlib import Path

from src.generator import api_client, prompt_builder
from src.validator import quality_checker, policy_checker


def run_e2e(
    title: str,
    template: str,
    output_dir: str = "output",
    upload: bool = False,
    video_id: str | None = None,
) -> dict:
    """E2E 파이프라인 실행.

    Returns:
        결과 dict {generate, validate, upload, elapsed_sec}
    """
    result = {"title": title, "template": template}
    start = time.time()

    # 1. 프롬프트 빌드
    prompt = prompt_builder.build_prompt(template, title)
    print(f"[1/4] 프롬프트 생성 완료 ({len(prompt)}자)")

    # 2. 이미지 생성
    output_path = Path(output_dir) / f"{template}_{title[:10]}.png"
    client = api_client.create_client()
    saved = api_client.generate_thumbnail(client, prompt, output_path)
    result["image_path"] = str(saved)
    print(f"[2/4] 이미지 생성 완료: {saved}")

    # 3. 검증
    quality = quality_checker.check_thumbnail(saved)
    policy = policy_checker.check_all(title, title, str(saved))
    result["quality_passed"] = quality.passed
    result["policy_passed"] = policy.passed
    print(f"[3/4] 검증 완료: 품질={'통과' if quality.passed else '실패'}, 정책={'통과' if policy.passed else '차단'}")

    if not quality.passed or not policy.passed:
        print(quality.report())
        print(policy.report())
        result["upload"] = "skipped"
        result["elapsed_sec"] = round(time.time() - start, 1)
        return result

    # 4. 업로드 (선택)
    if upload and video_id:
        from src.youtube import auth, uploader
        youtube = auth.build_youtube_client()
        upload_result = uploader.upload_thumbnail(youtube, video_id, saved)
        result["upload"] = "success"
        print(f"[4/4] 업로드 완료: {video_id}")
    else:
        result["upload"] = "skipped"
        print(f"[4/4] 업로드 건너뜀 (--upload --video-id 필요)")

    result["elapsed_sec"] = round(time.time() - start, 1)
    print(f"\n완료: {result['elapsed_sec']}초")
    return result


def main():
    parser = argparse.ArgumentParser(description="E2E 섬네일 파이프라인 테스트")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--template", "-t", required=True, help="프롬프트 패턴 ID")
    parser.add_argument("--output-dir", default="output", help="출력 디렉토리")
    parser.add_argument("--upload", action="store_true", help="YouTube 업로드 실행")
    parser.add_argument("--video-id", help="업로드 대상 영상 ID")

    args = parser.parse_args()
    run_e2e(args.title, args.template, args.output_dir, args.upload, args.video_id)


if __name__ == "__main__":
    main()
