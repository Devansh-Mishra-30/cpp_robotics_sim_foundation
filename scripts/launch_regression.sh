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
LAUNCH_FILE="sim.launch.py"

STARTUP_TIMEOUT_SECONDS="${STARTUP_TIMEOUT_SECONDS:-30}"
SHUTDOWN_TIMEOUT_SECONDS="${SHUTDOWN_TIMEOUT_SECONDS:-15}"

LAUNCH_PID=""
TEMP_DIRECTORY=""

require_command()
{
  local command_name="$1"

  if ! command -v "${command_name}" >/dev/null 2>&1; then
    printf 'ERROR: required command not found: %s\n' \
      "${command_name}" >&2
    return 1
  fi
}

process_group_exists()
{
  local process_group_id="$1"

  kill -0 -- "-${process_group_id}" 2>/dev/null
}

wait_for_process_group_exit()
{
  local process_group_id="$1"
  local deadline=$((SECONDS + SHUTDOWN_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if ! process_group_exists "${process_group_id}"; then
      return 0
    fi

    sleep 0.25
  done

  return 1
}

stop_launch()
{
  if [[ -z "${LAUNCH_PID}" ]]; then
    return 0
  fi

  if ! process_group_exists "${LAUNCH_PID}"; then
    wait "${LAUNCH_PID}" 2>/dev/null || true
    LAUNCH_PID=""
    return 0
  fi

  kill -INT -- "-${LAUNCH_PID}" 2>/dev/null || true

  if wait_for_process_group_exit "${LAUNCH_PID}"; then
    wait "${LAUNCH_PID}" 2>/dev/null || true
    LAUNCH_PID=""
    return 0
  fi

  kill -TERM -- "-${LAUNCH_PID}" 2>/dev/null || true
  sleep 1

  if process_group_exists "${LAUNCH_PID}"; then
    kill -KILL -- "-${LAUNCH_PID}" 2>/dev/null || true
  fi

  wait "${LAUNCH_PID}" 2>/dev/null || true
  LAUNCH_PID=""

  return 1
}

cleanup()
{
  local exit_code=$?

  stop_launch || exit_code=1

  if [[ -n "${TEMP_DIRECTORY}" ]]; then
    rm -rf -- "${TEMP_DIRECTORY}"
  fi

  exit "${exit_code}"
}

require_file_contains()
{
  local pattern="$1"
  local file_path="$2"
  local failure_message="$3"

  if grep -Eq "${pattern}" "${file_path}"; then
    return 0
  fi

  printf 'ERROR: %s\n' "${failure_message}" >&2
  printf 'File checked: %s\n' "${file_path}" >&2
  printf 'Expected pattern: %s\n' "${pattern}" >&2
  printf '%s\n' '----- file content -----' >&2
  cat "${file_path}" >&2
  printf '%s\n' '------------------------' >&2

  return 1
}

wait_for_node()
{
  local node_name="$1"
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if ros2 node list |
      grep -Fxq "${node_name}"; then
      return 0
    fi

    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      printf 'ERROR: launch exited while waiting for node %s\n' \
        "${node_name}" >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: node did not become ready: %s\n' \
    "${node_name}" >&2
  return 1
}

wait_for_topic()
{
  local topic_name="$1"
  local deadline=$((SECONDS + STARTUP_TIMEOUT_SECONDS))

  while ((SECONDS < deadline)); do
    if ros2 topic list |
      grep -Fxq "${topic_name}"; then
      return 0
    fi

    if ! kill -0 "${LAUNCH_PID}" 2>/dev/null; then
      printf 'ERROR: launch exited while waiting for topic %s\n' \
        "${topic_name}" >&2
      return 1
    fi

    sleep 1
  done

  printf 'ERROR: topic did not become ready: %s\n' \
    "${topic_name}" >&2
  return 1
}

read_parameter()
{
  local parameter_name="$1"
  local output_file="$2"

  ros2 param get \
    /sim_node \
    "${parameter_name}" \
    >"${output_file}" 2>&1
}

check_parameter()
{
  local parameter_name="$1"
  local expected_pattern="$2"
  local failure_message="$3"
  local output_file="${TEMP_DIRECTORY}/parameter_${parameter_name}.txt"

  read_parameter "${parameter_name}" "${output_file}"

  require_file_contains \
    "${expected_pattern}" \
    "${output_file}" \
    "${failure_message}"
}

start_launch()
{
  local log_file="$1"
  shift

  stop_launch
  LAUNCH_PID=""

  setsid ros2 launch \
    "${PACKAGE_NAME}" \
    "${LAUNCH_FILE}" \
    "$@" \
    >"${log_file}" 2>&1 &

  LAUNCH_PID=$!

  wait_for_node "/sim_node"
}

check_default_topics()
{
  local required_topics=(
    "/cmd_vel"
    "/robot_pose"
    "/odom"
    "/tf"
    "/diagnostics"
  )

  local topic_name

  for topic_name in "${required_topics[@]}"; do
    wait_for_topic "${topic_name}"
  done
}

check_default_parameters()
{
  check_parameter "dt" \
    'Double value is: 0\.1([0]*)?$' \
    "Default dt parameter is incorrect"

  check_parameter "initial_x" \
    'Double value is: 0(\.0*)?$' \
    "Default initial_x parameter is incorrect"

  check_parameter "initial_y" \
    'Double value is: 0(\.0*)?$' \
    "Default initial_y parameter is incorrect"

  check_parameter "initial_theta" \
    'Double value is: 0(\.0*)?$' \
    "Default initial_theta parameter is incorrect"

  check_parameter "cmd_timeout" \
    'Double value is: 0\.5([0]*)?$' \
    "Default cmd_timeout parameter is incorrect"

  check_parameter "max_linear_velocity" \
    'Double value is: 0\.5([0]*)?$' \
    "Default max_linear_velocity parameter is incorrect"

  check_parameter "max_angular_velocity" \
    'Double value is: 0\.8([0]*)?$' \
    "Default max_angular_velocity parameter is incorrect"
}

check_state_output()
{
  local pose_file="${TEMP_DIRECTORY}/pose.txt"
  local odom_file="${TEMP_DIRECTORY}/odom.txt"
  local tf_file="${TEMP_DIRECTORY}/tf.txt"
  local diagnostics_file="${TEMP_DIRECTORY}/diagnostics.txt"

  timeout 10 ros2 topic echo \
    --once \
    /robot_pose \
    >"${pose_file}"

  timeout 10 ros2 topic echo \
    --once \
    /odom \
    >"${odom_file}"

  timeout 10 ros2 topic echo \
    --once \
    /tf \
    >"${tf_file}"

  timeout 10 ros2 topic echo \
    --once \
    /diagnostics \
    >"${diagnostics_file}"

  require_file_contains \
    'x:' \
    "${pose_file}" \
    "/robot_pose did not publish x"

  require_file_contains \
    'child_frame_id: base_link' \
    "${odom_file}" \
    "/odom is missing base_link child frame"

  require_file_contains \
    'frame_id: odom' \
    "${odom_file}" \
    "/odom is missing odom frame"

  require_file_contains \
    'child_frame_id: base_link' \
    "${tf_file}" \
    "/tf is missing base_link child frame"

  require_file_contains \
    'name: sim_node' \
    "${diagnostics_file}" \
    "/diagnostics is missing sim_node status"

  require_file_contains \
    'timeout_active' \
    "${diagnostics_file}" \
    "/diagnostics is missing timeout_active"
}

check_command_response()
{
  local pose_file="${TEMP_DIRECTORY}/pose_after_command.txt"

  ros2 topic pub \
    --once \
    /cmd_vel \
    geometry_msgs/msg/Twist \
    '{linear: {x: 0.3}, angular: {z: 0.2}}' \
    >"${TEMP_DIRECTORY}/command_publish.txt" 2>&1

  sleep 1

  timeout 10 ros2 topic echo \
    --once \
    /robot_pose \
    >"${pose_file}"

  require_file_contains \
    'theta:' \
    "${pose_file}" \
    "/robot_pose is missing theta after command"
}

check_diagnostics_interface()
{
  local diagnostics_info="${TEMP_DIRECTORY}/diagnostics_info.txt"

  ros2 topic info \
    /diagnostics \
    --verbose \
    >"${diagnostics_info}"

  require_file_contains \
    'diagnostic_msgs/msg/DiagnosticArray' \
    "${diagnostics_info}" \
    "/diagnostics has the wrong message type"

  require_file_contains \
    'RELIABLE' \
    "${diagnostics_info}" \
    "/diagnostics QoS is not reliable"

  require_file_contains \
    'VOLATILE' \
    "${diagnostics_info}" \
    "/diagnostics QoS is not volatile"
}

check_override_parameters()
{
  check_parameter "initial_x" \
    'Double value is: 2(\.0*)?$' \
    "initial_x override failed"

  check_parameter "initial_y" \
    'Double value is: 1(\.0*)?$' \
    "initial_y override failed"

  check_parameter "initial_theta" \
    'Double value is: 0\.5([0]*)?$' \
    "initial_theta override failed"

  check_parameter "dt" \
    'Double value is: 0\.05([0]*)?$' \
    "dt override failed"

  check_parameter "cmd_timeout" \
    'Double value is: 1(\.0*)?$' \
    "cmd_timeout override failed"

  check_parameter "max_linear_velocity" \
    'Double value is: 0\.2([0]*)?$' \
    "max_linear_velocity override failed"

  check_parameter "max_angular_velocity" \
    'Double value is: 0\.4([0]*)?$' \
    "max_angular_velocity override failed"
}

main()
{
  require_command bash
  require_command cat
  require_command grep
  require_command mktemp
  require_command ros2
  require_command setsid
  require_command timeout

  if [[ ! -f "${ROS_SETUP}" ]]; then
    printf 'ERROR: ROS setup file not found: %s\n' \
      "${ROS_SETUP}" >&2
    return 1
  fi

  if [[ ! -f "${WORKSPACE_SETUP}" ]]; then
    printf 'ERROR: workspace setup file not found: %s\n' \
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

  TEMP_DIRECTORY="$(mktemp -d)"
  trap cleanup EXIT INT TERM

  printf '\n========== Launch regression ==========\n'

  printf '[1/8] Starting default launch...\n'
  start_launch "${TEMP_DIRECTORY}/default_launch.log"

  printf '[2/8] Checking expected topics...\n'
  check_default_topics

  printf '[3/8] Checking default parameters...\n'
  check_default_parameters

  printf '[4/8] Checking state output...\n'
  check_state_output

  printf '[5/8] Checking command response...\n'
  check_command_response

  printf '[6/8] Checking diagnostics interface...\n'
  check_diagnostics_interface

  printf '[7/8] Starting launch with overrides...\n'
  start_launch \
    "${TEMP_DIRECTORY}/override_launch.log" \
    initial_x:=2.0 \
    initial_y:=1.0 \
    initial_theta:=0.5 \
    dt:=0.05 \
    cmd_timeout:=1.0 \
    max_linear_velocity:=0.2 \
    max_angular_velocity:=0.4

  check_override_parameters

  printf '[8/8] Checking overridden pose output...\n'

  timeout 10 ros2 topic echo \
    --once \
    /robot_pose \
    >"${TEMP_DIRECTORY}/override_pose.txt"

  require_file_contains \
    'x:' \
    "${TEMP_DIRECTORY}/override_pose.txt" \
    "Overridden /robot_pose is missing x"

  require_file_contains \
    'y:' \
    "${TEMP_DIRECTORY}/override_pose.txt" \
    "Overridden /robot_pose is missing y"

  require_file_contains \
    'theta:' \
    "${TEMP_DIRECTORY}/override_pose.txt" \
    "Overridden /robot_pose is missing theta"

  printf '\nPASS: launch regression succeeded.\n'
}

main "$@"
