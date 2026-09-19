# 프로젝트 문서화 규약

1. **JSDoc/Docstring 표준 준수**:
   - TypeScript/JavaScript: JSDoc (`/** ... */`)
   - Python: Sphinx 또는 Google 스타일 Docstring (`""" ... """`)
2. **필수 포함 항목 (함수/메서드)**:
   - 한 줄 요약
   - (필요시) 상세 설명
   - `@param` / `Args:`
   - `@returns` / `Returns:`
   - `@throws` / `Raises:` (예외 발생 시)
3. **What vs Why**:
   - 나쁜 예: `// 데이터를 필터링한다`
   - 좋은 예: `// 활성 사용자만 대상으로 프로모션 알림을 보내기 위해 필터링`
