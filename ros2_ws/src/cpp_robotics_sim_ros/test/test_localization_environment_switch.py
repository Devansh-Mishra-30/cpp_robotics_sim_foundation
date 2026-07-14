#!/usr/bin/env python3

import importlib.util
import json
from pathlib import Path
from types import ModuleType

from std_msgs.msg import String


def load_localization_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "localization_manager_node.py"
    )

    specification = importlib.util.spec_from_file_location(
        "localization_manager_node",
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            "Unable to load localization manager module"
        )

    module = importlib.util.module_from_spec(
        specification
    )
    specification.loader.exec_module(module)
    return module


MODULE = load_localization_manager_module()
LocalizationManagerNode = (
    MODULE.LocalizationManagerNode
)


def make_manager(
    *,
    selected_environment: str = "warehouse",
    selected_map_environment: str = "warehouse",
):
    manager = object.__new__(
        LocalizationManagerNode
    )

    manager.selected_environment = (
        selected_environment
    )
    manager.selected_map_environment = (
        selected_map_environment
    )
    manager.selected_map_name = "test_map"
    manager.selected_map_path = (
        "/tmp/maps/warehouse/test_map.yaml"
    )

    published_maps = []
    published_statuses = []
    warnings = []

    manager.publish_selected_map = (
        lambda: published_maps.append(
            {
                "name": manager.selected_map_name,
                "environment": (
                    manager.selected_map_environment
                ),
                "path": manager.selected_map_path,
            }
        )
    )

    manager.publish_status = (
        lambda **payload:
        published_statuses.append(payload)
    )

    class Logger:
        def warning(self, message: str) -> None:
            warnings.append(message)

    manager.get_logger = lambda: Logger()

    return (
        manager,
        published_maps,
        published_statuses,
        warnings,
    )


def environment_message(
    environment: str,
) -> String:
    message = String()
    message.data = json.dumps(
        {
            "selected_environment": environment,
        }
    )
    return message


def test_clears_map_after_environment_switch() -> None:
    (
        manager,
        published_maps,
        published_statuses,
        _,
    ) = make_manager()

    manager.environment_status_callback(
        environment_message("hospital")
    )

    assert manager.selected_environment == "hospital"
    assert manager.selected_map_name == ""
    assert manager.selected_map_path == ""
    assert manager.selected_map_environment == ""

    assert published_maps[-1] == {
        "name": "",
        "environment": "",
        "path": "",
    }

    assert published_statuses[-1]["status"] == (
        "ready"
    )
    assert "environment changed" in (
        published_statuses[-1]["message"]
    )


def test_preserves_map_when_environment_is_unchanged() -> None:
    manager, published_maps, statuses, _ = (
        make_manager()
    )

    manager.environment_status_callback(
        environment_message("warehouse")
    )

    assert manager.selected_environment == "warehouse"
    assert manager.selected_map_name == "test_map"
    assert manager.selected_map_environment == (
        "warehouse"
    )
    assert published_maps == []
    assert statuses == []


def test_preserves_legacy_map_after_switch() -> None:
    manager, published_maps, statuses, _ = (
        make_manager(
            selected_map_environment="legacy"
        )
    )

    manager.environment_status_callback(
        environment_message("hospital")
    )

    assert manager.selected_environment == "hospital"
    assert manager.selected_map_name == "test_map"
    assert manager.selected_map_environment == "legacy"
    assert published_maps == []
    assert statuses == []


def test_ignores_malformed_environment_json() -> None:
    manager, published_maps, statuses, warnings = (
        make_manager()
    )

    message = String()
    message.data = '{"selected_environment":'

    manager.environment_status_callback(message)

    assert manager.selected_environment == "warehouse"
    assert manager.selected_map_name == "test_map"
    assert published_maps == []
    assert statuses == []
    assert warnings


def test_ignores_empty_environment() -> None:
    manager, published_maps, statuses, _ = (
        make_manager()
    )

    manager.environment_status_callback(
        environment_message("")
    )

    assert manager.selected_environment == "warehouse"
    assert manager.selected_map_name == "test_map"
    assert published_maps == []
    assert statuses == []
