# 컴포넌트 규약 상세

SKILL.md 의 핵심 규약만으로 판단이 서지 않을 때 읽습니다.

## props 설계

boolean props가 늘어나면 조합 폭발이 생깁니다.

```tsx
// 피할 것: 2^3 = 8가지 조합, 그중 다수가 무의미
interface ButtonProps { isPrimary?: boolean; isDanger?: boolean; isGhost?: boolean }

// 권장: 유효한 값만 표현됨
interface ButtonProps { variant: 'primary' | 'danger' | 'ghost' }
```

기본값은 구조 분해에서 지정하고, `defaultProps`는 쓰지 않습니다.

## 파일 배치

```
src/components/Button/
  Button.tsx        컴포넌트
  Button.test.tsx   테스트
  index.ts          re-export
```

단일 파일로 충분한 컴포넌트는 디렉터리를 만들지 않고 `src/components/Button.tsx` 로 둡니다.
파일이 2개를 넘길 때 디렉터리로 승격합니다.

## 접근성

- 클릭 가능한 요소는 `<div onClick>` 이 아니라 `<button>` 을 씁니다.
- 아이콘만 있는 버튼은 `aria-label` 이 필수입니다.
- 포커스 링을 `outline: none` 으로 제거하지 않습니다. 대체 스타일 없이 제거하면 키보드 사용자가 위치를 잃습니다.

## 상태

서버 데이터는 컴포넌트 안에서 `useEffect` + `fetch` 로 가져오지 않습니다.
데이터 페칭은 상위 레이어에 두고, 컴포넌트는 props로 받은 값만 그립니다.
