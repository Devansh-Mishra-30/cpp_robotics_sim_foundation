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

ROS_DISTRO="${ROS_DISTRO:-jazzy}"
ROS_SETUP="/opt/ros/${ROS_DISTRO}/setup.bash"
ROS_WS="${REPO_ROOT}/ros2_ws"
WORKSPACE_SETUP="${ROS_WS}/install/setup.bash"

PACKAGE_NAME="cpp_robotics_sim_ros"
LAUNCH_FILE="web_interface.launch.py"

DASHBOARD_PORT="${DASHBOARD_PORT:-8080}"
ROSBRIDGE_PORT="${ROSBRIDGE_PORT:-9090}"
OPEN_BROWSER="${OPEN_BROWSER:-true}"

SHUTDOWN_TIMEOUT_SECONDS="${SHUTDOWN_TIMEOUT_SECONDS:-15}"

LAUNCH_PID=""
BROWSER_PID=""
SHUTDOWN_STARTED=false

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

detect_wsl_ip() {
  local detected_ip=""

  if command -v ip >/dev/null 2>&1; then
    detected_ip="$(
      ip -4 route get 1.1.1.1 2>/dev/null |
        awk '
          {
            for (field_number = 1; field_number <= NF; field_number++) {
              if ($field_number == "src") {
                print $(field_number + 1)
                exit
              }
            }
          }
        '
    )"
  fi

  if [[ -z "${detected_ip}" ]]; then
    detected_ip="$(
      hostname -I 2>/dev/null |
        awk '{print $1}'
    )"
  fi

  if [[ -z "${detected_ip}" ]]; then
    printf 'ERROR: unable to determine the WSL IP address.\n' \
      >&2
    return 1
  fi

  printf '%s\n' "${detected_ip}"
}

open_windows_browser() {
  local dashboard_url="$1"

  if [[ "${OPEN_BROWSER}" != "true" ]]; then
    return 0
  fi

  if command -v powershell.exe >/dev/null 2>&1; then
    powershell.exe \
      -NoProfile \
      -Command \
      "Start-Process '${dashboard_url}'" \
      >/dev/null 2>&1
    return 0
  fi

  if command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /C start "" "${dashboard_url}" \
      >/dev/null 2>&1
    return 0
  fi

  printf 'NOTICE: Windows browser launcher was not found.\n'
  printf 'Open this URL manually:\n  %s\n' \
    "${dashboard_url}"
}

process_group_exists() {
  local process_group_id="$1"

  kill -0 -- "-${process_group_id}" 2>/dev/null
}

wait_for_process_group_exit() {
  local process_group_id="$1"
  local timeout_seconds="$2"
  local deadline=$((SECONDS + timeout_seconds))

  while ((SECONDS < deadline)); do
    if ! process_group_exists "${process_group_id}"; then
      return 0
    fi

    sleep 0.25
  done

  return 1
}

stop_browser_helper() {
  if [[ -z "${BROWSER_PID}" ]]; then
    return 0
  fi

  if kill -0 "${BROWSER_PID}" 2>/dev/null; then
    kill -TERM "${BROWSER_PID}" 2>/dev/null || true
  fi

  wait "${BROWSER_PID}" 2>/dev/null || true
  BROWSER_PID=""
}

