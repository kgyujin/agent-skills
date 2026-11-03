#!/usr/bin/env bash
# 작성자: Git 이력 참조
# 작성목적: sources.tsv에 적힌 개별 스킬 저장소의 최신 내용을 skills/<이름>/ 으로 복사한다.
# 작성일: 2026-11-03
# 주의사항:
#   - 원본은 개별 저장소다. skills/ 아래를 직접 고치면 다음 동기화 때 덮어써진다.
#   - .git, .github, install.sh(개별 저장소용 링크 설치기), tests, evals 는 복사하지 않는다.
#   - sources.tsv 에서 빠진 스킬 폴더는 지운다.
# 사용법: scripts/sync.sh
# 변경사항 내역:
# - 2026-11-03 | 최초 작성 | 개별 저장소 7개 동기화
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

mkdir -p "$ROOT/skills"
keep=()
while IFS=$'\t' read -r name repo path; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  keep+=("$name")
  git clone -q --depth 1 "https://github.com/${repo}.git" "$WORK/$name"
  src="$WORK/$name/$path"
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "중단: ${repo} 의 ${path}/SKILL.md 가 없습니다." >&2
    exit 1
  fi
  mkdir -p "$ROOT/skills/$name"
  rsync -a --delete \
    --exclude .git --exclude .github --exclude install.sh --exclude tests --exclude evals --exclude .DS_Store \
    "$src/" "$ROOT/skills/$name/"
  echo "동기화: ${name} <- ${repo} ($(git -C "$WORK/$name" rev-parse --short HEAD))"
done < "$ROOT/sources.tsv"

for dir in "$ROOT"/skills/*/; do
  name="$(basename "$dir")"
  if [[ ! " ${keep[*]} " == *" ${name} "* ]]; then
    rm -rf "$dir"
    echo "제거: ${name} (sources.tsv 에 없음)"
  fi
done
