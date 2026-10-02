---
name: code-quality-essentials
description: 코드 품질 개선을 위한 8가지 필수 스킬 패턴을 제공합니다. "변수명 통일", "타입 추가", "미사용 코드 정리", "에러 처리" 같은 일상적인 요청에서 사용됩니다.
allowed-tools:
  - Edit             # 코드 수정 (git으로 되돌릴 수 있으므로 매번 묻지 않음)
  - Bash(npm test *) # 수정 뒤 테스트 실행
---

# 8가지 코드 품질 개선 스킬 패턴

이 섹션은 모든 프로젝트에 적용할 수 있는 **기본 8개의 재사용 가능한 스킬**을 정의합니다.

## 포함된 스킬

1. **find-and-replace** — 일괄 찾기 및 바꾸기
2. **add-missing-imports** — 누락된 import 추가
3. **unused-variable-cleanup** — 미사용 변수 제거
4. **add-error-handling** — try-catch 추가
5. **update-comments** — 주석 동기화
6. **extract-magic-numbers** — 상수 추출
7. **normalize-code-style** — 스타일 통일
8. **add-type-annotations** — TypeScript 타입 추가

## 각 스킬의 구조

각 하위 스킬 디렉토리는 다음을 포함합니다:

- `SKILL.md` — 메타데이터 및 체크리스트
- `README.md` — 사용 예시 및 함정

## 적용 순서 (초기 프로젝트 세팅)

```
1️⃣ normalize-code-style    (스타일 통일)
2️⃣ find-and-replace        (이름 정리)
3️⃣ add-missing-imports     (import 완성)
4️⃣ unused-variable-cleanup (미사용 제거)
5️⃣ extract-magic-numbers   (상수화)
6️⃣ add-error-handling      (안정성)
7️⃣ update-comments         (문서화)
8️⃣ add-type-annotations    (타입 안정성)
```

## 각 스킬 링크

| 스킬 | 설명 | 복잡도 |
| --- | --- | --- |
| [01-find-and-replace](./01-find-and-replace/) | 일괄 문자열 변경 | ⭐ |
| [02-add-missing-imports](./02-add-missing-imports/) | 누락된 import 추가 | ⭐ |
| [03-unused-variable-cleanup](./03-unused-variable-cleanup/) | 미사용 코드 제거 | ⭐⭐ |
| [04-add-error-handling](./04-add-error-handling/) | 에러 처리 추가 | ⭐⭐ |
| [05-update-comments](./05-update-comments/) | 주석 동기화 | ⭐ |
| [06-extract-magic-numbers](./06-extract-magic-numbers/) | 상수 추출 | ⭐ |
| [07-normalize-code-style](./07-normalize-code-style/) | 스타일 통일 | ⭐ |
| [08-add-type-annotations](./08-add-type-annotations/) | 타입 추가 | ⭐⭐⭐ |

## 핵심 원칙

- ✅ **사전 승인은 좁게**: `allowed-tools`에는 확인 없이 실행해도 되돌릴 수 있는 도구만 적음
- ✅ **명시적 의도**: 각 도구 옆에 역할 명시
- ✅ **재사용 가능**: 모든 프로젝트/언어에서 적용 가능
- ✅ **체크리스트**: 각 스킬의 완료 기준 명확화
