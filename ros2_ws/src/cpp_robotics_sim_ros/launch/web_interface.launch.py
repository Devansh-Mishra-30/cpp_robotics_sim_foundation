from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
)
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    websocket_port = LaunchConfiguration("websocket_port")
    dashboard_port = LaunchConfiguration("dashboard_port")

    package_share = FindPackageShare(
        "cpp_robotics_sim_ros"
    )

    dashboard_directory = PathJoinSubstitution(
        [
            package_share,
            "web",
            "dashboard",
        ]
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
            dashboard_directory,
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
            rosbridge_websocket,
            dashboard_server,
        ]
    )