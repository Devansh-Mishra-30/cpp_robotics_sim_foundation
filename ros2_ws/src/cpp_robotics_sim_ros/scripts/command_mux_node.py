#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


from dataclasses import dataclass
from typing import Optional

from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


@dataclass
class CommandSource:
    name: str
    topic: str
    priority: int
    timeout: float
    latest_command: Optional[TwistStamped] = None
    last_received_time_ns: Optional[int] = None


class CommandMuxNode(Node):
    """
    Select one velocity-command source and safely forward it to the robot.

    Supported sources:
      - keyboard
      - gamepad
      - GUI
      - navigation

    Selection rules:
      1. Ignore expired sources.
      2. Select the active source with the highest priority.
      3. Clamp linear and angular velocity.
      4. Publish zero velocity when no source is active.
      5. Emergency stop overrides every source.
    """

    def __init__(self) -> None:
        super().__init__('command_mux')

        self.declare_parameter('publish_rate', 20.0)

        self.declare_parameter('max_linear_velocity', 0.30)
        self.declare_parameter('max_angular_velocity', 1.00)

        self.declare_parameter(
            'keyboard_topic',
            '/cmd_vel/keyboard',
        )
        self.declare_parameter('keyboard_priority', 90)
        self.declare_parameter('keyboard_timeout', 0.50)

        self.declare_parameter(
            'gamepad_topic',
            '/cmd_vel/gamepad',
        )
        self.declare_parameter('gamepad_priority', 100)
        self.declare_parameter('gamepad_timeout', 0.50)

        self.declare_parameter(
            'gui_topic',
            '/cmd_vel/gui',
        )
        self.declare_parameter('gui_priority', 80)
        self.declare_parameter('gui_timeout', 0.75)

        self.declare_parameter(
            'navigation_topic',
            '/cmd_vel/navigation',
        )
        self.declare_parameter('navigation_priority', 50)
        self.declare_parameter('navigation_timeout', 0.50)

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

        if self.publish_rate <= 0.0:
            raise ValueError('publish_rate must be greater than zero')

        if self.max_linear_velocity <= 0.0:
            raise ValueError(
                'max_linear_velocity must be greater than zero'
            )

        if self.max_angular_velocity <= 0.0:
            raise ValueError(
                'max_angular_velocity must be greater than zero'
            )

        self.sources = [
            self.create_source('keyboard'),
            self.create_source('gamepad'),
            self.create_source('gui'),
            self.create_source('navigation'),
        ]

        output_topic = self.get_string_parameter('output_topic')

        active_source_topic = self.get_string_parameter(
            'active_source_topic'
        )

        emergency_stop_topic = self.get_string_parameter(
            'emergency_stop_topic'
        )

        self.command_publisher = self.create_publisher(
            TwistStamped,
            output_topic,
            10,
        )

        self.active_source_publisher = self.create_publisher(
            String,
            active_source_topic,
            10,
        )

        self.emergency_stop_subscription = (
            self.create_subscription(
                Bool,
                emergency_stop_topic,
                self.emergency_stop_callback,
                10,
            )
        )

        self.source_subscriptions = []

        for source in self.sources:
            subscription = self.create_subscription(
                TwistStamped,
                source.topic,
                lambda msg, selected_source=source: (
                    self.command_callback(
                        selected_source,
                        msg,
                    )
                ),
                10,
            )

            self.source_subscriptions.append(subscription)

        self.emergency_stop_active = False
        self.last_reported_source: Optional[str] = None

        timer_period = 1.0 / self.publish_rate

        self.publish_timer = self.create_timer(
            timer_period,
            self.publish_command,
        )

        self.get_logger().info('Command multiplexer started')
        self.get_logger().info(
            f'Output topic: {output_topic}'
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

    def create_source(self, name: str) -> CommandSource:
        topic = self.get_string_parameter(f'{name}_topic')
        priority = self.get_integer_parameter(
            f'{name}_priority'
        )
        timeout = self.get_double_parameter(
            f'{name}_timeout'
        )

        if not topic:
            raise ValueError(
                f'{name}_topic must not be empty'
            )

        if timeout <= 0.0:
            raise ValueError(
                f'{name}_timeout must be greater than zero'
            )

        return CommandSource(
            name=name,
            topic=topic,
            priority=priority,
            timeout=timeout,
        )

    def command_callback(
        self,
        source: CommandSource,
        message: TwistStamped,
    ) -> None:
        source.latest_command = message
        source.last_received_time_ns = (
            self.get_clock().now().nanoseconds
        )

    def emergency_stop_callback(self, message: Bool) -> None:
        previous_state = self.emergency_stop_active
        self.emergency_stop_active = bool(message.data)

        if self.emergency_stop_active != previous_state:
            if self.emergency_stop_active:
                self.get_logger().warn(
                    'Emergency stop activated'
                )

                self.publish_zero_command()
                self.publish_active_source(
                    'emergency_stop'
                )
            else:
                self.get_logger().info(
                    'Emergency stop released'
                )

    def publish_command(self) -> None:
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
        now_ns = self.get_clock().now().nanoseconds

        active_sources = []

        for source in self.sources:
            if source.last_received_time_ns is None:
                continue

            if source.latest_command is None:
                continue

            elapsed_seconds = (
                now_ns - source.last_received_time_ns
            ) / 1e9

            if elapsed_seconds <= source.timeout:
                active_sources.append(source)

        if not active_sources:
            return None

        return max(
            active_sources,
            key=lambda source: source.priority,
        )

    def sanitize_command(
        self,
        input_command: Optional[TwistStamped],
    ) -> TwistStamped:
        output = TwistStamped()

        output.header.stamp = (
            self.get_clock().now().to_msg()
        )
        output.header.frame_id = 'base_link'

        if input_command is None:
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

        # Unsupported planar components are intentionally zeroed.
        output.twist.linear.y = 0.0
        output.twist.linear.z = 0.0
        output.twist.angular.x = 0.0
        output.twist.angular.y = 0.0

        return output

    def publish_zero_command(self) -> None:
        message = TwistStamped()

        message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        message.header.frame_id = 'base_link'

        self.command_publisher.publish(message)

    def publish_active_source(
        self,
        source_name: str,
    ) -> None:
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
            f'Control source changed: '
            f'{previous_source} -> {source_name}'
        )

        self.last_reported_source = source_name

    @staticmethod
    def clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:
        return max(minimum, min(value, maximum))

    def get_string_parameter(self, name: str) -> str:
        return (
            self.get_parameter(name)
            .get_parameter_value()
            .string_value
        )

    def get_integer_parameter(self, name: str) -> int:
        return int(
            self.get_parameter(name)
            .get_parameter_value()
            .integer_value
        )

    def get_double_parameter(self, name: str) -> float:
        return float(
            self.get_parameter(name)
            .get_parameter_value()
            .double_value
        )


def main(args=None) -> None:
    rclpy.init(args=args)

    node = CommandMuxNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_zero_command()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
