#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &&
    pwd
)"
REPO_ROOT="$(
  cd -- "${SCRIPT_DIR}/.." &&
    pwd
)"

cd "${REPO_ROOT}"

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

collect_files() {
  local extension="$1"

  find . \
    \( \
      -path './.git' \
      -o -path './build' \
      -o -path './install' \
      -o -path './log' \
      -o -path './ros2_ws/build' \
      -o -path './ros2_ws/install' \
      -o -path './ros2_ws/log' \
      -o -path '*/__pycache__' \
      -o -path '*/node_modules' \
    \) -prune \
    -o -type f -name "*.${extension}" -print0
}

check_python_syntax() {
  local file_count=0
  local file

  printf '\nChecking Python syntax...\n'

  while IFS= read -r -d '' file; do
    python3 -m py_compile "${file}"
    file_count=$((file_count + 1))
  done < <(collect_files "py")

  if ((file_count == 0)); then
    printf 'ERROR: no Python files were found.\n' >&2
    return 1
  fi

  printf 'PASS: %d Python files passed syntax checks.\n' \
    "${file_count}"
}

check_javascript_syntax() {
  local file_count=0
  local file

  printf '\nChecking JavaScript syntax...\n'

  while IFS= read -r -d '' file; do
    node --check "${file}"
    file_count=$((file_count + 1))
  done < <(collect_files "js")

  if ((file_count == 0)); then
    printf 'ERROR: no JavaScript files were found.\n' >&2
    return 1
  fi

  printf 'PASS: %d JavaScript files passed syntax checks.\n' \
    "${file_count}"
}

check_bash_syntax() {
  local file_count=0
  local file

  printf '\nChecking Bash syntax...\n'

  while IFS= read -r -d '' file; do
    bash -n "${file}"
    file_count=$((file_count + 1))
  done < <(collect_files "sh")

  if ((file_count == 0)); then
    printf 'ERROR: no Bash files were found.\n' >&2
    return 1
  fi

  printf 'PASS: %d Bash files passed syntax checks.\n' \
    "${file_count}"
}

main() {
  require_command python3
  require_command node
  require_command bash
  require_command find

  check_python_syntax
  check_javascript_syntax
  check_bash_syntax

  printf '\nAll syntax checks passed.\n'
}

main "$@"
