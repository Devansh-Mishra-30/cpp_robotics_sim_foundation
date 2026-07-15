#!/usr/bin/env bash

# Copyright 2026 Devansh Mishra
#
# Licensed under the MIT License. See LICENSE in the project root for details.

set -euo pipefail

SCRIPT_DIR="$(
  cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &&
    pwd
)"
REPO_ROOT="$(
  cd -- "${SCRIPT_DIR}/.." &&
    pwd
)"

ROS_WS="${REPO_ROOT}/ros2_ws"

remove_directory_if_present() {
  local target_path="$1"

  if [[ -d "${target_path}" ]]; then
    printf 'Removing directory: %s\n' "${target_path}"
    rm -rf -- "${target_path}"
  else
    printf 'Already absent:     %s\n' "${target_path}"
  fi
}

remove_file_if_present() {
  local target_path="$1"

  if [[ -f "${target_path}" ]]; then
    printf 'Removing file:      %s\n' "${target_path}"
    rm -f -- "${target_path}"
  fi
}

remove_python_caches() {
  printf '\nRemoving Python cache directories...\n'

  find "${REPO_ROOT}" \
    -path "${REPO_ROOT}/.git" -prune -o \
    -type d \
    \( \
      -name __pycache__ -o \
      -name .pytest_cache -o \
      -name .ruff_cache -o \
      -name .mypy_cache \
    \) \
    -print0 |
    while IFS= read -r -d '' cache_directory; do
      printf 'Removing directory: %s\n' "${cache_directory}"
      rm -rf -- "${cache_directory}"
    done

  printf '\nRemoving compiled Python files...\n'

  find "${REPO_ROOT}" \
    -path "${REPO_ROOT}/.git" -prune -o \
    -type f \
    \( -name '*.pyc' -o -name '*.pyo' \) \
    -print0 |
    while IFS= read -r -d '' cache_file; do
      printf 'Removing file:      %s\n' "${cache_file}"
      rm -f -- "${cache_file}"
    done
}

main() {
  printf '\n=== Clean generated project state ===\n'
  printf 'Repository: %s\n\n' "${REPO_ROOT}"

  if [[ ! -d "${ROS_WS}" ]]; then
    printf 'ERROR: ROS workspace not found: %s\n' \
      "${ROS_WS}" >&2
    return 1
  fi

  printf 'Removing workspace-generated artifacts...\n'
  remove_directory_if_present "${ROS_WS}/build"
  remove_directory_if_present "${ROS_WS}/install"
  remove_directory_if_present "${ROS_WS}/log"

  printf '\nRemoving repository-root generated artifacts...\n'
  remove_directory_if_present "${REPO_ROOT}/build"
  remove_directory_if_present "${REPO_ROOT}/install"
  remove_directory_if_present "${REPO_ROOT}/log"

  remove_python_caches

  remove_file_if_present "${REPO_ROOT}/.coverage"
  remove_directory_if_present "${REPO_ROOT}/htmlcov"

  printf '\nPreserved user and project assets:\n'
  printf '  %s\n' "${REPO_ROOT}/data"
  printf '  %s\n' "${ROS_WS}/src"
  printf '  %s\n' "${HOME}/.ros/cpp_robotics_sim/maps"

  printf '\nClean completed successfully.\n'
}

main "$@"
