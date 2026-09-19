#!/usr/bin/env python3
"""카드·은행 명세서 CSV를 읽어 범주별 합계만 출력합니다 (표준 라이브러리만 사용).

이 스크립트의 목적은 계산이 아니라 **원본을 대화 밖에 두는 것**입니다.
명세서 원본에는 가맹점명·카드번호·거래 시각이 줄줄이 들어 있습니다.
원본은 이 프로세스 안에서만 읽고, 밖으로는 범주별 합계·건수·기간만 내보냅니다.
개별 거래 내역은 출력하지 않습니다(예외: 미분류 가맹점명 최대 5개. 사용자가 분류를 고쳐야 하므로).

사용법:
    python summarize_spending.py <명세서.csv>
    python summarize_spending.py <명세서.csv> --month 2026-08
    python summarize_spending.py <명세서.csv> --date-col 승인일 --merchant-col 이용하신곳 --amount-col 승인금액

종료 코드:
    0 = 집계 성공 (집계한 행이 1건 이상)
    1 = 파일은 열었지만 집계할 수 없음 (빈 파일 / 열 1개 / 열 이름 매칭 실패 / 데이터 행 0건)
        -> "지출이 없습니다"가 아니라 "집계하지 못했습니다"로 보고해야 하는 경우입니다.
    2 = 파일을 열지 못했거나 인자가 잘못됨
"""
import argparse
import csv
import re
import sys
import unicodedata
from collections import defaultdict

# 범주 정의는 여기 한 곳에만 둡니다. 보고서에서 임의 범주를 새로 만들지 않습니다.
CATEGORY_RULES = [
    ("식비", ["식당", "김밥", "국밥", "분식", "치킨", "피자", "백반", "food"]),
    ("카페·간식", ["카페", "커피", "베이커리", "제과", "디저트", "cafe", "coffee"]),
    ("생활·마트", ["마트", "슈퍼", "편의점", "잡화", "생활", "mart"]),
    ("교통", ["주유", "충전소", "택시", "버스", "지하철", "철도", "주차", "톨게이트"]),
    ("통신·구독", ["통신", "모바일", "인터넷", "구독", "멤버십"]),
    ("의료·약국", ["약국", "의원", "병원", "치과", "한의원"]),
    ("문화·여가", ["서점", "영화", "체육", "헬스", "문화", "도서"]),
]
UNCATEGORIZED = "미분류"
MAX_UNCATEGORIZED_NAMES = 5  # 미분류 가맹점명은 금액 큰 순으로 이만큼까지만 보여 줍니다

# 열 이름은 카드사·은행마다 다릅니다. 후보를 먼저 맞춰 보고, 실패하면 실제 열 이름을 출력하고 멈춥니다.
COLUMN_CANDIDATES = {
    "date": ["이용일자", "이용일", "거래일자", "거래일", "승인일자", "승인일", "사용일", "매출일자", "날짜", "date"],
    "merchant": ["가맹점명", "가맹점", "이용하신곳", "사용처", "거래처", "적요", "내용", "merchant", "description"],
    "amount": ["이용금액", "승인금액", "결제금액", "사용금액", "거래금액", "출금액", "출금", "금액", "amount"],
}
ROLE_LABEL = {"date": "날짜", "merchant": "가맹점", "amount": "금액"}
DATE_PATTERN = re.compile(r"(\d{4})[-./]?(\d{2})[-./]?(\d{2})")


def normalize(header):
    return re.sub(r"[\s_\-()\[\]/]", "", header).lower()


def match_columns(header, overrides):
    """열 이름을 역할에 맞춥니다. 맞추지 못한 역할 목록을 함께 돌려줍니다."""
    normalized = {normalize(name): name for name in header}
    matched, missing = {}, []
    for role, candidates in COLUMN_CANDIDATES.items():
        if overrides.get(role):
            if overrides[role] not in header:
                missing.append(role)
            else:
                matched[role] = overrides[role]
            continue
        found = next((normalized[normalize(c)] for c in candidates if normalize(c) in normalized), None)
        if found is None:
            found = next((name for c in candidates for key, name in normalized.items() if normalize(c) in key), None)
        if found is None:
            missing.append(role)
        else:
            matched[role] = found
    return matched, missing


def parse_amount(text):
    """쉼표·통화 기호·괄호 음수를 걷어내고 정수로 만듭니다. 실패하면 ValueError."""
    value = (text or "").strip().replace(" ", " ")
    if not value:
        raise ValueError("빈 값")
    negative = value.startswith("(") and value.endswith(")")
    if negative:
        value = value[1:-1]
    for token in (",", "₩", "원", "KRW", "krw", "\\", " "):
        value = value.replace(token, "")
    if value.startswith("-"):
        negative, value = True, value[1:]
    elif value.startswith("+"):
        value = value[1:]
    if not re.fullmatch(r"\d+(\.\d+)?", value):
        raise ValueError("숫자로 읽을 수 없음")
    number = int(round(float(value)))
    return -number if negative else number


