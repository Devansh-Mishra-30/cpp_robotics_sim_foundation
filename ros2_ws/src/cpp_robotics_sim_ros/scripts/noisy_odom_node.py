#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""Publish a configurable noisy odometry stream for validation."""

import copy
import math
import random
from typing import Optional

from geometry_msgs.msg import Quaternion

from nav_msgs.msg import Odometry

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


def yaw_from_quaternion(quaternion: Quaternion) -> float:
    """Extract planar yaw from a quaternion."""
    siny_cosp = 2.0 * (
        quaternion.w * quaternion.z
        + quaternion.x * quaternion.y
    )
    cosy_cosp = 1.0 - 2.0 * (
        quaternion.y * quaternion.y
        + quaternion.z * quaternion.z
    )
    return math.atan2(siny_cosp, cosy_cosp)


def quaternion_from_yaw(yaw: float) -> Quaternion:
    """Create a quaternion representing planar yaw."""
    quaternion = Quaternion()
    quaternion.z = math.sin(yaw * 0.5)
    quaternion.w = math.cos(yaw * 0.5)
    return quaternion


def wrap_angle(angle: float) -> float:
    """Wrap a finite angle to the interval [-pi, pi]."""
    if not math.isfinite(angle):
        raise ValueError('angle must be finite')

    return math.atan2(
        math.sin(angle),
        math.cos(angle),
    )


