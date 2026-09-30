# clarification-hitl 사용 예시

## 요청

"사용자 이름 필드에 가명 지원해줄래?"

## 에이전트의 동작

```
1️⃣ Read: 현재 사용자 이름 필드 분석
   → 현재: fullName (단일 필드)

2️⃣ "가명 지원"의 의미 파악
   → 여러 해석 가능:
   - 해석 A: 닉네임을 추가 필드로 (fullName + nickname)
   - 해석 B: fullName 대신 nickname으로 표시
   - 해석 C: fullName은 비공개, nickname은 공개

3️⃣ AskUserQuestion: 명확화
   "가명 지원이 의미하는 바가:
   A) fullName + nickname 필드 추가?
   B) nickname만 표시 가능?
   C) fullName 감춤 + nickname 표시?
   
   [A] [B] [C]"
```

## 산출물

```
✅ 3가지 해석 분석 완료
✅ 각 해석의 코드 예시 제시
✅ 사용자 선택: B) nickname만 표시
✅ 선택된 해석으로 구현
```

## 핵심

- 불명확하면 멈추고 질문
- 추측하지 않기
