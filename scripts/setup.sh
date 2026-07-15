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
ROSDEP_SOURCES_FILE="/etc/ros/rosdep/sources.list.d/20-default.list"

require_command() {
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

verify_platform() {
  if [[ ! -r /etc/os-release ]]; then
    printf 'ERROR: /etc/os-release is unavailable.\n' >&2
    return 1
  fi

  # shellcheck disable=SC1091
  source /etc/os-release

  printf 'Operating system: %s %s\n' \
    "${NAME:-unknown}" "${VERSION_ID:-unknown}"

  if [[ "${ID:-}" != "ubuntu" ]]; then
    printf 'ERROR: this setup script currently supports Ubuntu only.\n' \
      >&2
    return 1
  fi

  if [[ "${VERSION_ID:-}" != "24.04" ]]; then
    printf 'ERROR: Ubuntu 24.04 is required for this release.\n' \
      >&2
    return 1
  fi
}

install_rosdep_if_missing() {
  if command -v rosdep >/dev/null 2>&1; then
    printf 'rosdep: already installed\n'
    return 0
  fi

  require_command sudo
  require_command apt-get

  printf '\nrosdep is not installed.\n'
  printf 'Installing python3-rosdep through apt...\n\n'

  sudo apt-get update
  sudo apt-get install --yes python3-rosdep

  require_command rosdep
}

initialize_rosdep() {
  if [[ -f "${ROSDEP_SOURCES_FILE}" ]]; then
    printf 'rosdep sources: already initialized\n'
  else
    printf 'Initializing rosdep sources...\n'
    sudo rosdep init
  fi

  printf 'Updating rosdep database...\n'
  rosdep update
}

install_workspace_dependencies() {
  printf '\nResolving ROS package dependencies...\n'

  rosdep install \
    --from-paths "${ROS_WS}/src" \
    --ignore-src \
    --rosdistro "${ROS_DISTRO}" \
    --default-yes
}

main() {
  printf '\n=== Project setup ===\n'
  printf 'Repository:       %s\n' "${REPO_ROOT}"
  printf 'ROS distribution: %s\n' "${ROS_DISTRO}"
  printf 'Workspace:        %s\n\n' "${ROS_WS}"

  verify_platform

  require_command bash
  require_command sudo
  require_command apt-get

  if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ERROR: ROS 2 setup file not found: %s\n' \
      "${ROS_SETUP}" >&2
    printf 'Install ROS 2 %s before running this script.\n' \
      "${ROS_DISTRO}" >&2
    return 1
  fi

  if [[ ! -d "${ROS_WS}/src" ]]; then
    printf 'ERROR: workspace source directory not found: %s\n' \
      "${ROS_WS}/src" >&2
    return 1
  fi

  install_rosdep_if_missing
  initialize_rosdep
  install_workspace_dependencies

  require_command colcon
  require_command ros2

  printf '\nSetup completed successfully.\n'
  printf 'Next commands:\n'
  printf '  ./scripts/build.sh\n'
  printf '  ./scripts/test.sh\n'
}

main "$@"
