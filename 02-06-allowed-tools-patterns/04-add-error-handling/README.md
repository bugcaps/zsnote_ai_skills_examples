# add-error-handling 사용 예시

## 요청

"에러 처리 빠진 곳 있나?"

## 에이전트의 동작

```
1️⃣ Grep: "await " 검색
   → 23개 발견

2️⃣ Read: try-catch 감싸여 있는지 확인
   → 5개 누락 발견:
      const user = await db.users.findById(id);

3️⃣ Edit: try-catch 5개 추가
   try {
     const user = await db.users.findById(id);
   } catch (error) {
     logger.error("User fetch failed", error);
   }
```

## 산출물

```
✅ 5개 await에 try-catch 추가됨
✅ 에러 로깅 포함됨
✅ 테스트 통과
```

## 함정

❌ 빈 catch 블록 (예: catch() {})
✅ 항상 에러 로깅 또는 처리 로직 포함
