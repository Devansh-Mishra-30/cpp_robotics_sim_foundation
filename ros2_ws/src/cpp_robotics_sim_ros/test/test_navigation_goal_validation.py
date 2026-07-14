#!/usr/bin/env python3

import importlib.util
import json
import math
from pathlib import Path
from types import ModuleType


def load_navigation_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "navigation_goal_manager_node.py"
    )

    specification = importlib.util.spec_from_file_location(
        "navigation_goal_manager_node",
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            "Unable to load navigation goal manager module"
        )

    module = importlib.util.module_from_spec(
        specification
    )
    specification.loader.exec_module(module)
    return module


MODULE = load_navigation_manager_module()
NavigationGoalManagerNode = (
    MODULE.NavigationGoalManagerNode
)


def parse_request(raw_request: str):
    node = object.__new__(NavigationGoalManagerNode)
    node.minimum_goal_x = -9.5
    node.maximum_goal_x = 9.5
    node.minimum_goal_y = -7.5
    node.maximum_goal_y = 7.5
    return node.parse_goal_request(raw_request)


def test_accepts_valid_navigation_goal() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 1.25,
                "y": -2.5,
                "yaw": math.pi / 2.0,
            }
        )
    )

    assert error is None
    assert goal == {
        "x": 1.25,
        "y": -2.5,
        "yaw": math.pi / 2.0,
    }


def test_rejects_malformed_json() -> None:
    goal, error = parse_request(
        '{"x": 1.0, "y": 2.0,'
    )

    assert goal is None
    assert error is not None
    assert "valid JSON" in error


def test_rejects_non_object_json() -> None:
    goal, error = parse_request(
        json.dumps([1.0, 2.0, 3.0])
    )

    assert goal is None
    assert error is not None
    assert "JSON object" in error


def test_rejects_missing_fields() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 1.0,
                "y": 2.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "yaw" in error


def test_rejects_boolean_values() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": True,
                "y": 2.0,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "booleans" in error


def test_rejects_non_numeric_values() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": "not-a-number",
                "y": 2.0,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "numeric" in error


def test_rejects_nan() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": float("nan"),
                "y": 2.0,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "finite" in error


def test_rejects_positive_infinity() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 1.0,
                "y": float("inf"),
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "finite" in error


def test_rejects_negative_infinity() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 1.0,
                "y": 2.0,
                "yaw": float("-inf"),
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "finite" in error


def test_accepts_goal_on_coordinate_boundaries() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 9.5,
                "y": -7.5,
                "yaw": 0.0,
            }
        )
    )

    assert error is None
    assert goal is not None


def test_rejects_x_below_minimum() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": -9.5001,
                "y": 0.0,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "goal x" in error


def test_rejects_x_above_maximum() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 9.5001,
                "y": 0.0,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "goal x" in error


def test_rejects_y_below_minimum() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 0.0,
                "y": -7.5001,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "goal y" in error


def test_rejects_y_above_maximum() -> None:
    goal, error = parse_request(
        json.dumps(
            {
                "x": 0.0,
                "y": 7.5001,
                "yaw": 0.0,
            }
        )
    )

    assert goal is None
    assert error is not None
    assert "goal y" in error
