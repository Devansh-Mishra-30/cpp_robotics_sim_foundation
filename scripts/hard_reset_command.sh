cd ~/robotics_projects/cpp_robotics_sim_foundation
echo "Resetting ROS 2 / Gazebo..."
pkill -f "ros2 launch" || true
pkill -f "gz sim" || true
pkill -f "ruby.*gz" || true
pkill -f "gzserver" || true
pkill -f "gzclient" || true

pkill -f "controller_manager" || true
pkill -f "spawner" || true
pkill -f "robot_state_publisher" || true
pkill -f "joint_state_publisher" || true

pkill -f "parameter_bridge" || true
pkill -f "ros_gz_bridge" || true
pkill -f "clock_bridge" || true
pkill -f "scan_bridge" || true
pkill -f "cmd_vel_twist_bridge" || true

pkill -f "controller_server" || true
pkill -f "planner_server" || true
pkill -f "bt_navigator" || true
pkill -f "behavior_server" || true
pkill -f "waypoint_follower" || true
pkill -f "velocity_smoother" || true
pkill -f "smoother_server" || true
pkill -f "route_server" || true
pkill -f "collision_monitor" || true
pkill -f "docking_server" || true
pkill -f "lifecycle_manager" || true

ros2 daemon stop
sleep 2
ros2 daemon start
sleep 2

echo "Remaining ROS nodes:"
ros2 node list
echo "Reset complete"