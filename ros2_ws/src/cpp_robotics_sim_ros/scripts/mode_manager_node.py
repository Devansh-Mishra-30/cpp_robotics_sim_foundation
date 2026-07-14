#!/usr/bin/env python3

import json
import os
import signal
import subprocess
import threading
import time
from enum import Enum
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
from std_srvs.srv import Trigger


class OperatingMode(str, Enum):
    STOPPED = "stopped"
    MANUAL = "manual"
    MAPPING = "mapping"
    LOCALIZATION = "localization"
    NAVIGATION = "navigation"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"


class ModeManagerNode(Node):
    """
    Manage mutually exclusive robot operating modes.

    Manual mode requires no auxiliary launch process. Mapping,
    localization, and navigation each launch one dedicated ROS 2
    launch file.

    The base simulation is owned by simulation_manager_node.py.
    """

    def __init__(self) -> None:
        super().__init__("mode_manager")

        self.declare_parameter(
            "launch_package",
            "cpp_robotics_sim_ros",
        )
        self.declare_parameter(
            "mapping_launch_file",
            "slam_mapping.launch.py",
        )
        self.declare_parameter(
            "localization_launch_file",
            "amcl_localization.launch.py",
        )
        self.declare_parameter(
            "navigation_launch_file",
            "nav2_navigation.launch.py",
        )
        self.declare_parameter(
            "managed_use_sim_time",
            True,
        )
        self.declare_parameter(
            "startup_grace_period",
            3.0,
        )
        self.declare_parameter(
            "shutdown_timeout",
            10.0,
        )
        self.declare_parameter(
            "kill_timeout",
            3.0,
        )

        self.launch_package = str(
            self.get_parameter("launch_package").value
        )
        self.managed_use_sim_time = bool(
            self.get_parameter(
                "managed_use_sim_time"
            ).value
        )
        self.startup_grace_period = float(
            self.get_parameter(
                "startup_grace_period"
            ).value
        )
        self.shutdown_timeout = float(
            self.get_parameter("shutdown_timeout").value
        )
        self.kill_timeout = float(
            self.get_parameter("kill_timeout").value
        )

        self.launch_files = {
            OperatingMode.MAPPING: str(
                self.get_parameter(
                    "mapping_launch_file"
                ).value
            ),
            OperatingMode.LOCALIZATION: str(
                self.get_parameter(
                    "localization_launch_file"
                ).value
            ),
            OperatingMode.NAVIGATION: str(
                self.get_parameter(
                    "navigation_launch_file"
                ).value
            ),
        }

        self.validate_parameters()

        status_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.status_publisher = self.create_publisher(
            String,
            "/mode/status",
            status_qos,
        )

        self.simulation_subscription = (
            self.create_subscription(
                String,
                "/simulation/status",
                self.simulation_status_callback,
                status_qos,
            )
        )

        self.selected_map_subscription = (
            self.create_subscription(
                String,
                "/localization/selected_map",
                self.selected_map_callback,
                status_qos,
            )
        )

        self.manual_service = self.create_service(
            Trigger,
            "/mode/manual",
            self.manual_callback,
        )
        self.mapping_service = self.create_service(
            Trigger,
            "/mode/mapping",
            self.mapping_callback,
        )
        self.localization_service = self.create_service(
            Trigger,
            "/mode/localization",
            self.localization_callback,
        )
        self.navigation_service = self.create_service(
            Trigger,
            "/mode/navigation",
            self.navigation_callback,
        )
        self.stop_service = self.create_service(
            Trigger,
            "/mode/stop",
            self.stop_callback,
        )

        self.process: Optional[subprocess.Popen] = None
        self.process_group_id: Optional[int] = None
        self.process_lock = threading.RLock()

        self.mode = OperatingMode.STOPPED
        self.requested_mode = OperatingMode.STOPPED
        self.simulation_state = "unknown"
        self.selected_map_name = ""
        self.selected_map_path = ""
        self.last_error = ""

        self.monitor_timer = self.create_timer(
            0.5,
            self.monitor_process,
        )

        self.publish_mode(OperatingMode.STOPPED)

        self.get_logger().info(
            "Operating-mode manager ready"
        )

    def validate_parameters(self) -> None:
        if not self.launch_package:
            raise ValueError(
                "launch_package must not be empty"
            )

        for mode, launch_file in self.launch_files.items():
            if not launch_file:
                raise ValueError(
                    f"{mode.value} launch file must not be empty"
                )

        if self.startup_grace_period < 0.0:
            raise ValueError(
                "startup_grace_period must not be negative"
            )

        if self.shutdown_timeout <= 0.0:
            raise ValueError(
                "shutdown_timeout must be greater than zero"
            )

        if self.kill_timeout <= 0.0:
            raise ValueError(
                "kill_timeout must be greater than zero"
            )

    def simulation_status_callback(
        self,
        message: String,
    ) -> None:
        previous_state = self.simulation_state
        self.simulation_state = message.data

        if (
            previous_state == self.simulation_state
            or self.simulation_state
            in ("running", "starting")
        ):
            return

        if self.mode not in (
            OperatingMode.STOPPED,
            OperatingMode.ERROR,
        ):
            self.get_logger().warning(
                "Simulation is no longer running; "
                "stopping active operating mode"
            )

            self.stop_current_mode()

    def selected_map_callback(
        self,
        message: String,
    ) -> None:
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            self.get_logger().error(
                "Received invalid selected-map payload"
            )
            return

        self.selected_map_name = str(
            payload.get("name", "")
        )
        self.selected_map_path = str(
            payload.get("yaml_path", "")
        )

    def manual_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        return self.fill_response(
            response,
            *self.activate_mode(OperatingMode.MANUAL),
        )

    def mapping_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        return self.fill_response(
            response,
            *self.activate_mode(OperatingMode.MAPPING),
        )

    def localization_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        return self.fill_response(
            response,
            *self.activate_mode(
                OperatingMode.LOCALIZATION
            ),
        )

    def navigation_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        return self.fill_response(
            response,
            *self.activate_mode(
                OperatingMode.NAVIGATION
            ),
        )

    def stop_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request
        return self.fill_response(
            response,
            *self.stop_current_mode(),
        )

    @staticmethod
    def fill_response(
        response: Trigger.Response,
        success: bool,
        message: str,
    ) -> Trigger.Response:
        response.success = success
        response.message = message
        return response

    def activate_mode(
        self,
        requested_mode: OperatingMode,
    ) -> tuple[bool, str]:
        with self.process_lock:
            if self.simulation_state != "running":
                message = (
                    "Simulation must be running before "
                    "selecting an operating mode"
                )
                self.get_logger().warning(message)
                return False, message

            if (
                requested_mode
                in (
                    OperatingMode.LOCALIZATION,
                    OperatingMode.NAVIGATION,
                )
                and not self.selected_map_path
            ):
                message = (
                    "Select a saved map before starting "
                    f"{requested_mode.value.capitalize()} mode"
                )
                self.get_logger().warning(message)
                return False, message

            if self.mode == requested_mode:
                message = (
                    f"{requested_mode.value} mode is "
                    "already active"
                )
                self.get_logger().warning(message)
                return False, message

            stopped, stop_message = (
                self.stop_current_mode()
            )

            if not stopped:
                return False, (
                    "Unable to stop previous mode: "
                    f"{stop_message}"
                )

            if requested_mode == OperatingMode.MANUAL:
                self.requested_mode = requested_mode
                self.publish_mode(OperatingMode.MANUAL)

                message = "Manual mode activated"
                self.get_logger().info(message)
                return True, message

            launch_file = self.launch_files[
                requested_mode
            ]

            self.requested_mode = requested_mode
            self.last_error = ""
            self.publish_mode(OperatingMode.STARTING)

            command = [
                "ros2",
                "launch",
                self.launch_package,
                launch_file,
                (
                    "use_sim_time:="
                    + (
                        "true"
                        if self.managed_use_sim_time
                        else "false"
                    )
                ),
            ]

            if requested_mode in (
                OperatingMode.LOCALIZATION,
                OperatingMode.NAVIGATION,
            ):
                command.append(
                    f"map:={self.selected_map_path}"
                )

            self.get_logger().info(
                "Starting operating mode: "
                + " ".join(command)
            )

            try:
                self.process = subprocess.Popen(
                    command,
                    start_new_session=True,
                )
                self.process_group_id = os.getpgid(
                    self.process.pid
                )
            except (
                OSError,
                subprocess.SubprocessError,
            ) as error:
                self.process = None
                self.process_group_id = None

                self.last_error = str(error)
                self.publish_mode(OperatingMode.ERROR)

                message = (
                    f"Failed to launch "
                    f"{requested_mode.value}: {error}"
                )
                self.get_logger().error(message)
                return False, message

            time.sleep(self.startup_grace_period)

            if self.process.poll() is not None:
                return_code = self.process.returncode
                process_group_id = self.process_group_id
                self.process = None

                if process_group_id is not None:
                    self.terminate_process_group(
                        process_group_id
                    )

                self.process_group_id = None

                self.last_error = (
                    f"{requested_mode.value} launch "
                    "exited during startup with return "
                    f"code {return_code}"
                )

                self.publish_mode(OperatingMode.ERROR)
                self.get_logger().error(self.last_error)
                return False, self.last_error

            self.publish_mode(requested_mode)

            message = (
                f"{requested_mode.value.capitalize()} "
                f"mode started with PID "
                f"{self.process.pid}"
            )
            self.get_logger().info(message)
            return True, message
        
    def process_group_exists(
        self,
        process_group_id: int,
    ) -> bool:
        try:
            os.killpg(process_group_id, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True

        return True

    def terminate_process_group(
        self,
        process_group_id: int,
    ) -> None:
        if not self.process_group_exists(
            process_group_id
        ):
            return

        if rclpy.ok(context=self.context):
            self.get_logger().warning(
                "Remaining mode processes detected in "
                f"group {process_group_id}; sending SIGTERM"
            )

        try:
            os.killpg(
                process_group_id,
                signal.SIGTERM,
            )
        except ProcessLookupError:
            return

        deadline = (
            time.monotonic() + self.kill_timeout
        )

        while time.monotonic() < deadline:
            if not self.process_group_exists(
                process_group_id
            ):
                return

            time.sleep(0.1)

        if rclpy.ok(context=self.context):
            self.get_logger().error(
                "Mode process group still exists; "
                f"sending SIGKILL to {process_group_id}"
            )

        try:
            os.killpg(
                process_group_id,
                signal.SIGKILL,
            )
        except ProcessLookupError:
            pass

    def stop_current_mode(
        self,
    ) -> tuple[bool, str]:
        with self.process_lock:
            if not self.process_is_running():
                self.clear_finished_process()
                self.requested_mode = OperatingMode.STOPPED
                self.publish_mode(OperatingMode.STOPPED)

                return True, "Operating mode stopped"

            assert self.process is not None

            process = self.process
            process_pid = process.pid

            process_group_id = (
                self.process_group_id
                if self.process_group_id is not None
                else os.getpgid(process_pid)
            )

            self.publish_mode(OperatingMode.STOPPING)

            if rclpy.ok(context=self.context):
                self.get_logger().info(
                    "Stopping operating-mode process group "
                    f"{process_group_id}"
                )

            try:
                os.killpg(
                    process_group_id,
                    signal.SIGINT,
                )

                process.wait(
                    timeout=self.shutdown_timeout
                )

            except subprocess.TimeoutExpired:
                if rclpy.ok(context=self.context):
                    self.get_logger().warning(
                        "Mode did not stop after SIGINT; "
                        "sending SIGTERM"
                    )

                try:
                    os.killpg(
                        process_group_id,
                        signal.SIGTERM,
                    )

                    process.wait(
                        timeout=self.kill_timeout
                    )

                except subprocess.TimeoutExpired:
                    if rclpy.ok(context=self.context):
                        self.get_logger().error(
                            "Mode did not stop after SIGTERM; "
                            "sending SIGKILL"
                        )

                    try:
                        os.killpg(
                            process_group_id,
                            signal.SIGKILL,
                        )
                    except ProcessLookupError:
                        pass

                    try:
                        process.wait(
                            timeout=self.kill_timeout
                        )
                    except subprocess.TimeoutExpired:
                        pass

            except ProcessLookupError:
                if rclpy.ok(context=self.context):
                    self.get_logger().warning(
                        "Operating-mode process group "
                        "no longer exists"
                    )

            except (
                OSError,
                subprocess.SubprocessError,
            ) as error:
                self.last_error = str(error)
                self.publish_mode(OperatingMode.ERROR)

                message = (
                    "Failed to stop operating mode: "
                    f"{error}"
                )

                if rclpy.ok(context=self.context):
                    self.get_logger().error(message)

                return False, message

            finally:
                self.process = None

            self.terminate_process_group(
                process_group_id
            )
            self.process_group_id = None

            self.requested_mode = OperatingMode.STOPPED
            self.publish_mode(OperatingMode.STOPPED)

            message = "Operating mode stopped"

            if rclpy.ok(context=self.context):
                self.get_logger().info(message)

            return True, message

    def monitor_process(self) -> None:
        with self.process_lock:
            if self.process is None:
                return

            return_code = self.process.poll()

            if return_code is None:
                return

            previous_mode = self.mode
            process_group_id = self.process_group_id

            self.process = None

            if process_group_id is not None:
                self.terminate_process_group(
                    process_group_id
                )

            self.process_group_id = None

            if previous_mode in (
                OperatingMode.STOPPING,
                OperatingMode.STOPPED,
            ):
                self.publish_mode(
                    OperatingMode.STOPPED
                )
                return

            self.last_error = (
                f"{self.requested_mode.value} mode "
                "exited unexpectedly with return code "
                f"{return_code}"
            )

            self.publish_mode(OperatingMode.ERROR)

            if rclpy.ok(context=self.context):
                self.get_logger().error(
                    self.last_error
                )

    def process_is_running(self) -> bool:
        return (
            self.process is not None
            and self.process.poll() is None
        )

    def clear_finished_process(self) -> None:
        if (
            self.process is not None
            and self.process.poll() is not None
        ):
            self.process = None

            if self.process_group_id is not None:
                self.terminate_process_group(
                    self.process_group_id
                )
                self.process_group_id = None

    def publish_mode(
        self,
        mode: OperatingMode,
    ) -> None:
        self.mode = mode

        if not rclpy.ok(context=self.context):
            return

        message = String()
        message.data = mode.value

        try:
            self.status_publisher.publish(message)
        except Exception:
            if rclpy.ok(context=self.context):
                raise

    def shutdown(self) -> None:
        if rclpy.ok(context=self.context):
            self.get_logger().info(
                "Operating-mode manager shutting down"
            )

        self.stop_current_mode()


def main(args=None) -> None:
    rclpy.init(args=args)

    node: Optional[ModeManagerNode] = None

    try:
        node = ModeManagerNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        if node is not None:
            node.shutdown()
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
