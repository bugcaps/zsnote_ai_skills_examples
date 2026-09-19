# 디자인 토큰 기준 (Design Tokens)

본 프로젝트는 에이전트가 임의의 디자인 값을 생성하는 것을 방지하기 위해, 아래의 사전 정의된 토큰 집합 내에서만 컬러와 타이포그래피를 선택하도록 제한합니다.

## 1. 허용된 색상 팔레트 (Tailwind CSS 기반)

기본적으로 Tailwind CSS v3의 기본 색상표를 사용합니다. 새로운 HEX 값을 만들어내지 마십시오.

- **Slate, Gray, Zinc, Neutral, Stone:** 무채색 및 배경/텍스트용
- **Red, Orange, Amber, Yellow, Lime, Green, Emerald, Teal, Cyan, Sky, Blue, Indigo, Violet, Purple, Fuchsia, Pink, Rose:** 유채색 포인트용

각 색상은 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950의 명도 단계를 가집니다. (예: `blue-600` = `#2563eb`)

## 2. 타이포그래피 스케일

- **폰트 패밀리:** 
  - Sans-serif: `Inter`, `Pretendard`
  - Serif: `Merriweather`, `Noto Serif KR`
  - Mono: `Fira Code`, `D2Coding`
- **폰트 크기 (px/rem):**
  - `xs`: 12px (0.75rem)
  - `sm`: 14px (0.875rem)
  - `base`: 16px (1rem)
  - `lg`: 18px (1.125rem)
  - `xl`: 20px (1.25rem)
  - `2xl`: 24px (1.5rem)
  - `3xl`: 30px (1.875rem)
  - `4xl`: 36px (2.25rem)
- **폰트 굵기:** Regular(400), Medium(500), SemiBold(600), Bold(700)

## 3. 접근성 기준

텍스트 색상과 배경 색상을 매핑할 때, WCAG 2.1 AA 기준을 준수해야 합니다.
- 일반 텍스트: 최소 4.5:1
- 큰 텍스트(18pt 이상 또는 14pt 굵은 글씨): 최소 3:1
