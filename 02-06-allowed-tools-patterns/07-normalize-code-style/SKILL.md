---
name: normalize-code-style
description: 코드 포맷팅 및 스타일 일관성을 확보합니다. "따옴표 통일", "들여쓰기 정렬", "Prettier 적용", "세미콜론 규칙" 같은 요청에서 트리거됩니다.
allowed-tools:
  - Edit                      # 포매터가 못 고친 부분 수동 조정
  - Bash(npx prettier --write *)  # 포매터 실행
  - Bash(npx eslint --fix *)      # 린터 자동 수정
---

# normalize-code-style (스타일 통일)

## 작업 순서

1. **스타일 규칙 확인**: 팀의 .eslintrc, .prettierrc, tsconfig.json 등 확인
2. **불일치 패턴 검색**: Grep으로 따옴표, 들여쓰기, 세미콜론 등 검색
3. **자동 포맷팅**: 가능하면 `prettier --write` 또는 `eslint --fix` 사용
4. **수동 조정**: 자동화로 불가능한 부분만 Edit으로 수정

## 핵심 규약

- **린터 설정 우선**: 팀의 `.eslintrc`, `.prettierrc`를 따를 것
- **자동화 도구 활용**: 수동 수정보다 prettier/eslint 선호
- **한 번에 하나씩**: 따옴표 통일과 들여쓰기는 별도 커밋

## 체크리스트

- [ ] 팀의 코드 스타일 가이드 확인됨
- [ ] prettier 또는 eslint 설정을 사용함
- [ ] 자동화 불가능한 부분만 수동 수정됨
- [ ] 변경 후 린팅 에러 0개
