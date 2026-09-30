# normalize-code-style 사용 예시

## 요청

"따옴표 스타일 통일해줄래? (큰따옴표로)"

## 에이전트의 동작

```
1️⃣ Grep: 작은따옴표 검색
   → 47개 발견

2️⃣ Read: 따옴표 패턴 확인

3️⃣ Bash: prettier --write (자동 포맷팅)
   또는 Edit으로 수동 변경
```

## 산출물

```
✅ 47개 따옴표 통일됨
✅ prettier로 자동 포맷팅됨
✅ 린팅 에러 0개
```

## 함정

❌ 팀의 .prettierrc를 무시하고 독단적으로 포맷팅
✅ 반드시 .prettierrc, .eslintrc 설정 준수
