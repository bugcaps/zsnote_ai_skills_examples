#!/usr/bin/env python3
"""하루 브리핑용 기준 시각·일정 수집기 (표준 라이브러리만 사용).

맨 먼저 시스템 시계와 시간대를 읽어 기준 시각 한 줄을 출력합니다.
에이전트가 오늘 날짜를 스스로 짐작하지 않게 하는 것이 이 스크립트의 첫 번째 목적입니다.
--ics 를 주면 내보낸 캘린더 파일에서 대상 날짜의 일정을 뽑습니다.

사용법:
    python collect_agenda.py
    python collect_agenda.py --ics sample-calendar.ics --date tomorrow
    python collect_agenda.py --ics ~/Downloads/calendar.ics --date 2026-09-21

읽기만 합니다. 일정을 만들거나 고치거나 지우지 않습니다.
반복 일정(RRULE)은 펼치지 않습니다. 조용히 빠뜨리지 않도록 "확인 못 함"으로 따로 출력합니다.

종료 코드:
    0 = 기준 시각 출력 성공 (일정을 읽었거나, --ics 를 주지 않아 일정 칸이 비었음)
    1 = --ics 파일을 읽지 못했거나 캘린더 파일이 아님(BEGIN:VCALENDAR 없음)
        -> 일정 칸을 "확인 못 함"으로 적으라는 신호 (브리핑 중단 신호가 아님)
        "0건"은 BEGIN:VCALENDAR 가 있는 파일에서 일정이 실제로 0개일 때만 나옵니다.
    2 = 입력 오류 (날짜 형식 등)
"""
import argparse
import datetime
import sys

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
WANTED = ("DTSTART", "DTEND", "SUMMARY", "RRULE")


def unfold(text):
    """RFC 5545 줄 접힘(다음 줄이 공백으로 시작)을 편다."""
    lines = []
    for raw in text.splitlines():
        if raw[:1] in (" ", "\t") and lines:
            lines[-1] += raw[1:]
        else:
            lines.append(raw)
    return lines


def parse_events(text):
    events, current = [], None
    for line in unfold(text):
        stripped = line.strip()
        if stripped.upper() == "BEGIN:VEVENT":
            current = {}
        elif stripped.upper() == "END:VEVENT":
            if current is not None:
                events.append(current)
            current = None
        elif current is not None and ":" in stripped:
            head, _, value = stripped.partition(":")
            name, *params = head.split(";")
            name = name.upper()
            if name in WANTED:
                current[name] = (value, params)
    return events


def unescape(value):
    return value.replace("\\n", " ").replace("\\,", ",").replace("\\;", ";").strip()


def parse_dt(field):
    """(값, 파라미터) -> (date 또는 datetime, 종일 여부, 주의 문구 또는 None)"""
    value, params = field
    upper = [p.upper() for p in params]
    tzid = next((p.split("=", 1)[1] for p in params if p.upper().startswith("TZID=")), None)
    if "VALUE=DATE" in upper or len(value) == 8:
        return datetime.date(int(value[:4]), int(value[4:6]), int(value[6:8])), True, None
    naive = datetime.datetime.strptime(value.rstrip("Z"), "%Y%m%dT%H%M%S")
    if value.endswith("Z"):
        return naive.replace(tzinfo=datetime.timezone.utc).astimezone(), False, None
    if tzid:
        try:
            from zoneinfo import ZoneInfo
            return naive.replace(tzinfo=ZoneInfo(tzid)).astimezone(), False, None
        except Exception:
            return naive, False, f"시간대 {tzid} 를 해석하지 못해 적힌 시각 그대로 읽었습니다"
    return naive, False, None


def as_date(value):
    return value.date() if isinstance(value, datetime.datetime) else value


def occurs_on(start, end, all_day, target):
    first = as_date(start)
    last = first if end is None else as_date(end)
    if all_day and end is not None:
        last -= datetime.timedelta(days=1)  # 종일 일정의 DTEND 는 끝나는 날 다음 날이다
    if last < first:
        last = first
    return first <= target <= last


def format_time(start, end, all_day):
    if all_day:
        return "종일"
    if end is None or as_date(end) != as_date(start):
        return f"{start:%H:%M}~"
    return f"{start:%H:%M}~{end:%H:%M}"


