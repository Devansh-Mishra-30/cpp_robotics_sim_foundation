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
PACKAGE_NAME="cpp_robotics_sim_ros"

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
    printf 'Install ROS 2 %s or set ROS_DISTRO correctly.\n' \
      "${ROS_DISTRO}" >&2
    return 1
  fi

  if [[ ! -d "${ROS_WS}/src/${PACKAGE_NAME}" ]]; then
    printf 'ERROR: ROS 2 package directory not found: %s\n' \
      "${ROS_WS}/src/${PACKAGE_NAME}" >&2
    return 1
  fi

  printf '\n=== Source validation ===\n'
  "${REPO_ROOT}/scripts/check_syntax.sh"

  printf '\n=== ROS 2 build ===\n'
  printf 'Distribution: %s\n' "${ROS_DISTRO}"
  printf 'Workspace:    %s\n' "${ROS_WS}"
  printf 'Package:      %s\n\n' "${PACKAGE_NAME}"

  # ROS setup scripts are not guaranteed to be compatible
  # with nounset, so temporarily disable it while sourcing.
  set +u
  # shellcheck disable=SC1090
  source "${ROS_SETUP}"
  set -u

  cd "${ROS_WS}"

  colcon build \
    --packages-select "${PACKAGE_NAME}" \
    --cmake-args -DBUILD_TESTING=ON \
    --event-handlers console_direct+

  printf '\nBuild completed successfully.\n'
  printf 'Source the workspace with:\n'
  printf '  source %s/install/setup.bash\n' "${ROS_WS}"
}

main "$@"
