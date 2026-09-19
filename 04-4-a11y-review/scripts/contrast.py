#!/usr/bin/env python3
"""WCAG 2.1 명암비 계산기 (표준 라이브러리만 사용).

사용법:
    python contrast.py "#ffffff" "#cccccc"              # 한 쌍
    python contrast.py --pairs pairs.txt                # 여러 쌍 (한 줄에 "전경 배경 [설명]")
    python contrast.py "#fff" "#ccc" --large            # 큰 텍스트(18pt+/14pt bold) 기준 적용

출력: PASS/FAIL, 명암비, 적용 기준, 그리고 FAIL일 때 통과에 필요한 최소 조정치.
종료 코드: 0 = 전부 통과, 1 = 하나라도 실패, 2 = 입력 오류
색상 값만 판정합니다. 이미지·스크린샷의 색을 추출하지는 못하므로 값은 사람이 뽑아 넘겨야 합니다.
"""
import sys

AA_NORMAL, AA_LARGE, AAA_NORMAL = 4.5, 3.0, 7.0


def parse_hex(value):
    v = value.strip().lstrip("#")
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    if len(v) != 6 or any(c not in "0123456789abcdefABCDEF" for c in v):
        raise ValueError(f"색상 형식이 아닙니다: {value}")
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4))


def luminance(rgb):
    channels = []
    for c in rgb:
        s = c / 255
        channels.append(s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    l1, l2 = sorted((luminance(parse_hex(fg)), luminance(parse_hex(bg))), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def report(fg, bg, note, large):
    threshold = AA_LARGE if large else AA_NORMAL
    label = "AA 큰 텍스트(3:1)" if large else "AA 일반 텍스트(4.5:1)"
    r = ratio(fg, bg)
    status = "PASS" if r >= threshold else "FAIL"
    line = f"{status} {r:.2f}:1  {fg} on {bg}  [{label}]"
    if note:
        line += f"  - {note}"
    print(line)
    if status == "PASS" and r < AAA_NORMAL and not large:
        print(f"      AAA(7:1)에는 미달합니다. 본문 텍스트라면 검토하세요.")
    if status == "FAIL":
        need = threshold / r
        print(f"      기준 미달: {threshold}:1을 넘기려면 명암 차이를 약 {need:.2f}배 키워야 합니다.")
    return status == "PASS"


def main():
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 콘솔에서 한글이 깨지지 않게 고정
    args = [a for a in sys.argv[1:]]
    large = "--large" in args
    if large:
        args.remove("--large")

    pairs = []
    if args[:1] == ["--pairs"]:
        if len(args) < 2:
            print("--pairs 뒤에 파일 경로가 필요합니다.")
            return 2
        with open(args[1], encoding="utf-8") as f:
            for raw in f:
                parts = raw.split("#")[0].split() if raw.strip().startswith(("//", ";")) else raw.split()
                if len(parts) >= 2:
                    pairs.append((parts[0], parts[1], " ".join(parts[2:])))
    elif len(args) == 2:
        pairs.append((args[0], args[1], ""))
    else:
        print(__doc__)
        return 2

    if not pairs:
        print("검사할 색상 쌍이 없습니다.")
        return 2

    try:
        results = [report(fg, bg, note, large) for fg, bg, note in pairs]
    except ValueError as e:
        print(f"입력 오류: {e}")
        return 2

    failed = results.count(False)
    print(f"요약: {len(results)}쌍 중 {failed}쌍 미달")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
