#!/usr/bin/env python3
"""콘텐츠 캘린더 CSV 생성기 (표준 라이브러리만 사용).

노션·캘린더 MCP가 연결되지 않았을 때 쓰는 대체 경로 전용 보조 도구입니다.
"다음 달 4주, 화·금 발행" 같은 요일 지정을 실제 날짜로 환산하고,
노션·구글 캘린더에 그대로 임포트되는 CSV를 만듭니다.

사용법:
    python make_calendar_csv.py --start 2026-10-01 --weeks 4 \
        --slot "블로그:화" --slot "인스타그램:금" \
        --topics "가을 신제품 티저,사용법 3단계" \
        --output content-calendar-2026-10.csv

--dry-run 을 붙이면 파일을 만들지 않고 생성될 행만 출력합니다.

종료 코드: 0 = 성공, 1 = 같은 이름의 파일이 이미 있어 쓰지 않음, 2 = 입력 오류
기존 파일은 덮어쓰지 않습니다. 한 번에 최대 4주치까지만 만듭니다.
"""
import argparse
import csv
import datetime
import os
import sys

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
COLUMNS = ["발행일", "요일", "채널", "주제", "형식", "담당", "상태"]
MAX_WEEKS = 4


def parse_slot(text):
    """"블로그:화" -> ("블로그", 1)"""
    parts = [part.strip() for part in text.split(":")]
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f'--slot 형식이 잘못됐습니다: "{text}" (예: "블로그:화")')
    channel, day = parts[0], parts[1].replace("요일", "")
    if day not in WEEKDAYS:
        raise ValueError(f'요일을 알 수 없습니다: "{day}" (월화수목금토일 중 하나)')
    return channel, WEEKDAYS.index(day)


def build_rows(start, weeks, slots, topics):
    rows = []
    for channel, weekday in slots:
        first = start + datetime.timedelta(days=(weekday - start.weekday()) % 7)
        for week in range(weeks):
            date = first + datetime.timedelta(weeks=week)
            rows.append({
                "발행일": date.isoformat(),
                "요일": WEEKDAYS[date.weekday()],
                "채널": channel,
                "주제": "",
                "형식": "",
                "담당": "",
                "상태": "예정",
            })
    rows.sort(key=lambda row: (row["발행일"], row["채널"]))
    for row, topic in zip(rows, topics):
        row["주제"] = topic
    return rows


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="발행 슬롯을 실제 날짜로 환산해 캘린더 CSV를 만듭니다.")
    parser.add_argument("--start", default=datetime.date.today().isoformat(),
                        help="기준 시작일 YYYY-MM-DD (기본: 오늘). 이 날짜 이후 첫 해당 요일부터 시작합니다")
    parser.add_argument("--weeks", type=int, default=MAX_WEEKS, help=f"주 수 (1~{MAX_WEEKS}, 기본 {MAX_WEEKS})")
    parser.add_argument("--slot", action="append", required=True, metavar="채널:요일",
                        help='발행 슬롯. 여러 번 쓸 수 있습니다. 예: --slot "블로그:화"')
    parser.add_argument("--topics", default="", help="주제 목록(쉼표 구분). 날짜 순서대로 채웁니다")
    parser.add_argument("--output", required=True, help="저장할 CSV 경로")
    parser.add_argument("--dry-run", action="store_true", help="파일을 만들지 않고 생성될 행만 출력")
    args = parser.parse_args()

    try:
        start = datetime.date.fromisoformat(args.start)
    except ValueError:
        print(f"오류: --start 날짜 형식이 잘못됐습니다: {args.start} (예: 2026-10-01)", file=sys.stderr)
        return 2
    if not 1 <= args.weeks <= MAX_WEEKS:
        print(f"오류: --weeks 는 1~{MAX_WEEKS} 입니다. 한 번에 {MAX_WEEKS}주치까지만 만듭니다.", file=sys.stderr)
        return 2
    try:
        slots = [parse_slot(text) for text in args.slot]
    except ValueError as error:
        print(f"오류: {error}", file=sys.stderr)
        return 2
    if not args.dry_run and os.path.exists(args.output):
        print(f"오류: {args.output} 파일이 이미 있습니다. 덮어쓰지 않습니다. 다른 이름으로 실행하세요.", file=sys.stderr)
        return 1

    topics = [topic.strip() for topic in args.topics.split(",") if topic.strip()]
    rows = build_rows(start, args.weeks, slots, topics)
    print(f"슬롯 {len(slots)}개 × {args.weeks}주 = 항목 {len(rows)}개 ({rows[0]['발행일']} ~ {rows[-1]['발행일']})")
    for row in rows:
        print(f"  {row['발행일']}({row['요일']}) {row['채널']} / {row['주제'] or '주제 미정'}")
    if len(topics) > len(rows):
        print(f"참고: 주제 {len(topics) - len(rows)}개가 남아 쓰이지 않았습니다.")

    if args.dry_run:
        print("DRY-RUN: 파일을 만들지 않았습니다.")
        return 0

    with open(args.output, "w", encoding="utf-8-sig", newline="\n") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"저장 완료: {args.output} (항목 {len(rows)}개, 인코딩 utf-8-sig)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
