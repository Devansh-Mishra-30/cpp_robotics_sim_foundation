#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_mapping_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / 'scripts'
        / 'mapping_manager_node.py'
    )

    specification = importlib.util.spec_from_file_location(
        'mapping_manager_node',
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            'Unable to load mapping manager module'
        )

    module = importlib.util.module_from_spec(
        specification
    )
    specification.loader.exec_module(module)
    return module


MODULE = load_mapping_manager_module()
MappingManagerNode = MODULE.MappingManagerNode


def make_mapping_manager(
    *,
    simulation_state: str = 'running',
    mode_state: str = 'mapping',
    selected_environment: str = 'warehouse',
):
    node = object.__new__(MappingManagerNode)
    node.simulation_state = simulation_state
    node.mode_state = mode_state
    node.selected_environment = selected_environment
    return node


@pytest.mark.parametrize(
    'map_name',
    [
        'warehouse',
        'warehouse_map',
        'warehouse-map',
        'Map01',
        'a',
        'a' * 64,
    ],
)
def test_accepts_valid_map_names(
    map_name: str,
) -> None:
    node = make_mapping_manager()

    error = node.validate_save_request(map_name)

    assert error is None


@pytest.mark.parametrize(
    'map_name',
    [
        '',
        '../secret',
        '../../tmp/map',
        'warehouse/map',
        r'warehouse\map',
        '.',
        '..',
        '-warehouse',
        '_warehouse',
        'warehouse map',
        'warehouse.map',
        'warehouse;rm',
        'warehouse$(whoami)',
        'warehouse\nmap',
        'a' * 65,
    ],
)
def test_rejects_unsafe_map_names(
    map_name: str,
) -> None:
    node = make_mapping_manager()

    error = node.validate_save_request(map_name)

    assert error is not None


def test_requires_running_simulation() -> None:
    node = make_mapping_manager(
        simulation_state='stopped'
    )

    error = node.validate_save_request(
        'warehouse_map'
    )

    assert error is not None
    assert 'Simulation must be running' in error


def test_requires_mapping_mode() -> None:
    node = make_mapping_manager(
        mode_state='navigation'
    )

    error = node.validate_save_request(
        'warehouse_map'
    )

    assert error is not None
    assert 'Mapping mode must be active' in error


def test_requires_selected_environment() -> None:
    node = make_mapping_manager(
        selected_environment=''
    )

    error = node.validate_save_request(
        'warehouse_map'
    )

    assert error is not None
    assert 'No simulation environment' in error
