# 테스트 보고서 — commit-message 스킬 (AI 초안 v0 vs 최종본 v1)

- 환경: Windows 11, Claude Code 2.1.287, 비대화형(`claude -p`), 2026-10-03
- 저장소: 임시 git 저장소. `fix/123-login-timeout` 브랜치에 로그인 타임아웃·재시도 변경을 스테이징
- 함께 설치한 스킬: `github-pr-writer`(03-07) — 트리거 경계 확인용
- v0 = `drafts/ai-draft-SKILL.md`, v1 = `SKILL.md`

## 1. 초안을 만든 대화 (5턴)

| 턴 | 사용자 | 결과 |
| :--- | :--- | :--- |
| 1 | 스테이징된 변경으로 커밋 메시지 써 줘 | 영어 첫 줄 + 영어 본문 + 불릿 구현 설명, `(#123)` 추정 |
| 2 | Conventional Commits, 첫 줄 50자 이내 | `fix(login)!: …` + `BREAKING CHANGE` footer (사용자가 요청하지 않은 `!` 추가) |
| 3 | 본문은 한국어로 무엇·왜만, 이슈 번호는 브랜치에 있을 때만 `Refs #번호` | 반영. "메모리에 저장해서 다음 세션에서도 따르겠다" |
| 4 | 커밋은 직접 하지 말고 메시지만 | 반영. 메모리에 추가 |
| 5 | 팀원도 쓸 수 있게 `.claude/skills/`에 스킬로 만들어 줘 | `.claude/` 쓰기가 권한 거부되어 초안을 화면에 출력 → `drafts/ai-draft-SKILL.md` |

## 2. 트리거 테스트 (새 세션, 발화마다 1회)

| 발화 | v0 | v1 |
| :--- | :--- | :--- |
| 방금 add 한 변경 커밋 메시지 하나 뽑아 줘 | commit-message | commit-message |
| 이거 커밋하려는데 메시지 좀 정리해 줘 | commit-message | commit-message |
| commit message 추천해 줘 | commit-message | commit-message |
| 이 브랜치 PR 본문 써 줘 (트리거되면 안 됨) | github-pr-writer | github-pr-writer |

판정: 두 버전 모두 3/3, 비트리거 통과. 이 실험에서는 description을 보강한 효과가 트리거 결과에 나타나지 않았습니다.

## 3. 실행 테스트

| 조건 | v0 | v1 |
| :--- | :--- | :--- |
| 로그인 변경, 3회 | 3회 모두 첫 줄 `fix(login)!: enforce client timeout with retries` (초안 예시와 글자까지 같음), `!` 적용 | 3회 모두 다른 첫 줄, `!` 없음 |
| 무관한 변경(`feature/csv-export`, CSV 내보내기) | `feat(export): add CSV export for user list`, `Refs` 없음, 본문에 근거 없는 "왜" | (수정 전) 근거 없는 "왜" |
| 위 변경, v1에 "왜 근거 규칙" 추가 후 | — | 본문 둘째 줄 `[TODO: 변경 이유 확인]`, 이유를 물음 |
| 로그인 변경, 규칙 추가 후 | — | "왜"를 쓰고 근거(브랜치 이름·diff)를 밝힘, `Refs #123` |
| 스테이징 없음 | — | 멈추고 `git add`를 안내 |

공통: 어느 실행에서도 `git commit`을 실행하지 않았습니다.

## 4. 결론

- 테스트로 확인된 v0의 결함: 사용자가 정하지 않은 `!` 규칙이 매번 적용됨.
- 무관한 변경에서 초안 예시의 값(`login`, `Refs #123`)이 새는 현상은 이번 실험에서 나타나지 않았음.
- v0와 v1(수정 전) 모두 diff에 없는 변경 이유를 지어냄 → v1에 근거 규칙과 체크 항목을 추가해 해결.
