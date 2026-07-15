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

RUN_SCRIPT="${REPO_ROOT}/scripts/run.sh"

DASHBOARD_PORT="${DASHBOARD_PORT:-8080}"
ROSBRIDGE_PORT="${ROSBRIDGE_PORT:-9090}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-30}"
SHUTDOWN_TIMEOUT_SECONDS="${SHUTDOWN_TIMEOUT_SECONDS:-15}"

RUN_PID=""
RUN_LOG=""
SHUTDOWN_REQUESTED=false

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

process_group_exists() {
  local process_group_id="$1"

  kill -0 -- "-${process_group_id}" 2>/dev/null
}

force_cleanup() {
  if [[ -z "${RUN_PID}" ]]; then
    return 0
  fi

  if ! process_group_exists "${RUN_PID}"; then
    wait "${RUN_PID}" 2>/dev/null || true
    return 0
  fi

  kill -TERM -- "-${RUN_PID}" 2>/dev/null || true

  for _ in {1..20}; do
    if ! process_group_exists "${RUN_PID}"; then
      break
    fi

    sleep 0.25
  done

  if process_group_exists "${RUN_PID}"; then
    kill -KILL -- "-${RUN_PID}" 2>/dev/null || true
  fi

  wait "${RUN_PID}" 2>/dev/null || true
}

cleanup() {
  local exit_code=$?

  if [[ "${SHUTDOWN_REQUESTED}" != "true" ]]; then
    force_cleanup
  fi

  if ((exit_code != 0)) && [[ -f "${RUN_LOG}" ]]; then
    printf '\n===== run.sh log after failure =====\n' >&2
    cat "${RUN_LOG}" >&2
  fi

  if [[ -n "${RUN_LOG}" ]]; then
    rm -f -- "${RUN_LOG}"
  fi

  exit "${exit_code}"
}

wait_for_http() {
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))
  local url="http://127.0.0.1:${DASHBOARD_PORT}/"

  while ((SECONDS < deadline)); do
    if curl \
      --fail \
      --silent \
      --show-error \
      --max-time 2 \
      "${url}" |
      grep -qi '<html'; then
      return 0
    fi

    if ! kill -0 "${RUN_PID}" 2>/dev/null; then
      printf 'ERROR: run.sh exited before HTTP became ready.\n' \
        >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: dashboard did not become ready at %s\n' \
    "${url}" >&2
  return 1
}

wait_for_tcp_port() {
  local host="$1"
  local port="$2"
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if python3 - "${host}" "${port}" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])

try:
    with socket.create_connection((host, port), timeout=1.0):
        pass
except OSError:
    raise SystemExit(1)
PY
    then
      return 0
    fi

    if ! kill -0 "${RUN_PID}" 2>/dev/null; then
      printf 'ERROR: run.sh exited before port %s became ready.\n' \
        "${port}" >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: TCP port %s:%s did not become ready.\n' \
    "${host}" "${port}" >&2
  return 1
}

wait_for_topic() {
  local topic_name="$1"
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    local topic_list

    topic_list="$(
      ros2 topic list 2>/dev/null
    )"

    if grep -Fxq \
      -- "${topic_name}" \
      <<<"${topic_list}"; then
      return 0
    fi

    if ! kill -0 "${RUN_PID}" 2>/dev/null; then
      printf 'ERROR: run.sh exited while waiting for %s\n' \
        "${topic_name}" >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: required topic was not found: %s\n' \
    "${topic_name}" >&2
  return 1
}

wait_for_run_process_exit() {
  local deadline=$((SECONDS + SHUTDOWN_TIMEOUT_SECONDS))
  local process_state=""

  while ((SECONDS < deadline)); do
    if ! kill -0 "${RUN_PID}" 2>/dev/null; then
      return 0
    fi

    process_state="$(
      ps -o stat= -p "${RUN_PID}" 2>/dev/null |
        awk '{print $1}'
    )"

    if [[ "${process_state}" == Z* ]]; then
      return 0
    fi

    sleep 0.25
  done

  return 1
}

