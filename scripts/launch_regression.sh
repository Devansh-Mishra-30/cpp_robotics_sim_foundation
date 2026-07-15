#!/usr/bin/env bash

set -eo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROS_WS="$REPO_ROOT/ros2_ws"
PACKAGE_NAME="cpp_robotics_sim_ros"
LAUNCH_FILE="sim.launch.py"

LAUNCH_PID=""

cleanup() {
    if [[ -n "${LAUNCH_PID}" ]]; then
        kill "${LAUNCH_PID}" 2>/dev/null || true
        wait "${LAUNCH_PID}" 2>/dev/null || true
    fi
}

trap cleanup EXIT

require_grep() {
    local pattern="$1"
    local file="$2"
    local message="$3"

    if ! grep -q "$pattern" "$file"; then
        echo "FAIL: $message"
        echo "File checked: $file"
        echo "Expected pattern: $pattern"
        echo "----- file content -----"
        cat "$file"
        echo "------------------------"
        exit 1
    fi
}

require_command_contains() {
    local command="$1"
    local pattern="$2"
    local message="$3"
    local output_file
    output_file="$(mktemp)"

    bash -lc "$command" > "$output_file" 2>&1

    if ! grep -q "$pattern" "$output_file"; then
        echo "FAIL: $message"
        echo "Command: $command"
        echo "Expected pattern: $pattern"
        echo "----- command output -----"
        cat "$output_file"
        echo "--------------------------"
        exit 1
    fi
}

start_launch() {
    local log_file="$1"
    shift

    cleanup
    LAUNCH_PID=""

    ros2 launch "$PACKAGE_NAME" "$LAUNCH_FILE" "$@" > "$log_file" 2>&1 &
    LAUNCH_PID=$!

    sleep 4

    if ! kill -0 "$LAUNCH_PID" 2>/dev/null; then
        echo "FAIL: launch process exited early"
        echo "----- launch log -----"
        cat "$log_file"
        echo "----------------------"
        exit 1
    fi
}

echo "========== Launch Regression =========="

cd "$ROS_WS"

source /opt/ros/jazzy/setup.bash
source "$ROS_WS/install/setup.bash"

echo "[1/8] Testing default launch..."
DEFAULT_LOG="$(mktemp)"
start_launch "$DEFAULT_LOG"

echo "[2/8] Checking expected topics..."
TOPICS_FILE="$(mktemp)"
ros2 topic list > "$TOPICS_FILE"

require_grep "/cmd_vel" "$TOPICS_FILE" "Missing /cmd_vel"
require_grep "/robot_pose" "$TOPICS_FILE" "Missing /robot_pose"
require_grep "/odom" "$TOPICS_FILE" "Missing /odom"
require_grep "/tf" "$TOPICS_FILE" "Missing /tf"
require_grep "/diagnostics" "$TOPICS_FILE" "Missing /diagnostics"

echo "[3/8] Checking default parameters..."
require_command_contains "ros2 param get /sim_node dt" "0.1" "Default dt parameter is wrong"
require_command_contains "ros2 param get /sim_node initial_x" "0.0" "Default initial_x parameter is wrong"
require_command_contains "ros2 param get /sim_node initial_y" "0.0" "Default initial_y parameter is wrong"
require_command_contains "ros2 param get /sim_node initial_theta" "0.0" "Default initial_theta parameter is wrong"
require_command_contains "ros2 param get /sim_node cmd_timeout" "0.5" "Default cmd_timeout parameter is wrong"
require_command_contains "ros2 param get /sim_node max_linear_velocity" "0.5" "Default max_linear_velocity parameter is wrong"
require_command_contains "ros2 param get /sim_node max_angular_velocity" "0.8" "Default max_angular_velocity parameter is wrong"

echo "[4/8] Checking state topic output..."
POSE_FILE="$(mktemp)"
ODOM_FILE="$(mktemp)"
TF_FILE="$(mktemp)"
DIAG_FILE="$(mktemp)"

timeout 5 ros2 topic echo --once /robot_pose > "$POSE_FILE"
timeout 5 ros2 topic echo --once /odom > "$ODOM_FILE"
timeout 5 ros2 topic echo --once /tf > "$TF_FILE"
timeout 5 ros2 topic echo --once /diagnostics > "$DIAG_FILE"

require_grep "x:" "$POSE_FILE" "/robot_pose did not publish x"
require_grep "child_frame_id: base_link" "$ODOM_FILE" "/odom missing base_link child frame"
require_grep "frame_id: odom" "$ODOM_FILE" "/odom missing odom frame"
require_grep "child_frame_id: base_link" "$TF_FILE" "/tf missing base_link child frame"
require_grep "name: sim_node" "$DIAG_FILE" "/diagnostics missing sim_node status"
require_grep "timeout_active" "$DIAG_FILE" "/diagnostics missing timeout_active key"

echo "[5/8] Checking command response..."
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}, angular: {z: 0.2}}" >/tmp/launch_regression_cmd_pub.log 2>&1 || true
sleep 1

POSE_AFTER_CMD_FILE="$(mktemp)"
timeout 5 ros2 topic echo --once /robot_pose > "$POSE_AFTER_CMD_FILE"
require_grep "theta:" "$POSE_AFTER_CMD_FILE" "/robot_pose missing theta after command"

echo "[6/8] Checking diagnostics QoS/type..."
DIAG_INFO_FILE="$(mktemp)"
ros2 topic info /diagnostics --verbose > "$DIAG_INFO_FILE"
require_grep "diagnostic_msgs/msg/DiagnosticArray" "$DIAG_INFO_FILE" "/diagnostics has wrong message type"
require_grep "RELIABLE" "$DIAG_INFO_FILE" "/diagnostics QoS is not reliable"
require_grep "VOLATILE" "$DIAG_INFO_FILE" "/diagnostics QoS is not volatile"

echo "[7/8] Testing launch argument overrides..."
OVERRIDE_LOG="$(mktemp)"
start_launch "$OVERRIDE_LOG" \
    initial_x:=2.0 \
    initial_y:=1.0 \
    initial_theta:=0.5 \
    dt:=0.05 \
    cmd_timeout:=1.0 \
    max_linear_velocity:=0.2 \
    max_angular_velocity:=0.4

require_command_contains "ros2 param get /sim_node initial_x" "2" "Override initial_x failed"
require_command_contains "ros2 param get /sim_node initial_y" "1" "Override initial_y failed"
require_command_contains "ros2 param get /sim_node initial_theta" "0.5" "Override initial_theta failed"
require_command_contains "ros2 param get /sim_node dt" "0.05" "Override dt failed"
require_command_contains "ros2 param get /sim_node cmd_timeout" "1" "Override cmd_timeout failed"
require_command_contains "ros2 param get /sim_node max_linear_velocity" "0.2" "Override max_linear_velocity failed"
require_command_contains "ros2 param get /sim_node max_angular_velocity" "0.4" "Override max_angular_velocity failed"

echo "[8/8] Checking overridden pose output..."
OVERRIDE_POSE_FILE="$(mktemp)"
timeout 5 ros2 topic echo --once /robot_pose > "$OVERRIDE_POSE_FILE"

require_grep "x:" "$OVERRIDE_POSE_FILE" "Overridden /robot_pose missing x"
require_grep "y:" "$OVERRIDE_POSE_FILE" "Overridden /robot_pose missing y"
require_grep "theta:" "$OVERRIDE_POSE_FILE" "Overridden /robot_pose missing theta"

echo "========== PASS: launch regression succeeded =========="