def parse_date(text):
    match = DATE_PATTERN.search(text or "")
    if not match:
        return None
    year, month, day = match.groups()
    if not (1 <= int(month) <= 12 and 1 <= int(day) <= 31):
        return None
    return f"{year}-{month}-{day}"


def categorize(merchant):
    lowered = (merchant or "").lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword.lower() in lowered for keyword in keywords):
            return category
    return UNCATEGORIZED


def mask_cell(text):
    """열 이름을 알아보는 데 필요한 만큼만 남깁니다. 네 자리 이상 숫자는 가리고 20자에서 자릅니다."""
    masked = re.sub(r"\d{4,}", "****", (text or "").strip())
    return masked[:20] + "…" if len(masked) > 20 else masked


def cell_kind(text):
    value = (text or "").strip()
    if not value:
        return "빈칸"
    if parse_date(value):
        return "날짜꼴"
    try:
        parse_amount(value)
    except ValueError:
        return "글자"
    return "금액꼴"


def looks_like_data_row(cells):
    """첫 줄이 열 이름 줄이 아니라 거래 한 건인지 봅니다."""
    return any(cell_kind(cell) in ("날짜꼴", "금액꼴") for cell in cells)


def header_preview(cells):
    """첫 줄을 화면에 보여 줍니다. 헤더가 아니라 거래 한 건이면 값 대신 칸 모양만 내보냅니다.

    헤더 없이 내려받은 명세서에서 이 줄이 가맹점명·카드번호를 그대로 흘리는 자리입니다.
    열 이름을 알아보는 데는 값이 필요 없으므로, 의심스러우면 값을 내보내지 않습니다.
    """
    if looks_like_data_row(cells):
        return ["첫 줄이 열 이름 줄이 아니라 거래 한 건으로 보입니다. 값은 출력하지 않습니다.",
                f"첫 줄의 칸 모양: {' | '.join(cell_kind(cell) for cell in cells)}"]
    return [f"파일의 실제 열 이름: {' | '.join(mask_cell(cell) for cell in cells)}"]


def fail(*lines):
    """실패 메시지는 표준 출력을 먼저 비운 뒤 내보냅니다. 화면에서 순서가 뒤집히지 않게."""
    sys.stdout.flush()
    for line in lines:
        print(line, file=sys.stderr)
    sys.stderr.flush()


