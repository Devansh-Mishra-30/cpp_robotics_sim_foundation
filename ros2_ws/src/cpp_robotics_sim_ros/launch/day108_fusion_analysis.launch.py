import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory(
        "cpp_robotics_sim_ros"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_yaml = LaunchConfiguration("map")

    base_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                package_share,
                "launch",
                "ros2_control.launch.py",
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
        }.items(),
    )

    scan_frame_bridge = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="scan_frame_bridge",
        output="screen",
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", "lidar_link",
            "--child-frame-id",
            "diffbot/base_link/diffbot_lidar",
        ],
    )

    imu_frame_bridge = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="imu_sensor_frame_transform",
        output="screen",
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", "imu_link",
            "--child-frame-id",
            "diffbot/base_link/diffbot_imu",
        ],
    )

    noisy_odom = Node(
        package="cpp_robotics_sim_ros",
        executable="noisy_odom_node.py",
        name="noisy_odom_node",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "input_topic": "/diff_drive_controller/odom",
                "output_topic": "/odom_noisy",
                "position_noise_std": 0.02,
                "yaw_noise_std": 0.02,
                "linear_velocity_noise_std": 0.02,
                "angular_velocity_noise_std": 0.02,
                "random_seed": 42,
            }
        ],
    )

    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[
            {
                "yaml_filename": map_yaml,
                "use_sim_time": use_sim_time,
            }
        ],
    )

    amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        name="amcl",
        output="screen",
        parameters=[
            os.path.join(
                package_share,
                "config",
                "amcl_params.yaml",
            ),
            {
                "use_sim_time": use_sim_time,
            },
        ],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_localization",
        output="screen",
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": [
                    "map_server",
                    "amcl",
                ],
                "bond_timeout": 0.0,
            }
        ],
    )

    ekf = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(
                package_share,
                "config",
                "day108_ekf.yaml",
            ),
            {
                "use_sim_time": use_sim_time,
            },
        ],
    )

    delayed_localization = TimerAction(
        period=10.0,
        actions=[
            scan_frame_bridge,
            imu_frame_bridge,
            noisy_odom,
            map_server,
            amcl,
            lifecycle_manager,
            ekf,
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="true",
                description="Use Gazebo simulation time",
            ),
            DeclareLaunchArgument(
                "map",
                default_value=os.path.join(
                    package_share,
                    "maps",
                    "day102_diffbot_map.yaml",
                ),
                description="Map YAML file",
            ),
            base_simulation,
            delayed_localization,
        ]
    )