import os

from ament_index_python.packages import (
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import (
    PythonLaunchDescriptionSource,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration(
        "use_sim_time"
    )

    package_share_dir = get_package_share_directory(
        "cpp_robotics_sim_ros"
    )
    nav2_bringup_dir = get_package_share_directory(
        "nav2_bringup"
    )

    nav2_launch = os.path.join(
        nav2_bringup_dir,
        "launch",
        "navigation_launch.py",
    )

    nav2_params = os.path.join(
        package_share_dir,
        "nav2",
        "diffbot_nav2_params.yaml",
    )

    cmd_vel_bridge = Node(
        package="cpp_robotics_sim_ros",
        executable="cmd_vel_twist_bridge.py",
        name="cmd_vel_twist_bridge",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "input_topic": "/cmd_vel",
                "output_topic": "/cmd_vel/navigation",
                "frame_id": "base_link",
            },
        ],
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

    nav2_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            nav2_launch
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "params_file": nav2_params,
            "autostart": "true",
            "use_composition": "False",
        }.items(),
    )

    delayed_nav2_stack = TimerAction(
        period=3.0,
        actions=[
            cmd_vel_bridge,
            scan_frame_bridge,
            nav2_stack,
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time",
            ),
            delayed_nav2_stack,
        ]
    )
