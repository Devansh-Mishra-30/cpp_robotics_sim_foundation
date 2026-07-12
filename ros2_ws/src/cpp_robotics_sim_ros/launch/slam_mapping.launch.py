import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_share_dir = get_package_share_directory(
        "cpp_robotics_sim_ros"
    )

    ros2_control_launch = os.path.join(
        package_share_dir,
        "launch",
        "ros2_control.launch.py",
    )

    slam_params_file = os.path.join(
        package_share_dir,
        "config",
        "slam_toolbox.yaml",
    )

    robot_sim_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(ros2_control_launch),
        launch_arguments={
            "use_sim_time": "true",
        }.items(),
    )

    scan_frame_bridge = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="scan_frame_bridge",
        arguments=[
            "0",
            "0",
            "0",
            "0",
            "0",
            "0",
            "lidar_link",
            "diffbot/base_link/diffbot_lidar",
        ],
        output="screen",
    )

    slam_toolbox_node = Node(
        package="slam_toolbox",
        executable="async_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[
            slam_params_file,
            {"use_sim_time": True},
        ],
    )

    slam_lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_slam",
        output="screen",
        parameters=[
        {
            "use_sim_time": True,
            "autostart": True,
            "node_names": ["slam_toolbox"],
            "bond_timeout": 0.0,
        }
    ],
    )

    delayed_mapping_stack = TimerAction(
        period=10.0,
        actions=[
            scan_frame_bridge,
            slam_toolbox_node,
            slam_lifecycle_manager,
        ],
    )

    return LaunchDescription(
        [
            robot_sim_stack,
            delayed_mapping_stack,
        ]
    )