#!/usr/bin/env python3
"""회의록(형식: 회의록 v1)의 액션 아이템을 할일목록.md에 이어 붙입니다.

사용법:
    python merge_actions.py <회의록 파일> [--date YYYYMMDD] [--list <할일목록 경로>] [--apply]

--apply 가 없으면 무엇을 더할지만 보여 주고 파일은 건드리지 않습니다.
식별자는 "회의날짜-번호"입니다. 이미 있는 식별자는 다시 넣지 않고, 기존 행은 고치지 않습니다.

종료 코드: 0 정상, 2 시작하지 못함(형식 불일치·날짜 없음 등). 2이면 아무 파일도 바꾸지 않습니다.
"""
import argparse
import re
import sys
from pathlib import Path

NOTES_FORMAT = "형식: 회의록 v1"
LIST_FORMAT = "형식: 할일목록 v1"
LIST_HEADER = [
    "# 할 일 목록",
    "",
    LIST_FORMAT,
    "",
    "> 이 표는 action-tracker 스킬이 회의록에서 옮겨 적습니다. `상태` 열은 사람이 고칩니다. 스크립트는 기존 행을 고치지 않습니다.",
    "",
    "| 식별자 | 할 일 | 담당 | 기한 | 상태 | 출처 |",
    "| :--- | :--- | :--- | :--- | :--- | :--- |",
]


def stop(msg):
    print(f"[중단] {msg}")
    print("아무 파일도 바꾸지 않았습니다.")
    sys.exit(2)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_actions(text):
    lines = text.splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == "## 액션 아이템")
    except StopIteration:
        stop("회의록에 '## 액션 아이템' 절이 없습니다.")
    rows, header = [], None
    for l in lines[start + 1:]:
        if l.startswith("## ") or l.startswith("---"):
            break
        if not l.strip().startswith("|"):
            continue
        c = cells(l)
        if header is None:
            header = c
            if header[:4] != ["번호", "할 일", "담당", "기한"]:
                stop(f"액션 표의 열이 '번호 | 할 일 | 담당 | 기한'이 아닙니다: {' | '.join(header)}")
            continue
        if set(c[0]) <= set(":- "):
            continue
        if not c[0].isdigit():
            stop(f"번호가 숫자가 아닌 행이 있습니다: {l.strip()}")
        rows.append(c[:4])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("notes")
    ap.add_argument("--date", help="회의록 파일명에 날짜가 없을 때 사용자에게 확인받은 회의 날짜(YYYYMMDD)")
    ap.add_argument("--list", help="할일목록 경로. 생략하면 회의록과 같은 폴더의 할일목록.md")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    notes = Path(a.notes)
    if not notes.is_file():
        stop(f"회의록 파일이 없습니다: {notes}")
    text = notes.read_text(encoding="utf-8")
    if NOTES_FORMAT not in text.splitlines()[:5]:
        stop(f"'{NOTES_FORMAT}' 표시가 없습니다. 이 형식을 만드는 meeting-notes-summarizer의 회의록인지 확인하세요.")
    if "____" in text:
        stop("회의록 커버리지에 빈칸(____)이 남아 있습니다. 회의록이 완성된 뒤에 실행하세요.")

    m = re.search(r"회의록-(\d{8})", notes.name)
    date = m.group(1) if m else None
    if a.date:
        if not re.fullmatch(r"\d{8}", a.date):
            stop("--date 는 YYYYMMDD 여덟 자리여야 합니다.")
        if date and date != a.date:
            stop(f"파일명의 날짜({date})와 --date({a.date})가 다릅니다.")
        date = a.date
    if not date:
        stop("회의 날짜가 없어 식별자를 만들 수 없습니다. 사용자에게 회의 날짜를 확인한 뒤 --date YYYYMMDD 로 다시 실행하세요.")

    rows = read_actions(text)
    lst = Path(a.list) if a.list else notes.with_name("할일목록.md")
    existing = set()
    if lst.exists():
        ltext = lst.read_text(encoding="utf-8")
        if LIST_FORMAT not in ltext.splitlines()[:5]:
            stop(f"'{lst}'에 '{LIST_FORMAT}' 표시가 없습니다. 다른 형식의 파일을 덮어쓰지 않습니다.")
        existing = {cells(l)[0] for l in ltext.splitlines() if re.match(r"\|\s*\d{8}-\d+\s*\|", l)}

    new, dup, todo = [], 0, 0
    for num, task, owner, due in rows:
        key = f"{date}-{num}"
        if key in existing:
            dup += 1
            continue
        if "[TODO" in owner or "[TODO" in due:
            todo += 1
        new.append(f"| {key} | {task} | {owner} | {due} | 미완료 | {notes.name} |")

    print(f"회의록: {notes.name} · 회의 날짜 {date} · 액션 {len(rows)}건")
    print(f"추가 {len(new)} / 이미 있음 {dup} / 추가분 중 확인 필요(TODO) {todo}")
    for r in new:
        print("  + " + r)
    if not a.apply:
        print("미리보기입니다. --apply 를 붙이면 할일목록에 씁니다.")
        return
    if not new:
        print(f"더할 행이 없어 {lst} 를 바꾸지 않았습니다.")
        return
    if lst.exists():
        body = lst.read_text(encoding="utf-8").rstrip("\n") + "\n"
    else:
        body = "\n".join(LIST_HEADER) + "\n"
    lst.write_text(body + "\n".join(new) + "\n", encoding="utf-8")
    print(f"저장: {lst}")


if __name__ == "__main__":
    main()
