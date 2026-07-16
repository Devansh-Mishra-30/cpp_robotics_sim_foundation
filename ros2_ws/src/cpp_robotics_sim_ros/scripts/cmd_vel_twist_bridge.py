#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""Bridge ROS 2 Twist commands to stamped controller commands."""

import math
from typing import Optional

from geometry_msgs.msg import Twist, TwistStamped

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node


class CmdVelTwistBridge(Node):
    """Convert unstamped velocity commands into TwistStamped commands."""

    def __init__(self) -> None:
        """Initialize parameters and ROS interfaces."""
        super().__init__('cmd_vel_twist_bridge')

        self.declare_parameter('input_topic', '/cmd_vel')
        self.declare_parameter(
            'output_topic',
            '/diff_drive_controller/cmd_vel',
        )
        self.declare_parameter('frame_id', 'base_link')

        self.input_topic = str(
            self.get_parameter('input_topic').value
        )
        self.output_topic = str(
            self.get_parameter('output_topic').value
        )
        self.frame_id = str(
            self.get_parameter('frame_id').value
        )

        self.validate_parameters()

        self.publisher = self.create_publisher(
            TwistStamped,
            self.output_topic,
            10,
        )

        self.subscription = self.create_subscription(
            Twist,
            self.input_topic,
            self.cmd_callback,
            10,
        )

        self.get_logger().info(
            'Velocity bridge started: '
            f'{self.input_topic} Twist -> '
            f'{self.output_topic} TwistStamped'
        )

    def validate_parameters(self) -> None:
        """Validate required topic and frame parameters."""
        if not self.input_topic.strip():
            raise ValueError('input_topic must not be empty')

        if not self.output_topic.strip():
            raise ValueError('output_topic must not be empty')

        if not self.frame_id.strip():
            raise ValueError('frame_id must not be empty')

        if self.input_topic == self.output_topic:
            raise ValueError(
                'input_topic and output_topic must be different'
            )

    def cmd_callback(self, message: Twist) -> None:
        """Stamp and forward a finite planar velocity command."""
        if not self.command_is_finite(message):
            self.get_logger().warn(
                'Rejected non-finite velocity command'
            )
            self.publish_zero_command()
            return

        stamped_message = TwistStamped()
        stamped_message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        stamped_message.header.frame_id = self.frame_id
        stamped_message.twist = message

        self.publisher.publish(stamped_message)

    @staticmethod
    def command_is_finite(message: Twist) -> bool:
        """Return whether every Twist component is finite."""
        values = (
            message.linear.x,
            message.linear.y,
            message.linear.z,
            message.angular.x,
            message.angular.y,
            message.angular.z,
        )

        return all(math.isfinite(value) for value in values)

    def publish_zero_command(self) -> None:
        """Publish a stamped zero-velocity command."""
        message = TwistStamped()
        message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        message.header.frame_id = self.frame_id

        self.publisher.publish(message)


def main(args=None) -> None:
    """Run the velocity bridge node."""
    rclpy.init(args=args)

    node: Optional[CmdVelTwistBridge] = None

    try:
        node = CmdVelTwistBridge()
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                node.publish_zero_command()

            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
