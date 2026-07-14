#!/usr/bin/env python3

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


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


def test_resolves_environment_map_inside_root(
    tmp_path: Path,
) -> None:
    result = (
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            "warehouse",
            "test_map.yaml",
        )
    )

    assert result == (
        tmp_path.resolve()
        / "warehouse"
        / "test_map.yaml"
    )


def test_resolves_legacy_map_inside_root(
    tmp_path: Path,
) -> None:
    result = (
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            "test_map.yaml",
        )
    )

    assert result == (
        tmp_path.resolve()
        / "test_map.yaml"
    )


@pytest.mark.parametrize(
    "unsafe_environment",
    [
        "..",
        "../outside",
        "../../tmp",
        "../../../etc",
        "/tmp",
        "/etc",
        "warehouse/../../outside",
    ],
)
def test_rejects_environment_path_escape(
    tmp_path: Path,
    unsafe_environment: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="escapes",
    ):
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            unsafe_environment,
            "test_map.yaml",
        )


def test_rejects_map_filename_path_escape(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="escapes",
    ):
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            "warehouse",
            "../../../outside.yaml",
        )


def test_rejects_absolute_map_filename(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="escapes",
    ):
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            "warehouse",
            "/tmp/outside.yaml",
        )


def test_rejects_symlink_escape(
    tmp_path: Path,
) -> None:
    outside_directory = tmp_path.parent / "outside_maps"
    outside_directory.mkdir(exist_ok=True)

    symlink_path = tmp_path / "linked_environment"
    symlink_path.symlink_to(
        outside_directory,
        target_is_directory=True,
    )

    with pytest.raises(
        ValueError,
        match="escapes",
    ):
        LocalizationManagerNode.resolve_path_within_root(
            tmp_path,
            "linked_environment",
            "test_map.yaml",
        )
