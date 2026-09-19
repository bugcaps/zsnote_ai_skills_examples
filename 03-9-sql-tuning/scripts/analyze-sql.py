#!/usr/bin/env python3
"""SQL 안티패턴 정적 검사기 (표준 라이브러리만 사용).

사용법:
    python analyze-sql.py query.sql      # 파일에서 읽기
    python analyze-sql.py < query.sql    # 표준 입력에서 읽기
    (쿼리를 명령행 인자로 넘기면 따옴표·% 문자가 셸에서 깨지므로 지원하지 않습니다.)

종료 코드: 0 = 발견 없음, 1 = 안티패턴 발견, 2 = 입력 없음
정규식 기반이라 중첩 서브쿼리나 CTE 내부는 정확히 보지 못합니다. 결과는 '후보'로 다루세요.
"""
import re
import sys

RULES = [
    ("select-star", r"\bSELECT\s+(DISTINCT\s+)?\*",
     "SELECT * 사용. 필요한 컬럼만 명시하면 커버링 인덱스를 쓸 수 있습니다."),
    ("leading-wildcard", r"\bLIKE\s+'%",
     "'%'로 시작하는 LIKE. B-Tree 인덱스를 사용할 수 없어 전체 스캔이 됩니다."),
    ("function-on-column", r"\b(WHERE|AND|OR|ON)\s+\w+\s*\(\s*[\w.]+\s*(,[^)]*)?\)\s*(=|<|>|<=|>=|<>|!=|\bIN\b|\bBETWEEN\b)",
     "조건절에서 컬럼을 함수로 감쌌습니다. 범위 조건으로 바꾸면 인덱스를 쓸 수 있습니다."),
    ("not-in-subquery", r"\bNOT\s+IN\s*\(\s*SELECT\b",
     "NOT IN (서브쿼리). NULL이 섞이면 결과가 비고 성능도 나쁩니다. NOT EXISTS를 검토하세요."),
    ("or-conditions", r"\bWHERE\b(?:(?!\bGROUP\b|\bORDER\b|\bLIMIT\b).)*\bOR\b",
     "WHERE에 OR 사용. 서로 다른 컬럼이면 인덱스 병합이 되지 않을 수 있습니다. UNION ALL을 검토하세요."),
    ("large-offset", r"\bOFFSET\s+\d{4,}|\bLIMIT\s+\d{4,}\s*,",
     "큰 OFFSET. 건너뛴 행도 모두 읽습니다. 키 기반(seek) 페이지네이션을 검토하세요."),
    ("order-by-rand", r"\bORDER\s+BY\s+RAND\s*\(",
     "ORDER BY RAND(). 전체 행을 정렬합니다."),
]


def strip_comments(sql):
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    return re.sub(r"--[^\n]*", " ", sql)


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔·파이프에서 한글이 깨지지 않게 고정
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            raw = f.read()
    elif not sys.stdin.isatty():
        raw = sys.stdin.read()
    else:
        print(__doc__)
        return 2
    if not raw.strip():
        print("입력이 비어 있습니다.")
        return 2

    sql = strip_comments(raw)
    flat = re.sub(r"\s+", " ", sql)
    found = []
    for rule_id, pattern, message in RULES:
        match = re.search(pattern, flat, flags=re.I)
        if match:
            found.append((rule_id, match.group(0).strip()[:60], message))

    for rule_id, snippet, message in found:
        print(f"FOUND [{rule_id}] `{snippet}` - {message}")
    print(f"요약: 안티패턴 후보 {len(found)}건 (검사 규칙 {len(RULES)}개)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
