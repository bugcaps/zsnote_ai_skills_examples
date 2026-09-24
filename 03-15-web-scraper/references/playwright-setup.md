# Playwright 준비와 셀렉터 찾기

## 설치

이 스킬의 스크립트는 표준 라이브러리 밖의 도구인 Playwright를 씁니다. 처음 한 번만 설치합니다.

```bash
pip install playwright
python -m playwright install chromium
```

브라우저 내려받기에 수백 MB가 필요합니다. 설치할 수 없는 환경이면 스킬을 멈추고 사용자에게 알립니다. `requests` 등으로 바꿔 짜면 JS로 그려지는 항목이 0건으로 나옵니다. `--check-only`는 표준 라이브러리만 쓰므로 설치 전에도 실행됩니다.

## 스크래핑보다 먼저 볼 것

| 순서 | 확인할 것 | 있으면 |
| :--- | :--- | :--- |
| 1 | robots.txt | 스크립트(`--check-only`)가 판정합니다. 에이전트가 따로 판단하지 않습니다. robots.txt가 없으면(404) 허용, 401·403이면 금지입니다 |
| 2 | 문서로 공개된 API, 데이터 내려받기(CSV 등) | 스크래핑하지 않고 그것을 씁니다 |
| 3 | 이용약관의 자동 수집 금지 조항 | 사용자에게 알리고 멈춥니다 |

## 셀렉터 찾기

`--check-only`가 통과한 뒤에만 합니다.

1. 렌더링된 DOM을 봅니다. view-source나 `curl`은 JS 실행 전 HTML이라 항목이 없을 수 있습니다.
   - 사람: 브라우저 개발자 도구(F12)의 Elements 탭
   - 에이전트: 아래 한 줄로 렌더링 후 HTML을 `<script>`·`<style>`을 뺀 채 출력합니다. 인라인 스크립트가 길면 항목이 뒤로 밀려 앞부분만 봐서는 보이지 않기 때문입니다.
     ```bash
     python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from playwright.sync_api import sync_playwright as s; p=s().start(); b=p.chromium.launch(); g=b.new_page(); g.goto('<URL>'); g.wait_for_load_state('networkidle'); g.evaluate('document.querySelectorAll(\"script,style\").forEach(e=>e.remove())'); print(g.inner_html('body')[:6000]); b.close(); p.stop()"
     ```
   - 6000자 안에 반복 항목이 보이지 않으면 `[:6000]`을 `[6000:12000]`으로 바꿔 이어서 봅니다.
2. 반복되는 항목 하나를 감싸는 요소로 `--item`을 정합니다. 예: `div.quote`
3. 항목 **안에서** 필드를 가리키는 셀렉터로 `--field`를 정합니다. 예: `--field "text=span.text"`, `--field "author=small.author"`
4. 값이 여러 개인 필드는 `이름[]=셀렉터`로 씁니다. `이름=셀렉터`로 쓰면 첫 번째 값만 들어가고도 빈 필드로 잡히지 않습니다. 예: `--field "tags[]=a.tag"`. zsh에서는 따옴표가 없으면 `[]` 때문에 오류가 납니다.
5. 링크처럼 텍스트가 아닌 값은 `셀렉터@속성`으로 씁니다. 예: `--field "link=a@href"`
6. `id`나 `data-*` 속성을 추측해 쓰지 않습니다. 출력된 DOM에서 본 것만 씁니다.

## 여러 쪽 수집

- `--pages N --next "<다음 쪽 링크 셀렉터>"`로 최대 N쪽을 돌고 결과를 한 파일에 합칩니다. 예: `--next "li.next a"`
- 새 쪽으로 넘어갈 때마다 스크립트가 robots.txt를 다시 확인하고 `--delay`초(기본 2, 1 미만은 거부) 기다립니다.
- 다음 쪽 링크가 없으면 그 쪽에서 멈추고 `[안내]`를 출력합니다.

## 스크립트 메시지

| 메시지 | 뜻 | 할 일 |
| :--- | :--- | :--- |
| `[확인] robots.txt 허용` | 수집해도 되는 경로 | 계속합니다 |
| `[중단] robots.txt가 … 금지` | 사이트가 수집을 막음 | 멈추고 보고합니다 |
| `[중단] robots.txt 확인 못 함` | 네트워크·서버 오류 | 멈추고 보고합니다. 허용으로 간주하지 않습니다 |
| `[중단] playwright가 없습니다` / `chromium을 실행하지 못했습니다` | 도구 미설치 | 위 설치 명령을 안내하고 멈춥니다 |
| `[중단] … 나타나지 않았습니다` | `--item` 셀렉터가 틀렸거나 로딩이 느림 | 셀렉터를 다시 찾고, 맞다면 `--wait-ms`를 늘립니다 |
| `[중단] --item과 --field가 필요합니다` 등 인자 오류 | 명령 형식이 틀림 | 메시지대로 인자를 고칩니다 |
| `[쪽 N] URL M건` | 쪽별 진행 | — |
| `[안내] 다음 쪽 링크가 없어 N쪽에서 멈췄습니다` | 마지막 쪽에 도달했거나 `--next`가 틀림 | 쪽 수가 예상보다 적으면 `--next` 셀렉터를 확인합니다 |
| `[통과] N쪽 M건 추출, 빈 필드 K개` | 추출 완료 | K가 1 이상이면 빈 항목의 DOM을 봅니다. 셀렉터 문제면 고치고, 원본에 값이 없으면 보고합니다 |
