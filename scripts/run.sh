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

ROS_DISTRO="${ROS_DISTRO:-jazzy}"
ROS_SETUP="/opt/ros/${ROS_DISTRO}/setup.bash"
ROS_WS="${REPO_ROOT}/ros2_ws"
WORKSPACE_SETUP="${ROS_WS}/install/setup.bash"

PACKAGE_NAME="cpp_robotics_sim_ros"
LAUNCH_FILE="web_interface.launch.py"

DASHBOARD_PORT="${DASHBOARD_PORT:-8080}"
ROSBRIDGE_PORT="${ROSBRIDGE_PORT:-9090}"
OPEN_BROWSER="${OPEN_BROWSER:-true}"

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
            for (index = 1; index <= NF; index++) {
              if ($index == "src") {
                print $(index + 1)
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
      >/dev/null 2>&1 &
    return 0
  fi

  if command -v cmd.exe >/dev/null 2>&1; then
    cmd.exe /C start "" "${dashboard_url}" \
      >/dev/null 2>&1 &
    return 0
  fi

  printf 'NOTICE: Windows browser launcher was not found.\n'
  printf 'Open this URL manually:\n  %s\n' \
    "${dashboard_url}"
}

main() {
  require_command ros2
  require_command awk
  require_command hostname

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

  wsl_ip="$(detect_wsl_ip)"
  dashboard_url="http://${wsl_ip}:${DASHBOARD_PORT}/"

  printf '\n=== Robotics simulation dashboard ===\n'
  printf 'ROS distribution: %s\n' "${ROS_DISTRO}"
  printf 'Workspace:        %s\n' "${ROS_WS}"
  printf 'Dashboard:        %s\n' "${dashboard_url}"
  printf 'Rosbridge port:   %s\n' "${ROSBRIDGE_PORT}"
  printf '\nPress Ctrl+C to stop the dashboard stack.\n\n'

  (
    sleep 3
    open_windows_browser "${dashboard_url}"
  ) &

  exec ros2 launch \
    "${PACKAGE_NAME}" \
    "${LAUNCH_FILE}" \
    dashboard_port:="${DASHBOARD_PORT}" \
    websocket_port:="${ROSBRIDGE_PORT}" \
    open_browser:=false
}

main "$@"
