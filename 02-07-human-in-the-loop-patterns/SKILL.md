---
name: hitl-design-patterns
description: 자동화와 인간 검증을 조합하는 5가지 휴먼-인-더-루프 패턴을 제공합니다. "이 작업은 자동으로 할까, 확인받을까?", "여러 선택지가 있는데" 같은 설계 판단에서 사용됩니다.
allowed-tools:
  - Read        # 상황 분석
  - Artifact    # 선택지/데이터 시각화
  - AskUserQuestion  # 사용자 개입
  - Bash        # 사전 검증 (dry-run)
---

# 5가지 휴먼-인-더-루프(HITL) 패턴

휴먼-인-더-루프는 자동화와 인간의 최종 판단을 결합하는 설계 패턴입니다.

## 포함된 패턴

1. **multi-option-decision** — 의사결정형
   - 여러 선택지를 분석한 후 사용자가 선택
   - 예: 설계안 비교, 기술 스택 선택

2. **safety-gate-hitl** — 안전장치형
   - 위험한 작업 전 최종 승인
   - 예: 프로덕션 배포, DB 마이그레이션

3. **clarification-hitl** — 불확실성 해소형
   - 요구사항이 불명확할 때 질문
   - 예: "이렇게 이해하는 게 맞나?"

4. **tradeoff-verification-hitl** — 트레이드오프 검증형
   - 성능 vs 복잡도 같은 선택사항 제시
   - 예: 최적화 여부, 아키텍처 선택

5. **error-analysis-hitl** — 오류 분석형
   - 자동 해결 불가능한 오류 시 분석 제시
   - 예: 테스트 실패 원인 분석, 빌드 에러

## 팀 HITL 정책 템플릿

각 조직은 다음을 정의해야 합니다:
- **HITL 필수 영역**: 배포, 데이터 변경, 보안
- **HITL 권장 영역**: 아키텍처, 대규모 변경
- **자동화 전용**: 포맷팅, import 정렬

## 참고 자료

- 상세 가이드: `pages/02-07-human-in-the-loop.md`
- 체크리스트: `references/hitl-checklist.md`
- 팀 정책 템플릿: `references/team-hitl-policy.md`
