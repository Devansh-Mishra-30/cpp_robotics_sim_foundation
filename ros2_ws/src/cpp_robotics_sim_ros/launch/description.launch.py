from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    model = LaunchConfiguration("model")
    use_sim_time = LaunchConfiguration("use_sim_time")

    default_model_path = PathJoinSubstitution([
        FindPackageShare("cpp_robotics_sim_ros"),
        "xacro",
        "diffbot.xacro"
    ])

    robot_description_content = Command(['xacro "', model, '"'])

    robot_description = {
        "robot_description": ParameterValue(
            robot_description_content,
            value_type=str
        )
    }

    robot_state_publisher_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        output="screen",
        parameters=[
            robot_description,
            {"use_sim_time": use_sim_time}
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "model",
            default_value=default_model_path,
            description="Absolute path to robot Xacro/URDF model file"
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="false",
            description="Use simulation time if true"
        ),
        robot_state_publisher_node
    ])