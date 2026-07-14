from pathlib import Path

from ament_index_python.packages import (
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    websocket_port = LaunchConfiguration(
        "websocket_port"
    )
    dashboard_port = LaunchConfiguration(
        "dashboard_port"
    )

    package_share = Path(
        get_package_share_directory(
            "cpp_robotics_sim_ros"
        )
    )

    dashboard_directory = (
        package_share / "web" / "dashboard"
    )

    manager_config = (
        package_share
        / "config"
        / "simulation_manager.yaml"
    )

    simulation_manager = Node(
        package="cpp_robotics_sim_ros",
        executable="simulation_manager_node.py",
        name="simulation_manager",
        output="screen",
        parameters=[
            str(manager_config),
            {
                # The manager must remain responsive while
                # Gazebo and /clock are not running.
                "use_sim_time": False,
            },
        ],
    )

    mode_manager_config = (
    package_share
    / "config"
    / "mode_manager.yaml"
    )

    mode_manager = Node(
        package="cpp_robotics_sim_ros",
        executable="mode_manager_node.py",
        name="mode_manager",
        output="screen",
        parameters=[
            str(mode_manager_config),
            {
                "use_sim_time": False,
            },
        ],
    )

    rosbridge_websocket = Node(
        package="rosbridge_server",
        executable="rosbridge_websocket",
        name="rosbridge_websocket",
        output="screen",
        parameters=[
            {
                "port": websocket_port,
                "address": "0.0.0.0",
                "retry_startup_delay": 5.0,
                "fragment_timeout": 600,
                "delay_between_messages": 0.0,
                "max_message_size": 10_000_000,
                "unregister_timeout": 10.0,
                "use_compression": False,
            }
        ],
    )

    dashboard_server = ExecuteProcess(
        cmd=[
            "python3",
            "-m",
            "http.server",
            dashboard_port,
            "--bind",
            "0.0.0.0",
            "--directory",
            str(dashboard_directory),
        ],
        output="screen",
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "websocket_port",
                default_value="9090",
                description="Rosbridge WebSocket port",
            ),
            DeclareLaunchArgument(
                "dashboard_port",
                default_value="8080",
                description="Dashboard HTTP port",
            ),
            simulation_manager,
            mode_manager,
            rosbridge_websocket,
            dashboard_server,
        ]
    )
