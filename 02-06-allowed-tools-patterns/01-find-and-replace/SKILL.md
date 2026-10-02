---
name: find-and-replace
description: 코드 내 특정 문자열을 일괄 변경합니다. "함수명 A를 B로 바꿔줄래?", "변수명 변경", "console.log를 logger로" 같은 요청에서 트리거됩니다.
allowed-tools:
  - Edit        # 여러 파일의 일괄 변경 (git diff로 되돌릴 수 있으므로 매번 묻지 않음)
---

# find-and-replace (일괄 찾기 및 바꾸기)

## 작업 순서

1. **검색 범위 확인**: Grep으로 바꿀 문자열이 몇 개 있는지 파악
2. **대상 선정**: 정말로 바뀌어야 하는지 확인 (오탈자 X, 주석 X)
3. **일괄 변경**: Edit의 replace_all 사용
4. **검증**: git diff로 변경사항 확인

## 핵심 규약

- **replace_all은 신중하게**: 변수명 a → b 같은 짧은 문자열은 오류 가능성이 높음
- **정규식 활용**: 함수명 변경 시 `getUserData(` → `fetchUserData(` 처럼 컨텍스트 포함
- **git diff 필수**: 예상과 다른 변경이 없는지 반드시 확인

## 체크리스트

- [ ] Grep으로 변경 대상 개수 확인
- [ ] replace_all 대신 구체적인 문자열/정규식 사용
- [ ] 변경 후 git diff로 20개 이상 변경되면 샘플 확인
- [ ] 테스트 통과 (또는 npm run lint 통과)
