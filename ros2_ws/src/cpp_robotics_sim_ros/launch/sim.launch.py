import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
	package_share_dir = get_package_share_directory("cpp_robotics_sim_ros")
	params_file = os.path.join(package_share_dir, "config", "sim_params.yaml")

	dt_arg = DeclareLaunchArgument(
		"dt",
		default_value="0.1",
		description="Simulation timestep in seconds",
	)

	initial_x_arg = DeclareLaunchArgument(
		"initial_x",
		default_value="0.0",
		description="Initial robot x position in meters",
	)

	initial_y_arg = DeclareLaunchArgument(
		"initial_y",
		default_value="0.0",
		description="Initial robot y position in meters",
	)

	initial_theta_arg = DeclareLaunchArgument(
		"initial_theta",
		default_value="0.0",
		description="Initial robot heading in radians",
	)

	cmd_timeout_arg = DeclareLaunchArgument(
		"cmd_timeout",
		default_value="0.5",
		description="Command timeout in seconds",
	)

	max_linear_velocity_arg = DeclareLaunchArgument(
		"max_linear_velocity",
		default_value="0.5",
		description="Maximum allowed linear velocity in m/s",
	)

	max_angular_velocity_arg = DeclareLaunchArgument(
		"max_angular_velocity",
		default_value="0.8",
		description="Maximum allowed angular velocity in rad/s",
	)

	sim_node = Node(
		package="cpp_robotics_sim_ros",
		executable="sim_node",
		name="sim_node",
		output="screen",
		parameters=[
			params_file, 
			{
				"dt": ParameterValue(LaunchConfiguration("dt"), value_type=float),
				"initial_x": ParameterValue(LaunchConfiguration("initial_x"), value_type=float),
				"initial_y": ParameterValue(LaunchConfiguration("initial_y"), value_type=float),
				"initial_theta": ParameterValue(LaunchConfiguration("initial_theta"), value_type=float),
				"cmd_timeout": ParameterValue(LaunchConfiguration("cmd_timeout"), value_type=float),
				"max_linear_velocity": ParameterValue(LaunchConfiguration("max_linear_velocity"), value_type=float),
				"max_angular_velocity": ParameterValue(LaunchConfiguration("max_angular_velocity"), value_type=float),
			},
		],
	)
	return LaunchDescription([dt_arg, initial_x_arg, initial_y_arg, initial_theta_arg, cmd_timeout_arg, max_linear_velocity_arg, max_angular_velocity_arg, sim_node])

