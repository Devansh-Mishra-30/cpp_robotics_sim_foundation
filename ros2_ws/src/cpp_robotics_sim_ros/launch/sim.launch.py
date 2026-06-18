from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
	sim_node=Node(
		package="cpp_robotics_sim_ros",
		executable="sim_node",
		name="sim_node",
		output="screen",
		parameters=[
			{
				"dt": 0.1,
				"initial_x": 0.0,
				"initial_y": 0.0,
				"initial_theta": 0.0,
				"cmd_timeout": 0.5,
				"max_linear_velocity": 0.5,
				"max_angular_velocity": 0.8,
			}
		],
	)
	return LaunchDescription([sim_node])