wait_for_process_group_exit() {
  local deadline=$((SECONDS + SHUTDOWN_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if ! process_group_exists "${RUN_PID}"; then
      return 0
    fi

    sleep 0.25
  done

  return 1
}

wait_for_port_release() {
  local port="$1"
  local deadline=$((SECONDS + SHUTDOWN_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if ! ss -ltn "sport = :${port}" |
      tail -n +2 |
      grep -q .; then
      return 0
    fi

    sleep 0.25
  done

  printf 'ERROR: TCP port remained occupied after shutdown: %s\n' \
    "${port}" >&2
  return 1
}

find_remaining_project_processes() {
  ps -eo pid=,ppid=,pgid=,cmd= |
    grep -E \
      'web_interface\.launch\.py|simulation_manager_node\.py|mode_manager_node\.py|mapping_manager_node\.py|localization_manager_node\.py|navigation_goal_manager_node\.py|rosbridge_websocket|python3 -m http\.server' |
    grep -vE \
      'grep -E|run_lifecycle_test\.sh' ||
    true
}

main() {
  require_command bash
  require_command curl
  require_command grep
  require_command mktemp
  require_command python3
  require_command ros2
  require_command setsid
  require_command ss
  require_command tail

  if [[ ! -x "${RUN_SCRIPT}" ]]; then
    printf 'ERROR: run script is not executable: %s\n' \
      "${RUN_SCRIPT}" >&2
    return 1
  fi

  RUN_LOG="$(mktemp)"

  trap cleanup EXIT INT TERM

  printf '\n=== Public launcher lifecycle test ===\n'
  printf 'Dashboard port: %s\n' "${DASHBOARD_PORT}"
  printf 'Rosbridge port: %s\n\n' "${ROSBRIDGE_PORT}"

  printf '[1/7] Starting scripts/run.sh...\n'

  OPEN_BROWSER=false \
  DASHBOARD_PORT="${DASHBOARD_PORT}" \
  ROSBRIDGE_PORT="${ROSBRIDGE_PORT}" \
    python3 -c '
import os
import signal
import sys

os.setsid()
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)
os.execv(sys.argv[1], sys.argv[1:])
' "${RUN_SCRIPT}" >"${RUN_LOG}" 2>&1 &

  RUN_PID=$!

  sleep 2

  if ! kill -0 "${RUN_PID}" 2>/dev/null; then
    printf 'ERROR: run.sh exited during startup.\n' >&2
    return 1
  fi

  printf '[2/7] Checking dashboard HTTP server...\n'
  wait_for_http

  printf '[3/7] Checking rosbridge TCP port...\n'
  wait_for_tcp_port \
    "127.0.0.1" \
    "${ROSBRIDGE_PORT}"

  printf '[4/7] Checking required ROS topics...\n'

  local required_topics=(
    "/simulation/status"
    "/simulation/environment_status"
    "/mode/status"
    "/mapping/save_status"
    "/mapping/saved_maps"
    "/localization/status"
    "/localization/selected_map"
    "/navigation/status"
  )

  local topic_name

  for topic_name in "${required_topics[@]}"; do
    printf '  Checking %s\n' "${topic_name}"
    wait_for_topic "${topic_name}"
  done

  printf '[5/7] Sending SIGINT to run.sh process group...\n'
  SHUTDOWN_REQUESTED=true
  kill -INT -- "-${RUN_PID}"

  if ! wait_for_run_process_exit; then
    printf 'ERROR: run.sh did not respond to SIGINT in time.\n' \
      >&2
    force_cleanup
    return 1
  fi

  set +e
  wait "${RUN_PID}"
  local run_status=$?
  set -e

  if ! wait_for_process_group_exit; then
    printf 'ERROR: managed process group remained after run.sh exited.\n' \
      >&2
    force_cleanup
    return 1
  fi

  if ((run_status != 0 && run_status != 130)); then
    printf 'ERROR: unexpected run.sh exit code after SIGINT: %s\n' \
      "${run_status}" >&2
    return 1
  fi

  printf '  run.sh exit code: %s\n' "${run_status}"

  printf '[6/7] Checking port release...\n'
  wait_for_port_release "${DASHBOARD_PORT}"
  wait_for_port_release "${ROSBRIDGE_PORT}"

  printf '[7/7] Checking for remaining managed processes...\n'

  local remaining_processes
  remaining_processes="$(find_remaining_project_processes)"

  if [[ -n "${remaining_processes}" ]]; then
    printf 'ERROR: managed processes remained after shutdown:\n' \
      >&2
    printf '%s\n' "${remaining_processes}" >&2
    return 1
  fi

  printf '\nPASS: scripts/run.sh lifecycle test succeeded.\n'
}

main "$@"
