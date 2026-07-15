#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import select
import sys
import termios
import threading
import time
import tty
from typing import Dict, Optional

from geometry_msgs.msg import TwistStamped
import rclpy
from rclpy.node import Node


class KeyboardTeleopNode(Node):
    """
    Terminal keyboard teleoperation with combined-key support.

    Controls:
      W / Up Arrow       Forward
      S / Down Arrow     Reverse
      A / Left Arrow     Rotate left
      D / Right Arrow    Rotate right
      Space              Stop immediately
      Q                   Quit

    Each motion key has an independent timeout. This allows combinations
    such as W+A, W+D, S+A and S+D using normal keyboard repeat behavior.
    """

    def __init__(self) -> None:
        super().__init__('keyboard_teleop')

        self.declare_parameter(
            'output_topic',
            '/cmd_vel/keyboard',
        )
        self.declare_parameter('linear_speed', 0.15)
        self.declare_parameter('angular_speed', 0.60)
        self.declare_parameter('publish_rate', 20.0)
        self.declare_parameter('deadman_timeout', 0.30)
        self.declare_parameter('frame_id', 'base_link')

        self.output_topic = str(
            self.get_parameter('output_topic').value
        )
        self.linear_speed = float(
            self.get_parameter('linear_speed').value
        )
        self.angular_speed = float(
            self.get_parameter('angular_speed').value
        )
        self.publish_rate = float(
            self.get_parameter('publish_rate').value
        )
        self.deadman_timeout = float(
            self.get_parameter('deadman_timeout').value
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

        self.state_lock = threading.Lock()

        self.key_times: Dict[str, Optional[float]] = {
            'forward': None,
            'reverse': None,
            'left': None,
            'right': None,
        }

        self.running = True
        self.quit_requested = False

        self.stdin_fd: Optional[int] = None
        self.original_terminal_settings = None
        self.input_thread: Optional[threading.Thread] = None

        self.publish_timer = self.create_timer(
            1.0 / self.publish_rate,
            self.publish_current_command,
        )

        self.configure_terminal()
        self.start_input_thread()
        self.print_instructions()

        self.get_logger().info(
            f'Publishing keyboard commands to: {self.output_topic}'
        )
        self.get_logger().info(
            'Keyboard speeds: '
            f'linear={self.linear_speed:.3f} m/s, '
            f'angular={self.angular_speed:.3f} rad/s'
        )
        self.get_logger().info(
            f'Deadman timeout: {self.deadman_timeout:.3f} s'
        )

    def validate_parameters(self) -> None:
        if not self.output_topic:
            raise ValueError('output_topic must not be empty')

        if self.linear_speed <= 0.0:
            raise ValueError(
                'linear_speed must be greater than zero'
            )

        if self.angular_speed <= 0.0:
            raise ValueError(
                'angular_speed must be greater than zero'
            )

        if self.publish_rate <= 0.0:
            raise ValueError(
                'publish_rate must be greater than zero'
            )

        if self.deadman_timeout <= 0.0:
            raise ValueError(
                'deadman_timeout must be greater than zero'
            )

        if not self.frame_id:
            raise ValueError('frame_id must not be empty')

    def configure_terminal(self) -> None:
        if not sys.stdin.isatty():
            raise RuntimeError(
                'Keyboard teleop requires an interactive terminal.'
            )

        self.stdin_fd = sys.stdin.fileno()
        self.original_terminal_settings = termios.tcgetattr(
            self.stdin_fd
        )

        tty.setraw(self.stdin_fd)

    def restore_terminal(self) -> None:
        if (
            self.stdin_fd is not None
            and self.original_terminal_settings is not None
        ):
            termios.tcsetattr(
                self.stdin_fd,
                termios.TCSADRAIN,
                self.original_terminal_settings,
            )
            self.original_terminal_settings = None

    def start_input_thread(self) -> None:
        self.input_thread = threading.Thread(
            target=self.keyboard_input_loop,
            name='keyboard_input',
            daemon=True,
        )
        self.input_thread.start()

    def keyboard_input_loop(self) -> None:
        while self.running and rclpy.ok():
            try:
                ready, _, _ = select.select(
                    [sys.stdin],
                    [],
                    [],
                    0.05,
                )

                if not ready:
                    continue

                key = os.read(sys.stdin.fileno(), 1)

                if key == b'\x1b':
                    key += self.read_escape_sequence()

                self.handle_key(key)

            except OSError:
                if self.running:
                    self.get_logger().exception(
                        'Keyboard input failed'
                    )
                break

    @staticmethod
    def read_escape_sequence() -> bytes:
        sequence = b''

        for _ in range(2):
            ready, _, _ = select.select(
                [sys.stdin],
                [],
                [],
                0.03,
            )

            if not ready:
                break

            sequence += os.read(sys.stdin.fileno(), 1)

        return sequence

    def handle_key(self, key: bytes) -> None:
        normalized_key = key.lower()
        now = time.monotonic()

        if normalized_key in (b'w', b'\x1b[A'):
            self.record_key('forward', now)
            return

        if normalized_key in (b's', b'\x1b[B'):
            self.record_key('reverse', now)
            return

        if normalized_key in (b'a', b'\x1b[D'):
            self.record_key('left', now)
            return

        if normalized_key in (b'd', b'\x1b[C'):
            self.record_key('right', now)
            return

        if key == b' ':
            self.clear_motion_keys()
            self.publish_zero_command()
            self.get_logger().info('Keyboard stop requested')
            return

        if normalized_key == b'q':
            self.clear_motion_keys()
            self.publish_zero_command()
            self.quit_requested = True
            self.running = False

    def record_key(
        self,
        key_name: str,
        timestamp: float,
    ) -> None:
        with self.state_lock:
            self.key_times[key_name] = timestamp

    def clear_motion_keys(self) -> None:
        with self.state_lock:
            for key_name in self.key_times:
                self.key_times[key_name] = None

    def is_key_active(
        self,
        key_name: str,
        now: float,
    ) -> bool:
        timestamp = self.key_times[key_name]

        if timestamp is None:
            return False

        if now - timestamp > self.deadman_timeout:
            self.key_times[key_name] = None
            return False

        return True

    def calculate_command(
        self,
    ) -> tuple[float, float]:
        now = time.monotonic()

        with self.state_lock:
            forward = self.is_key_active('forward', now)
            reverse = self.is_key_active('reverse', now)
            left = self.is_key_active('left', now)
            right = self.is_key_active('right', now)

        linear_x = 0.0
        angular_z = 0.0

        if forward and not reverse:
            linear_x = self.linear_speed
        elif reverse and not forward:
            linear_x = -self.linear_speed

        if left and not right:
            angular_z = self.angular_speed
        elif right and not left:
            angular_z = -self.angular_speed

        return linear_x, angular_z

    def publish_current_command(self) -> None:
        if self.quit_requested:
            self.clear_motion_keys()
            self.publish_zero_command()

            if rclpy.ok():
                rclpy.shutdown()

            return

        linear_x, angular_z = self.calculate_command()

        self.publisher.publish(
            self.make_command(
                linear_x=linear_x,
                angular_z=angular_z,
            )
        )

    def publish_zero_command(self) -> None:
        self.publisher.publish(
            self.make_command(
                linear_x=0.0,
                angular_z=0.0,
            )
        )

    def make_command(
        self,
        linear_x: float,
        angular_z: float,
    ) -> TwistStamped:
        message = TwistStamped()

        message.header.stamp = (
            self.get_clock().now().to_msg()
        )
        message.header.frame_id = self.frame_id

        message.twist.linear.x = linear_x
        message.twist.angular.z = angular_z

        return message

    @staticmethod
    def print_instructions() -> None:
        instructions = """
==================================================
 Keyboard Teleoperation
==================================================
 W / Up Arrow       Move forward
 S / Down Arrow     Move backward
 A / Left Arrow     Rotate left
 D / Right Arrow    Rotate right

 Combined controls:
 W + A              Forward-left
 W + D              Forward-right
 S + A              Reverse-left
 S + D              Reverse-right

 Space              Stop immediately
 Q                  Stop and quit
==================================================
"""
        sys.stdout.write(instructions)
        sys.stdout.flush()

    def shutdown(self) -> None:
        self.running = False
        self.clear_motion_keys()
        self.publish_zero_command()

        if (
            self.input_thread is not None
            and self.input_thread.is_alive()
        ):
            self.input_thread.join(timeout=0.25)

        self.restore_terminal()


def main(args=None) -> None:
    rclpy.init(args=args)

    node: Optional[KeyboardTeleopNode] = None

    try:
        node = KeyboardTeleopNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.shutdown()
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
