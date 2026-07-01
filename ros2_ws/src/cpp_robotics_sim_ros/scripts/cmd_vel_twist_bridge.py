#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from geometry_msgs.msg import TwistStamped


class CmdVelTwistBridge(Node):
    def __init__(self):
        super().__init__("cmd_vel_twist_bridge")

        self.input_topic = self.declare_parameter("input_topic", "/cmd_vel").value
        self.output_topic = self.declare_parameter(
            "output_topic",
            "/diff_drive_controller/cmd_vel",
        ).value
        self.frame_id = self.declare_parameter("frame_id", "base_link").value

        self.publisher = self.create_publisher(TwistStamped, self.output_topic, 10)

        self.subscription = self.create_subscription(
            Twist,
            self.input_topic,
            self.cmd_callback,
            10,
        )

        self.get_logger().info(
            f"Bridging {self.input_topic} Twist -> {self.output_topic} TwistStamped"
        )

    def cmd_callback(self, msg: Twist):
        stamped = TwistStamped()
        stamped.header.stamp = self.get_clock().now().to_msg()
        stamped.header.frame_id = self.frame_id
        stamped.twist = msg
        self.publisher.publish(stamped)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelTwistBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()