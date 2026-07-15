#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import csv
import math
from pathlib import Path
from typing import Optional

from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    """Convert a quaternion into planar yaw."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def wrap_to_pi(angle: float) -> float:
    """Wrap an angle to [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


class LocalizationComparisonRecorder(Node):
    """Record AMCL and odometry data for comparison."""

    def __init__(self) -> None:
        super().__init__('localization_comparison_recorder')

        self.declare_parameter(
            'output_csv',
            'data/localization_comparison.csv',
        )

        output_csv = (
            self.get_parameter('output_csv')
            .get_parameter_value()
            .string_value
        )

        self.output_path = Path(output_csv).expanduser().resolve()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.latest_odom: Optional[Odometry] = None

        self.initialized = False
        self.initial_map_to_odom_x = 0.0
        self.initial_map_to_odom_y = 0.0
        self.initial_map_to_odom_yaw = 0.0

        self.start_time = self.get_clock().now()

        self.csv_file = self.output_path.open(
            'w',
            newline='',
            encoding='utf-8',
        )

        self.writer = csv.writer(self.csv_file)

        self.writer.writerow(
            [
                'time_sec',
                'amcl_x',
                'amcl_y',
                'amcl_yaw_rad',
                'odom_raw_x',
                'odom_raw_y',
                'odom_raw_yaw_rad',
                'odom_aligned_x',
                'odom_aligned_y',
                'odom_aligned_yaw_rad',
                'position_error_m',
                'yaw_error_rad',
                'amcl_covariance_x',
                'amcl_covariance_y',
                'amcl_covariance_yaw',
            ]
        )

        self.odom_subscription = self.create_subscription(
            Odometry,
            '/diff_drive_controller/odom',
            self.odom_callback,
            20,
        )

        self.amcl_subscription = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_callback,
            20,
        )

        self.get_logger().info(
            f'Localization comparison recorder writing to: {self.output_path}'
        )

        self.get_logger().info(
            'Waiting for odometry and AMCL pose messages...'
        )

    def odom_callback(self, msg: Odometry) -> None:
        self.latest_odom = msg

    def amcl_callback(
        self,
        amcl_msg: PoseWithCovarianceStamped,
    ) -> None:
        if self.latest_odom is None:
            self.get_logger().warn(
                'Received AMCL pose before odometry; waiting for odometry.'
            )
            return

        odom_msg = self.latest_odom

        amcl_pose = amcl_msg.pose.pose
        odom_pose = odom_msg.pose.pose

        amcl_x = amcl_pose.position.x
        amcl_y = amcl_pose.position.y

        amcl_yaw = quaternion_to_yaw(
            amcl_pose.orientation.x,
            amcl_pose.orientation.y,
            amcl_pose.orientation.z,
            amcl_pose.orientation.w,
        )

        odom_x = odom_pose.position.x
        odom_y = odom_pose.position.y

        odom_yaw = quaternion_to_yaw(
            odom_pose.orientation.x,
            odom_pose.orientation.y,
            odom_pose.orientation.z,
            odom_pose.orientation.w,
        )

        if not self.initialized:
            self.capture_initial_alignment(
                amcl_x,
                amcl_y,
                amcl_yaw,
                odom_x,
                odom_y,
                odom_yaw,
            )

        aligned_x, aligned_y, aligned_yaw = self.align_odometry(
            odom_x,
            odom_y,
            odom_yaw,
        )

        error_x = amcl_x - aligned_x
        error_y = amcl_y - aligned_y

        position_error = math.hypot(error_x, error_y)
        yaw_error = wrap_to_pi(amcl_yaw - aligned_yaw)

        elapsed = (
            self.get_clock().now() - self.start_time
        ).nanoseconds / 1e9

        covariance = amcl_msg.pose.covariance

        self.writer.writerow(
            [
                elapsed,
                amcl_x,
                amcl_y,
                amcl_yaw,
                odom_x,
                odom_y,
                odom_yaw,
                aligned_x,
                aligned_y,
                aligned_yaw,
                position_error,
                yaw_error,
                covariance[0],
                covariance[7],
                covariance[35],
            ]
        )

        self.csv_file.flush()

        self.get_logger().info(
            'AMCL=(%.3f, %.3f, %.3f) | '
            'aligned odom=(%.3f, %.3f, %.3f) | '
            'position error=%.3f m | yaw error=%.3f rad'
            % (
                amcl_x,
                amcl_y,
                amcl_yaw,
                aligned_x,
                aligned_y,
                aligned_yaw,
                position_error,
                yaw_error,
            )
        )

    def capture_initial_alignment(
        self,
        amcl_x: float,
        amcl_y: float,
        amcl_yaw: float,
        odom_x: float,
        odom_y: float,
        odom_yaw: float,
    ) -> None:
        """Compute and freeze the initial map-to-odometry transform."""
        self.initial_map_to_odom_yaw = wrap_to_pi(
            amcl_yaw - odom_yaw
        )

        cos_yaw = math.cos(self.initial_map_to_odom_yaw)
        sin_yaw = math.sin(self.initial_map_to_odom_yaw)

        rotated_odom_x = (
            cos_yaw * odom_x - sin_yaw * odom_y
        )

        rotated_odom_y = (
            sin_yaw * odom_x + cos_yaw * odom_y
        )

        self.initial_map_to_odom_x = amcl_x - rotated_odom_x
        self.initial_map_to_odom_y = amcl_y - rotated_odom_y

        self.initialized = True

        self.get_logger().info(
            'Captured fixed initial map-to-odom alignment: '
            'x=%.3f, y=%.3f, yaw=%.3f rad'
            % (
                self.initial_map_to_odom_x,
                self.initial_map_to_odom_y,
                self.initial_map_to_odom_yaw,
            )
        )

    def align_odometry(
        self,
        odom_x: float,
        odom_y: float,
        odom_yaw: float,
    ) -> tuple[float, float, float]:
        cos_yaw = math.cos(self.initial_map_to_odom_yaw)
        sin_yaw = math.sin(self.initial_map_to_odom_yaw)

        aligned_x = (
            self.initial_map_to_odom_x
            + cos_yaw * odom_x
            - sin_yaw * odom_y
        )

        aligned_y = (
            self.initial_map_to_odom_y
            + sin_yaw * odom_x
            + cos_yaw * odom_y
        )

        aligned_yaw = wrap_to_pi(
            self.initial_map_to_odom_yaw + odom_yaw
        )

        return aligned_x, aligned_y, aligned_yaw

    def destroy_node(self) -> bool:
        if not self.csv_file.closed:
            self.csv_file.flush()
            self.csv_file.close()

        if rclpy.ok():
            self.get_logger().info(
                f'Localization comparison CSV saved: {self.output_path}'
            )

        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)

    node = LocalizationComparisonRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
