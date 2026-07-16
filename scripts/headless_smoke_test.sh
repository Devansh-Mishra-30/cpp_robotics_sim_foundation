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
WEBSOCKET_PORT="${WEBSOCKET_PORT:-9090}"
STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-30}"

LAUNCH_PID=""
LAUNCH_LOG=""

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

cleanup() {
  local exit_code=$?

  if [[ -n "${LAUNCH_PID}" ]]; then
    kill -INT -- "-${LAUNCH_PID}" 2>/dev/null || true

    for _ in {1..20}; do
      if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
        break
      fi

      sleep 0.25
    done

    if kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      kill -TERM -- "-${LAUNCH_PID}" 2>/dev/null || true
    fi

    wait "${LAUNCH_PID}" 2>/dev/null || true
  fi

  if ((exit_code != 0)) && [[ -f "${LAUNCH_LOG}" ]]; then
    printf '\n=== Launch log after failure ===\n' >&2
    cat "${LAUNCH_LOG}" >&2
  fi

  if [[ -n "${LAUNCH_LOG}" ]]; then
    rm -f "${LAUNCH_LOG}"
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
      "${url}" \
      | grep -qi '<html'; then
      return 0
    fi

    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      printf 'ERROR: launch process exited before HTTP became ready.\n' \
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
    with socket.create_connection(
        (host, port),
        timeout=1.0,
    ):
        pass
except OSError:
    raise SystemExit(1)
PY
    then
      return 0
    fi

    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      printf 'ERROR: launch process exited before port %s became ready.\n' \
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

    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      printf 'ERROR: launch exited while waiting for topic %s\n' \
        "${topic_name}" >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: required topic was not found: %s\n' \
    "${topic_name}" >&2
  return 1
}

main() {
  require_command bash
  require_command curl
  require_command grep
  require_command python3
  require_command ros2
  require_command mktemp
  require_command setsid

  if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ERROR: ROS setup file not found: %s\n' \
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

  LAUNCH_LOG="$(mktemp)"

  trap cleanup EXIT INT TERM

  printf '\n=== Headless dashboard integration test ===\n'
  printf 'Dashboard port: %s\n' "${DASHBOARD_PORT}"
  printf 'WebSocket port: %s\n\n' "${WEBSOCKET_PORT}"

  setsid ros2 launch \
    "${PACKAGE_NAME}" \
    "${LAUNCH_FILE}" \
    dashboard_port:="${DASHBOARD_PORT}" \
    websocket_port:="${WEBSOCKET_PORT}" \
    open_browser:=false \
    >"${LAUNCH_LOG}" 2>&1 &

  LAUNCH_PID=$!

  printf '[1/4] Waiting for launch process...\n'
  sleep 2

  if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
    printf 'ERROR: launch process exited during startup.\n' >&2
    return 1
  fi

  printf '[2/4] Checking dashboard HTTP server...\n'
  wait_for_http

  printf '[3/4] Checking rosbridge TCP port...\n'
  wait_for_tcp_port \
    "127.0.0.1" \
    "${WEBSOCKET_PORT}"

  printf '[4/4] Checking manager status topics...\n'

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

  printf '\nPASS: headless dashboard integration test succeeded.\n'
}

main "$@"
