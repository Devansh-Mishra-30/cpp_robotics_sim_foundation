#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import argparse
import math
from pathlib import Path
import statistics
import time
from typing import List

from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu


class CovarianceAnalysisNode(Node):
    def __init__(self, duration: float, output_path: Path) -> None:
        super().__init__('covariance_analysis')

        self.duration = duration
        self.output_path = output_path
        self.start_wall_time = time.monotonic()

        self.raw_linear_x: List[float] = []
        self.raw_yaw_rate: List[float] = []
        self.imu_yaw_rate: List[float] = []
        self.filtered_linear_x: List[float] = []
        self.filtered_yaw_rate: List[float] = []

        self.raw_twist_covariance_x: List[float] = []
        self.raw_twist_covariance_yaw: List[float] = []

        self.imu_covariance_yaw: List[float] = []

        self.filtered_twist_covariance_x: List[float] = []
        self.filtered_twist_covariance_yaw: List[float] = []

        self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.raw_odom_callback,
            50,
        )

        self.create_subscription(
            Imu,
            '/imu/data',
            self.imu_callback,
            100,
        )

        self.create_subscription(
            Odometry,
            '/odometry/filtered',
            self.filtered_odom_callback,
            50,
        )

        self.timer = self.create_timer(0.2, self.timer_callback)

        self.get_logger().info(
            f'Recording covariance data for {self.duration:.1f} seconds'
        )

    def raw_odom_callback(self, msg: Odometry) -> None:
        self.raw_linear_x.append(msg.twist.twist.linear.x)
        self.raw_yaw_rate.append(msg.twist.twist.angular.z)

        self.raw_twist_covariance_x.append(
            msg.twist.covariance[0]
        )

        self.raw_twist_covariance_yaw.append(
            msg.twist.covariance[35]
        )

    def imu_callback(self, msg: Imu) -> None:
        self.imu_yaw_rate.append(msg.angular_velocity.z)

        self.imu_covariance_yaw.append(
            msg.angular_velocity_covariance[8]
        )

    def filtered_odom_callback(self, msg: Odometry) -> None:
        self.filtered_linear_x.append(msg.twist.twist.linear.x)
        self.filtered_yaw_rate.append(msg.twist.twist.angular.z)

        self.filtered_twist_covariance_x.append(
            msg.twist.covariance[0]
        )

        self.filtered_twist_covariance_yaw.append(
            msg.twist.covariance[35]
        )

    def timer_callback(self) -> None:
        elapsed = time.monotonic() - self.start_wall_time

        if elapsed >= self.duration:
            self.write_report()
            rclpy.shutdown()

    @staticmethod
    def safe_mean(values: List[float]) -> float:
        return statistics.mean(values) if values else math.nan

    @staticmethod
    def safe_stddev(values: List[float]) -> float:
        if len(values) < 2:
            return math.nan

        return statistics.stdev(values)

    @staticmethod
    def safe_min(values: List[float]) -> float:
        return min(values) if values else math.nan

    @staticmethod
    def safe_max(values: List[float]) -> float:
        return max(values) if values else math.nan

    def format_statistics(
        self,
        name: str,
        values: List[float],
        unit: str,
    ) -> str:
        return (
            f'### {name}\n\n'
            f'- Samples: {len(values)}\n'
            f'- Mean: {self.safe_mean(values):.8f} {unit}\n'
            f'- Standard deviation: '
            f'{self.safe_stddev(values):.8f} {unit}\n'
            f'- Minimum: {self.safe_min(values):.8f} {unit}\n'
            f'- Maximum: {self.safe_max(values):.8f} {unit}\n'
        )

    def write_report(self) -> None:
        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report = """# Covariance analysis Covariance Analysis

## Purpose

Compare raw wheel odometry, IMU yaw-rate measurements, and
EKF-filtered odometry.

The report records observed measurement variation and the covariance
values published by each source.

"""

        report += self.format_statistics(
            'Raw wheel odometry linear velocity',
            self.raw_linear_x,
            'm/s',
        )

        report += '\n'

        report += self.format_statistics(
            'Raw wheel odometry yaw rate',
            self.raw_yaw_rate,
            'rad/s',
        )

        report += '\n'

        report += self.format_statistics(
            'Raw IMU yaw rate',
            self.imu_yaw_rate,
            'rad/s',
        )

        report += '\n'

        report += self.format_statistics(
            'Filtered linear velocity',
            self.filtered_linear_x,
            'm/s',
        )

        report += '\n'

        report += self.format_statistics(
            'Filtered yaw rate',
            self.filtered_yaw_rate,
            'rad/s',
        )

        report += f"""
## Published covariance values

### Raw wheel odometry

- Mean linear-X twist covariance:
  {self.safe_mean(self.raw_twist_covariance_x):.10f}
- Mean yaw-rate twist covariance:
  {self.safe_mean(self.raw_twist_covariance_yaw):.10f}

### IMU

- Mean yaw-rate covariance:
  {self.safe_mean(self.imu_covariance_yaw):.10f}

### EKF-filtered odometry

- Mean linear-X twist covariance:
  {self.safe_mean(self.filtered_twist_covariance_x):.10f}
- Mean yaw-rate twist covariance:
  {self.safe_mean(self.filtered_twist_covariance_yaw):.10f}

## Initial interpretation

Wheel odometry supplies forward velocity and yaw rate.

The IMU supplies an independent noisy measurement of yaw rate.

The EKF combines both yaw-rate sources. The filtered output should retain
the robot's motion response while reducing sensitivity to individual IMU
noise samples.

A covariance value represents estimated uncertainty, not the measured
value itself. A smaller covariance gives that measurement greater weight
inside the Kalman filter.
"""

        self.output_path.write_text(
            report,
            encoding='utf-8',
        )

        self.get_logger().info(
            f'Covariance analysis report saved to: {self.output_path}'
        )


def main(args=None) -> None:
    parser = argparse.ArgumentParser(
        description='Analyze Covariance analysis EKF covariance behavior.'
    )

    parser.add_argument(
        '--duration',
        type=float,
        default=20.0,
        help='Recording duration in seconds.',
    )

    parser.add_argument(
        '--output',
        required=True,
        help='Output Markdown report path.',
    )

    parsed_args, ros_args = parser.parse_known_args(args=args)

    rclpy.init(args=ros_args)

    node = CovarianceAnalysisNode(
        duration=parsed_args.duration,
        output_path=Path(parsed_args.output).expanduser().resolve(),
    )

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.write_report()
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
