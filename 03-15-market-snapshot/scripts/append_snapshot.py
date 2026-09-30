#!/usr/bin/env python3
"""오늘의 시장지표 스냅샷을 검사한 뒤 누적 파일에 한 줄로 덧붙입니다.

사용법:
    python append_snapshot.py <스냅샷.csv> <누적.csv> [--items <항목목록.csv>] [--date YYYY-MM-DD]

스냅샷 CSV의 열: 항목,값,기준시각
  - 값은 화면에 보인 숫자 그대로(쉼표 허용) 또는 `확인 못 함`
누적 CSV는 날짜 한 줄에 항목이 열로 늘어선 형태이며, 없으면 새로 만듭니다.

종료 코드: 0 추가함, 1 거부(형식 오류·항목 누락·같은 날짜 중복)
"""
import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

MISSING = "확인 못 함"
NUMBER = re.compile(r"^-?[\d,]+(\.\d+)?$")
DEFAULT_ITEMS = Path(__file__).resolve().parent.parent / "assets" / "market-items.csv"


def refuse(message):
    print(f"[거부] {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="시장지표 스냅샷을 누적 파일에 덧붙입니다.")
    ap.add_argument("snapshot")
    ap.add_argument("history")
    ap.add_argument("--items", default=str(DEFAULT_ITEMS), help="수집할 항목 목록 CSV")
    ap.add_argument("--date", default=date.today().isoformat(), help="기록 날짜 (기본 오늘)")
    args = ap.parse_args()

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        refuse(f"날짜 형식은 YYYY-MM-DD입니다: {args.date}")
    items = [row["항목"] for row in read_csv(args.items)]
    rows = read_csv(args.snapshot)
    if not rows or not {"항목", "값", "기준시각"} <= set(rows[0]):
        refuse("스냅샷 CSV에는 항목,값,기준시각 열이 있어야 합니다")

    snapshot = {row["항목"].strip(): row for row in rows}
    problems = [f"항목 누락: {name}" for name in items if name not in snapshot]
    problems += [f"목록에 없는 항목: {name}" for name in snapshot if name not in items]
    for name in items:
        row = snapshot.get(name)
        if row is None:
            continue
        value = row["값"].strip()
        if value != MISSING and not NUMBER.match(value):
            problems.append(f"숫자가 아님: {name} = {value!r}")
        if value != MISSING and not row["기준시각"].strip():
            problems.append(f"기준시각 없음: {name}")
    if problems:
        refuse("스냅샷을 고쳐야 합니다\n  " + "\n  ".join(problems))

    header = ["날짜"] + items
    history = Path(args.history)
    if history.exists():
        with open(history, encoding="utf-8-sig", newline="") as f:
            existing = list(csv.reader(f))
        if existing and existing[0] != header:
            refuse(f"{history}의 열이 항목 목록과 다릅니다. 항목을 바꿨다면 새 파일로 시작합니다")
        if any(line and line[0] == args.date for line in existing[1:]):
            refuse(f"{args.date} 기록이 이미 있습니다. 같은 날짜는 한 번만 기록합니다")
    else:
        existing = []

    values = [snapshot[name]["값"].strip().replace(",", "") for name in items]
    with open(history, "a", encoding="utf-8-sig" if not existing else "utf-8", newline="") as f:
        writer = csv.writer(f)
        if not existing:
            writer.writerow(header)
        writer.writerow([args.date] + values)

    missing = values.count(MISSING)
    print(f"[추가] {args.date}: {len(items)}개 항목, 확인 못 함 {missing}개 → {history} (누적 {len(existing[1:]) + 1}일)")


if __name__ == "__main__":
    main()
