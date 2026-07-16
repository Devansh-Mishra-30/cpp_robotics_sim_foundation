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

# ROS 2 Jazzy suppresses cppcheck 2.13 by default because it can be slow.
# Run it deliberately so CI performs complete C++ static analysis.
export AMENT_CPPCHECK_ALLOW_SLOW_VERSIONS=1

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

main() {
  require_command bash
  require_command colcon

  if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ERROR: ROS 2 setup file not found: %s\n' \
      "${ROS_SETUP}" >&2
    return 1
  fi

  if [[ ! -f "${WORKSPACE_SETUP}" ]]; then
    printf 'ERROR: built workspace setup file not found: %s\n' \
      "${WORKSPACE_SETUP}" >&2
    printf 'Run ./scripts/build.sh first.\n' >&2
    return 1
  fi

  printf '\n=== Source validation ===\n'
  "${REPO_ROOT}/scripts/check_syntax.sh"

  printf '\n=== ROS 2 test suite ===\n'
  printf 'Distribution: %s\n' "${ROS_DISTRO}"
  printf 'Workspace:    %s\n' "${ROS_WS}"
  printf 'Package:      %s\n\n' "${PACKAGE_NAME}"

  set +u
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
  # shellcheck disable=SC1090
  source "${WORKSPACE_SETUP}"
  set -u

  cd "${ROS_WS}"

  colcon test \
    --packages-select "${PACKAGE_NAME}" \
    --event-handlers console_direct+ \
    --return-code-on-test-failure

  printf '\n=== Test results ===\n'
  colcon test-result --verbose

  printf '\n=== Simulator launch regression ===\n'
  "${REPO_ROOT}/scripts/launch_regression.sh"

  printf '\n=== Headless integration test ===\n'
  "${REPO_ROOT}/scripts/headless_smoke_test.sh"

  printf '\n=== Public launcher lifecycle test ===\n'
  "${REPO_ROOT}/scripts/run_lifecycle_test.sh"

  printf '\nAll unit and integration tests completed successfully.\n'
}

main "$@"
