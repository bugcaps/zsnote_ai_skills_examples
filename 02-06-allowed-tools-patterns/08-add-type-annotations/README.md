# add-type-annotations 사용 예시

## 요청

"함수들에 타입 추가해줄래?"

## 에이전트의 동작

```
1️⃣ Read: 함수 정의 확인
   function add(a, b) {  // ← 타입 없음
     return a + b;
   }

2️⃣ Grep: 타입 없는 함수 검색
   → 12개 발견

3️⃣ Edit: 타입 추가
   function add(a: number, b: number): number {
     return a + b;
   }
```

## 산출물

```
✅ 12개 함수 타입 추가됨
✅ TypeScript 컴파일 성공
✅ 타입 안정성 확보
```

## 함정

❌ any 타입 사용 (any는 타입 안정성 무시)
✅ 구체적 타입 사용: string, number, User, etc.