def read_rows(path):
    """utf-8 로 먼저 읽고, 실패하면 cp949 로 다시 읽습니다. 어떤 인코딩이었는지 함께 돌려줍니다."""
    for encoding in ("utf-8-sig", "cp949"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                return list(csv.reader(f)), encoding
        except UnicodeDecodeError:
            continue
        except OSError as error:
            fail(f"오류: 파일을 열지 못했습니다 - {error}")
            sys.exit(2)
    fail(f"오류: {path} 를 utf-8 로도 cp949 로도 읽지 못했습니다. 텍스트 CSV 파일이 맞는지 확인하세요.")
    sys.exit(2)


def won(number):
    return f"{number:,}원"


def pad(text, width, right=False):
    """한글은 두 칸을 차지하므로 글자 수가 아니라 화면 폭으로 맞춥니다."""
    span = sum(2 if unicodedata.east_asian_width(ch) in "WFA" else 1 for ch in text)
    fill = " " * max(width - span, 0)
    return fill + text if right else text + fill


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="명세서 CSV에서 범주별 합계만 뽑습니다. 개별 거래는 출력하지 않습니다.")
    parser.add_argument("csv_path", help="카드사·은행에서 내려받은 명세서 CSV 경로")
    parser.add_argument("--month", help="YYYY-MM 으로 한 달만 집계합니다")
    parser.add_argument("--date-col", help="날짜 열 이름을 직접 지정합니다")
    parser.add_argument("--merchant-col", help="가맹점 열 이름을 직접 지정합니다")
    parser.add_argument("--amount-col", help="금액 열 이름을 직접 지정합니다")
    args = parser.parse_args()

    if args.month and not re.fullmatch(r"\d{4}-\d{2}", args.month):
        fail(f"오류: --month 형식이 잘못됐습니다: {args.month} (예: 2026-08)")
        return 2

    rows, encoding = read_rows(args.csv_path)
    print("가계 지출 집계기 — 원본은 이 스크립트 안에서만 읽고, 밖으로는 합계만 내보냅니다")
    print(f"입력 파일: {args.csv_path}")
    print(f"읽은 인코딩: {encoding}")

    if not rows:
        fail("상태: 집계 못 함 / 사유: 파일이 비어 있습니다(헤더 줄도 없음).",
             "'지출이 없습니다'로 보고하지 마세요. 내려받은 파일을 다시 확인해야 합니다.")
        return 1

    header = [cell.strip() for cell in rows[0]]
    if len(header) < 2:
        fail(f"상태: 집계 못 함 / 사유: 쉼표로 나뉜 열이 {len(header)}개뿐입니다. CSV 파일이 맞는지 확인하세요.",
             *header_preview(header))
        return 1

    overrides = {"date": args.date_col, "merchant": args.merchant_col, "amount": args.amount_col}
    matched, missing = match_columns(header, overrides)
    if missing:
        advice = ("열 이름 줄이 없는 파일입니다. 첫 줄에 열 이름을 직접 적어 넣은 뒤 다시 실행하세요."
                  if looks_like_data_row(header) else
                  "열 이름은 카드사마다 다릅니다. --date-col / --merchant-col / --amount-col 로 지정해 다시 실행하세요.")
        fail(f"상태: 집계 못 함 / 사유: {', '.join(ROLE_LABEL[r] for r in missing)} 열을 찾지 못했습니다.",
             *header_preview(header),
             advice,
             "이 파일이 명세서 CSV가 맞는지도 확인하세요.",
             "0건으로 읽고 '지출이 없습니다'라고 쓰지 마세요.")
        return 1

    index = {role: header.index(name) for role, name in matched.items()}
    print("열 이름 매칭: " + " / ".join(f"{ROLE_LABEL[r]}={matched[r]}" for r in ("date", "merchant", "amount")))

    totals, counts = defaultdict(int), defaultdict(int)
    uncategorized = defaultdict(int)
    dates, months = [], defaultdict(lambda: [0, 0])
    data_rows = failed_amount = failed_date = skipped_month = refunds = 0
    failed_lines = []

    for line_number, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        data_rows += 1
        if len(row) <= max(index.values()):
            failed_amount += 1
            failed_lines.append(line_number)
            continue
        try:
            amount = parse_amount(row[index["amount"]])
        except ValueError:
            failed_amount += 1
            failed_lines.append(line_number)
            continue
        date = parse_date(row[index["date"]])
        if args.month:
            if date is None or not date.startswith(args.month):
                skipped_month += 1
                continue
        if date is None:
            failed_date += 1
        else:
            dates.append(date)
            months[date[:7]][0] += 1
            months[date[:7]][1] += amount
        merchant = row[index["merchant"]].strip()
        category = categorize(merchant)
        totals[category] += amount
        counts[category] += 1
        if category == UNCATEGORIZED:
            uncategorized[merchant or "(가맹점명 없음)"] += amount
        if amount < 0:
            refunds += 1

    counted = sum(counts.values())

    print()
    print("[행 집계]")
    print(f"전체 데이터 행: {data_rows}")
    print(f"집계한 행: {counted}")
    print(f"읽지 못한 행: {failed_amount}")
    if failed_amount:
        preview = ", ".join(str(n) for n in failed_lines[:10])
        print(f"- 금액 칸을 숫자로 읽지 못함(열이 모자란 행 포함): {failed_amount}건 "
              f"(줄 번호 {preview}{' 외' if failed_amount > 10 else ''})")
        print("  ※ 줄 번호만 표시합니다. 내용은 출력하지 않습니다. 이 건수를 반드시 보고서에 적으세요.")
    if args.month:
        print(f"--month {args.month} 로 제외한 행: {skipped_month}")

    if counted == 0:
        print()
        fail("상태: 집계 못 함 / 사유: 집계된 행이 0건입니다.",
             "열은 맞췄지만 읽을 수 있는 금액이 하나도 없었습니다. 열 지정이나 기간 조건을 다시 확인하세요.",
             "'지출이 없습니다'로 보고하지 마세요.")
        return 1

    print()
    print("[기간]")
    print(f"{min(dates)} ~ {max(dates)}" if dates else "날짜를 읽은 행이 없습니다")
    print(f"날짜를 읽지 못한 행: {failed_date}건 (금액은 집계에 포함됨)")

    net = sum(totals.values())
    print()
    print("[범주별 합계]  ※ 개별 거래는 출력하지 않습니다")
    print(pad("범주", 12) + pad("건수", 6, True) + pad("합계", 16, True) + pad("비중", 8, True))
    for category, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        share = f"{amount / net * 100:.1f}%" if net > 0 else "-"
        print(pad(category, 12) + pad(str(counts[category]), 6, True) + pad(won(amount), 16, True) + pad(share, 8, True))
    total_share = "100.0%" if net > 0 else "-"
    print(pad("합계", 12) + pad(str(counted), 6, True) + pad(won(net), 16, True) + pad(total_share, 8, True))
    print(f"※ 합계는 환불·취소(음수 {refunds}건)를 뺀 순액입니다.")

    if uncategorized:
        names = sorted(uncategorized.items(), key=lambda item: item[1], reverse=True)
        shown = ", ".join(name for name, _ in names[:MAX_UNCATEGORIZED_NAMES])
        rest = len(names) - MAX_UNCATEGORIZED_NAMES
        print()
        print("[미분류]")
        print(f"{counts[UNCATEGORIZED]}건 / {won(totals[UNCATEGORIZED])} / 가맹점 {len(names)}곳")
        print(f"가맹점 예시(금액 큰 순, 최대 {MAX_UNCATEGORIZED_NAMES}개): {shown}{f' 외 {rest}곳' if rest > 0 else ''}")
        print("※ 분류를 고치려면 이 스크립트의 CATEGORY_RULES 에 키워드를 추가한 뒤 다시 실행하세요.")

    if len(months) > 1:
        print()
        print("[월별 합계]")
        for month in sorted(months):
            print(f"{month}  {months[month][0]}건  {won(months[month][1])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
