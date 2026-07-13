from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    websocket_port = LaunchConfiguration("websocket_port")

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

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "websocket_port",
                default_value="9090",
                description="TCP port used by rosbridge WebSocket server",
            ),
            rosbridge_websocket,
        ]
    )