stop_launcher() {
  if [[ "${SHUTDOWN_STARTED}" == "true" ]]; then
    return 0
  fi

  SHUTDOWN_STARTED=true
  stop_browser_helper

  if [[ -z "${LAUNCH_PID}" ]]; then
    return 0
  fi

  if ! process_group_exists "${LAUNCH_PID}"; then
    wait "${LAUNCH_PID}" 2>/dev/null || true
    LAUNCH_PID=""
    return 0
  fi

  printf '\nStopping dashboard stack with SIGINT...\n'
  kill -INT -- "-${LAUNCH_PID}" 2>/dev/null || true

  if wait_for_process_group_exit \
    "${LAUNCH_PID}" \
    "${SHUTDOWN_TIMEOUT_SECONDS}"; then
    wait "${LAUNCH_PID}" 2>/dev/null || true
    LAUNCH_PID=""
    printf 'Dashboard stack stopped cleanly.\n'
    return 0
  fi

  printf 'Dashboard stack did not stop after SIGINT; '
  printf 'sending SIGTERM.\n'

  kill -TERM -- "-${LAUNCH_PID}" 2>/dev/null || true

  if wait_for_process_group_exit \
    "${LAUNCH_PID}" \
    5; then
    wait "${LAUNCH_PID}" 2>/dev/null || true
    LAUNCH_PID=""
    printf 'Dashboard stack stopped after SIGTERM.\n'
    return 0
  fi

  printf 'Dashboard stack did not stop after SIGTERM; '
  printf 'sending SIGKILL.\n' >&2

  kill -KILL -- "-${LAUNCH_PID}" 2>/dev/null || true
  wait "${LAUNCH_PID}" 2>/dev/null || true
  LAUNCH_PID=""

  return 1
}

handle_signal() {
  local signal_name="$1"

  printf '\nReceived %s.\n' "${signal_name}"
  stop_launcher
}

cleanup() {
  local exit_code=$?

  stop_browser_helper

  if [[ "${SHUTDOWN_STARTED}" != "true" ]]; then
    stop_launcher || exit_code=1
  fi

  return "${exit_code}"
}

main() {
  require_command ros2
  require_command awk
  require_command hostname
  require_command setsid

  if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ERROR: ROS 2 setup file not found: %s\n' \
      "${ROS_SETUP}" >&2
    return 1
  fi

  if [[ ! -f "${WORKSPACE_SETUP}" ]]; then
    printf 'ERROR: built workspace not found: %s\n' \
      "${WORKSPACE_SETUP}" >&2
    printf 'Run ./scripts/build.sh first.\n' >&2
    return 1
  fi

  set +u
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
  # shellcheck disable=SC1090
  source "${WORKSPACE_SETUP}"
  set -u

  local wsl_ip
  local dashboard_url
  local launch_status

  wsl_ip="$(detect_wsl_ip)"
  dashboard_url="http://${wsl_ip}:${DASHBOARD_PORT}/"

  printf '\n=== Robotics simulation dashboard ===\n'
  printf 'ROS distribution: %s\n' "${ROS_DISTRO}"
  printf 'Workspace:        %s\n' "${ROS_WS}"
  printf 'Dashboard:        %s\n' "${dashboard_url}"
  printf 'Rosbridge port:   %s\n' "${ROSBRIDGE_PORT}"
  printf '\nPress Ctrl+C to stop the dashboard stack.\n\n'

  trap 'handle_signal SIGINT' INT
  trap 'handle_signal SIGTERM' TERM
  trap cleanup EXIT

  if [[ "${OPEN_BROWSER}" == "true" ]]; then
    (
      sleep 3
      open_windows_browser "${dashboard_url}"
    ) &

    BROWSER_PID=$!
  fi

  python3 -c '
import os
import signal
import sys

os.setsid()
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)
os.execvp(sys.argv[1], sys.argv[1:])
' \
    ros2 launch \
    "${PACKAGE_NAME}" \
    "${LAUNCH_FILE}" \
    dashboard_port:="${DASHBOARD_PORT}" \
    websocket_port:="${ROSBRIDGE_PORT}" \
    open_browser:=false &

  LAUNCH_PID=$!

  set +e
  wait "${LAUNCH_PID}"
  launch_status=$?
  set -e

  LAUNCH_PID=""

  if [[ "${SHUTDOWN_STARTED}" == "true" ]]; then
    return 0
  fi

  if ((launch_status != 0)); then
    printf 'ERROR: dashboard launcher exited with code %s.\n' \
      "${launch_status}" >&2
    return "${launch_status}"
  fi

  printf 'Dashboard launcher exited normally.\n'
}

main "$@"
