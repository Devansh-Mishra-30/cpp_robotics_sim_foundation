# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    world = LaunchConfiguration('world')
    use_sim_time = LaunchConfiguration('use_sim_time')
    package_share = FindPackageShare('cpp_robotics_sim_ros')
    ros_gz_sim_share = FindPackageShare('ros_gz_sim')

    default_world_path = PathJoinSubstitution([
        package_share,
        'worlds',
        'empty_diffbot_world.sdf'
    ])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                ros_gz_sim_share,
                'launch',
                'gz_sim.launch.py'
            ])
        ),

        launch_arguments={
            'gz_args': ['-r -v 4 \"', world, '\"'],
            'on_exit_shutdown': 'true'
        }.items()
    )

    description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                package_share,
                'launch',
                'description.launch.py'
            ])
        ),

        launch_arguments={
            'use_sim_time': use_sim_time
        }.items()
    )

    spawn_diffbot = Node(
        package='ros_gz_sim',
        executable='create',
        name='spawn_diffbot',
        output='screen',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'diffbot',
            '-allow_renaming', 'true',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.20'
        ]
    )

    delayed_spawn = TimerAction(
        period=3.0,
        actions=[spawn_diffbot]
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=default_world_path,
            description='Path to Gazebo world SDF file'
        ),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use Gazebo simulation time'
        ),

        gazebo,
        description,
        delayed_spawn
    ])
