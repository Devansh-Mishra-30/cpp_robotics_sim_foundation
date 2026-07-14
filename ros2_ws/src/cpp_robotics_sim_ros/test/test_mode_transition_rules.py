#!/usr/bin/env python3

import importlib.util
import threading
from pathlib import Path
from types import ModuleType


def load_mode_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "mode_manager_node.py"
    )

    specification = importlib.util.spec_from_file_location(
        "mode_manager_node",
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            "Unable to load mode manager module"
        )

    module = importlib.util.module_from_spec(
        specification
    )
    specification.loader.exec_module(module)
    return module


MODULE = load_mode_manager_module()
ModeManagerNode = MODULE.ModeManagerNode
OperatingMode = MODULE.OperatingMode


class TestLogger:
    def __init__(self) -> None:
        self.messages = []

    def warning(self, message: str) -> None:
        self.messages.append(("warning", message))

    def info(self, message: str) -> None:
        self.messages.append(("info", message))

    def error(self, message: str) -> None:
        self.messages.append(("error", message))


def make_manager(
    *,
    simulation_state: str = "running",
    mode=OperatingMode.STOPPED,
    selected_map_path: str = "",
    stop_result=(True, "Operating mode stopped"),
):
    manager = object.__new__(ModeManagerNode)

    manager.process_lock = threading.RLock()
    manager.simulation_state = simulation_state
    manager.mode = mode
    manager.requested_mode = mode

    manager.selected_map_name = (
        "test_map"
        if selected_map_path
        else ""
    )
    manager.selected_map_path = selected_map_path

    manager.last_error = ""
    manager.process = None
    manager.process_group_id = None

    manager.managed_use_sim_time = True
    manager.startup_grace_period = 0.0

    manager.launch_package = (
        "cpp_robotics_sim_ros"
    )
    manager.launch_files = {
        OperatingMode.MAPPING:
            "slam_mapping.launch.py",
        OperatingMode.LOCALIZATION:
            "amcl_localization.launch.py",
        OperatingMode.NAVIGATION:
            "nav2_navigation.launch.py",
    }

    logger = TestLogger()
    published_modes = []
    stop_calls = []

    manager.get_logger = lambda: logger

    def publish_mode(mode_to_publish) -> None:
        published_modes.append(mode_to_publish)
        manager.mode = mode_to_publish

    manager.publish_mode = publish_mode

    def stop_current_mode():
        stop_calls.append(True)
        return stop_result

    manager.stop_current_mode = stop_current_mode

    return (
        manager,
        logger,
        published_modes,
        stop_calls,
    )


def test_rejects_mode_when_simulation_is_stopped() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager(
            simulation_state="stopped"
        )
    )

    success, message = manager.activate_mode(
        OperatingMode.MANUAL
    )

    assert success is False
    assert "Simulation must be running" in message
    assert published_modes == []
    assert stop_calls == []


def test_localization_requires_selected_map() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager()
    )

    success, message = manager.activate_mode(
        OperatingMode.LOCALIZATION
    )

    assert success is False
    assert "Select a saved map" in message
    assert "Localization" in message
    assert published_modes == []
    assert stop_calls == []


def test_navigation_requires_selected_map() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager()
    )

    success, message = manager.activate_mode(
        OperatingMode.NAVIGATION
    )

    assert success is False
    assert "Select a saved map" in message
    assert "Navigation" in message
    assert published_modes == []
    assert stop_calls == []


def test_rejects_already_active_mode() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager(
            mode=OperatingMode.MANUAL
        )
    )

    success, message = manager.activate_mode(
        OperatingMode.MANUAL
    )

    assert success is False
    assert "already active" in message
    assert published_modes == []
    assert stop_calls == []


def test_manual_mode_stops_previous_mode_first() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager(
            mode=OperatingMode.MAPPING
        )
    )

    success, message = manager.activate_mode(
        OperatingMode.MANUAL
    )

    assert success is True
    assert message == "Manual mode activated"
    assert len(stop_calls) == 1
    assert published_modes == [
        OperatingMode.MANUAL
    ]
    assert manager.requested_mode == (
        OperatingMode.MANUAL
    )


def test_failed_stop_prevents_mode_change() -> None:
    manager, _, published_modes, stop_calls = (
        make_manager(
            mode=OperatingMode.MAPPING,
            stop_result=(
                False,
                "process did not stop",
            ),
        )
    )

    success, message = manager.activate_mode(
        OperatingMode.MANUAL
    )

    assert success is False
    assert "Unable to stop previous mode" in message
    assert "process did not stop" in message
    assert len(stop_calls) == 1
    assert published_modes == []
