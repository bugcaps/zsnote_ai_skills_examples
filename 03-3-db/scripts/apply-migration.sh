#!/bin/bash
# 사람이 직접 실행하는 마이그레이션 적용 래퍼. 에이전트는 이 스크립트를 실행하지 않습니다.
# 사용법: bash apply-migration.sh <마이그레이션 파일> -- <적용 명령...>
#   예:  bash apply-migration.sh prisma/migrations/20260302_add_avatar/migration.sql -- npx prisma migrate deploy
set -euo pipefail

file="${1:-}"
if [ -z "$file" ] || [ "${2:-}" != "--" ] || [ $# -lt 3 ]; then
  echo "사용법: bash apply-migration.sh <마이그레이션 파일> -- <적용 명령...>"
  exit 2
fi
[ -f "$file" ] || { echo "파일을 찾을 수 없습니다: $file"; exit 2; }
shift 2

echo "===== 적용할 마이그레이션: $file ====="
cat "$file"
echo "======================================"

if grep -qiE '\b(DROP|TRUNCATE|DELETE\s+FROM|ALTER\s+TABLE\s+.*\bDROP)\b' "$file"; then
  echo "경고: 파괴적 구문이 포함되어 있습니다. 백업 여부를 확인하세요."
fi

# 파이프나 에이전트 셸처럼 터미널이 아닌 곳에서는 실행을 거부합니다.
if [ ! -t 0 ]; then
  echo "대화형 터미널에서만 실행할 수 있습니다."
  exit 1
fi

read -r -p "위 내용을 검토했고 '$*' 를 실행합니다. 계속하려면 yes 입력: " confirm
if [ "$confirm" = "yes" ]; then
  "$@"
else
  echo "취소했습니다."
fi
