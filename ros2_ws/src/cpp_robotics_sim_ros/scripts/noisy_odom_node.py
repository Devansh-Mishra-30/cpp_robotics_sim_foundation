#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import copy
import math
import random

from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def quaternion_from_yaw(yaw):
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw * 0.5)
    q.w = math.cos(yaw * 0.5)
    return q


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class NoisyOdomNode(Node):
    def __init__(self):
        super().__init__('noisy_odom_node')

        self.declare_parameter('input_topic', '/diff_drive_controller/odom')
        self.declare_parameter('output_topic', '/odom_noisy')

        self.declare_parameter('position_noise_std', 0.02)
        self.declare_parameter('yaw_noise_std', 0.02)
        self.declare_parameter('linear_velocity_noise_std', 0.02)
        self.declare_parameter('angular_velocity_noise_std', 0.02)

        # Use -1 for non-deterministic random noise.
        # Use any non-negative integer for repeatable noise.
        self.declare_parameter('random_seed', 42)

        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value

        self.position_noise_std = float(
            self.get_parameter('position_noise_std').value
        )
        self.yaw_noise_std = float(
            self.get_parameter('yaw_noise_std').value
        )
        self.linear_velocity_noise_std = float(
            self.get_parameter('linear_velocity_noise_std').value
        )
        self.angular_velocity_noise_std = float(
            self.get_parameter('angular_velocity_noise_std').value
        )

        random_seed = int(self.get_parameter('random_seed').value)

        if random_seed < 0:
            self.rng = random.Random()
        else:
            self.rng = random.Random(random_seed)

        self.odom_pub = self.create_publisher(
            Odometry,
            self.output_topic,
            10
        )

        self.odom_sub = self.create_subscription(
            Odometry,
            self.input_topic,
            self.odom_callback,
            10
        )

        self.get_logger().info('Noisy odometry node started')
        self.get_logger().info(f'Subscribing: {self.input_topic}')
        self.get_logger().info(f'Publishing:  {self.output_topic}')
        self.get_logger().info(
            'Noise stddevs: '
            f'position={self.position_noise_std:.4f} m, '
            f'yaw={self.yaw_noise_std:.4f} rad, '
            f'linear_velocity={self.linear_velocity_noise_std:.4f} m/s, '
            f'angular_velocity={self.angular_velocity_noise_std:.4f} rad/s'
        )

    def odom_callback(self, msg):
        noisy_msg = copy.deepcopy(msg)

        x_noise = self.rng.gauss(0.0, self.position_noise_std)
        y_noise = self.rng.gauss(0.0, self.position_noise_std)
        yaw_noise = self.rng.gauss(0.0, self.yaw_noise_std)
        linear_velocity_noise = self.rng.gauss(
            0.0,
            self.linear_velocity_noise_std
        )
        angular_velocity_noise = self.rng.gauss(
            0.0,
            self.angular_velocity_noise_std
        )

        actual_yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        noisy_yaw = wrap_angle(actual_yaw + yaw_noise)

        noisy_msg.pose.pose.position.x = msg.pose.pose.position.x + x_noise
        noisy_msg.pose.pose.position.y = msg.pose.pose.position.y + y_noise
        noisy_msg.pose.pose.orientation = quaternion_from_yaw(noisy_yaw)

        noisy_msg.twist.twist.linear.x = (
            msg.twist.twist.linear.x + linear_velocity_noise
        )
        noisy_msg.twist.twist.angular.z = (
            msg.twist.twist.angular.z + angular_velocity_noise
        )

        self.set_covariance(noisy_msg)

        self.odom_pub.publish(noisy_msg)

    def set_covariance(self, msg):
        position_variance = self.position_noise_std ** 2
        yaw_variance = self.yaw_noise_std ** 2
        linear_velocity_variance = self.linear_velocity_noise_std ** 2
        angular_velocity_variance = self.angular_velocity_noise_std ** 2

        pose_covariance = [0.0] * 36
        twist_covariance = [0.0] * 36

        # Pose covariance index layout for 6x6:
        # x, y, z, roll, pitch, yaw
        pose_covariance[0] = position_variance       # x
        pose_covariance[7] = position_variance       # y
        pose_covariance[14] = 1.0                    # z unused
        pose_covariance[21] = 1.0                    # roll unused
        pose_covariance[28] = 1.0                    # pitch unused
        pose_covariance[35] = yaw_variance           # yaw

        # Twist covariance index layout for 6x6:
        # vx, vy, vz, roll_rate, pitch_rate, yaw_rate
        twist_covariance[0] = linear_velocity_variance
        twist_covariance[7] = 1.0
        twist_covariance[14] = 1.0
        twist_covariance[21] = 1.0
        twist_covariance[28] = 1.0
        twist_covariance[35] = angular_velocity_variance

        msg.pose.covariance = pose_covariance
        msg.twist.covariance = twist_covariance


def main(args=None):
    rclpy.init(args=args)

    node = NoisyOdomNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
