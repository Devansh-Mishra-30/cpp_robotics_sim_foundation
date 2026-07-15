#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import json
import math
from pathlib import Path
import re
from typing import Optional

from geometry_msgs.msg import PoseWithCovarianceStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from std_msgs.msg import String


class LocalizationManagerNode(Node):
    """
    Manage saved-map selection and AMCL initial-pose requests.

    Inputs:
        /localization/select_map_request
        /localization/initial_pose_request

    Outputs:
        /localization/selected_map
        /localization/status
        /initialpose
    """

    MAP_NAME_PATTERN = re.compile(
        r'^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$'
    )

    def __init__(self) -> None:
        super().__init__('localization_manager')

        self.declare_parameter(
            'map_directory',
            str(
                Path.home()
                / '.ros'
                / 'cpp_robotics_sim'
                / 'maps'
            ),
        )
        self.declare_parameter(
            'position_covariance',
            0.25,
        )
        self.declare_parameter(
            'yaw_covariance',
            0.06853891945200942,
        )

        self.map_directory = Path(
            str(
                self.get_parameter(
                    'map_directory'
                ).value
            )
        ).expanduser()

        self.position_covariance = float(
            self.get_parameter(
                'position_covariance'
            ).value
        )
        self.yaw_covariance = float(
            self.get_parameter(
                'yaw_covariance'
            ).value
        )

        self.validate_parameters()

        transient_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.selected_map_publisher = (
            self.create_publisher(
                String,
                '/localization/selected_map',
                transient_qos,
            )
        )

        self.status_publisher = self.create_publisher(
            String,
            '/localization/status',
            transient_qos,
        )

        self.initial_pose_publisher = (
            self.create_publisher(
                PoseWithCovarianceStamped,
                '/initialpose',
                10,
            )
        )

        self.select_map_subscription = (
            self.create_subscription(
                String,
                '/localization/select_map_request',
                self.select_map_callback,
                10,
            )
        )

        self.initial_pose_subscription = (
            self.create_subscription(
                String,
                '/localization/initial_pose_request',
                self.initial_pose_callback,
                10,
            )
        )

        self.mode_subscription = self.create_subscription(
            String,
            '/mode/status',
            self.mode_status_callback,
            transient_qos,
        )

        self.simulation_subscription = (
            self.create_subscription(
                String,
                '/simulation/status',
                self.simulation_status_callback,
                transient_qos,
            )
        )

        self.environment_subscription = (
            self.create_subscription(
                String,
                '/simulation/environment_status',
                self.environment_status_callback,
                transient_qos,
            )
        )

        self.selected_map_name = ''
        self.selected_map_path = ''
        self.selected_map_environment = ''
        self.selected_environment = ''
        self.mode_state = 'stopped'
        self.simulation_state = 'stopped'

        self.publish_status(
            status='ready',
            message='Localization manager ready',
        )

        self.publish_selected_map()

        self.get_logger().info(
            'Localization manager ready'
        )

    def validate_parameters(self) -> None:
        if self.position_covariance <= 0.0:
            raise ValueError(
                'position_covariance must be positive'
            )

        if self.yaw_covariance <= 0.0:
            raise ValueError(
                'yaw_covariance must be positive'
            )

    def mode_status_callback(
        self,
        message: String,
    ) -> None:
        self.mode_state = message.data

    def simulation_status_callback(
        self,
        message: String,
    ) -> None:
        self.simulation_state = message.data

    def environment_status_callback(
        self,
        message: String,
    ) -> None:
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            self.get_logger().warning(
                'Ignoring malformed environment status'
            )
            return

        environment = str(
            payload.get(
                'selected_environment',
                '',
            )
        ).strip().lower()

        if not environment:
            return

        environment_changed = (
            self.selected_environment
            and environment
            != self.selected_environment
        )

        self.selected_environment = environment

        if (
            environment_changed
            and self.selected_map_environment
            not in ('', 'legacy', environment)
        ):
            self.selected_map_name = ''
            self.selected_map_path = ''
            self.selected_map_environment = ''

            self.publish_selected_map()

            self.publish_status(
                status='ready',
                message=(
                    'Selected map cleared because the '
                    'simulation environment changed'
                ),
            )

    @staticmethod
    def resolve_path_within_root(
        root_directory: Path,
        *path_parts: str,
    ) -> Path:
        resolved_root = root_directory.expanduser().resolve()

        candidate_path = resolved_root.joinpath(
            *path_parts
        ).resolve()

        try:
            candidate_path.relative_to(resolved_root)
        except ValueError as error:
            raise ValueError(
                'Resolved map path escapes the configured '
                'map directory'
            ) from error

        return candidate_path

    def parse_map_request(
        self,
        raw_request: str,
    ) -> tuple[str, str]:
        raw_request = raw_request.strip()

        if raw_request.startswith('{'):
            payload = json.loads(raw_request)

            map_name = str(
                payload.get('name', '')
            ).strip()

            environment = str(
                payload.get(
                    'environment',
                    self.selected_environment,
                )
            ).strip().lower()

            return map_name, environment

        return raw_request, self.selected_environment

    def select_map_callback(
        self,
        message: String,
    ) -> None:
        try:
            map_name, environment = (
                self.parse_map_request(message.data)
            )
        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            self.publish_status(
                status='error',
                message='Invalid map-selection request',
            )
            return

        if not self.MAP_NAME_PATTERN.fullmatch(
            map_name
        ):
            self.publish_status(
                status='error',
                message=(
                    'Invalid map name. Use letters, '
                    'numbers, underscores, or hyphens.'
                ),
            )
            return

        try:
            environment_yaml_path = (
                self.resolve_path_within_root(
                    self.map_directory,
                    environment,
                    f'{map_name}.yaml',
                )
            )

            legacy_yaml_path = (
                self.resolve_path_within_root(
                    self.map_directory,
                    f'{map_name}.yaml',
                )
            )

        except ValueError:
            self.publish_status(
                status='error',
                message=(
                    'Invalid map path. The requested map '
                    'must remain inside the configured '
                    'map directory.'
                ),
                map_name=map_name,
            )
            return

        if environment_yaml_path.is_file():
            yaml_path = environment_yaml_path
            map_environment = environment
        elif legacy_yaml_path.is_file():
            yaml_path = legacy_yaml_path
            map_environment = 'legacy'
        else:
            yaml_path = environment_yaml_path
            map_environment = environment

        image_path = yaml_path.with_suffix('.pgm')

        if not yaml_path.is_file():
            self.publish_status(
                status='error',
                message=(
                    f'Map YAML does not exist: '
                    f'{yaml_path}'
                ),
                map_name=map_name,
            )
            return

        if not image_path.is_file():
            self.publish_status(
                status='error',
                message=(
                    f'Map image does not exist: '
                    f'{image_path}'
                ),
                map_name=map_name,
            )
            return

        self.selected_map_name = map_name
        self.selected_map_path = str(
            yaml_path.resolve()
        )
        self.selected_map_environment = (
            map_environment
        )

        self.publish_selected_map()

        self.publish_status(
            status='success',
            message=(
                f"Map '{map_name}' selected for "
                f'{self.selected_map_environment}'
            ),
            map_name=map_name,
            environment=(
                self.selected_map_environment
            ),
            yaml_path=self.selected_map_path,
        )

        self.get_logger().info(
            f'Selected map: {self.selected_map_path}'
        )

    def initial_pose_callback(
        self,
        message: String,
    ) -> None:
        if self.simulation_state != 'running':
            self.publish_status(
                status='error',
                message=(
                    'Simulation must be running before '
                    'setting the initial pose'
                ),
            )
            return

        if self.mode_state not in (
            'localization',
            'navigation',
        ):
            self.publish_status(
                status='error',
                message=(
                    'Localization or Navigation mode '
                    'must be active'
                ),
            )
            return

        if not self.selected_map_path:
            self.publish_status(
                status='error',
                message=(
                    'Select a saved map before setting '
                    'the initial pose'
                ),
            )
            return

        try:
            payload = json.loads(message.data)

            x = float(payload['x'])
            y = float(payload['y'])
            yaw = float(payload['yaw'])

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ):
            self.publish_status(
                status='error',
                message=(
                    'Initial pose must contain numeric '
                    'x, y, and yaw values'
                ),
            )
            return

        if not all(
            math.isfinite(value)
            for value in (x, y, yaw)
        ):
            self.publish_status(
                status='error',
                message=(
                    'Initial pose values must be finite'
                ),
            )
            return

        pose_message = PoseWithCovarianceStamped()

        pose_message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        pose_message.header.frame_id = 'map'

        pose_message.pose.pose.position.x = x
        pose_message.pose.pose.position.y = y
        pose_message.pose.pose.position.z = 0.0

        half_yaw = yaw * 0.5

        pose_message.pose.pose.orientation.z = (
            math.sin(half_yaw)
        )
        pose_message.pose.pose.orientation.w = (
            math.cos(half_yaw)
        )

        covariance = [0.0] * 36
        covariance[0] = self.position_covariance
        covariance[7] = self.position_covariance
        covariance[35] = self.yaw_covariance

        pose_message.pose.covariance = covariance

        self.initial_pose_publisher.publish(
            pose_message
        )

        self.publish_status(
            status='success',
            message=(
                'Initial pose published: '
                f'x={x:.2f}, y={y:.2f}, '
                f'yaw={yaw:.2f} rad'
            ),
            map_name=self.selected_map_name,
            yaml_path=self.selected_map_path,
        )

        self.get_logger().info(
            'Published AMCL initial pose: '
            f'x={x:.3f}, y={y:.3f}, '
            f'yaw={yaw:.3f}'
        )

    def publish_selected_map(self) -> None:
        payload = {
            'name': self.selected_map_name,
            'environment': (
                self.selected_map_environment
            ),
            'yaml_path': self.selected_map_path,
        }

        message = String()
        message.data = json.dumps(payload)

        if not rclpy.ok(context=self.context):
            return

        self.selected_map_publisher.publish(
            message
        )

    def publish_status(
        self,
        status: str,
        message: str,
        map_name: str = '',
        environment: str = '',
        yaml_path: str = '',
    ) -> None:
        payload = {
            'status': status,
            'message': message,
            'map_name': map_name,
            'environment': environment,
            'yaml_path': yaml_path,
        }

        ros_message = String()
        ros_message.data = json.dumps(payload)

        if not rclpy.ok(context=self.context):
            return

        self.status_publisher.publish(
            ros_message
        )


def main(args=None) -> None:
    rclpy.init(args=args)

    node: Optional[LocalizationManagerNode] = None

    try:
        node = LocalizationManagerNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
