#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""Prioritize, validate, and forward robot velocity commands."""

from dataclasses import dataclass
import math
from typing import Optional

from geometry_msgs.msg import TwistStamped

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from std_msgs.msg import Bool, String


@dataclass
class CommandSource:
    """Store configuration and runtime state for one command source."""

    name: str
    topic: str
    priority: int
    timeout: float
    order: int
    latest_command: Optional[TwistStamped] = None
    last_received_time_ns: Optional[int] = None


class CommandMuxNode(Node):
    """Select and safely forward one active velocity-command source."""

    def __init__(self) -> None:
        """Initialize parameters, command sources, and ROS interfaces."""
        super().__init__('command_mux')

        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('max_linear_velocity', 0.30)
        self.declare_parameter('max_angular_velocity', 1.00)
        self.declare_parameter('frame_id', 'base_link')

        self.declare_source_parameters(
            name='keyboard',
            topic='/cmd_vel/keyboard',
            priority=90,
            timeout=0.50,
        )
        self.declare_source_parameters(
            name='gamepad',
            topic='/cmd_vel/gamepad',
            priority=100,
            timeout=0.50,
        )
        self.declare_source_parameters(
            name='gui',
            topic='/cmd_vel/gui',
            priority=80,
            timeout=0.75,
        )
        self.declare_source_parameters(
            name='navigation',
            topic='/cmd_vel/navigation',
            priority=50,
            timeout=0.50,
        )

        self.declare_parameter(
            'output_topic',
            '/diff_drive_controller/cmd_vel',
        )
        self.declare_parameter(
            'active_source_topic',
            '/control/active_source',
        )
        self.declare_parameter(
            'emergency_stop_topic',
            '/control/emergency_stop',
        )

        self.publish_rate = self.get_double_parameter(
            'publish_rate'
        )
        self.max_linear_velocity = self.get_double_parameter(
            'max_linear_velocity'
        )
        self.max_angular_velocity = self.get_double_parameter(
            'max_angular_velocity'
        )
        self.frame_id = self.get_string_parameter('frame_id')

        self.output_topic = self.get_string_parameter(
            'output_topic'
        )
        self.active_source_topic = self.get_string_parameter(
            'active_source_topic'
        )
        self.emergency_stop_topic = self.get_string_parameter(
            'emergency_stop_topic'
        )

        self.validate_parameters()

        self.sources = [
            self.create_source('keyboard', 0),
            self.create_source('gamepad', 1),
            self.create_source('gui', 2),
            self.create_source('navigation', 3),
        ]

        self.command_publisher = self.create_publisher(
            TwistStamped,
            self.output_topic,
            10,
        )
        self.active_source_publisher = self.create_publisher(
            String,
            self.active_source_topic,
            10,
        )
        self.emergency_stop_subscription = (
            self.create_subscription(
                Bool,
                self.emergency_stop_topic,
                self.emergency_stop_callback,
                10,
            )
        )

        self.source_subscriptions = []

        for source in self.sources:
            subscription = self.create_subscription(
                TwistStamped,
                source.topic,
                lambda message, selected_source=source: (
                    self.command_callback(
                        selected_source,
                        message,
                    )
                ),
                10,
            )
            self.source_subscriptions.append(subscription)

        self.emergency_stop_active = False
        self.last_reported_source: Optional[str] = None

        self.publish_timer = self.create_timer(
            1.0 / self.publish_rate,
            self.publish_command,
        )

        self.get_logger().info('Command multiplexer started')
        self.get_logger().info(
            f'Output topic: {self.output_topic}'
        )
        self.get_logger().info(
            'Velocity limits: '
            f'linear={self.max_linear_velocity:.3f} m/s, '
            f'angular={self.max_angular_velocity:.3f} rad/s'
        )

        for source in self.sources:
            self.get_logger().info(
                f"Source '{source.name}': "
                f'topic={source.topic}, '
                f'priority={source.priority}, '
                f'timeout={source.timeout:.3f} s'
            )

    def declare_source_parameters(
        self,
        name: str,
        topic: str,
        priority: int,
        timeout: float,
    ) -> None:
        """Declare parameters for one command source."""
        self.declare_parameter(f'{name}_topic', topic)
        self.declare_parameter(f'{name}_priority', priority)
        self.declare_parameter(f'{name}_timeout', timeout)

    def validate_parameters(self) -> None:
        """Validate shared multiplexer parameters."""
        self.require_positive_finite(
            'publish_rate',
            self.publish_rate,
        )
        self.require_positive_finite(
            'max_linear_velocity',
            self.max_linear_velocity,
        )
        self.require_positive_finite(
            'max_angular_velocity',
            self.max_angular_velocity,
        )

        required_strings = {
            'frame_id': self.frame_id,
            'output_topic': self.output_topic,
            'active_source_topic': self.active_source_topic,
            'emergency_stop_topic': self.emergency_stop_topic,
        }

        for name, value in required_strings.items():
            if not value.strip():
                raise ValueError(f'{name} must not be empty')

    def create_source(
        self,
        name: str,
        order: int,
    ) -> CommandSource:
        """Create and validate one command source."""
        topic = self.get_string_parameter(f'{name}_topic')
        priority = self.get_integer_parameter(
            f'{name}_priority'
        )
        timeout = self.get_double_parameter(
            f'{name}_timeout'
        )

        if not topic.strip():
            raise ValueError(
                f'{name}_topic must not be empty'
            )

        self.require_positive_finite(
            f'{name}_timeout',
            timeout,
        )

        return CommandSource(
            name=name,
            topic=topic,
            priority=priority,
            timeout=timeout,
            order=order,
        )

    def command_callback(
        self,
        source: CommandSource,
        message: TwistStamped,
    ) -> None:
        """Record the latest finite command for a source."""
        if not self.command_is_finite(message):
            self.get_logger().warn(
                f"Rejected non-finite command from '{source.name}'"
            )
            source.latest_command = None
            source.last_received_time_ns = None
            return

        source.latest_command = message
        source.last_received_time_ns = (
            self.get_clock().now().nanoseconds
        )

    def emergency_stop_callback(self, message: Bool) -> None:
        """Update emergency-stop state."""
        previous_state = self.emergency_stop_active
        self.emergency_stop_active = bool(message.data)

        if self.emergency_stop_active == previous_state:
            return

        if self.emergency_stop_active:
            self.get_logger().warn('Emergency stop activated')
            self.publish_zero_command()
            self.publish_active_source('emergency_stop')
        else:
            self.get_logger().info('Emergency stop released')

    def publish_command(self) -> None:
        """Publish the highest-priority active command."""
        if self.emergency_stop_active:
            self.publish_zero_command()
            self.publish_active_source('emergency_stop')
            return

        selected_source = self.select_active_source()

        if selected_source is None:
            self.publish_zero_command()
            self.publish_active_source('none')
            return

        output = self.sanitize_command(
            selected_source.latest_command
        )

        self.command_publisher.publish(output)
        self.publish_active_source(selected_source.name)

    def select_active_source(
        self,
    ) -> Optional[CommandSource]:
        """Return the highest-priority non-expired source."""
        now_ns = self.get_clock().now().nanoseconds
        active_sources = []

        for source in self.sources:
            if source.last_received_time_ns is None:
                continue

            if source.latest_command is None:
                continue

            elapsed_ns = now_ns - source.last_received_time_ns

            if elapsed_ns < 0:
                source.latest_command = None
                source.last_received_time_ns = None
                continue

            elapsed_seconds = elapsed_ns / 1e9

            if elapsed_seconds <= source.timeout:
                active_sources.append(source)

        if not active_sources:
            return None

        return max(
            active_sources,
            key=lambda source: (
                source.priority,
                -source.order,
            ),
        )

    def sanitize_command(
        self,
        input_command: Optional[TwistStamped],
    ) -> TwistStamped:
        """Clamp a command and clear unsupported components."""
        output = self.make_zero_command()

        if input_command is None:
            return output

        if not self.command_is_finite(input_command):
            return output

        output.twist.linear.x = self.clamp(
            input_command.twist.linear.x,
            -self.max_linear_velocity,
            self.max_linear_velocity,
        )
        output.twist.angular.z = self.clamp(
            input_command.twist.angular.z,
            -self.max_angular_velocity,
            self.max_angular_velocity,
        )

        return output

    def publish_zero_command(self) -> None:
        """Publish a zero-velocity command."""
        self.command_publisher.publish(
            self.make_zero_command()
        )

    def make_zero_command(self) -> TwistStamped:
        """Construct a stamped zero-velocity command."""
        message = TwistStamped()
        message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        message.header.frame_id = self.frame_id
        return message

    def publish_active_source(
        self,
        source_name: str,
    ) -> None:
        """Publish and log the selected command source."""
        message = String()
        message.data = source_name
        self.active_source_publisher.publish(message)

        if source_name == self.last_reported_source:
            return

        previous_source = (
            self.last_reported_source
            if self.last_reported_source is not None
            else 'uninitialized'
        )

        self.get_logger().info(
            'Control source changed: '
            f'{previous_source} -> {source_name}'
        )
        self.last_reported_source = source_name

    @staticmethod
    def command_is_finite(message: TwistStamped) -> bool:
        """Return whether every Twist component is finite."""
        values = (
            message.twist.linear.x,
            message.twist.linear.y,
            message.twist.linear.z,
            message.twist.angular.x,
            message.twist.angular.y,
            message.twist.angular.z,
        )

        return all(math.isfinite(value) for value in values)

    @staticmethod
    def clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        """Clamp a finite value to inclusive bounds."""
        return max(minimum, min(value, maximum))

    @staticmethod
    def require_positive_finite(
        name: str,
        value: float,
    ) -> None:
        """Require a finite numeric value greater than zero."""
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(
                f'{name} must be finite and greater than zero'
            )

    def get_string_parameter(self, name: str) -> str:
        """Read a string parameter."""
        return str(self.get_parameter(name).value)

    def get_integer_parameter(self, name: str) -> int:
        """Read an integer parameter."""
        return int(self.get_parameter(name).value)

    def get_double_parameter(self, name: str) -> float:
        """Read a floating-point parameter."""
        return float(self.get_parameter(name).value)


def main(args=None) -> None:
    """Run the command multiplexer node."""
    rclpy.init(args=args)

    node: Optional[CommandMuxNode] = None

    try:
        node = CommandMuxNode()
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
