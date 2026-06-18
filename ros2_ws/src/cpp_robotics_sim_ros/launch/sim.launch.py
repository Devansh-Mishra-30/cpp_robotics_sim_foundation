import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
	package_share_dir = get_package_share_directory("cpp_robotics_sim_ros")
	params_file = os.path.join(package_share_dir, "config", "sim_params.yaml")

	sim_node = Node(
		package="cpp_robotics_sim_ros",
		executable="sim_node",
		name="sim_node",
		output="screen",
		parameters=[params_file],
	)
	return LaunchDescription([sim_node])

