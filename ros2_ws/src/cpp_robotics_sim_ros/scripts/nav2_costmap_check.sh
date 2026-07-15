#!/usr/bin/env bash
set -e

echo "======================================"
echo " Nav2 Costmap Check"
echo "======================================"

PASS=true

check_node() {
  NODE="$1"
  if ros2 node list | grep -q "^${NODE}$"; then
    echo "PASS: node exists -> $NODE"
  else
    echo "FAIL: node missing -> $NODE"
    PASS=false
  fi
}

check_topic() {
  TOPIC="$1"
  if ros2 topic list | grep -q "^${TOPIC}$"; then
    echo "PASS: topic exists -> $TOPIC"
  else
    echo "FAIL: topic missing -> $TOPIC"
    PASS=false
  fi
}

check_topic_msg() {
  TOPIC="$1"
  echo "Checking message output from $TOPIC ..."
  if timeout 6 ros2 topic echo --once "$TOPIC" >/tmp/nav2_costmap_topic_check.txt 2>/dev/null; then
    echo "PASS: $TOPIC publishes messages"
  else
    echo "FAIL: $TOPIC did not publish within timeout"
    PASS=false
  fi
}

echo ""
echo "[1] Checking costmap nodes..."
check_node "/local_costmap/local_costmap"
check_node "/global_costmap/global_costmap"

echo ""
echo "[2] Checking sensor and costmap topics..."
check_topic "/scan"
check_topic "/local_costmap/costmap"
check_topic "/global_costmap/costmap"
check_topic "/local_costmap/published_footprint"
check_topic "/global_costmap/published_footprint"

echo ""
echo "[3] Checking topic message flow..."
check_topic_msg "/scan"
check_topic_msg "/local_costmap/costmap"
check_topic_msg "/global_costmap/costmap"

echo ""
echo "[4] Checking local costmap frame params..."
LOCAL_GLOBAL_FRAME="$(ros2 param get /local_costmap/local_costmap global_frame 2>/dev/null || true)"
LOCAL_BASE_FRAME="$(ros2 param get /local_costmap/local_costmap robot_base_frame 2>/dev/null || true)"

echo "local_costmap global_frame: $LOCAL_GLOBAL_FRAME"
echo "local_costmap robot_base_frame: $LOCAL_BASE_FRAME"

if echo "$LOCAL_GLOBAL_FRAME" | grep -q "odom"; then
  echo "PASS: local_costmap global_frame uses odom"
else
  echo "FAIL: local_costmap global_frame is not odom"
  PASS=false
fi

if echo "$LOCAL_BASE_FRAME" | grep -q "base_link"; then
  echo "PASS: local_costmap robot_base_frame uses base_link"
else
  echo "FAIL: local_costmap robot_base_frame is not base_link"
  PASS=false
fi

echo ""
echo "[5] Checking global costmap frame params..."
GLOBAL_GLOBAL_FRAME="$(ros2 param get /global_costmap/global_costmap global_frame 2>/dev/null || true)"
GLOBAL_BASE_FRAME="$(ros2 param get /global_costmap/global_costmap robot_base_frame 2>/dev/null || true)"

echo "global_costmap global_frame: $GLOBAL_GLOBAL_FRAME"
echo "global_costmap robot_base_frame: $GLOBAL_BASE_FRAME"

if echo "$GLOBAL_GLOBAL_FRAME" | grep -q "odom"; then
  echo "PASS: global_costmap global_frame uses odom"
else
  echo "FAIL: global_costmap global_frame is not odom"
  PASS=false
fi

if echo "$GLOBAL_BASE_FRAME" | grep -q "base_link"; then
  echo "PASS: global_costmap robot_base_frame uses base_link"
else
  echo "FAIL: global_costmap robot_base_frame is not base_link"
  PASS=false
fi

echo ""
echo "[6] Checking odom -> base_link TF..."
timeout 6 ros2 run tf2_ros tf2_echo odom base_link >/tmp/nav2_costmap_tf_check.txt 2>/tmp/nav2_costmap_tf_error.txt || true

if grep -qi "translation\|rotation\|at time" /tmp/nav2_costmap_tf_check.txt; then
  echo "PASS: TF exists -> odom to base_link"
else
  echo "FAIL: TF missing -> odom to base_link"
  echo "tf2_echo output:"
  cat /tmp/nav2_costmap_tf_check.txt
  echo "tf2_echo errors:"
  cat /tmp/nav2_costmap_tf_error.txt
  PASS=false
fi

echo ""
echo "======================================"
if [ "$PASS" = true ]; then
  echo "NAV2 COSTMAP CHECK: PASS"
  exit 0
else
  echo "NAV2 COSTMAP CHECK: FAIL"
  exit 1
fi