class NoisyOdomNode(Node):
    """Add configurable Gaussian noise to planar odometry."""

    def __init__(self) -> None:
        """Initialize noise parameters and ROS interfaces."""
        super().__init__('noisy_odom_node')

        self.declare_parameter(
            'input_topic',
            '/diff_drive_controller/odom',
        )
        self.declare_parameter(
            'output_topic',
            '/odom_noisy',
        )

        self.declare_parameter('position_noise_std', 0.02)
        self.declare_parameter('yaw_noise_std', 0.02)
        self.declare_parameter(
            'linear_velocity_noise_std',
            0.02,
        )
        self.declare_parameter(
            'angular_velocity_noise_std',
            0.02,
        )
        self.declare_parameter('random_seed', 42)

        self.input_topic = str(
            self.get_parameter('input_topic').value
        )
        self.output_topic = str(
            self.get_parameter('output_topic').value
        )
        self.position_noise_std = float(
            self.get_parameter('position_noise_std').value
        )
        self.yaw_noise_std = float(
            self.get_parameter('yaw_noise_std').value
        )
        self.linear_velocity_noise_std = float(
            self.get_parameter(
                'linear_velocity_noise_std'
            ).value
        )
        self.angular_velocity_noise_std = float(
            self.get_parameter(
                'angular_velocity_noise_std'
            ).value
        )
        self.random_seed = int(
            self.get_parameter('random_seed').value
        )

        self.validate_parameters()

        if self.random_seed < 0:
            self.rng = random.Random()
        else:
            self.rng = random.Random(self.random_seed)

        self.odom_publisher = self.create_publisher(
            Odometry,
            self.output_topic,
            10,
        )
        self.odom_subscription = self.create_subscription(
            Odometry,
            self.input_topic,
            self.odom_callback,
            10,
        )

        self.get_logger().info('Noisy odometry node started')
        self.get_logger().info(
            f'Subscribing: {self.input_topic}'
        )
        self.get_logger().info(
            f'Publishing: {self.output_topic}'
        )
        self.get_logger().info(
            'Noise standard deviations: '
            f'position={self.position_noise_std:.4f} m, '
            f'yaw={self.yaw_noise_std:.4f} rad, '
            'linear_velocity='
            f'{self.linear_velocity_noise_std:.4f} m/s, '
            'angular_velocity='
            f'{self.angular_velocity_noise_std:.4f} rad/s'
        )

    def validate_parameters(self) -> None:
        """Validate topic names and Gaussian noise parameters."""
        if not self.input_topic.strip():
            raise ValueError('input_topic must not be empty')

        if not self.output_topic.strip():
            raise ValueError('output_topic must not be empty')

        if self.input_topic == self.output_topic:
            raise ValueError(
                'input_topic and output_topic must be different'
            )

        noise_parameters = {
            'position_noise_std':
                self.position_noise_std,
            'yaw_noise_std':
                self.yaw_noise_std,
            'linear_velocity_noise_std':
                self.linear_velocity_noise_std,
            'angular_velocity_noise_std':
                self.angular_velocity_noise_std,
        }

        for name, value in noise_parameters.items():
            self.require_nonnegative_finite(name, value)

    @staticmethod
    def require_nonnegative_finite(
        name: str,
        value: float,
    ) -> None:
        """Require a finite numeric value greater than or equal to zero."""
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(
                f'{name} must be finite and nonnegative'
            )

    def odom_callback(self, message: Odometry) -> None:
        """Publish a noisy copy of one finite odometry message."""
        if not self.odometry_is_finite(message):
            self.get_logger().warn(
                'Rejected non-finite odometry input'
            )
            return

        noisy_message = copy.deepcopy(message)

        x_noise = self.rng.gauss(
            0.0,
            self.position_noise_std,
        )
        y_noise = self.rng.gauss(
            0.0,
            self.position_noise_std,
        )
        yaw_noise = self.rng.gauss(
            0.0,
            self.yaw_noise_std,
        )
        linear_velocity_noise = self.rng.gauss(
            0.0,
            self.linear_velocity_noise_std,
        )
        angular_velocity_noise = self.rng.gauss(
            0.0,
            self.angular_velocity_noise_std,
        )

        actual_yaw = yaw_from_quaternion(
            message.pose.pose.orientation
        )
        noisy_yaw = wrap_angle(
            actual_yaw + yaw_noise
        )

        noisy_message.pose.pose.position.x = (
            message.pose.pose.position.x
            + x_noise
        )
        noisy_message.pose.pose.position.y = (
            message.pose.pose.position.y
            + y_noise
        )
        noisy_message.pose.pose.orientation = (
            quaternion_from_yaw(noisy_yaw)
        )

        noisy_message.twist.twist.linear.x = (
            message.twist.twist.linear.x
            + linear_velocity_noise
        )
        noisy_message.twist.twist.angular.z = (
            message.twist.twist.angular.z
            + angular_velocity_noise
        )

        self.set_covariance(noisy_message)
        self.odom_publisher.publish(noisy_message)

    @staticmethod
    def odometry_is_finite(message: Odometry) -> bool:
        """Return whether the planar odometry fields are finite."""
        orientation = message.pose.pose.orientation

        values = (
            message.pose.pose.position.x,
            message.pose.pose.position.y,
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w,
            message.twist.twist.linear.x,
            message.twist.twist.angular.z,
        )

        return all(
            math.isfinite(value)
            for value in values
        )

    def set_covariance(
        self,
        message: Odometry,
    ) -> None:
        """Set diagonal covariance from configured noise variances."""
        position_variance = (
            self.position_noise_std ** 2
        )
        yaw_variance = self.yaw_noise_std ** 2
        linear_velocity_variance = (
            self.linear_velocity_noise_std ** 2
        )
        angular_velocity_variance = (
            self.angular_velocity_noise_std ** 2
        )

        pose_covariance = [0.0] * 36
        twist_covariance = [0.0] * 36

        pose_covariance[0] = position_variance
        pose_covariance[7] = position_variance
        pose_covariance[14] = 1.0
        pose_covariance[21] = 1.0
        pose_covariance[28] = 1.0
        pose_covariance[35] = yaw_variance

        twist_covariance[0] = (
            linear_velocity_variance
        )
        twist_covariance[7] = 1.0
        twist_covariance[14] = 1.0
        twist_covariance[21] = 1.0
        twist_covariance[28] = 1.0
        twist_covariance[35] = (
            angular_velocity_variance
        )

        message.pose.covariance = pose_covariance
        message.twist.covariance = twist_covariance


def main(args=None) -> None:
    """Run the noisy odometry node."""
    rclpy.init(args=args)

    node: Optional[NoisyOdomNode] = None

    try:
        node = NoisyOdomNode()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
