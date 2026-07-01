#!/usr/bin/env bash
set -e

echo "======================================"
echo " Day 92 Nav2 Lifecycle Check"
echo "======================================"

NODES=(
  "/controller_server"
  "/smoother_server"
  "/planner_server"
  "/behavior_server"
  "/velocity_smoother"
  "/bt_navigator"
  "/waypoint_follower"
)

PASS=true

echo ""
echo "[1] Checking lifecycle manager node..."
if ros2 node list | grep -q "^/lifecycle_manager_navigation$"; then
  echo "PASS: /lifecycle_manager_navigation exists"
else
  echo "FAIL: /lifecycle_manager_navigation missing"
  PASS=false
fi

echo ""
echo "[2] Checking lifecycle states..."
for NODE in "${NODES[@]}"; do
  STATE="$(ros2 lifecycle get "$NODE" 2>/dev/null || true)"

  if echo "$STATE" | grep -q "active \[3\]"; then
    echo "PASS: $NODE -> $STATE"
  else
    echo "FAIL: $NODE -> ${STATE:-not found}"
    PASS=false
  fi
done

echo ""
echo "[3] Checking Nav2 action servers..."
if ros2 action list -t | grep -q "/navigate_to_pose \[nav2_msgs/action/NavigateToPose\]"; then
  echo "PASS: /navigate_to_pose exists"
else
  echo "FAIL: /navigate_to_pose missing"
  PASS=false
fi

if ros2 action list -t | grep -q "/navigate_through_poses \[nav2_msgs/action/NavigateThroughPoses\]"; then
  echo "PASS: /navigate_through_poses exists"
else
  echo "FAIL: /navigate_through_poses missing"
  PASS=false
fi

echo ""
echo "[4] Checking lifecycle manager service..."
if ros2 service list | grep -q "/lifecycle_manager_navigation/manage_nodes"; then
  echo "PASS: /lifecycle_manager_navigation/manage_nodes exists"
else
  echo "FAIL: /lifecycle_manager_navigation/manage_nodes missing"
  PASS=false
fi

echo ""
echo "======================================"
if [ "$PASS" = true ]; then
  echo "DAY 92 LIFECYCLE CHECK: PASS"
  exit 0
else
  echo "DAY 92 LIFECYCLE CHECK: FAIL"
  exit 1
fi
