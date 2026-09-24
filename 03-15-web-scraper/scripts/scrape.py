#!/usr/bin/env python3
"""JS로 렌더링되는 페이지에서 반복 항목을 추출해 JSON으로 저장합니다.

robots.txt를 먼저 확인하고, 막혀 있거나 확인하지 못하면 브라우저를 열지 않고 종료합니다.

사용법:
    python scrape.py <URL> --check-only
    python scrape.py <URL> --item "<항목 셀렉터>" --field 이름=<셀렉터> [--field ...]
                     [--pages N --next "<다음 쪽 링크 셀렉터>"] [--output 파일]

--field의 셀렉터는 항목 안에서 찾습니다.
  이름=셀렉터        첫 번째 요소의 텍스트
  이름=셀렉터@속성   첫 번째 요소의 속성값. 예: link="a@href"
  이름[]=셀렉터      일치하는 모든 요소의 텍스트 목록. 예: tags[]=a.tag

종료 코드: 0 통과, 1 수집 중단(robots 금지·확인 못 함·항목 0건·도구 없음)
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from urllib.error import URLError
from urllib.parse import urljoin, urlsplit
from urllib.robotparser import RobotFileParser

USER_AGENT = "zsnote-web-scraper"
INSTALL = "pip install playwright && python -m playwright install chromium"


def stop(message):
    print(f"[중단] {message}", file=sys.stderr)
    sys.exit(1)


def check_robots(url):
    parts = urlsplit(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser(robots_url)
    try:
        parser.read()
    except (URLError, OSError) as e:
        stop(f"robots.txt 확인 못 함 ({robots_url}: {e}). 확인하지 못한 사이트는 수집하지 않습니다.")
    # 5xx 응답이면 허용·금지 어느 쪽으로도 정해지지 않습니다
    if not (parser.allow_all or parser.disallow_all or parser.mtime()):
        stop(f"robots.txt 확인 못 함 ({robots_url}: 서버 오류). 확인하지 못한 사이트는 수집하지 않습니다.")
    if not parser.can_fetch(USER_AGENT, url):
        stop(f"robots.txt가 이 경로의 수집을 금지합니다 ({robots_url}). 우회하지 않습니다.")
    print(f"[확인] robots.txt 허용: {url}", file=sys.stderr)


def parse_fields(specs):
    fields = {}
    for spec in specs:
        name, sep, selector = spec.partition("=")
        if not sep or not name or not selector:
            stop(f"--field 형식은 이름=셀렉터입니다: {spec}")
        many = name.endswith("[]")
        selector, _, attr = selector.partition("@")
        fields[name.removesuffix("[]")] = (selector, attr or None, many)
    return fields


def read_value(element, attr):
    return element.get_attribute(attr) if attr else element.inner_text().strip()


def extract(page, item_selector, fields):
    items = []
    for element in page.query_selector_all(item_selector):
        row = {}
        for name, (selector, attr, many) in fields.items():
            if many:
                row[name] = [read_value(e, attr) for e in element.query_selector_all(selector)] or None
            else:
                found = element.query_selector(selector)
                row[name] = read_value(found, attr) if found else None
        items.append(row)
    return items


def scrape(url, args, fields):
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeout
        from playwright.sync_api import sync_playwright
    except ImportError:
        stop(f"playwright가 없습니다. {INSTALL}")

    items, visited = [], []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch()
        except PlaywrightError:
            stop(f"chromium을 실행하지 못했습니다. {INSTALL}")
        page = browser.new_page(user_agent=USER_AGENT)
        while url:
            page.goto(url)
            try:
                page.wait_for_selector(args.item, timeout=args.wait_ms)
            except PlaywrightTimeout:
                browser.close()
                stop(f"{url}: {args.wait_ms}ms 안에 '{args.item}' 항목이 나타나지 않았습니다. 0건이 아니라 수집 실패입니다.")
            found = extract(page, args.item, fields)
            items.extend(found)
            visited.append(url)
            print(f"[쪽 {len(visited)}] {url} {len(found)}건", file=sys.stderr)

            url = None
            if len(visited) < args.pages:
                link = page.query_selector(args.next)
                href = link.get_attribute("href") if link else None
                if href:
                    url = urljoin(visited[-1], href)
                    check_robots(url)
                    time.sleep(args.delay)
                else:
                    print(f"[안내] 다음 쪽 링크가 없어 {len(visited)}쪽에서 멈췄습니다", file=sys.stderr)
        browser.close()
    return items, visited


def main():
    for stream in (sys.stdout, sys.stderr):  # Windows 콘솔에서 한글이 깨지지 않게 고정
        stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="렌더링된 페이지의 반복 항목을 JSON으로 추출합니다.")
    ap.add_argument("url")
    ap.add_argument("--check-only", action="store_true", help="robots.txt만 확인하고 끝냅니다")
    ap.add_argument("--item", help="항목 하나를 가리키는 CSS 셀렉터")
    ap.add_argument("--field", action="append", help="이름=셀렉터[@속성], 목록은 이름[]=셀렉터")
    ap.add_argument("--pages", type=int, default=1, help="최대 쪽 수 (기본 1)")
    ap.add_argument("--next", help="다음 쪽 링크 셀렉터. --pages가 2 이상이면 필요합니다")
    ap.add_argument("--delay", type=float, default=2.0, help="쪽 사이 대기 초 (기본 2, 최소 1)")
    ap.add_argument("--wait-ms", type=int, default=10000)
    ap.add_argument("--output", help="저장할 파일. 생략하면 표준 출력")
    args = ap.parse_args()

    check_robots(args.url)
    if args.check_only:
        return
    if not args.item or not args.field:
        stop("--item과 --field가 필요합니다")
    if args.pages > 1 and not args.next:
        stop("--pages가 2 이상이면 --next가 필요합니다")
    if args.delay < 1:
        stop("--delay는 1초 이상이어야 합니다")

    fields = parse_fields(args.field)
    items, visited = scrape(args.url, args, fields)

    missing = sum(1 for row in items for value in row.values() if value is None)
    result = {
        "url": args.url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pages": len(visited),
        "count": len(items),
        "missing_fields": missing,
        "items": items,
    }
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    else:
        print(text)
    print(f"[통과] {len(visited)}쪽 {len(items)}건 추출, 빈 필드 {missing}개", file=sys.stderr)


if __name__ == "__main__":
    main()
