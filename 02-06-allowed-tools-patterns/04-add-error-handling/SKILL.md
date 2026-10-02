---
name: add-error-handling
description: await, fetch 등 비동기 작업의 에러 처리 누락 여부를 확인하고 try-catch를 추가합니다. "에러 처리 빠진 곳 있나?", "API 호출 안전성", "Promise 에러 처리" 같은 요청에서 트리거됩니다.
allowed-tools:
  - Edit        # try-catch 추가
---

# add-error-handling (에러 처리 추가)

## 작업 순서

1. **비동기 작업 검색**: Grep으로 `await|\.then\(|fetch` 검색
2. **에러 처리 확인**: 각 await 앞에 try가 있는지, .then 뒤에 .catch가 있는지 Read로 확인
3. **누락 지점 파악**: try-catch나 .catch() 없는 항목 표시
4. **처리 추가**: Edit으로 try-catch 또는 .catch() 추가

## 핵심 규약

- **에러를 버리지 말 것**: `catch() {}` 금지, 최소한 로그 남기기
- **에러 전파 vs 기본값**: throw할지 기본값을 반환할지 명확히
- **async/await 선호**: `.then().catch()` 보다 try-catch가 가독성 좋음

## 체크리스트

- [ ] 모든 await이 try 블록 안에 있음
- [ ] 모든 .catch()에 로깅 또는 처리가 있음
- [ ] 에러 메시지가 최종 사용자용과 개발자용으로 구분됨
- [ ] 외부 API 호출은 타임아웃 처리 포함
