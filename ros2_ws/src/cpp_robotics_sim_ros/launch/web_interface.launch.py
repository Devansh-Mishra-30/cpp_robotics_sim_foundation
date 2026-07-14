import atexit
import fcntl
import os
import shutil
from pathlib import Path

from ament_index_python.packages import (
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    ExecuteProcess,
    LogInfo,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.substitutions import (
    LaunchConfiguration,
    PythonExpression,
)
from launch_ros.actions import Node


_LOCK_FILE_HANDLE = None
PACKAGE_NAME = "cpp_robotics_sim_ros"


def acquire_single_instance_lock() -> None:
    global _LOCK_FILE_HANDLE

    lock_path = (
        Path.home()
        / ".ros"
        / "cpp_robotics_sim"
        / "web_interface.lock"
    )

    lock_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lock_file = lock_path.open(
        "w",
        encoding="utf-8",
    )

    try:
        fcntl.flock(
            lock_file.fileno(),
            fcntl.LOCK_EX | fcntl.LOCK_NB,
        )
    except BlockingIOError as error:
        lock_file.close()

        raise RuntimeError(
            "Another dashboard instance is already running."
        ) from error

    lock_file.write(str(os.getpid()))
    lock_file.flush()

    _LOCK_FILE_HANDLE = lock_file


def release_single_instance_lock() -> None:
    global _LOCK_FILE_HANDLE

    if _LOCK_FILE_HANDLE is None:
        return

    try:
        fcntl.flock(
            _LOCK_FILE_HANDLE.fileno(),
            fcntl.LOCK_UN,
        )
    finally:
        _LOCK_FILE_HANDLE.close()
        _LOCK_FILE_HANDLE = None


def validate_workspace(
    package_share: Path,
) -> None:
    resolved = str(package_share.resolve())

    expected_fragment = (
        "/ros2_ws/install/"
        f"{PACKAGE_NAME}/share/{PACKAGE_NAME}"
    )

    if expected_fragment not in resolved:
        raise RuntimeError(
            "Wrong ROS overlay selected.\n"
            "Source only:\n"
            "  ros2_ws/install/setup.bash\n"
            f"Resolved package share:\n  {resolved}"
        )


def create_browser_action(
    dashboard_port,
    open_browser,
):
    dashboard_url = PythonExpression(
        [
            "'http://localhost:' + str(",
            dashboard_port,
            ")",
        ]
    )

    if shutil.which("powershell.exe"):
        command = [
            "powershell.exe",
            "-NoProfile",
            "-Command",
            "Start-Process",
            dashboard_url,
        ]
    elif shutil.which("cmd.exe"):
        command = [
            "cmd.exe",
            "/C",
            "start",
            "",
            dashboard_url,
        ]
    elif shutil.which("xdg-open"):
        command = [
            "xdg-open",
            dashboard_url,
        ]
    else:
        return LogInfo(
            msg=(
                "Open http://localhost:8080 manually."
            )
        )

    return TimerAction(
        period=2.0,
        actions=[
            ExecuteProcess(
                cmd=command,
                output="screen",
                condition=IfCondition(open_browser),
            ),
        ],
    )


def generate_launch_description():
    acquire_single_instance_lock()

    atexit.register(
        release_single_instance_lock
    )

    websocket_port = LaunchConfiguration(
        "websocket_port"
    )

    dashboard_port = LaunchConfiguration(
        "dashboard_port"
    )

    open_browser = LaunchConfiguration(
        "open_browser"
    )

    package_share = Path(
        get_package_share_directory(
            PACKAGE_NAME
        )
    )

    validate_workspace(package_share)

    dashboard_directory = (
        package_share
        / "web"
        / "dashboard"
    )

    simulation_manager_config = (
        package_share
        / "config"
        / "simulation_manager.yaml"
    )

    mode_manager_config = (
        package_share
        / "config"
        / "mode_manager.yaml"
    )

    mapping_manager_config = (
        package_share
        / "config"
        / "mapping_manager.yaml"
    )

    localization_manager_config = (
        package_share
        / "config"
        / "localization_manager.yaml"
    )

    required_paths = (
        dashboard_directory,
        simulation_manager_config,
        mode_manager_config,
        mapping_manager_config,
        localization_manager_config,
    )

    missing_paths = [
        str(path)
        for path in required_paths
        if not path.exists()
    ]

    if missing_paths:
        raise RuntimeError(
            "Required installed files are missing:\n"
            + "\n".join(
                f"  {path}"
                for path in missing_paths
            )
        )

    simulation_manager = Node(
        package=PACKAGE_NAME,
        executable="simulation_manager_node.py",
        name="simulation_manager",
        output="screen",
        parameters=[
            str(simulation_manager_config),
            {
                "use_sim_time": False,
            },
        ],
    )

    mode_manager = Node(
        package=PACKAGE_NAME,
        executable="mode_manager_node.py",
        name="mode_manager",
        output="screen",
        parameters=[
            str(mode_manager_config),
            {
                "use_sim_time": False,
            },
        ],
    )

    mapping_manager = Node(
        package=PACKAGE_NAME,
        executable="mapping_manager_node.py",
        name="mapping_manager",
        output="screen",
        parameters=[
            str(mapping_manager_config),
            {
                "use_sim_time": False,
            },
        ],
    )

    localization_manager = Node(
        package=PACKAGE_NAME,
        executable="localization_manager_node.py",
        name="localization_manager",
        output="screen",
        parameters=[
            str(localization_manager_config),
            {
                "use_sim_time": False,
            },
        ],
    )

    rosbridge_websocket = Node(
        package="rosbridge_server",
        executable="rosbridge_websocket",
        name="rosbridge_websocket",
        output="screen",
        parameters=[
            {
                "port": websocket_port,
                "address": "0.0.0.0",
                "retry_startup_delay": 5.0,
                "fragment_timeout": 600,
                "delay_between_messages": 0.0,
                "max_message_size": 10_000_000,
                "unregister_timeout": 10.0,
                "use_compression": False,
            },
        ],
    )

    dashboard_server = ExecuteProcess(
        cmd=[
            "python3",
            "-m",
            "http.server",
            dashboard_port,
            "--bind",
            "0.0.0.0",
            "--directory",
            str(dashboard_directory),
        ],
        output="screen",
    )

    browser_action = create_browser_action(
        dashboard_port,
        open_browser,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "websocket_port",
                default_value="9090",
                description="Rosbridge WebSocket port",
            ),
            DeclareLaunchArgument(
                "dashboard_port",
                default_value="8080",
                description="Dashboard HTTP port",
            ),
            DeclareLaunchArgument(
                "open_browser",
                default_value="true",
                description=(
                    "Open the dashboard automatically"
                ),
            ),
            LogInfo(
                msg=(
                    "Dashboard single-instance lock acquired."
                )
            ),
            LogInfo(
                msg=[
                    "Package share: ",
                    str(package_share),
                ]
            ),
            LogInfo(
                msg=[
                    "Dashboard URL: http://localhost:",
                    dashboard_port,
                ]
            ),
            simulation_manager,
            mode_manager,
            mapping_manager,
            localization_manager,
            rosbridge_websocket,
            dashboard_server,
            browser_action,
        ]
    )
