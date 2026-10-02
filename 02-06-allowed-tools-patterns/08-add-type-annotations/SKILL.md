---
name: add-type-annotations
description: JavaScript 코드에 TypeScript 타입 주석을 추가합니다. "함수에 타입 추가", "JS → TS 마이그레이션", "타입 안정성 확보" 같은 요청에서 트리거됩니다.
allowed-tools:
  - Edit        # 타입 주석 추가
---

# add-type-annotations (타입 추가)

## 작업 순서

1. **함수 분석**: Read로 함수의 매개변수와 반환값 파악
2. **타입 검색**: Grep으로 타입 주석이 없는 함수 검색
3. **타입 결정**: 각 매개변수와 반환값의 타입 파악
4. **타입 추가**: Edit으로 함수 시그니처에 타입 추가

## 핵심 규약

- **any 타입 금지**: `any` 사용 금지, 구체적 타입 사용
- **Union/Intersection 구분**: `string | number` vs `{ name: string } & { age: number }`
- **Nullable 명확히**: `string | null` vs `string | undefined` 구분

## 체크리스트

- [ ] 모든 함수 매개변수에 타입 있음
- [ ] 모든 함수 반환값에 타입 있음
- [ ] `any` 타입이 사용되지 않음
- [ ] TypeScript 컴파일 에러 0개 (`npm run type-check`)
