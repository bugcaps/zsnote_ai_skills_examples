#!/usr/bin/env python3
"""폴더 안의 파일을 분류 폴더로 옮기고, 옮긴 자취를 로그로 남깁니다 (표준 라이브러리만 사용).

이 스크립트의 목적은 분류가 아니라 **되돌릴 수 있게 옮기는 것**입니다.
파일 정리는 "이렇게 옮길까요?"라고 미리 물어도 소용이 없습니다. 수백 개를 한 번에 옮기면
사용자는 목록을 제대로 읽지 못하고 승인하며, 잘못됐다는 것은 며칠 뒤에 압니다.
그때 필요한 것은 승인 기록이 아니라 어느 파일이 어디에서 어디로 갔는지 적힌 로그입니다.

그래서 이 스크립트는 **한 건마다 로그를 먼저 쓰고(디스크에 밀어 넣고) 그다음 옮깁니다.**
순서가 반대면 중간에 멈췄을 때 무엇이 옮겨졌는지 알 수 없습니다.
로그를 쓸 수 없으면 한 건도 옮기지 않습니다.

무엇도 삭제하지 않습니다. 옮기기만 하고, 덮어쓰지 않고, 빈 폴더도 지우지 않습니다.

사용법:
    python organize_files.py <폴더>                     # 미리보기 (기본값, 아무것도 옮기지 않음)
    python organize_files.py <폴더> --apply             # 실제로 옮김
    python organize_files.py <폴더> --by date --apply   # 날짜(YYYY-MM)별로 묶음
    python organize_files.py --undo <로그파일.csv>      # 로그를 보고 전부 제자리로 되돌림

종료 코드:
    0 = 성공 (실패 0건, 되돌리기는 건너뛴 것도 0건)
    1 = 일부만 처리됨 (로그는 남아 있으므로 --undo 로 되돌릴 수 있음)
    2 = 시작하지 못함 (폴더 없음 / 로그를 쓸 수 없음 / 인자 오류) — 한 건도 옮기지 않음
"""
import argparse
import csv
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── 분류 규칙은 여기 한 곳에만 둡니다. SKILL.md 나 보고서에서 범주를 새로 만들지 않습니다. ──
CATEGORY_RULES = [
    ("이미지", [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tif", ".tiff", ".svg"]),
    ("동영상", [".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"]),
    ("음악", [".mp3", ".m4a", ".wav", ".flac", ".aac", ".ogg"]),
    ("문서", [".pdf", ".doc", ".docx", ".hwp", ".hwpx", ".txt", ".md", ".rtf", ".odt"]),
    ("표·데이터", [".xls", ".xlsx", ".csv", ".tsv", ".json"]),
    ("발표자료", [".ppt", ".pptx", ".key"]),
    ("압축파일", [".zip", ".7z", ".rar", ".tar", ".gz", ".tgz"]),
    ("설치파일", [".exe", ".msi", ".dmg", ".pkg", ".apk", ".deb"]),
]
NO_EXTENSION = "_확장자없음"   # 점이 없거나 이름이 점으로 끝나는 파일
OTHER = "_기타"               # 확장자는 있지만 위 목록에 없는 파일
UNKNOWN_DATE = "_날짜모름"     # --by date 에서 날짜를 정할 수 없는 파일

# 날짜 기준: ① 파일 이름 속 YYYYMMDD / YYYY-MM-DD 가 있으면 그것 ② 없으면 파일 수정 시각(mtime)
# mtime 은 '찍은 날'이 아니라 '마지막으로 고치거나 내려받은 날'입니다. 촬영일(EXIF)은 읽지 않습니다.
FILENAME_DATE = re.compile(r"(20\d{2})[-_. ]?(\d{2})[-_. ]?(\d{2})")
OLDEST_VALID_YEAR = 1980  # 이보다 이른 mtime 은 시각이 지워진 것으로 보고 _날짜모름 으로 보냅니다

LOG_HEADER = ["time", "action", "src", "dst", "note"]
LOG_DIR_DEFAULT = Path.home() / "file-organizer-logs"


def now():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def fail(*lines):
    """실패 메시지는 표준 출력을 먼저 비운 뒤 내보냅니다. 화면에서 순서가 뒤집히지 않게."""
    sys.stdout.flush()
    for line in lines:
        print(line, file=sys.stderr)
    sys.stderr.flush()


def categorize_by_ext(path):
    suffix = path.suffix.lower()
    if not suffix:
        return NO_EXTENSION
    for category, extensions in CATEGORY_RULES:
        if suffix in extensions:
            return category
    return OTHER


def categorize_by_date(path):
    match = FILENAME_DATE.search(path.name)
    if match:
        year, month, day = (int(g) for g in match.groups())
        if 1 <= month <= 12 and 1 <= day <= 31:
            return f"{year:04d}-{month:02d}"
    try:
        stamp = datetime.fromtimestamp(path.stat().st_mtime)
    except OSError:
        return UNKNOWN_DATE
    if stamp.year < OLDEST_VALID_YEAR:
        return UNKNOWN_DATE
    return f"{stamp.year:04d}-{stamp.month:02d}"


def build_plan(target, mode):
    """옮길 것과 건너뛸 것을 나눕니다. 하위 폴더와 숨김 파일은 건드리지 않습니다(재귀하지 않음)."""
    categorize = categorize_by_ext if mode == "ext" else categorize_by_date
    known = {name for name, _ in CATEGORY_RULES} | {NO_EXTENSION, OTHER, UNKNOWN_DATE}
    moves, skips = [], []
    for entry in sorted(target.iterdir(), key=lambda p: p.name):
        if entry.name.startswith("."):
            skips.append((entry, "숨김 파일"))
        elif entry.is_dir():
            reason = "분류 폴더" if (mode == "ext" and entry.name in known) else "하위 폴더"
            skips.append((entry, reason))
        elif not entry.is_file():
            skips.append((entry, "일반 파일이 아님"))
        else:
            moves.append((entry, target / categorize(entry) / entry.name))
    return moves, skips


def open_log(log_path, target, mode):
    """로그 파일을 열고 헤더를 씁니다. 여기서 실패하면 한 건도 옮기지 않습니다."""
    if log_path == target or target in log_path.parents:
        fail(f"오류: 로그 파일이 정리 대상 폴더 안({target})에 있습니다. 로그도 정리 대상이 되어 버립니다.",
             "--log 로 대상 폴더 밖의 경로를 지정하세요.")
        return None
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handle = open(log_path, "w", encoding="utf-8", newline="")
    except OSError as error:
        fail(f"오류: 로그 파일을 쓸 수 없습니다 - {error}",
             "로그를 남길 수 없으면 되돌릴 수 없으므로 한 건도 옮기지 않았습니다.")
        return None
    writer = csv.writer(handle)
    writer.writerow(LOG_HEADER)
    writer.writerow([now(), "RUN", str(target), mode, "이 아래 MOVE 행을 거꾸로 되짚으면 원래대로 돌아갑니다"])
    handle.flush()
    return handle, writer


def write_row(handle, writer, row):
    """로그 한 줄을 디스크까지 밀어 넣습니다. 이 함수가 끝난 뒤에야 파일을 옮깁니다."""
    writer.writerow(row)
    handle.flush()
    os.fsync(handle.fileno())


def move_one(handle, writer, src, dst):
    """로그를 먼저 쓰고 옮깁니다. 실패하면 FAILED 행을 덧붙입니다."""
    write_row(handle, writer, [now(), "MOVE", str(src), str(dst), ""])
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
    except OSError as error:
        write_row(handle, writer, [now(), "FAILED", str(src), str(dst), str(error)])
        return str(error)
    return None


def organize(args):
    target = Path(args.folder).expanduser()
    if not target.is_dir():
        fail(f"오류: 폴더를 찾을 수 없습니다 - {target}")
        return 2
    target = target.resolve()

    moves, skips = build_plan(target, args.by)
    collisions = [(src, dst) for src, dst in moves if dst.exists()]
    collided = {src for src, _ in collisions}
    moves = [(src, dst) for src, dst in moves if src not in collided]

    # 로그부터 엽니다. 옮길 목록을 먼저 보여 준 뒤 실패하면, 성공한 것처럼 보이는 목록 끝에
    # 오류가 붙어 사용자가 '옮겨졌구나'라고 오해합니다. 시작하지 못할 것이면 아무것도 출력하지 않습니다.
    handle = writer = log_path = None
    if args.apply:
        log_path = Path(args.log).expanduser() if args.log else LOG_DIR_DEFAULT / f"move-{datetime.now():%Y%m%d-%H%M%S}.csv"
        log_path = log_path.resolve()
        opened = open_log(log_path, target, args.by)
        if opened is None:
            return 2
        handle, writer = opened

    print(f"대상 폴더: {target}")
    print(f"분류 기준: {'확장자' if args.by == 'ext' else '날짜(YYYY-MM, 파일명 우선 · 없으면 수정 시각)'}")
    print()
    print("[옮길 파일]")
    groups = {}
    for src, dst in moves:
        groups.setdefault(dst.parent.name, []).append(src.name)
    for category in sorted(groups):
        names = groups[category]
        sample = ", ".join(names[:3]) + (f" 외 {len(names) - 3}개" if len(names) > 3 else "")
        print(f"{category}/  {len(names)}개  ({sample})")
    if not groups:
        print("없음")

    print()
    print("[건너뜀]")
    for path, reason in skips:
        print(f"{path.name}  — {reason}")
    for src, dst in collisions:
        print(f"{src.name}  — 같은 이름이 {dst.parent.name}/ 에 이미 있어 그대로 둡니다(덮어쓰지 않음)")
    if not skips and not collisions:
        print("없음")

    if not args.apply:
        print()
        print(f"미리보기입니다. 옮길 {len(moves)}개 / 건너뛸 {len(skips) + len(collisions)}개")
        print("실제로 옮기려면 같은 명령 끝에 --apply 를 붙이세요.")
        print("이 목록을 다 읽고 승인할 필요는 없습니다. 옮긴 뒤 --undo 로 되돌릴 수 있습니다.")
        return 0

    moved = failed = 0
    with handle:
        for path, reason in skips:
            write_row(handle, writer, [now(), "SKIP", str(path), "", reason])
        for src, dst in collisions:
            write_row(handle, writer, [now(), "SKIP", str(src), str(dst), "이름 충돌 — 덮어쓰지 않고 그대로 둠"])
        for src, dst in moves:
            error = move_one(handle, writer, src, dst)
            if error:
                failed += 1
                fail(f"실패: {src.name} — {error}")
            else:
                moved += 1

    print()
    print(f"옮김 {moved}개 / 건너뜀 {len(skips) + len(collisions)}개 / 실패 {failed}개")
    print(f"이동 로그: {log_path}")
    print(f"되돌리려면: python {Path(__file__).name} --undo \"{log_path}\"")
    return 1 if failed else 0


def undo(args):
    """로그를 거꾸로 되짚어 전부 제자리로 돌려놓습니다. 되돌리기도 로그를 남깁니다."""
    log_path = Path(args.undo).expanduser()
    try:
        with open(log_path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
    except OSError as error:
        fail(f"오류: 로그 파일을 읽을 수 없습니다 - {error}")
        return 2
    if not rows or rows[0] != LOG_HEADER:
        fail(f"오류: 이 스크립트가 만든 이동 로그가 아닙니다 - {log_path}")
        return 2

    records = [dict(zip(LOG_HEADER, row)) for row in rows[1:] if len(row) == len(LOG_HEADER)]
    failed_src = {r["src"] for r in records if r["action"] == "FAILED"}
    done = [r for r in records if r["action"] == "MOVE" and r["src"] not in failed_src]
    print(f"이동 로그: {log_path}")
    print(f"되돌릴 대상: {len(done)}건")

    if args.dry_run:
        for record in reversed(done):
            print(f"{record['dst']}  ->  {record['src']}")
        print("미리보기입니다. --dry-run 을 빼면 실제로 되돌립니다.")
        return 0

    undo_log = log_path.with_name(f"undo-{datetime.now():%Y%m%d-%H%M%S}.csv")
    try:
        handle = open(undo_log, "w", encoding="utf-8", newline="")
    except OSError as error:
        fail(f"오류: 되돌리기 로그를 쓸 수 없습니다 - {error}",
             "되돌리기도 기록이 남아야 다시 되돌릴 수 있으므로 한 건도 옮기지 않았습니다.")
        return 2

    writer = csv.writer(handle)
    writer.writerow(LOG_HEADER)
    writer.writerow([now(), "RUN", str(log_path), "undo", "이 실행은 위 로그를 되돌린 기록입니다"])
    handle.flush()

    restored = skipped = failed = 0
    with handle:
        for record in reversed(done):
            src, dst = Path(record["src"]), Path(record["dst"])
            if not dst.exists():
                write_row(handle, writer, [now(), "SKIP", str(dst), str(src), "옮겨 둔 자리에 파일이 없음"])
                fail(f"건너뜀: {dst} — 옮겨 둔 자리에 파일이 없습니다")
                skipped += 1
            elif src.exists():
                write_row(handle, writer, [now(), "SKIP", str(dst), str(src), "원래 자리에 다른 파일이 있어 덮어쓰지 않음"])
                fail(f"건너뜀: {src.name} — 원래 자리에 같은 이름이 이미 있어 덮어쓰지 않았습니다")
                skipped += 1
            else:
                error = move_one(handle, writer, dst, src)
                if error:
                    failed += 1
                    fail(f"실패: {dst} — {error}")
                else:
                    restored += 1

    print(f"되돌림 {restored}건 / 건너뜀 {skipped}건 / 실패 {failed}건")
    print(f"되돌리기 로그: {undo_log}")
    print("빈 채로 남은 분류 폴더는 지우지 않았습니다. 필요하면 직접 지우세요.")
    return 1 if (failed or skipped) else 0  # 하나라도 제자리로 못 돌아갔으면 0이 아닙니다


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="폴더를 정리하고 이동 로그를 남깁니다. 삭제는 하지 않습니다.")
    parser.add_argument("folder", nargs="?", help="정리할 폴더 (하위 폴더는 건드리지 않습니다)")
    parser.add_argument("--apply", action="store_true", help="실제로 옮깁니다. 없으면 미리보기만 합니다")
    parser.add_argument("--by", choices=["ext", "date"], default="ext", help="분류 기준 (기본값: ext)")
    parser.add_argument("--log", help="이동 로그 경로 (기본값: ~/file-organizer-logs/move-<시각>.csv)")
    parser.add_argument("--undo", help="이 이동 로그에 적힌 파일을 전부 제자리로 되돌립니다")
    parser.add_argument("--dry-run", action="store_true", help="--undo 와 함께 쓰면 되돌릴 목록만 보여 줍니다(정리는 --apply 가 없으면 이미 미리보기)")
    args = parser.parse_args()

    if args.apply and args.dry_run:
        fail("오류: --apply 와 --dry-run 은 같이 쓸 수 없습니다.")
        return 2
    if args.undo:
        return undo(args)
    if not args.folder:
        parser.print_usage(sys.stderr)
        fail("오류: 정리할 폴더를 지정하거나 --undo <로그파일> 을 쓰세요.")
        return 2
    return organize(args)


if __name__ == "__main__":
    sys.exit(main())
