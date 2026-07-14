#!/usr/bin/env python3

import json
import re
import subprocess
import threading
from pathlib import Path
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from std_msgs.msg import String


class MappingManagerNode(Node):
    MAP_NAME_PATTERN = re.compile(
        r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$"
    )

    def __init__(self) -> None:
        super().__init__("mapping_manager")

        self.declare_parameter(
            "map_directory",
            str(
                Path.home()
                / ".ros"
                / "cpp_robotics_sim"
                / "maps"
            ),
        )
        self.declare_parameter("save_timeout", 20.0)
        self.declare_parameter("free_threshold", 0.25)
        self.declare_parameter("occupied_threshold", 0.65)

        self.map_directory = Path(
            str(
                self.get_parameter(
                    "map_directory"
                ).value
            )
        ).expanduser()

        self.save_timeout = float(
            self.get_parameter("save_timeout").value
        )
        self.free_threshold = float(
            self.get_parameter(
                "free_threshold"
            ).value
        )
        self.occupied_threshold = float(
            self.get_parameter(
                "occupied_threshold"
            ).value
        )

        self.validate_parameters()

        self.map_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        transient_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.status_publisher = self.create_publisher(
            String,
            "/mapping/save_status",
            transient_qos,
        )

        self.maps_publisher = self.create_publisher(
            String,
            "/mapping/saved_maps",
            transient_qos,
        )

        self.save_subscription = self.create_subscription(
            String,
            "/mapping/save_request",
            self.save_request_callback,
            10,
        )

        self.mode_subscription = self.create_subscription(
            String,
            "/mode/status",
            self.mode_status_callback,
            transient_qos,
        )

        self.simulation_subscription = (
            self.create_subscription(
                String,
                "/simulation/status",
                self.simulation_status_callback,
                transient_qos,
            )
        )

        self.mode_state = "stopped"
        self.simulation_state = "stopped"
        self.save_in_progress = False
        self.save_lock = threading.Lock()

        self.publish_status(
            status="ready",
            message="Mapping manager ready",
        )

        self.publish_saved_maps()

        self.get_logger().info(
            f"Mapping manager ready: {self.map_directory}"
        )

    def validate_parameters(self) -> None:
        if self.save_timeout <= 0.0:
            raise ValueError(
                "save_timeout must be greater than zero"
            )

        if not 0.0 <= self.free_threshold <= 1.0:
            raise ValueError(
                "free_threshold must be within [0, 1]"
            )

        if not 0.0 <= self.occupied_threshold <= 1.0:
            raise ValueError(
                "occupied_threshold must be within [0, 1]"
            )

        if (
            self.free_threshold
            >= self.occupied_threshold
        ):
            raise ValueError(
                "free_threshold must be less than "
                "occupied_threshold"
            )

    def mode_status_callback(
        self,
        message: String,
    ) -> None:
        self.mode_state = message.data

    def simulation_status_callback(
        self,
        message: String,
    ) -> None:
        self.simulation_state = message.data

    def save_request_callback(
        self,
        message: String,
    ) -> None:
        map_name = message.data.strip()

        with self.save_lock:
            if self.save_in_progress:
                self.publish_status(
                    status="error",
                    message=(
                        "A map save operation is already "
                        "in progress"
                    ),
                )
                return

            validation_error = (
                self.validate_save_request(map_name)
            )

            if validation_error:
                self.publish_status(
                    status="error",
                    message=validation_error,
                )
                return

            self.save_in_progress = True

        thread = threading.Thread(
            target=self.save_map,
            args=(map_name,),
            daemon=True,
        )
        thread.start()

    def validate_save_request(
        self,
        map_name: str,
    ) -> Optional[str]:
        if self.simulation_state != "running":
            return (
                "Simulation must be running before "
                "saving a map"
            )

        if self.mode_state != "mapping":
            return (
                "Mapping mode must be active before "
                "saving a map"
            )

        if not map_name:
            return "Map name must not be empty"

        if not self.MAP_NAME_PATTERN.fullmatch(
            map_name
        ):
            return (
                "Map name may contain letters, numbers, "
                "underscores, and hyphens only"
            )

        return None

    def save_map(
        self,
        map_name: str,
    ) -> None:
        output_prefix = (
            self.map_directory / map_name
        )

        self.publish_status(
            status="saving",
            message=f"Saving map '{map_name}'...",
            map_name=map_name,
        )

        command = [
            "ros2",
            "run",
            "nav2_map_server",
            "map_saver_cli",
            "-f",
            str(output_prefix),
            "--free",
            str(self.free_threshold),
            "--occ",
            str(self.occupied_threshold),
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.save_timeout,
                check=False,
            )

            yaml_path = output_prefix.with_suffix(
                ".yaml"
            )
            pgm_path = output_prefix.with_suffix(
                ".pgm"
            )

            if (
                result.returncode != 0
                or not yaml_path.exists()
                or not pgm_path.exists()
            ):
                details = (
                    result.stderr.strip()
                    or result.stdout.strip()
                    or "Expected map files were not created"
                )

                self.publish_status(
                    status="error",
                    message=(
                        f"Failed to save map "
                        f"'{map_name}': {details}"
                    ),
                    map_name=map_name,
                )
                return

            self.publish_status(
                status="success",
                message=(
                    f"Map '{map_name}' saved successfully"
                ),
                map_name=map_name,
                yaml_path=str(yaml_path),
                image_path=str(pgm_path),
            )

            self.publish_saved_maps()

        except subprocess.TimeoutExpired:
            self.publish_status(
                status="error",
                message=(
                    f"Saving map '{map_name}' timed out"
                ),
                map_name=map_name,
            )

        except OSError as error:
            self.publish_status(
                status="error",
                message=(
                    f"Unable to run map saver: {error}"
                ),
                map_name=map_name,
            )

        finally:
            with self.save_lock:
                self.save_in_progress = False

    def publish_status(
        self,
        status: str,
        message: str,
        map_name: str = "",
        yaml_path: str = "",
        image_path: str = "",
    ) -> None:
        payload = {
            "status": status,
            "message": message,
            "map_name": map_name,
            "yaml_path": yaml_path,
            "image_path": image_path,
        }

        ros_message = String()
        ros_message.data = json.dumps(payload)

        if rclpy.ok(context=self.context):
            self.status_publisher.publish(
                ros_message
            )

    def publish_saved_maps(self) -> None:
        maps = []

        for yaml_path in sorted(
            self.map_directory.glob("*.yaml")
        ):
            image_path = yaml_path.with_suffix(
                ".pgm"
            )

            maps.append(
                {
                    "name": yaml_path.stem,
                    "yaml_path": str(yaml_path),
                    "image_path": str(image_path),
                    "complete": image_path.exists(),
                }
            )

        message = String()
        message.data = json.dumps(maps)

        if rclpy.ok(context=self.context):
            self.maps_publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)

    node: Optional[MappingManagerNode] = None

    try:
        node = MappingManagerNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
