#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""Manage mutually exclusive robot operating modes and launch processes."""

from enum import Enum
import json
import math
import os
import signal
import subprocess
import threading
import time
from typing import Optional

import rclpy
from rclpy.executors import ExternalShutdownException
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
    """Represent the externally visible robot operating modes."""

    STOPPED = 'stopped'
    MANUAL = 'manual'
    MAPPING = 'mapping'
    LOCALIZATION = 'localization'
    NAVIGATION = 'navigation'
    STARTING = 'starting'
    STOPPING = 'stopping'
    ERROR = 'error'


class ModeManagerNode(Node):
    """Manage mutually exclusive robot operating modes."""

    def __init__(self) -> None:
        """Initialize parameters, ROS interfaces, and process state."""
        super().__init__('mode_manager')

        self.declare_parameter(
            'launch_package',
            'cpp_robotics_sim_ros',
        )
        self.declare_parameter(
            'mapping_launch_file',
            'slam_mapping.launch.py',
        )
        self.declare_parameter(
            'localization_launch_file',
            'amcl_localization.launch.py',
        )
        self.declare_parameter(
            'navigation_launch_file',
            'nav2_navigation.launch.py',
        )
        self.declare_parameter(
            'managed_use_sim_time',
            True,
        )
        self.declare_parameter(
            'startup_grace_period',
            3.0,
        )
        self.declare_parameter(
            'shutdown_timeout',
            10.0,
        )
        self.declare_parameter(
            'kill_timeout',
            3.0,
        )

        self.launch_package = str(
            self.get_parameter('launch_package').value
        )
        self.managed_use_sim_time = bool(
            self.get_parameter(
                'managed_use_sim_time'
            ).value
        )
        self.startup_grace_period = float(
            self.get_parameter(
                'startup_grace_period'
            ).value
        )
        self.shutdown_timeout = float(
            self.get_parameter('shutdown_timeout').value
        )
        self.kill_timeout = float(
            self.get_parameter('kill_timeout').value
        )

        self.launch_files = {
            OperatingMode.MAPPING: str(
                self.get_parameter(
                    'mapping_launch_file'
                ).value
            ),
            OperatingMode.LOCALIZATION: str(
                self.get_parameter(
                    'localization_launch_file'
                ).value
            ),
            OperatingMode.NAVIGATION: str(
                self.get_parameter(
                    'navigation_launch_file'
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
            '/mode/status',
            status_qos,
        )

        self.simulation_subscription = (
            self.create_subscription(
                String,
                '/simulation/status',
                self.simulation_status_callback,
                status_qos,
            )
        )

        self.selected_map_subscription = (
            self.create_subscription(
                String,
                '/localization/selected_map',
                self.selected_map_callback,
                status_qos,
            )
        )

        self.manual_service = self.create_service(
            Trigger,
            '/mode/manual',
            self.manual_callback,
        )
        self.mapping_service = self.create_service(
            Trigger,
            '/mode/mapping',
            self.mapping_callback,
        )
        self.localization_service = self.create_service(
            Trigger,
            '/mode/localization',
            self.localization_callback,
        )
        self.navigation_service = self.create_service(
            Trigger,
            '/mode/navigation',
            self.navigation_callback,
        )
        self.stop_service = self.create_service(
            Trigger,
            '/mode/stop',
            self.stop_callback,
        )

        self.process: Optional[subprocess.Popen] = None
        self.process_group_id: Optional[int] = None
        self.process_lock = threading.RLock()

        self.mode = OperatingMode.STOPPED
        self.requested_mode = OperatingMode.STOPPED
        self.simulation_state = 'unknown'
        self.selected_map_name = ''
        self.selected_map_path = ''
        self.last_error = ''
        self.shutdown_complete = False

        self.monitor_timer = self.create_timer(
            0.5,
            self.monitor_process,
        )

        self.publish_mode(OperatingMode.STOPPED)

        self.get_logger().info(
            'Operating-mode manager ready'
        )

    def validate_parameters(self) -> None:
        """Validate launch names and process timing parameters."""
        self.launch_package = self.launch_package.strip()

        if not self.launch_package:
            raise ValueError(
                'launch_package must not be empty'
            )

        for mode, launch_file in self.launch_files.items():
            normalized_launch_file = launch_file.strip()

            if not normalized_launch_file:
                raise ValueError(
                    f'{mode.value} launch file must not be empty'
                )

            self.launch_files[mode] = normalized_launch_file

        self.require_nonnegative_finite(
            'startup_grace_period',
            self.startup_grace_period,
        )
        self.require_positive_finite(
            'shutdown_timeout',
            self.shutdown_timeout,
        )
        self.require_positive_finite(
            'kill_timeout',
            self.kill_timeout,
        )

    @staticmethod
    def require_nonnegative_finite(
        name: str,
        value: float,
    ) -> None:
        """Require a finite numeric value that is not negative."""
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(
                f'{name} must be finite and nonnegative'
            )

    @staticmethod
    def require_positive_finite(
        name: str,
        value: float,
    ) -> None:
        """Require a finite numeric value greater than zero."""
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(
                f'{name} must be finite and greater than zero'
            )

    def simulation_status_callback(
        self,
        message: String,
    ) -> None:
        """Stop the active mode when simulation stops running."""
        previous_state = self.simulation_state
        self.simulation_state = message.data

        if (
            previous_state == self.simulation_state
            or self.simulation_state
            in ('running', 'starting')
        ):
            return

        if self.mode not in (
            OperatingMode.STOPPED,
            OperatingMode.ERROR,
        ):
            self.get_logger().warning(
                'Simulation is no longer running; '
                'stopping active operating mode'
            )

            self.stop_current_mode()

    def selected_map_callback(
        self,
        message: String,
    ) -> None:
        """Update the selected map from a validated JSON payload."""
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError:
            self.get_logger().error(
                'Received invalid selected-map payload'
            )
            return

        if not isinstance(payload, dict):
            self.get_logger().error(
                'Selected-map payload must be a JSON object'
            )
            return

        self.selected_map_name = str(
            payload.get('name', '')
        ).strip()
        self.selected_map_path = str(
            payload.get('yaml_path', '')
        ).strip()

    def manual_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        """Handle a request to activate manual mode."""
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
        """Handle a request to activate mapping mode."""
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
        """Handle a request to activate localization mode."""
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
        """Handle a request to activate navigation mode."""
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
        """Handle a request to stop the active mode."""
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
        """Populate and return a Trigger service response."""
        response.success = success
        response.message = message
        return response

    def activate_mode(
        self,
        requested_mode: OperatingMode,
    ) -> tuple[bool, str]:
        """Stop the previous mode and activate the requested mode."""
        with self.process_lock:
            if self.simulation_state != 'running':
                message = (
                    'Simulation must be running before '
                    'selecting an operating mode'
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
                    'Select a saved map before starting '
                    f'{requested_mode.value.capitalize()} mode'
                )
                self.get_logger().warning(message)
                return False, message

            if self.mode == requested_mode:
                message = (
                    f'{requested_mode.value} mode is '
                    'already active'
                )
                self.get_logger().warning(message)
                return False, message

            stopped, stop_message = (
                self.stop_current_mode()
            )

            if not stopped:
                return False, (
                    'Unable to stop previous mode: '
                    f'{stop_message}'
                )

            if requested_mode == OperatingMode.MANUAL:
                self.requested_mode = requested_mode
                self.publish_mode(OperatingMode.MANUAL)

                message = 'Manual mode activated'
                self.get_logger().info(message)
                return True, message

            launch_file = self.launch_files[
                requested_mode
            ]

            self.requested_mode = requested_mode
            self.last_error = ''
            self.publish_mode(OperatingMode.STARTING)

            command = [
                'ros2',
                'launch',
                self.launch_package,
                launch_file,
                (
                    'use_sim_time:='
                    + (
                        'true'
                        if self.managed_use_sim_time
                        else 'false'
                    )
                ),
            ]

            if requested_mode in (
                OperatingMode.LOCALIZATION,
                OperatingMode.NAVIGATION,
            ):
                command.append(
                    f'map:={self.selected_map_path}'
                )

            self.get_logger().info(
                'Starting operating mode: '
                + ' '.join(command)
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
                    f'Failed to launch '
                    f'{requested_mode.value}: {error}'
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
                    f'{requested_mode.value} launch '
                    'exited during startup with return '
                    f'code {return_code}'
                )

                self.publish_mode(OperatingMode.ERROR)
                self.get_logger().error(self.last_error)
                return False, self.last_error

            self.publish_mode(requested_mode)

            message = (
                f'{requested_mode.value.capitalize()} '
                f'mode started with PID '
                f'{self.process.pid}'
            )
            self.get_logger().info(message)
            return True, message

    def process_group_exists(
        self,
        process_group_id: int,
    ) -> bool:
        """Return whether a managed operating-system process group exists."""
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
    ) -> bool:
        """Terminate a process group and confirm that it disappeared."""
        if not self.process_group_exists(
            process_group_id
        ):
            return True

        if rclpy.ok(context=self.context):
            self.get_logger().warning(
                'Remaining mode processes detected in '
                f'group {process_group_id}; sending SIGTERM'
            )

        try:
            os.killpg(
                process_group_id,
                signal.SIGTERM,
            )
        except ProcessLookupError:
            return True
        except OSError as error:
            if rclpy.ok(context=self.context):
                self.get_logger().error(
                    'Unable to send SIGTERM to mode '
                    f'process group {process_group_id}: {error}'
                )
            return False

        deadline = (
            time.monotonic() + self.kill_timeout
        )

        while time.monotonic() < deadline:
            if not self.process_group_exists(
                process_group_id
            ):
                return True

            time.sleep(0.1)

        if rclpy.ok(context=self.context):
            self.get_logger().error(
                'Mode process group still exists; '
                f'sending SIGKILL to {process_group_id}'
            )

        try:
            os.killpg(
                process_group_id,
                signal.SIGKILL,
            )
        except ProcessLookupError:
            return True
        except OSError as error:
            if rclpy.ok(context=self.context):
                self.get_logger().error(
                    'Unable to send SIGKILL to mode '
                    f'process group {process_group_id}: {error}'
                )
            return False

        deadline = (
            time.monotonic() + self.kill_timeout
        )

        while time.monotonic() < deadline:
            if not self.process_group_exists(
                process_group_id
            ):
                return True

            time.sleep(0.1)

        if rclpy.ok(context=self.context):
            self.get_logger().error(
                'Mode process group survived SIGKILL: '
                f'{process_group_id}'
            )

        return False

    def cleanup_orphan_scan_frame_bridges(
        self,
    ) -> None:
        """
        Remove orphaned scan-frame bridge processes.

        These processes may escape the managed ROS 2 launch
        process group and become adopted by PID 1. The match is
        restricted to this project's exact static transform and
        node name.
        """
        pattern = (
            'static_transform_publisher '
            '0 0 0 0 0 0 '
            'lidar_link '
            'diffbot/base_link/diffbot_lidar '
            '--ros-args -r __node:=scan_frame_bridge'
        )

        try:
            result = subprocess.run(
                [
                    'pkill',
                    '-TERM',
                    '-f',
                    pattern,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=self.kill_timeout,
            )
        except (
            OSError,
            subprocess.SubprocessError,
        ) as error:
            if rclpy.ok(context=self.context):
                self.get_logger().warning(
                    'Unable to clean orphan scan-frame '
                    f'bridge: {error}'
                )
            return

        # pkill returns:
        #   0 when at least one process matched
        #   1 when nothing matched
        if (
            result.returncode == 0
            and rclpy.ok(context=self.context)
        ):
            self.get_logger().info(
                'Cleaned orphan scan-frame bridge process'
            )
        elif (
            result.returncode not in (0, 1)
            and rclpy.ok(context=self.context)
        ):
            self.get_logger().warning(
                'Scan-frame bridge cleanup returned code '
                f'{result.returncode}'
            )

    def stop_current_mode(
        self,
    ) -> tuple[bool, str]:
        """Stop the active mode process group and clear runtime state."""
        with self.process_lock:
            if not self.process_is_running():
                self.clear_finished_process()
                self.cleanup_orphan_scan_frame_bridges()
                self.requested_mode = OperatingMode.STOPPED
                self.publish_mode(OperatingMode.STOPPED)

                return True, 'Operating mode stopped'

            assert self.process is not None

            process = self.process
            process_pid = process.pid

            try:
                process_group_id = (
                    self.process_group_id
                    if self.process_group_id is not None
                    else os.getpgid(process_pid)
                )
            except ProcessLookupError:
                self.process = None
                self.process_group_id = None
                self.cleanup_orphan_scan_frame_bridges()
                self.requested_mode = OperatingMode.STOPPED
                self.publish_mode(OperatingMode.STOPPED)
                return True, 'Operating mode stopped'
            except OSError as error:
                self.process = None
                self.process_group_id = None
                self.last_error = str(error)
                self.publish_mode(OperatingMode.ERROR)

                message = (
                    'Failed to resolve operating-mode '
                    f'process group: {error}'
                )

                if rclpy.ok(context=self.context):
                    self.get_logger().error(message)

                return False, message

            self.publish_mode(OperatingMode.STOPPING)

            if rclpy.ok(context=self.context):
                self.get_logger().info(
                    'Stopping operating-mode process group '
                    f'{process_group_id}'
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
                        'Mode did not stop after SIGINT; '
                        'sending SIGTERM'
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
                            'Mode did not stop after SIGTERM; '
                            'sending SIGKILL'
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
                        'Operating-mode process group '
                        'no longer exists'
                    )

            except (
                OSError,
                subprocess.SubprocessError,
            ) as error:
                self.last_error = str(error)
                self.publish_mode(OperatingMode.ERROR)

                message = (
                    'Failed to stop operating mode: '
                    f'{error}'
                )

                if rclpy.ok(context=self.context):
                    self.get_logger().error(message)

                return False, message

            finally:
                self.process = None

            termination_confirmed = (
                self.terminate_process_group(
                    process_group_id
                )
            )
            self.process_group_id = None

            self.cleanup_orphan_scan_frame_bridges()

            if not termination_confirmed:
                self.last_error = (
                    'Unable to confirm termination of '
                    'operating-mode process group '
                    f'{process_group_id}'
                )
                self.requested_mode = (
                    OperatingMode.ERROR
                )
                self.publish_mode(OperatingMode.ERROR)

                if rclpy.ok(context=self.context):
                    self.get_logger().error(
                        self.last_error
                    )

                return False, self.last_error

            self.requested_mode = OperatingMode.STOPPED
            self.publish_mode(OperatingMode.STOPPED)

            message = 'Operating mode stopped'

            if rclpy.ok(context=self.context):
                self.get_logger().info(message)

            return True, message

    def monitor_process(self) -> None:
        """Detect and report an unexpected managed-process exit."""
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
                f'{self.requested_mode.value} mode '
                'exited unexpectedly with return code '
                f'{return_code}'
            )

            self.publish_mode(OperatingMode.ERROR)

            if rclpy.ok(context=self.context):
                self.get_logger().error(
                    self.last_error
                )

    def process_is_running(self) -> bool:
        """Return whether the managed launch process is still running."""
        return (
            self.process is not None
            and self.process.poll() is None
        )

    def clear_finished_process(self) -> None:
        """Clear and clean a managed process that has already exited."""
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
        """Publish the current operating mode when ROS is active."""
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
        """Stop managed processes exactly once during node shutdown."""
        if self.shutdown_complete:
            return

        self.shutdown_complete = True

        if rclpy.ok(context=self.context):
            self.get_logger().info(
                'Operating-mode manager shutting down'
            )

        self.stop_current_mode()


def main(args=None) -> None:
    """Run the operating-mode manager node."""
    rclpy.init(args=args)

    node: Optional[ModeManagerNode] = None

    try:
        node = ModeManagerNode()
        rclpy.spin(node)

    except (
        KeyboardInterrupt,
        ExternalShutdownException,
    ):
        pass

    finally:
        if node is not None:
            node.shutdown()
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
