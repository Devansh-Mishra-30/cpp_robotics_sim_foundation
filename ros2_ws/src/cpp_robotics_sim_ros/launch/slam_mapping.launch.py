# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os

from ament_index_python.packages import (
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration(
        'use_sim_time'
    )

    package_share_dir = get_package_share_directory(
        'cpp_robotics_sim_ros'
    )

    slam_params_file = os.path.join(
        package_share_dir,
        'config',
        'slam_toolbox.yaml',
    )

    scan_frame_bridge = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='scan_frame_bridge',
        arguments=[
            '0',
            '0',
            '0',
            '0',
            '0',
            '0',
            'lidar_link',
            'diffbot/base_link/diffbot_lidar',
        ],
        output='screen',
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_file,
            {
                'use_sim_time': use_sim_time,
            },
        ],
    )

    slam_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_slam',
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': [
                    'slam_toolbox',
                ],
                'bond_timeout': 0.0,
            },
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                description=(
                    'Use the simulation clock'
                ),
            ),
            scan_frame_bridge,
            slam_toolbox_node,
            slam_lifecycle_manager,
        ]
    )
