from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    world = LaunchConfiguration("world")
    use_sim_time = LaunchConfiguration("use_sim_time")

    package_share = FindPackageShare("cpp_robotics_sim_ros")
    ros_gz_sim_share = FindPackageShare("ros_gz_sim")

    default_world_path = PathJoinSubstitution([
        package_share,
        "worlds",
        "empty_diffbot_world.sdf"
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                ros_gz_sim_share,
                "launch",
                "gz_sim.launch.py"
            ])
        ),
        launch_arguments={
            "gz_args": ["-r -v 4 \"", world, "\""],
            "on_exit_shutdown": "true"
        }.items()
    )

    clock_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="clock_bridge",
        output="screen",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock"
        ]
    )

    scan_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="scan_bridge",
        output="screen",
        arguments=[
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan"
        ],
        parameters=[
            {"use_sim_time": use_sim_time}
        ]
    )

    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                package_share,
                "launch",
                "description.launch.py"
            ])
        ),
        launch_arguments={
            "use_sim_time": use_sim_time
        }.items()
    )

    spawn_diffbot = Node(
        package="ros_gz_sim",
        executable="create",
        name="spawn_diffbot",
        output="screen",
        arguments=[
            "-topic", "robot_description",
            "-name", "diffbot",
            "-allow_renaming", "false",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.20"
        ]
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="joint_state_broadcaster_spawner",
        output="screen",
        arguments=[
            "joint_state_broadcaster",
            "--controller-manager",
            "/controller_manager"
        ]
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        name="diff_drive_controller_spawner",
        output="screen",
        arguments=[
            "diff_drive_controller",
            "--controller-manager",
            "/controller_manager"
        ]
    )

    delayed_diff_drive_controller = TimerAction(
        period=8.0,
        actions=[diff_drive_controller_spawner]
    )

    delayed_spawn = TimerAction(
        period=3.0,
        actions=[spawn_diffbot]
    )

    delayed_joint_state_broadcaster = TimerAction(
        period=6.0,
        actions=[joint_state_broadcaster_spawner]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "world",
            default_value=default_world_path,
            description="Path to Gazebo world SDF file"
        ),
        DeclareLaunchArgument(
            "use_sim_time",
            default_value="true",
            description="Use Gazebo simulation time"
        ),
        gazebo,
        clock_bridge,
        scan_bridge,
        description,
        delayed_spawn,
        delayed_joint_state_broadcaster,
        delayed_diff_drive_controller
    ])