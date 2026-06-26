
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    rviz_config = LaunchConfiguration("rviz_config")
    package_share = FindPackageShare("cpp_robotics_sim_ros")

    default_rviz_config_path = PathJoinSubstitution([
        package_share,
        "rviz",
        "diffbot_robot_model.rviz"
    ])

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                package_share,
                "launch",
                "sim.launch.py"
            ])
        )
    )



    description_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                package_share,
                "launch",
                "description.launch.py"
            ])
        )
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "rviz_config",
            default_value=default_rviz_config_path,
            description="Path to RViz config file"
        ),

        sim_launch,
        description_launch,
        rviz_node
    ])

