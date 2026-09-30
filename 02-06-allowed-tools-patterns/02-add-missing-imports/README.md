# add-missing-imports 사용 예시

## 요청

"index.js에 import 빠진 게 있나?"

## 에이전트의 동작

```
1️⃣ Read: index.js 읽기
   → formatDate() 함수 사용 중 발견

2️⃣ Grep: "import.*formatDate" 검색
   → 결과: 없음 ❌

3️⃣ Edit: import 추가
   추가: import { formatDate } from "./utils"
```

## 산출물

```
✅ formatDate import 추가됨
✅ 경로 확인됨 (./utils)
✅ IDE 린터 에러 해결
```

## 함정

❌ 잘못된 경로로 import 추가하면 런타임 에러
✅ 반드시 경로 확인: `../utils` vs `./utils` vs `@/utils`
