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
    package_share_dir = get_package_share_directory(
        'cpp_robotics_sim_ros'
    )

    default_map_path = os.path.join(
        package_share_dir,
        'maps',
        'default_diffbot_map.yaml',
    )

    amcl_params_file = os.path.join(
        package_share_dir,
        'config',
        'amcl_params.yaml',
    )

    map_yaml = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')

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

    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {
                'yaml_filename': map_yaml,
                'use_sim_time': use_sim_time,
            },
        ],
    )

    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_params_file,
            {
                'use_sim_time': use_sim_time,
            },
        ],
    )

    localization_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[
            {
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': [
                    'map_server',
                    'amcl',
                ],
                'bond_timeout': 0.0,
            },
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'map',
                default_value=default_map_path,
                description=(
                    'Absolute path to the saved map YAML file'
                ),
            ),
            DeclareLaunchArgument(
                'use_sim_time',
                default_value='true',
                description='Use Gazebo simulation time',
            ),
            scan_frame_bridge,
            map_server,
            amcl,
            localization_lifecycle_manager,
        ]
    )
