#!/usr/bin/env python3
"""로그에서 장애 시간대의 핵심 이벤트만 시간순으로 추려 타임라인을 만듭니다.

사용법:
    python parse_logs.py app.log
    python parse_logs.py app.log --around "2026-03-02 02:00:15" --minutes 10
    cat app.log | python parse_logs.py - --level ERROR

대상 형식: [2026-03-02 02:00:15] [ERROR] 메시지   (ISO 형식의 T 구분자와 소수점 초도 허용)
형식이 다르면 LINE 정규식만 고쳐 쓰세요. 표준 라이브러리만 사용합니다.
"""
import argparse
import re
import sys
from collections import Counter
from datetime import datetime, timedelta

LINE = re.compile(r"\[(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2})[^\]]*\]\s*\[(\w+)\]\s*(.*)")
LEVELS = ["WARN", "ERROR", "FATAL"]
MAX_EVENTS = 200  # 에이전트 컨텍스트 보호


def parse_time(text):
    return datetime.strptime(text.replace("T", " "), "%Y-%m-%d %H:%M:%S")


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔·파이프에서 한글이 깨지지 않게 고정
    parser = argparse.ArgumentParser(description="장애 타임라인 추출")
    parser.add_argument("path", help="로그 파일 경로. '-'이면 표준 입력")
    parser.add_argument("--around", help="기준 시각 'YYYY-MM-DD HH:MM:SS'")
    parser.add_argument("--minutes", type=int, default=10, help="기준 시각 전후 범위(분)")
    parser.add_argument("--level", default="WARN", choices=LEVELS, help="이 수준 이상만 출력")
    args = parser.parse_args()

    wanted = set(LEVELS[LEVELS.index(args.level):])
    center = parse_time(args.around) if args.around else None
    span = timedelta(minutes=args.minutes)

    source = sys.stdin if args.path == "-" else open(args.path, encoding="utf-8", errors="replace")
    events, total, unparsed = [], 0, 0
    with source:
        for line in source:
            total += 1
            match = LINE.match(line.strip())
            if not match:
                unparsed += 1
                continue
            when, level, message = parse_time(match.group(1)), match.group(2).upper(), match.group(3)
            if level == "WARNING":
                level = "WARN"
            if level not in wanted or (center and abs(when - center) > span):
                continue
            events.append((when, level, message))

    events.sort(key=lambda e: e[0])
    print(f"# 타임라인 ({len(events)}건 / 전체 {total}줄, 형식 불일치 {unparsed}줄)")
    for when, level, message in events[:MAX_EVENTS]:
        print(f"{when:%Y-%m-%d %H:%M:%S} {level:<5} {message}")
    if len(events) > MAX_EVENTS:
        print(f"... 외 {len(events) - MAX_EVENTS}건 생략. --around 와 --minutes 로 범위를 좁히세요.")

    if events:
        print("\n# 요약")
        print(f"최초 이벤트: {events[0][0]:%H:%M:%S} {events[0][1]} {events[0][2]}")
        counts = Counter(re.sub(r"\d+", "N", message) for _, _, message in events)
        for message, count in counts.most_common(5):
            print(f"{count:>4}회  {message}")
    return 0 if events else 1


if __name__ == "__main__":
    sys.exit(main())
