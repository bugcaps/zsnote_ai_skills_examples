# find-and-replace 사용 예시

## 요청

"모든 파일에서 console.log를 logger.info로 바꿔줄래?"

## 에이전트의 동작

```
1️⃣ Grep: "console.log" 검색
   → 37개의 파일에서 발견

2️⃣ Edit: replace_all로 변경
   OLD: console.log("message")
   NEW: logger.info("message")

3️⃣ Bash: git diff로 확인
   → 37개 모두 변경됨 ✅
```

## 산출물

```
✅ console.log 37개 → logger.info로 변경됨
✅ 테스트 통과
✅ git diff로 변경사항 검증 완료
```

## 함정

❌ "user"라는 짧은 단어로 replace_all 하면 변수명, 주석 등 예상치 못한 곳까지 변경될 수 있음
✅ 정규식이나 더 구체적인 문자열 사용: `getUserData(` → `fetchUserData(`
