#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from enum import Enum
import json
import os
import signal
import subprocess
import threading
import time
from typing import Optional

from ament_index_python.packages import (
    get_package_share_directory,
)
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


class SimulationState(str, Enum):
    STOPPED = 'stopped'
    STARTING = 'starting'
    RUNNING = 'running'
    STOPPING = 'stopping'
    ERROR = 'error'


class SimulationManagerNode(Node):
    """Manage simulation startup, state, and shutdown."""

    def __init__(self) -> None:
        super().__init__('simulation_manager')

        self.declare_parameter(
            'launch_package',
            'cpp_robotics_sim_ros',
        )
        self.declare_parameter(
            'launch_file',
            'interactive_control.launch.py',
        )
        self.declare_parameter(
            'managed_use_sim_time',
            True,
        )

        self.declare_parameter(
            'default_environment',
            'warehouse',
        )
        self.declare_parameter(
            'environment_names',
            [
                'warehouse',
                'hospital',
            ],
        )
        self.declare_parameter(
            'warehouse_world_file',
            'warehouse_world.sdf',
        )
        self.declare_parameter(
            'hospital_world_file',
            'hospital_world.sdf',
        )

        self.declare_parameter(
            'startup_grace_period',
            4.0,
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
        self.launch_file = str(
            self.get_parameter('launch_file').value
        )
        self.managed_use_sim_time = bool(
            self.get_parameter(
                'managed_use_sim_time'
            ).value
        )

        self.environment_names = [
            str(name)
            for name in self.get_parameter(
                'environment_names'
            ).value
        ]
        self.selected_environment = str(
            self.get_parameter(
                'default_environment'
            ).value
        )

        self.environment_world_files = {
            'warehouse': str(
                self.get_parameter(
                    'warehouse_world_file'
                ).value
            ),
            'hospital': str(
                self.get_parameter(
                    'hospital_world_file'
                ).value
            ),
        }

        self.package_share_directory = (
            get_package_share_directory(
                self.launch_package
            )
        )

        self.startup_grace_period = float(
            self.get_parameter('startup_grace_period').value
        )
        self.shutdown_timeout = float(
            self.get_parameter('shutdown_timeout').value
        )
        self.kill_timeout = float(
            self.get_parameter('kill_timeout').value
        )

        self.validate_parameters()

        status_qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )

        self.status_publisher = self.create_publisher(
            String,
            '/simulation/status',
            status_qos,
        )

        self.environment_status_publisher = (
            self.create_publisher(
                String,
                '/simulation/environment_status',
                status_qos,
            )
        )

        self.environment_request_subscription = (
            self.create_subscription(
                String,
                '/simulation/environment_request',
                self.environment_request_callback,
                10,
            )
        )

        self.start_service = self.create_service(
            Trigger,
            '/simulation/start',
            self.start_callback,
        )

        self.stop_service = self.create_service(
            Trigger,
            '/simulation/stop',
            self.stop_callback,
        )

        self.reset_service = self.create_service(
            Trigger,
            '/simulation/reset',
            self.reset_callback,
        )

        self.process: Optional[subprocess.Popen] = None
        self.process_lock = threading.RLock()
        self.state = SimulationState.STOPPED
        self.last_error = ''

        self.monitor_timer = self.create_timer(
            0.5,
            self.monitor_process,
        )

        self.set_state(SimulationState.STOPPED)
        self.publish_environment_status(
            state='ready',
            message=(
                'Environment selection ready'
            ),
        )

        self.get_logger().info(
            'Simulation manager ready'
        )
        self.get_logger().info(
            f'Managed launch: '
            f'{self.launch_package} {self.launch_file}'
        )

    def validate_parameters(self) -> None:
        if not self.launch_package:
            raise ValueError(
                'launch_package must not be empty'
            )

        if not self.launch_file:
            raise ValueError(
                'launch_file must not be empty'
            )

        if not self.environment_names:
            raise ValueError(
                'environment_names must not be empty'
            )

        if (
            self.selected_environment
            not in self.environment_names
        ):
            raise ValueError(
                'default_environment must be one of '
                f'{self.environment_names}'
            )

        missing_world_entries = [
            environment
            for environment in self.environment_names
            if environment
            not in self.environment_world_files
        ]

        if missing_world_entries:
            raise ValueError(
                'Missing world-file configuration for: '
                f'{missing_world_entries}'
            )

        for environment in self.environment_names:
            world_file = self.environment_world_files[
                environment
            ]

            if not world_file:
                raise ValueError(
                    'World filename must not be empty for '
                    f'{environment}'
                )

        if self.startup_grace_period < 0.0:
            raise ValueError(
                'startup_grace_period must not be negative'
            )

        if self.shutdown_timeout <= 0.0:
            raise ValueError(
                'shutdown_timeout must be greater than zero'
            )

        if self.kill_timeout <= 0.0:
            raise ValueError(
                'kill_timeout must be greater than zero'
            )

    def environment_request_callback(
        self,
        message: String,
    ) -> None:
        requested_environment = message.data.strip().lower()

        if not requested_environment:
            self.publish_environment_status(
                state='invalid_request',
                message=(
                    'Environment request must not be empty'
                ),
            )
            return

        if (
            requested_environment
            not in self.environment_names
        ):
            self.publish_environment_status(
                state='invalid_request',
                message=(
                    'Unsupported environment: '
                    f'{requested_environment}'
                ),
            )
            return

        with self.process_lock:
            if (
                self.process_is_running()
                or self.state
                in (
                    SimulationState.STARTING,
                    SimulationState.RUNNING,
                    SimulationState.STOPPING,
                )
            ):
                self.publish_environment_status(
                    state='locked',
                    message=(
                        'Stop the simulation before changing '
                        'the environment'
                    ),
                )
                return

            self.selected_environment = (
                requested_environment
            )

        self.get_logger().info(
            'Selected simulation environment: '
            f'{self.selected_environment}'
        )

        self.publish_environment_status(
            state='selected',
            message=(
                'Selected environment: '
                f'{self.selected_environment}'
            ),
        )

    def resolve_selected_world_path(self) -> str:
        world_filename = self.environment_world_files[
            self.selected_environment
        ]

        world_path = os.path.join(
            self.package_share_directory,
            'worlds',
            world_filename,
        )

        if not os.path.isfile(world_path):
            raise FileNotFoundError(
                'World file does not exist: '
                f'{world_path}'
            )

        return world_path

    def publish_environment_status(
        self,
        state: str,
        message: str,
    ) -> None:
        if not rclpy.ok(context=self.context):
            return

        world_filename = self.environment_world_files.get(
            self.selected_environment,
            '',
        )

        payload = {
            'state': state,
            'message': message,
            'selected_environment': (
                self.selected_environment
            ),
            'available_environments': (
                self.environment_names
            ),
            'world_file': world_filename,
            'selection_locked': (
                self.state
                != SimulationState.STOPPED
                or self.process_is_running()
            ),
        }

        ros_message = String()
        ros_message.data = json.dumps(
            payload,
            separators=(',', ':'),
        )

        self.environment_status_publisher.publish(
            ros_message
        )

    def start_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request

        success, message = self.start_simulation()
        response.success = success
        response.message = message
        return response

    def stop_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request

        success, message = self.stop_simulation()
        response.success = success
        response.message = message
        return response

    def reset_callback(
        self,
        request: Trigger.Request,
        response: Trigger.Response,
    ) -> Trigger.Response:
        del request

        self.get_logger().info(
            'Simulation reset requested'
        )

        stopped, stop_message = self.stop_simulation()

        if not stopped:
            response.success = False
            response.message = (
                f'Reset failed while stopping: {stop_message}'
            )
            return response

        time.sleep(1.0)

        started, start_message = self.start_simulation()

        response.success = started
        response.message = (
            'Simulation reset successfully'
            if started
            else f'Reset failed while starting: {start_message}'
        )

        return response

    def start_simulation(self) -> tuple[bool, str]:
        with self.process_lock:
            if self.process_is_running():
                message = (
                    'Simulation is already running'
                )
                self.get_logger().warning(message)
                return False, message

            self.clear_finished_process()
            self.last_error = ''
            self.set_state(SimulationState.STARTING)

            try:
                selected_world_path = (
                    self.resolve_selected_world_path()
                )
            except (KeyError, FileNotFoundError) as error:
                self.last_error = str(error)
                self.set_state(SimulationState.ERROR)

                self.publish_environment_status(
                    state='error',
                    message=self.last_error,
                )

                self.get_logger().error(
                    self.last_error
                )
                return False, self.last_error

            command = [
                'ros2',
                'launch',
                self.launch_package,
                self.launch_file,
                f'world:={selected_world_path}',
                f"use_sim_time:={'true' if self.managed_use_sim_time else 'false'}",
            ]

            self.get_logger().info(
                'Starting simulation: '
                + ' '.join(command)
            )

            try:
                self.process = subprocess.Popen(
                    command,
                    start_new_session=True,
                )
            except (OSError, subprocess.SubprocessError) as error:
                self.process = None
                self.last_error = str(error)
                self.set_state(SimulationState.ERROR)

                message = (
                    f'Failed to start simulation: {error}'
                )
                self.get_logger().error(message)
                return False, message

            time.sleep(self.startup_grace_period)

            if self.process.poll() is not None:
                return_code = self.process.returncode
                self.last_error = (
                    'Simulation launch exited during startup '
                    f'with return code {return_code}'
                )
                self.process = None
                self.set_state(SimulationState.ERROR)

                self.get_logger().error(self.last_error)
                return False, self.last_error

            self.set_state(SimulationState.RUNNING)
            self.publish_environment_status(
                state='running',
                message=(
                    'Simulation running in '
                    f'{self.selected_environment}'
                ),
            )

            message = (
                f'Simulation started with PID '
                f'{self.process.pid}'
            )
            self.get_logger().info(message)
            return True, message

    def stop_simulation(self) -> tuple[bool, str]:
        with self.process_lock:
            if not self.process_is_running():
                self.clear_finished_process()
                self.cleanup_remaining_processes()
                self.set_state(SimulationState.STOPPED)

                message = 'Simulation is already stopped'
                self.get_logger().info(message)
                return True, message

            assert self.process is not None

            process = self.process
            process_pid = process.pid

            self.set_state(SimulationState.STOPPING)

            self.get_logger().info(
                f'Stopping simulation process group {process_pid}'
            )

            try:
                os.killpg(
                    os.getpgid(process_pid),
                    signal.SIGINT,
                )

                process.wait(
                    timeout=self.shutdown_timeout
                )

            except subprocess.TimeoutExpired:
                self.get_logger().warning(
                    'Simulation did not stop after SIGINT; '
                    'sending SIGTERM'
                )

                try:
                    os.killpg(
                        os.getpgid(process_pid),
                        signal.SIGTERM,
                    )
                    process.wait(
                        timeout=self.kill_timeout
                    )

                except subprocess.TimeoutExpired:
                    self.get_logger().error(
                        'Simulation did not stop after SIGTERM; '
                        'sending SIGKILL'
                    )

                    try:
                        os.killpg(
                            os.getpgid(process_pid),
                            signal.SIGKILL,
                        )
                    except ProcessLookupError:
                        pass

                    process.wait(
                        timeout=self.kill_timeout
                    )

            except ProcessLookupError:
                self.get_logger().warning(
                    'Simulation process group no longer exists'
                )

            except (OSError, subprocess.SubprocessError) as error:
                self.last_error = str(error)
                self.set_state(SimulationState.ERROR)

                message = (
                    f'Failed to stop simulation cleanly: {error}'
                )
                self.get_logger().error(message)
                return False, message

            finally:
                self.process = None

            self.cleanup_remaining_processes()
            self.set_state(SimulationState.STOPPED)
            self.publish_environment_status(
                state='selected',
                message=(
                    'Simulation stopped; environment '
                    'selection unlocked'
                ),
            )

            message = 'Simulation stopped successfully'

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

            previous_state = self.state
            self.process = None

            if previous_state in (
                SimulationState.STOPPING,
                SimulationState.STOPPED,
            ):
                self.set_state(SimulationState.STOPPED)
                return

            self.last_error = (
                'Simulation process exited unexpectedly '
                f'with return code {return_code}'
            )

            self.set_state(SimulationState.ERROR)
            self.get_logger().error(self.last_error)

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

    def set_state(
        self,
        new_state: SimulationState,
    ) -> None:
        state_changed = new_state != self.state
        self.state = new_state

        # SIGINT may invalidate the ROS context before shutdown cleanup
        # completes. Process cleanup must continue even when publishing
        # status is no longer possible.
        if not rclpy.ok(context=self.context):
            return

        message = String()
        message.data = new_state.value

        try:
            self.status_publisher.publish(message)
        except Exception as error:
            # Publishing is noncritical during shutdown. The managed
            # simulation process still needs to be terminated.
            if rclpy.ok(context=self.context):
                raise error
            return

        if state_changed:
            self.get_logger().info(
                f'Simulation state: {new_state.value}'
            )

    def cleanup_remaining_processes(self) -> None:
        """
        Remove known detached simulation processes.

        This is a fallback for processes that escape the managed
        ROS 2 launch process group after normal process-group
        shutdown.
        """
        process_patterns = [
            'gz sim',
            'gzserver',
            'gzclient',
            'ros2 launch cpp_robotics_sim_ros '
            'interactive_control.launch.py',
        ]

        for pattern in process_patterns:
            result = subprocess.run(
                [
                    'pgrep',
                    '-f',
                    pattern,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            process_ids = []

            for line in result.stdout.splitlines():
                try:
                    process_id = int(line.strip())
                except ValueError:
                    continue

                if process_id == os.getpid():
                    continue

                process_ids.append(process_id)

            for process_id in process_ids:
                try:
                    os.kill(process_id, signal.SIGTERM)
                    self.get_logger().warning(
                        'Terminated remaining process '
                        f'{process_id}: {pattern}'
                    )
                except ProcessLookupError:
                    pass
                except PermissionError as error:
                    self.get_logger().error(
                        f'Unable to terminate process '
                        f'{process_id}: {error}'
                    )

        time.sleep(1.0)

        for pattern in process_patterns:
            result = subprocess.run(
                [
                    'pgrep',
                    '-f',
                    pattern,
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            for line in result.stdout.splitlines():
                try:
                    process_id = int(line.strip())
                except ValueError:
                    continue

                if process_id == os.getpid():
                    continue

                try:
                    os.kill(process_id, signal.SIGKILL)
                    self.get_logger().error(
                        'Force-killed remaining process '
                        f'{process_id}: {pattern}'
                    )
                except ProcessLookupError:
                    pass
                except PermissionError as error:
                    self.get_logger().error(
                        f'Unable to force-kill process '
                        f'{process_id}: {error}'
                    )

    def shutdown(self) -> None:
        if rclpy.ok(context=self.context):
            self.get_logger().info(
                'Simulation manager shutting down'
            )

        success, message = self.stop_simulation()

        if (
            not success
            and rclpy.ok(context=self.context)
        ):
            self.get_logger().error(message)

        if rclpy.ok(context=self.context):
            self.get_logger().info(
                'Simulation shutdown cleanup complete'
            )


def main(args=None) -> None:
    rclpy.init(args=args)

    node: Optional[SimulationManagerNode] = None

    try:
        node = SimulationManagerNode()
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
