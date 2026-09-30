# extract-magic-numbers 사용 예시

## 요청

"하드코딩된 숫자들 상수로 만들어줄래?"

## 에이전트의 동작

```
1️⃣ Grep: 숫자 패턴 검색
   → "3600000", "86400" 등 발견

2️⃣ Read: 각 숫자의 의미 파악
   → 3600000ms = 1시간
   → 86400 = 1일의 초

3️⃣ Edit: 상수 정의 및 코드 수정
   const ONE_HOUR_MS = 3600000;
   const ONE_DAY_SECONDS = 86400;
   
   setTimeout(() => { ... }, ONE_HOUR_MS);
```

## 산출물

```
✅ 4개 매직 넘버 상수화됨
✅ 코드 가독성 개선
✅ 테스트 통과
```

## 함정

❌ 상수명이 모호함 (const NUM = 3600000)
✅ 명확한 상수명: ONE_HOUR_MS, MAX_RETRIES, etc.
