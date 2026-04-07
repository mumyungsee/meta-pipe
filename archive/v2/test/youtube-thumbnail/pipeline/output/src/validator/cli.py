"""정책/품질 검증 CLI.

사용법:
    python -m src.validator.cli --image output/thumb.png --title "AI 자동화 팁" --text "AI 자동화"
"""

import argparse
import sys

from . import quality_checker, policy_checker


def main():
    parser = argparse.ArgumentParser(description="섬네일 정책/품질 검증")
    parser.add_argument("--image", "-i", required=True, help="섬네일 이미지 경로")
    parser.add_argument("--title", required=True, help="영상 제목")
    parser.add_argument("--text", required=True, help="섬네일에 포함된 텍스트")

    args = parser.parse_args()

    # 품질 검증
    quality = quality_checker.check_thumbnail(args.image)
    print(quality.report())
    print()

    # 정책 검증
    policy = policy_checker.check_all(args.title, args.text, args.image)
    print(policy.report())
    print()

    # 종합
    if quality.passed and policy.passed:
        print("종합: 업로드 가능")
    elif not policy.passed:
        print("종합: 업로드 차단 (정책 위반)")
        sys.exit(1)
    else:
        print("종합: 업로드 가능 (경고 확인 필요)")


if __name__ == "__main__":
    main()
