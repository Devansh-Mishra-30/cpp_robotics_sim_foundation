#!/usr/bin/env python3

import importlib.util
import threading
from pathlib import Path
from types import ModuleType

import pytest
from std_msgs.msg import String


def load_simulation_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "simulation_manager_node.py"
    )

    specification = importlib.util.spec_from_file_location(
        "simulation_manager_node",
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            "Unable to load simulation manager module"
        )

    module = importlib.util.module_from_spec(
        specification
    )
    specification.loader.exec_module(module)
    return module


MODULE = load_simulation_manager_module()
SimulationManagerNode = MODULE.SimulationManagerNode
SimulationState = MODULE.SimulationState


def make_manager(
    *,
    state=SimulationState.STOPPED,
    process_running: bool = False,
):
    manager = object.__new__(SimulationManagerNode)

    manager.environment_names = [
        "warehouse",
        "hospital",
    ]
    manager.selected_environment = "warehouse"
    manager.state = state
    manager.process_lock = threading.RLock()

    published_statuses = []
    log_messages = []

    manager.publish_environment_status = (
        lambda *, state, message:
        published_statuses.append(
            {
                "state": state,
                "message": message,
            }
        )
    )

    manager.process_is_running = (
        lambda: process_running
    )

    class Logger:
        def info(self, message: str) -> None:
            log_messages.append(message)

    manager.get_logger = lambda: Logger()

    return manager, published_statuses, log_messages


def environment_message(value: str) -> String:
    message = String()
    message.data = value
    return message


@pytest.mark.parametrize(
    "requested_environment",
    [
        "warehouse",
        "hospital",
        " Warehouse ",
        "HOSPITAL",
    ],
)
def test_accepts_allowlisted_environments(
    requested_environment: str,
) -> None:
    manager, statuses, _ = make_manager()

    manager.environment_request_callback(
        environment_message(requested_environment)
    )

    assert manager.selected_environment == (
        requested_environment.strip().lower()
    )
    assert statuses[-1]["state"] == "selected"


@pytest.mark.parametrize(
    "requested_environment",
    [
        "",
        " ",
        "office",
        "warehouse/../hospital",
        "../warehouse",
        "../../tmp",
        "warehouse;rm",
        "warehouse map",
    ],
)
def test_rejects_unsupported_environments(
    requested_environment: str,
) -> None:
    manager, statuses, _ = make_manager()

    manager.environment_request_callback(
        environment_message(requested_environment)
    )

    assert manager.selected_environment == "warehouse"
    assert statuses[-1]["state"] == (
        "invalid_request"
    )


@pytest.mark.parametrize(
    "state",
    [
        SimulationState.STARTING,
        SimulationState.RUNNING,
        SimulationState.STOPPING,
    ],
)
def test_rejects_environment_change_while_busy(
    state,
) -> None:
    manager, statuses, _ = make_manager(
        state=state
    )

    manager.environment_request_callback(
        environment_message("hospital")
    )

    assert manager.selected_environment == "warehouse"
    assert statuses[-1]["state"] == "locked"


def test_rejects_environment_change_when_process_runs() -> None:
    manager, statuses, _ = make_manager(
        state=SimulationState.STOPPED,
        process_running=True,
    )

    manager.environment_request_callback(
        environment_message("hospital")
    )

    assert manager.selected_environment == "warehouse"
    assert statuses[-1]["state"] == "locked"


def test_allows_change_after_simulation_stops() -> None:
    manager, statuses, _ = make_manager(
        state=SimulationState.STOPPED,
        process_running=False,
    )

    manager.environment_request_callback(
        environment_message("hospital")
    )

    assert manager.selected_environment == "hospital"
    assert statuses[-1]["state"] == "selected"
