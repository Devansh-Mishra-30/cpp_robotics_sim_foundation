#!/usr/bin/env bash
set -e

echo "========================================"
echo "NAV2 PLANNER/CONTROLLER CHECK"
echo "========================================"

fail()
{
  echo "FAIL: $1"
  exit 1
}

pass_step()
{
  echo "PASS: $1"
}

echo ""
echo "[1/6] Checking required Nav2 actions..."

ACTION_LIST="$(ros2 action list -t)"

echo "$ACTION_LIST" | grep -q "/compute_path_to_pose \[nav2_msgs/action/ComputePathToPose\]" \
  || fail "/compute_path_to_pose action missing"

echo "$ACTION_LIST" | grep -q "/follow_path \[nav2_msgs/action/FollowPath\]" \
  || fail "/follow_path action missing"

echo "$ACTION_LIST" | grep -q "/navigate_to_pose \[nav2_msgs/action/NavigateToPose\]" \
  || fail "/navigate_to_pose action missing"

pass_step "Required planner/controller/navigation actions exist"

echo ""
echo "[2/6] Checking planner server lifecycle state..."

PLANNER_STATE="$(ros2 lifecycle get /planner_server || true)"
echo "$PLANNER_STATE"
echo "$PLANNER_STATE" | grep -q "active \[3\]" \
  || fail "/planner_server is not active"

pass_step "Planner server is active"

echo ""
echo "[3/6] Checking controller server lifecycle state..."

CONTROLLER_STATE="$(ros2 lifecycle get /controller_server || true)"
echo "$CONTROLLER_STATE"
echo "$CONTROLLER_STATE" | grep -q "active \[3\]" \
  || fail "/controller_server is not active"

pass_step "Controller server is active"

echo ""
echo "[4/6] Computing simple odom-frame path..."

PATH_OUTPUT="$(timeout 30s ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose "{
  goal: {
    header: {frame_id: odom},
    pose: {
      position: {x: 0.8, y: 0.4, z: 0.0},
      orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
    }
  },
  planner_id: GridBased,
  use_start: false
}" || true)"

echo "$PATH_OUTPUT"

echo "$PATH_OUTPUT" | grep -q "Goal accepted" \
  || fail "Planner goal was not accepted"

echo "$PATH_OUTPUT" | grep -q "frame_id: odom" \
  || fail "Computed path is not in odom frame"

echo "$PATH_OUTPUT" | grep -q "poses:" \
  || fail "Computed path does not contain poses"

echo "$PATH_OUTPUT" | grep -q "SUCCEEDED" \
  || fail "Planner action did not finish with SUCCEEDED"

pass_step "Planner computed an odom-frame path"

echo ""
echo "[5/6] Checking controller frequency..."

CONTROLLER_FREQUENCY="$(ros2 param get /controller_server controller_frequency || true)"
echo "$CONTROLLER_FREQUENCY"
echo "$CONTROLLER_FREQUENCY" | grep -q "10.0" \
  || fail "controller_frequency is not 10.0"

pass_step "controller_frequency is 10.0"

echo ""
echo "[6/6] Checking conservative FollowPath controller params..."

check_param()
{
  local param_name="$1"
  local expected="$2"

  local output
  output="$(ros2 param get /controller_server "$param_name" || true)"
  echo "$output"

  echo "$output" | grep -q "$expected" \
    || fail "$param_name is not $expected"
}

check_param "FollowPath.max_vel_x" "0.25"
check_param "FollowPath.max_vel_theta" "0.6"
check_param "FollowPath.acc_lim_x" "0.5"
check_param "FollowPath.acc_lim_theta" "1.0"
check_param "FollowPath.sim_time" "1.5"
check_param "FollowPath.vx_samples" "20"
check_param "FollowPath.vtheta_samples" "20"

pass_step "FollowPath params are conservative and readable"

echo ""
echo "========================================"
echo "NAV2 PLANNER/CONTROLLER CHECK: PASS"
echo "========================================"