def resolve_date(text, today):
    if text == "today":
        return today
    if text == "tomorrow":
        return today + datetime.timedelta(days=1)
    return datetime.date.fromisoformat(text)


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="기준 시각을 출력하고, .ics 파일에서 대상 날짜의 일정을 뽑습니다.")
    parser.add_argument("--ics", help="내보낸 캘린더 파일 경로. 없으면 기준 시각만 출력합니다")
    parser.add_argument("--date", default="today", help="대상 날짜: today | tomorrow | YYYY-MM-DD (기본 today)")
    args = parser.parse_args()

    now = datetime.datetime.now().astimezone()
    offset = now.strftime("%z")
    print(f"기준 시각: {now:%Y-%m-%d} ({WEEKDAYS[now.weekday()]}) {now:%H:%M} "
          f"/ 시간대 {now.tzname()}(UTC{offset[:3]}:{offset[3:]}) / 출처: 시스템 시계")

    try:
        target = resolve_date(args.date, now.date())
    except ValueError:
        print(f"오류: --date 형식이 잘못됐습니다: {args.date} (today | tomorrow | 2026-09-21)", file=sys.stderr)
        return 2
    print(f"대상 날짜: {target.isoformat()} ({WEEKDAYS[target.weekday()]})")
    print()
    print("[일정]")

    if not args.ics:
        print("상태: 확인 못 함")
        print("사유: --ics 파일을 주지 않았습니다. 캘린더 읽기 도구나 붙여 넣은 일정 텍스트로 대체하세요.")
        return 0

    try:
        with open(args.ics, encoding="utf-8-sig") as f:
            raw = f.read()
    except OSError as error:
        print("상태: 확인 못 함")
        print(f"사유: 파일을 읽지 못했습니다 - {error}")
        print("일정 칸을 '확인 못 함'으로 적고 브리핑은 계속하세요.")
        return 1

    if "BEGIN:VCALENDAR" not in raw.upper():
        # 빈 캘린더를 내보내도 BEGIN:VCALENDAR 는 남는다. 이 줄이 없으면 캘린더 파일이 아니다.
        print("상태: 확인 못 함")
        print(f"사유: {args.ics} 에 BEGIN:VCALENDAR 가 없습니다. 캘린더 파일이 아니거나 내보내기가 비어 있습니다.")
        print("'0건'으로 적지 마세요. 일정 칸을 '확인 못 함'으로 적고 브리핑은 계속하세요.")
        return 1

    print(f"출처: {args.ics} (내보낸 .ics 파일)")
    found, repeating, notes = [], [], []
    for event in parse_events(raw):
        if "DTSTART" not in event:
            continue
        summary = unescape(event["SUMMARY"][0]) if "SUMMARY" in event else "(제목 없음)"
        try:
            start, all_day, note = parse_dt(event["DTSTART"])
            end = parse_dt(event["DTEND"])[0] if "DTEND" in event else None
        except ValueError:
            notes.append(f"{summary}: 시작·종료 시각을 해석하지 못해 건너뛰었습니다")
            continue
        if note:
            notes.append(f"{summary}: {note}")
        on_target = occurs_on(start, end, all_day, target)
        if "RRULE" in event:
            if on_target:
                found.append((all_day, as_date(start), format_time(start, end, all_day),
                              f"{summary} (반복 일정, 이 회차만 확인됨)"))
            else:
                repeating.append(f"{summary} [{event['RRULE'][0]}]")
            continue
        if on_target:
            found.append((all_day, as_date(start), format_time(start, end, all_day), summary))

    found.sort(key=lambda item: (not item[0], item[2]))
    print(f"상태: {'읽음' if found else '0건'}")
    print(f"건수: {len(found)}")
    for item in found:
        print(f"- {item[2]} {item[3]}")

    if repeating:
        print()
        print(f"[확인 못 함] 반복 일정 {len(repeating)}건")
        print("이 스크립트는 반복 규칙(RRULE)을 펼치지 않습니다. 대상 날짜에 해당하는지 판단할 수 없으므로")
        print("0건에 넣지 말고 '확인 못 함'으로 따로 적으세요.")
        for line in repeating:
            print(f"- {line}")

    if notes:
        print()
        print("[주의]")
        for line in notes:
            print(f"- {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
