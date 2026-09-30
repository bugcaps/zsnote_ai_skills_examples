---
name: add-missing-imports
description: 사용된 함수/클래스의 import 문 누락 여부를 확인하고 자동으로 추가합니다. "import 빠진 거 있나?", "이 함수를 import 해야 하나?" 같은 요청에서 트리거됩니다.
allowed-tools:
  - Read        # 파일 읽기 (어떤 함수 사용하는지 확인)
  - Grep        # import 문 검색 (이미 있는 import 확인)
  - Edit        # import 문 추가
---

# add-missing-imports (누락된 import 추가)

## 작업 순서

1. **파일 분석**: Read로 파일 내용 확인, 사용 중인 함수/클래스 파악
2. **import 확인**: Grep으로 각 함수의 import 문이 있는지 검색
3. **누락 항목 추가**: Edit로 필요한 import 문 추가
4. **순서 정렬**: import 문의 순서를 팀 규칙에 맞춰 정렬

## 핵심 규약

- **불필요한 import는 추가 금지**: 사용 중인 것만 (Dead import 주의)
- **경로 확인**: 상대 경로가 맞는지 반드시 확인 (`../utils` vs `./utils`)
- **타입 import 구분** (TypeScript): `import type` vs `import` 구분

## 체크리스트

- [ ] 사용 중인 모든 함수/클래스 파악됨
- [ ] 기존 import와 중복되지 않음
- [ ] 경로가 정확함
- [ ] IDE 린터가 import 에러 표시하지 않음
