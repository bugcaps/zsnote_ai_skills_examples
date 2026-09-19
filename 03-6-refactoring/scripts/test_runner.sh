#!/bin/bash
# 리팩토링 전후에 기존 동작이 유지되는지 확인합니다.
# 에이전트가 로그를 해석하지 않아도 되도록 마지막 줄과 종료 코드로 결과를 알립니다.
#   종료 0 = 전부 통과, 1 = 실패 있음, 2 = 테스트를 실행할 수 없음
# 다른 테스트 도구를 쓰는 프로젝트는 TEST_CMD만 바꾸세요. 예: TEST_CMD="npx jest" bash test_runner.sh

TEST_CMD="${TEST_CMD:-pytest tests/ -q}"

if ! command -v "${TEST_CMD%% *}" >/dev/null 2>&1; then
  echo "RESULT: UNAVAILABLE (${TEST_CMD%% *} 명령을 찾을 수 없습니다)"
  exit 2
fi

$TEST_CMD 2>&1 | tail -n 30   # 실패 로그가 길어도 마지막 30줄만 전달
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
  echo "RESULT: PASS"
  exit 0
fi
echo "RESULT: FAIL (exit $status)"
exit 1
