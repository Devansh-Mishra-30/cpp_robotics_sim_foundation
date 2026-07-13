#!/usr/bin/env python3

import csv
import math
from pathlib import Path
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def wrap_to_pi(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def pose_from_odom(msg: Odometry) -> tuple[float, float, float]:
    pose = msg.pose.pose

    return (
        pose.position.x,
        pose.position.y,
        quaternion_to_yaw(
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        ),
    )


class Day108FusionRecorder(Node):
    def __init__(self) -> None:
        super().__init__("day108_fusion_analysis")

        self.declare_parameter(
            "output_csv",
            "plots/day108/fusion_comparison.csv",
        )

        output_csv = (
            self.get_parameter("output_csv")
            .get_parameter_value()
            .string_value
        )

        self.output_path = Path(output_csv).expanduser().resolve()
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        self.latest_raw: Optional[Odometry] = None
        self.latest_noisy: Optional[Odometry] = None
        self.latest_ekf: Optional[Odometry] = None

        self.initialized = False
        self.map_to_odom_x = 0.0
        self.map_to_odom_y = 0.0
        self.map_to_odom_yaw = 0.0

        self.start_time = self.get_clock().now()

        self.csv_file = self.output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        )

        self.writer = csv.writer(self.csv_file)

        self.writer.writerow(
            [
                "time_sec",
                "amcl_x",
                "amcl_y",
                "amcl_yaw",
                "raw_x",
                "raw_y",
                "raw_yaw",
                "noisy_x",
                "noisy_y",
                "noisy_yaw",
                "ekf_x",
                "ekf_y",
                "ekf_yaw",
                "raw_position_error",
                "noisy_position_error",
                "ekf_position_error",
                "raw_yaw_error",
                "noisy_yaw_error",
                "ekf_yaw_error",
            ]
        )

        self.create_subscription(
            Odometry,
            "/diff_drive_controller/odom",
            self.raw_callback,
            30,
        )

        self.create_subscription(
            Odometry,
            "/odom_noisy",
            self.noisy_callback,
            30,
        )

        self.create_subscription(
            Odometry,
            "/odometry/filtered",
            self.ekf_callback,
            30,
        )

        self.create_subscription(
            PoseWithCovarianceStamped,
            "/amcl_pose",
            self.amcl_callback,
            30,
        )

        self.get_logger().info(
            f"Day 108 recorder writing to: {self.output_path}"
        )

    def raw_callback(self, msg: Odometry) -> None:
        self.latest_raw = msg

    def noisy_callback(self, msg: Odometry) -> None:
        self.latest_noisy = msg

    def ekf_callback(self, msg: Odometry) -> None:
        self.latest_ekf = msg

    def capture_alignment(
        self,
        amcl_x: float,
        amcl_y: float,
        amcl_yaw: float,
        raw_x: float,
        raw_y: float,
        raw_yaw: float,
    ) -> None:
        self.map_to_odom_yaw = wrap_to_pi(amcl_yaw - raw_yaw)

        cosine = math.cos(self.map_to_odom_yaw)
        sine = math.sin(self.map_to_odom_yaw)

        rotated_x = cosine * raw_x - sine * raw_y
        rotated_y = sine * raw_x + cosine * raw_y

        self.map_to_odom_x = amcl_x - rotated_x
        self.map_to_odom_y = amcl_y - rotated_y
        self.initialized = True

        self.get_logger().info(
            "Captured fixed initial map-to-odom alignment"
        )

    def align(
        self,
        x: float,
        y: float,
        yaw: float,
    ) -> tuple[float, float, float]:
        cosine = math.cos(self.map_to_odom_yaw)
        sine = math.sin(self.map_to_odom_yaw)

        aligned_x = (
            self.map_to_odom_x
            + cosine * x
            - sine * y
        )

        aligned_y = (
            self.map_to_odom_y
            + sine * x
            + cosine * y
        )

        aligned_yaw = wrap_to_pi(
            self.map_to_odom_yaw + yaw
        )

        return aligned_x, aligned_y, aligned_yaw

    def amcl_callback(
        self,
        msg: PoseWithCovarianceStamped,
    ) -> None:
        if (
            self.latest_raw is None
            or self.latest_noisy is None
            or self.latest_ekf is None
        ):
            return

        amcl_pose = msg.pose.pose

        amcl_x = amcl_pose.position.x
        amcl_y = amcl_pose.position.y
        amcl_yaw = quaternion_to_yaw(
            amcl_pose.orientation.x,
            amcl_pose.orientation.y,
            amcl_pose.orientation.z,
            amcl_pose.orientation.w,
        )

        raw_x, raw_y, raw_yaw = pose_from_odom(self.latest_raw)
        noisy_x, noisy_y, noisy_yaw = pose_from_odom(self.latest_noisy)
        ekf_x, ekf_y, ekf_yaw = pose_from_odom(self.latest_ekf)

        if not self.initialized:
            self.capture_alignment(
                amcl_x,
                amcl_y,
                amcl_yaw,
                raw_x,
                raw_y,
                raw_yaw,
            )

        raw_x, raw_y, raw_yaw = self.align(
            raw_x,
            raw_y,
            raw_yaw,
        )

        noisy_x, noisy_y, noisy_yaw = self.align(
            noisy_x,
            noisy_y,
            noisy_yaw,
        )

        ekf_x, ekf_y, ekf_yaw = self.align(
            ekf_x,
            ekf_y,
            ekf_yaw,
        )

        raw_position_error = math.hypot(
            amcl_x - raw_x,
            amcl_y - raw_y,
        )

        noisy_position_error = math.hypot(
            amcl_x - noisy_x,
            amcl_y - noisy_y,
        )

        ekf_position_error = math.hypot(
            amcl_x - ekf_x,
            amcl_y - ekf_y,
        )

        raw_yaw_error = wrap_to_pi(amcl_yaw - raw_yaw)
        noisy_yaw_error = wrap_to_pi(amcl_yaw - noisy_yaw)
        ekf_yaw_error = wrap_to_pi(amcl_yaw - ekf_yaw)

        elapsed = (
            self.get_clock().now() - self.start_time
        ).nanoseconds / 1e9

        self.writer.writerow(
            [
                elapsed,
                amcl_x,
                amcl_y,
                amcl_yaw,
                raw_x,
                raw_y,
                raw_yaw,
                noisy_x,
                noisy_y,
                noisy_yaw,
                ekf_x,
                ekf_y,
                ekf_yaw,
                raw_position_error,
                noisy_position_error,
                ekf_position_error,
                raw_yaw_error,
                noisy_yaw_error,
                ekf_yaw_error,
            ]
        )

        self.csv_file.flush()

    def destroy_node(self) -> bool:
        if not self.csv_file.closed:
            self.csv_file.flush()
            self.csv_file.close()

        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)

    node = Day108FusionRecorder()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()