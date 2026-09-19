#!/usr/bin/env python3
"""이미지 생성 API 호출기 (표준 라이브러리만 사용).

사용법:
    python generate_image.py --prompt "<영문 프롬프트>" --output cat.png --dry-run
    python generate_image.py --prompt "<영문 프롬프트>" --output cat.png

--dry-run 은 네트워크를 쓰지 않고 보낼 요청과 예상 비용만 출력합니다. 키가 없어도 동작합니다.
실제 호출에는 OPENAI_API_KEY 환경 변수가 필요합니다.

종료 코드: 0 = 성공, 1 = 호출 실패, 2 = 입력/환경 오류
이 스크립트는 실패했을 때 출력 파일을 만들지 않습니다. 파일이 있으면 생성에 성공한 것입니다.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "dall-e-3"
PRICE_USD = {"1024x1024": 0.040, "1024x1792": 0.080, "1792x1024": 0.080}


def build_payload(args):
    return {
        "model": MODEL,
        "prompt": args.prompt,
        "size": args.size,
        "quality": args.quality,
        "n": 1,
    }


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="프롬프트로 이미지를 생성해 파일로 저장합니다.")
    parser.add_argument("--prompt", required=True, help="영문 프롬프트")
    parser.add_argument("--output", required=True, help="저장할 파일 경로 (.png)")
    parser.add_argument("--size", default="1024x1024", choices=sorted(PRICE_USD))
    parser.add_argument("--quality", default="standard", choices=["standard", "hd"])
    parser.add_argument("--dry-run", action="store_true", help="호출하지 않고 요청 내용만 출력")
    args = parser.parse_args()

    payload = build_payload(args)
    cost = PRICE_USD[args.size] * (2 if args.quality == "hd" else 1)
    print(f"요청: {MODEL} {args.size} {args.quality} / 예상 비용 약 ${cost:.3f}")
    print(f"프롬프트({len(args.prompt)}자): {args.prompt}")

    if args.dry_run:
        print("DRY-RUN: 네트워크를 호출하지 않았습니다. 파일도 만들지 않았습니다.")
        return 0

    if os.path.exists(args.output):
        print(f"오류: {args.output} 파일이 이미 있습니다. 덮어쓰지 않습니다.", file=sys.stderr)
        return 2

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("오류: OPENAI_API_KEY 환경 변수가 없습니다. --dry-run으로 요청 내용만 확인할 수 있습니다.", file=sys.stderr)
        return 2

    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.load(response)
        image_url = body["data"][0]["url"]
        with urllib.request.urlopen(image_url, timeout=120) as image:
            data = image.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        print(f"오류: API가 {e.code}를 반환했습니다. {detail}", file=sys.stderr)
        return 1
    except (urllib.error.URLError, KeyError, TimeoutError) as e:
        print(f"오류: 호출에 실패했습니다. {e}", file=sys.stderr)
        return 1

    if not data.startswith(b"\x89PNG"):
        print("오류: 응답이 PNG가 아닙니다. 파일을 저장하지 않았습니다.", file=sys.stderr)
        return 1

    with open(args.output, "wb") as f:
        f.write(data)
    print(f"저장 완료: {args.output} ({len(data):,} bytes)")
    if body["data"][0].get("revised_prompt"):
        print(f"API가 수정한 프롬프트: {body['data'][0]['revised_prompt']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
