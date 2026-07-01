import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

from launch_ros.actions import Node
from launch.actions import ExecuteProcess


def generate_launch_description():
    package_share_dir = get_package_share_directory("cpp_robotics_sim_ros")
    nav2_bringup_dir = get_package_share_directory("nav2_bringup")

    ros2_control_launch = os.path.join(
        package_share_dir,
        "launch",
        "ros2_control.launch.py",
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

    robot_sim_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(ros2_control_launch),
    )

    cmd_vel_bridge = Node(
        package="cpp_robotics_sim_ros",
        executable="cmd_vel_twist_bridge.py",
        name="cmd_vel_twist_bridge",
        output="screen",
        parameters=[
            {
                "use_sim_time": True,
                "input_topic": "/cmd_vel",
                "output_topic": "/diff_drive_controller/cmd_vel",
                "frame_id": "base_link",
            }
        ],
    )

    scan_frame_bridge = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="scan_frame_bridge",
        arguments=[
            "0", "0", "0",
            "0", "0", "0",
            "lidar_link",
            "diffbot/base_link/diffbot_lidar",
        ],
        output="screen",
    )

    nav2_stack = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(nav2_launch),
        launch_arguments={
            "use_sim_time": "true",
            "params_file": nav2_params,
            "autostart": "true",
            "use_composition": "False",
        }.items(),
    )

    delayed_nav2_stack = TimerAction(
        period=10.0,
        actions=[
            cmd_vel_bridge,
            scan_frame_bridge,
            nav2_stack,
        ],
    )

    delayed_lifecycle_activation = TimerAction(
        period=22.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    "bash",
                    "-lc",
                    'ros2 service call /lifecycle_manager_navigation/manage_nodes nav2_msgs/srv/ManageLifecycleNodes "{command: 2}" || true',
                ],
                output="screen",
            )
        ],
    )

    return LaunchDescription(
        [
            robot_sim_stack,
            delayed_nav2_stack,
            delayed_lifecycle_activation,
        ]
    )