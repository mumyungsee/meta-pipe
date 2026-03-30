"""YouTube 섬네일 업로드 CLI.

사용법:
    python -m src.youtube.cli upload --video-id VIDEO_ID --thumbnail output/thumb.png
    python -m src.youtube.cli list [--max 10]
    python -m src.youtube.cli info --video-id VIDEO_ID
"""

import argparse

from . import auth, uploader, metadata


def cmd_upload(args):
    youtube = auth.build_youtube_client()
    result = uploader.upload_thumbnail(youtube, args.video_id, args.thumbnail)
    urls = result.get("items", [{}])[0].get("default", {}).get("url", "")
    print(f"섬네일 URL: {urls}")


def cmd_list(args):
    youtube = auth.build_youtube_client()
    videos = metadata.list_videos(youtube, max_results=args.max)
    for v in videos:
        print(f"  {v['id']}  {v['title']}")


def cmd_info(args):
    youtube = auth.build_youtube_client()
    v = metadata.get_video(youtube, args.video_id)
    print(f"제목: {v['title']}")
    print(f"게시일: {v['published_at']}")
    print(f"조회수: {v['view_count']}")
    print(f"태그: {', '.join(v['tags'][:5])}")
    print(f"현재 섬네일: {v['thumbnail_url']}")


def main():
    parser = argparse.ArgumentParser(description="YouTube 섬네일 관리")
    sub = parser.add_subparsers(dest="command", required=True)

    p_upload = sub.add_parser("upload", help="섬네일 업로드")
    p_upload.add_argument("--video-id", required=True, help="YouTube 영상 ID")
    p_upload.add_argument("--thumbnail", required=True, help="섬네일 이미지 경로")

    p_list = sub.add_parser("list", help="내 영상 목록")
    p_list.add_argument("--max", type=int, default=10, help="최대 결과 수")

    p_info = sub.add_parser("info", help="영상 정보 조회")
    p_info.add_argument("--video-id", required=True, help="YouTube 영상 ID")

    args = parser.parse_args()
    {"upload": cmd_upload, "list": cmd_list, "info": cmd_info}[args.command](args)


if __name__ == "__main__":
    main()
