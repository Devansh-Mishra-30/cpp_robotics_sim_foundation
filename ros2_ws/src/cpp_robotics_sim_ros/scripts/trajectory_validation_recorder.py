#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import csv
import math
from pathlib import Path

from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node

CSV_COLUMNS = [
    'time_sec',
    'cmd_linear_x',
    'cmd_angular_z',
    'actual_x',
    'actual_y',
    'actual_yaw',
    'actual_linear_x',
    'actual_angular_z',
    'noisy_x',
    'noisy_y',
    'noisy_yaw',
]


def find_repo_root():
    cwd = Path.cwd().resolve()

    for path in [cwd] + list(cwd.parents):
        if (path / 'ros2_ws' / 'src' / 'cpp_robotics_sim_ros').exists():
            return path

        if path.name == 'ros2_ws' and (path / 'src' / 'cpp_robotics_sim_ros').exists():
            return path.parent

    return cwd


def resolve_repo_path(path_text):
    path = Path(path_text).expanduser()

    if path.is_absolute():
        return path

    return find_repo_root() / path


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def stamp_to_sec(header):
    stamp_sec = float(header.stamp.sec)
    stamp_nanosec = float(header.stamp.nanosec) * 1e-9
    value = stamp_sec + stamp_nanosec

    if value <= 0.0:
        return None

    return value


class TrajectoryValidationRecorder(Node):
    def __init__(self):
        super().__init__('trajectory_validation_recorder')

        self.declare_parameter('cmd_topic', '/diff_drive_controller/cmd_vel')
        self.declare_parameter('actual_odom_topic', '/diff_drive_controller/odom')
        self.declare_parameter('noisy_odom_topic', '/odom_noisy')
        self.declare_parameter('output_csv', 'data/trajectory_validation.csv')
        self.declare_parameter('sample_rate_hz', 20.0)

        self.cmd_topic = self.get_parameter('cmd_topic').value
        self.actual_odom_topic = self.get_parameter('actual_odom_topic').value
        self.noisy_odom_topic = self.get_parameter('noisy_odom_topic').value
        self.output_csv = resolve_repo_path(self.get_parameter('output_csv').value)
        self.sample_rate_hz = float(self.get_parameter('sample_rate_hz').value)

        self.latest_cmd = {
            'linear_x': 0.0,
            'angular_z': 0.0,
        }

        self.latest_actual = None
        self.latest_noisy = None
        self.start_time_sec = None
        self.rows_written = 0

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.output_csv.open('w', newline='')
        self.writer = csv.DictWriter(self.csv_file, fieldnames=CSV_COLUMNS)
        self.writer.writeheader()
        self.csv_file.flush()

        self.cmd_sub = self.create_subscription(
            TwistStamped,
            self.cmd_topic,
            self.cmd_callback,
            10
        )

        self.actual_odom_sub = self.create_subscription(
            Odometry,
            self.actual_odom_topic,
            self.actual_odom_callback,
            10
        )

        self.noisy_odom_sub = self.create_subscription(
            Odometry,
            self.noisy_odom_topic,
            self.noisy_odom_callback,
            10
        )

        timer_period = 1.0 / self.sample_rate_hz
        self.timer = self.create_timer(timer_period, self.write_sample)

        self.get_logger().info('Trajectory validation recorder started')
        self.get_logger().info(f'Command topic:     {self.cmd_topic}')
        self.get_logger().info(f'Actual odom topic: {self.actual_odom_topic}')
        self.get_logger().info(f'Noisy odom topic:  {self.noisy_odom_topic}')
        self.get_logger().info(f'Writing CSV:       {self.output_csv}')
        self.get_logger().info(f'Sample rate:       {self.sample_rate_hz:.1f} Hz')

    def cmd_callback(self, msg):
        self.latest_cmd['linear_x'] = float(msg.twist.linear.x)
        self.latest_cmd['angular_z'] = float(msg.twist.angular.z)

    def actual_odom_callback(self, msg):
        stamp_sec = stamp_to_sec(msg.header)

        if stamp_sec is None:
            stamp_sec = self.get_clock().now().nanoseconds * 1e-9

        self.latest_actual = {
            'stamp_sec': stamp_sec,
            'x': float(msg.pose.pose.position.x),
            'y': float(msg.pose.pose.position.y),
            'yaw': yaw_from_quaternion(msg.pose.pose.orientation),
            'linear_x': float(msg.twist.twist.linear.x),
            'angular_z': float(msg.twist.twist.angular.z),
        }

    def noisy_odom_callback(self, msg):
        self.latest_noisy = {
            'x': float(msg.pose.pose.position.x),
            'y': float(msg.pose.pose.position.y),
            'yaw': yaw_from_quaternion(msg.pose.pose.orientation),
        }

    def write_sample(self):
        if self.latest_actual is None:
            return

        if self.start_time_sec is None:
            self.start_time_sec = self.latest_actual['stamp_sec']

        time_sec = self.latest_actual['stamp_sec'] - self.start_time_sec

        row = {
            'time_sec': f'{time_sec:.6f}',
            'cmd_linear_x': f'{self.latest_cmd["linear_x"]:.6f}',
            'cmd_angular_z': f'{self.latest_cmd["angular_z"]:.6f}',
            'actual_x': f'{self.latest_actual["x"]:.6f}',
            'actual_y': f'{self.latest_actual["y"]:.6f}',
            'actual_yaw': f'{self.latest_actual["yaw"]:.6f}',
            'actual_linear_x': f'{self.latest_actual["linear_x"]:.6f}',
            'actual_angular_z': f'{self.latest_actual["angular_z"]:.6f}',
            'noisy_x': '',
            'noisy_y': '',
            'noisy_yaw': '',
        }

        if self.latest_noisy is not None:
            row['noisy_x'] = f'{self.latest_noisy["x"]:.6f}'
            row['noisy_y'] = f'{self.latest_noisy["y"]:.6f}'
            row['noisy_yaw'] = f'{self.latest_noisy["yaw"]:.6f}'

        self.writer.writerow(row)
        self.csv_file.flush()
        self.rows_written += 1

        log_interval = int(max(self.sample_rate_hz, 1.0))

        if self.rows_written % log_interval == 0:
            self.get_logger().info(f'Rows written: {self.rows_written}')

    def close(self):
        self.get_logger().info(f'Closing CSV after writing {self.rows_written} rows')
        self.csv_file.flush()
        self.csv_file.close()


def main(args=None):
    rclpy.init(args=args)

    node = TrajectoryValidationRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
