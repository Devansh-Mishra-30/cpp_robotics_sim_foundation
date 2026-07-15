#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import importlib.util
import json
import math
from pathlib import Path
from types import ModuleType, SimpleNamespace

from std_msgs.msg import String


def load_localization_manager_module() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[1]
        / 'scripts'
        / 'localization_manager_node.py'
    )

    specification = importlib.util.spec_from_file_location(
        'localization_manager_node',
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            'Unable to load localization manager module'
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
    selected_environment: str = 'warehouse',
    selected_map_environment: str = 'warehouse',
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
    manager.selected_map_name = 'test_map'
    manager.selected_map_path = (
        '/tmp/maps/warehouse/test_map.yaml'
    )

    published_maps = []
    published_statuses = []
    warnings = []

    manager.publish_selected_map = (
        lambda: published_maps.append(
            {
                'name': manager.selected_map_name,
                'environment': (
                    manager.selected_map_environment
                ),
                'path': manager.selected_map_path,
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
            'selected_environment': environment,
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
        environment_message('hospital')
    )

    assert manager.selected_environment == 'hospital'
    assert manager.selected_map_name == ''
    assert manager.selected_map_path == ''
    assert manager.selected_map_environment == ''

    assert published_maps[-1] == {
        'name': '',
        'environment': '',
        'path': '',
    }

    assert published_statuses[-1]['status'] == (
        'ready'
    )
    assert 'environment changed' in (
        published_statuses[-1]['message']
    )


def test_preserves_map_when_environment_is_unchanged() -> None:
    manager, published_maps, statuses, _ = (
        make_manager()
    )

    manager.environment_status_callback(
        environment_message('warehouse')
    )

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert manager.selected_map_environment == (
        'warehouse'
    )
    assert published_maps == []
    assert statuses == []


def test_preserves_legacy_map_after_switch() -> None:
    manager, published_maps, statuses, _ = (
        make_manager(
            selected_map_environment='legacy'
        )
    )

    manager.environment_status_callback(
        environment_message('hospital')
    )

    assert manager.selected_environment == 'hospital'
    assert manager.selected_map_name == 'test_map'
    assert manager.selected_map_environment == 'legacy'
    assert published_maps == []
    assert statuses == []


def test_ignores_malformed_environment_json() -> None:
    manager, published_maps, statuses, warnings = (
        make_manager()
    )

    message = String()
    message.data = '{"selected_environment":'

    manager.environment_status_callback(message)

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []
    assert warnings


def test_ignores_empty_environment() -> None:
    manager, published_maps, statuses, _ = (
        make_manager()
    )

    manager.environment_status_callback(
        environment_message('')
    )

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []


def make_parameter_validation_manager():
    manager = object.__new__(
        LocalizationManagerNode
    )
    manager.position_covariance = 0.25
    manager.yaw_covariance = 0.06853891945200942
    return manager


def test_parameter_validation_accepts_valid_covariances() -> None:
    manager = make_parameter_validation_manager()

    manager.validate_parameters()


def test_parameter_validation_rejects_nan_position_covariance() -> None:
    manager = make_parameter_validation_manager()
    manager.position_covariance = float('nan')

    try:
        manager.validate_parameters()
    except ValueError as error:
        assert 'position_covariance' in str(error)
    else:
        raise AssertionError(
            'NaN position_covariance should be rejected'
        )


def test_parameter_validation_rejects_infinite_position_covariance() -> None:
    manager = make_parameter_validation_manager()
    manager.position_covariance = float('inf')

    try:
        manager.validate_parameters()
    except ValueError as error:
        assert 'position_covariance' in str(error)
    else:
        raise AssertionError(
            'Infinite position_covariance should be rejected'
        )


def test_parameter_validation_rejects_nan_yaw_covariance() -> None:
    manager = make_parameter_validation_manager()
    manager.yaw_covariance = float('nan')

    try:
        manager.validate_parameters()
    except ValueError as error:
        assert 'yaw_covariance' in str(error)
    else:
        raise AssertionError(
            'NaN yaw_covariance should be rejected'
        )


def test_parameter_validation_rejects_infinite_yaw_covariance() -> None:
    manager = make_parameter_validation_manager()
    manager.yaw_covariance = float('inf')

    try:
        manager.validate_parameters()
    except ValueError as error:
        assert 'yaw_covariance' in str(error)
    else:
        raise AssertionError(
            'Infinite yaw_covariance should be rejected'
        )


def test_mode_status_callback_trims_state() -> None:
    manager = object.__new__(
        LocalizationManagerNode
    )
    manager.mode_state = 'stopped'

    message = String()
    message.data = '  navigation\n'

    manager.mode_status_callback(message)

    assert manager.mode_state == 'navigation'


def test_simulation_status_callback_trims_state() -> None:
    manager = object.__new__(
        LocalizationManagerNode
    )
    manager.simulation_state = 'stopped'

    message = String()
    message.data = '  running\n'

    manager.simulation_status_callback(message)

    assert manager.simulation_state == 'running'


def raw_environment_message(payload) -> String:
    message = String()
    message.data = json.dumps(payload)
    return message


def test_ignores_non_object_environment_json() -> None:
    manager, published_maps, statuses, warnings = (
        make_manager()
    )

    manager.environment_status_callback(
        raw_environment_message(
            ['hospital']
        )
    )

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []
    assert warnings


def test_ignores_null_environment_value() -> None:
    manager, published_maps, statuses, warnings = (
        make_manager()
    )

    manager.environment_status_callback(
        raw_environment_message(
            {
                'selected_environment': None,
            }
        )
    )

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []
    assert warnings


def test_ignores_boolean_environment_value() -> None:
    manager, published_maps, statuses, warnings = (
        make_manager()
    )

    manager.environment_status_callback(
        raw_environment_message(
            {
                'selected_environment': True,
            }
        )
    )

    assert manager.selected_environment == 'warehouse'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []
    assert warnings


def test_normalizes_valid_environment_value() -> None:
    manager, published_maps, statuses, _ = (
        make_manager(
            selected_environment='hospital',
            selected_map_environment='hospital',
        )
    )

    manager.environment_status_callback(
        raw_environment_message(
            {
                'selected_environment': '  HOSPITAL  ',
            }
        )
    )

    assert manager.selected_environment == 'hospital'
    assert manager.selected_map_name == 'test_map'
    assert published_maps == []
    assert statuses == []


def make_map_request_manager(
    *,
    selected_environment: str = 'warehouse',
):
    manager = object.__new__(
        LocalizationManagerNode
    )
    manager.selected_environment = selected_environment
    return manager


def test_parse_map_request_accepts_plain_map_name() -> None:
    manager = make_map_request_manager()

    map_name, environment = manager.parse_map_request(
        '  hospital_map  '
    )

    assert map_name == 'hospital_map'
    assert environment == 'warehouse'


def test_parse_map_request_accepts_object_request() -> None:
    manager = make_map_request_manager()

    map_name, environment = manager.parse_map_request(
        json.dumps(
            {
                'name': '  hospital_map  ',
                'environment': '  HOSPITAL  ',
            }
        )
    )

    assert map_name == 'hospital_map'
    assert environment == 'hospital'


def test_parse_map_request_rejects_non_object_json() -> None:
    manager = make_map_request_manager()

    try:
        manager.parse_map_request(
            json.dumps(
                ['hospital_map']
            )
        )
    except ValueError as error:
        assert 'JSON object' in str(error)
    else:
        raise AssertionError(
            'Non-object map request should be rejected'
        )


def test_parse_map_request_rejects_null_environment() -> None:
    manager = make_map_request_manager()

    try:
        manager.parse_map_request(
            json.dumps(
                {
                    'name': 'hospital_map',
                    'environment': None,
                }
            )
        )
    except ValueError as error:
        assert 'environment' in str(error)
    else:
        raise AssertionError(
            'Null map environment should be rejected'
        )


def test_parse_map_request_rejects_boolean_environment() -> None:
    manager = make_map_request_manager()

    try:
        manager.parse_map_request(
            json.dumps(
                {
                    'name': 'hospital_map',
                    'environment': True,
                }
            )
        )
    except ValueError as error:
        assert 'environment' in str(error)
    else:
        raise AssertionError(
            'Boolean map environment should be rejected'
        )


def test_parse_map_request_rejects_empty_request() -> None:
    manager = make_map_request_manager()

    try:
        manager.parse_map_request('   ')
    except ValueError as error:
        assert 'empty' in str(error)
    else:
        raise AssertionError(
            'Empty map request should be rejected'
        )


def test_parse_map_request_rejects_empty_environment() -> None:
    manager = make_map_request_manager(
        selected_environment=''
    )

    try:
        manager.parse_map_request(
            json.dumps(
                {
                    'name': 'hospital_map',
                    'environment': '   ',
                }
            )
        )
    except ValueError as error:
        assert 'environment' in str(error)
    else:
        raise AssertionError(
            'Empty map environment should be rejected'
        )


def test_resolve_path_rejects_parent_traversal() -> None:
    root = Path('/tmp/localization-map-root')

    try:
        LocalizationManagerNode.resolve_path_within_root(
            root,
            '..',
            'outside.yaml',
        )
    except ValueError as error:
        assert 'escapes' in str(error)
    else:
        raise AssertionError(
            'Parent traversal should be rejected'
        )


def test_resolve_path_rejects_absolute_path_escape() -> None:
    root = Path('/tmp/localization-map-root')

    try:
        LocalizationManagerNode.resolve_path_within_root(
            root,
            '/tmp/outside.yaml',
        )
    except ValueError as error:
        assert 'escapes' in str(error)
    else:
        raise AssertionError(
            'Absolute path escape should be rejected'
        )


class RecordingPublisher:
    def __init__(self) -> None:
        self.messages = []

    def publish(self, message) -> None:
        self.messages.append(message)


class FixedClock:
    def now(self):
        return SimpleNamespace(
            to_msg=lambda: 'fixed-stamp'
        )


def make_initial_pose_manager():
    manager = object.__new__(
        LocalizationManagerNode
    )

    manager.simulation_state = 'running'
    manager.mode_state = 'localization'
    manager.selected_map_name = 'hospital'
    manager.selected_map_path = (
        '/tmp/maps/hospital/hospital.yaml'
    )
    manager.position_covariance = 0.25
    manager.yaw_covariance = 0.06853891945200942

    manager.initial_pose_publisher = (
        RecordingPublisher()
    )
    manager.published_statuses = []
    manager.logged_messages = []

    manager.publish_status = (
        lambda **payload:
        manager.published_statuses.append(payload)
    )

    manager.get_clock = lambda: FixedClock()

    class Logger:
        def info(self, message: str) -> None:
            manager.logged_messages.append(message)

    manager.get_logger = lambda: Logger()

    return manager


def initial_pose_message(payload) -> String:
    message = String()
    message.data = json.dumps(payload)
    return message


def test_initial_pose_rejects_boolean_values() -> None:
    manager = make_initial_pose_manager()

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': True,
                'y': 2.0,
                'yaw': 0.0,
            }
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert manager.published_statuses[-1]['status'] == 'error'
    assert 'numeric' in (
        manager.published_statuses[-1]['message']
    )


def test_initial_pose_rejects_non_object_json() -> None:
    manager = make_initial_pose_manager()

    manager.initial_pose_callback(
        initial_pose_message(
            [1.0, 2.0, 0.0]
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert manager.published_statuses[-1]['status'] == 'error'


def test_initial_pose_rejects_nonfinite_values() -> None:
    manager = make_initial_pose_manager()

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': float('nan'),
                'y': 2.0,
                'yaw': 0.0,
            }
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert manager.published_statuses[-1]['status'] == 'error'
    assert 'finite' in (
        manager.published_statuses[-1]['message']
    )


def test_initial_pose_requires_running_simulation() -> None:
    manager = make_initial_pose_manager()
    manager.simulation_state = 'stopped'

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': 1.0,
                'y': 2.0,
                'yaw': 0.0,
            }
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert 'Simulation must be running' in (
        manager.published_statuses[-1]['message']
    )


def test_initial_pose_requires_supported_mode() -> None:
    manager = make_initial_pose_manager()
    manager.mode_state = 'mapping'

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': 1.0,
                'y': 2.0,
                'yaw': 0.0,
            }
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert 'must be active' in (
        manager.published_statuses[-1]['message']
    )


def test_initial_pose_requires_selected_map() -> None:
    manager = make_initial_pose_manager()
    manager.selected_map_path = ''

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': 1.0,
                'y': 2.0,
                'yaw': 0.0,
            }
        )
    )

    assert manager.initial_pose_publisher.messages == []
    assert 'Select a saved map' in (
        manager.published_statuses[-1]['message']
    )


def test_initial_pose_publishes_expected_pose() -> None:
    manager = make_initial_pose_manager()

    manager.initial_pose_callback(
        initial_pose_message(
            {
                'x': 1.25,
                'y': -2.5,
                'yaw': math.pi / 2.0,
            }
        )
    )

    assert len(manager.initial_pose_publisher.messages) == 1

    pose_message = (
        manager.initial_pose_publisher.messages[0]
    )

    assert pose_message.header.frame_id == 'map'
    assert pose_message.header.stamp == 'fixed-stamp'

    assert pose_message.pose.pose.position.x == 1.25
    assert pose_message.pose.pose.position.y == -2.5
    assert pose_message.pose.pose.position.z == 0.0

    assert math.isclose(
        pose_message.pose.pose.orientation.z,
        math.sin(math.pi / 4.0),
    )
    assert math.isclose(
        pose_message.pose.pose.orientation.w,
        math.cos(math.pi / 4.0),
    )

    assert pose_message.pose.covariance[0] == 0.25
    assert pose_message.pose.covariance[7] == 0.25
    assert (
        pose_message.pose.covariance[35]
        == 0.06853891945200942
    )

    assert manager.published_statuses[-1]['status'] == 'success'


def make_map_selection_manager(
    map_directory: Path,
    *,
    selected_environment: str = 'warehouse',
):
    manager = object.__new__(
        LocalizationManagerNode
    )

    manager.map_directory = map_directory
    manager.selected_environment = selected_environment
    manager.selected_map_name = ''
    manager.selected_map_path = ''
    manager.selected_map_environment = ''

    manager.published_maps = []
    manager.published_statuses = []
    manager.logged_messages = []

    manager.publish_selected_map = (
        lambda: manager.published_maps.append(
            {
                'name': manager.selected_map_name,
                'environment': (
                    manager.selected_map_environment
                ),
                'yaml_path': manager.selected_map_path,
            }
        )
    )

    manager.publish_status = (
        lambda **payload:
        manager.published_statuses.append(payload)
    )

    class Logger:
        def info(self, message: str) -> None:
            manager.logged_messages.append(message)

    manager.get_logger = lambda: Logger()

    return manager


def map_selection_message(payload) -> String:
    message = String()

    if isinstance(payload, str):
        message.data = payload
    else:
        message.data = json.dumps(payload)

    return message


def create_map_files(
    directory: Path,
    map_name: str,
    *,
    create_yaml: bool = True,
    create_image: bool = True,
) -> None:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    if create_yaml:
        (
            directory / f'{map_name}.yaml'
        ).write_text(
            'image: test_map.pgm\n'
        )

    if create_image:
        (
            directory / f'{map_name}.pgm'
        ).write_bytes(b'P5\n1 1\n255\n\x00')


def test_select_map_prefers_environment_specific_map(
    tmp_path: Path,
) -> None:
    manager = make_map_selection_manager(
        tmp_path,
        selected_environment='hospital',
    )

    create_map_files(
        tmp_path / 'hospital',
        'floor_one',
    )
    create_map_files(
        tmp_path,
        'floor_one',
    )

    manager.select_map_callback(
        map_selection_message('floor_one')
    )

    expected_yaml = (
        tmp_path
        / 'hospital'
        / 'floor_one.yaml'
    ).resolve()

    assert manager.selected_map_name == 'floor_one'
    assert manager.selected_map_path == str(expected_yaml)
    assert manager.selected_map_environment == 'hospital'
    assert manager.published_maps[-1]['yaml_path'] == str(
        expected_yaml
    )
    assert manager.published_statuses[-1]['status'] == 'success'


def test_select_map_falls_back_to_legacy_map(
    tmp_path: Path,
) -> None:
    manager = make_map_selection_manager(
        tmp_path,
        selected_environment='hospital',
    )

    create_map_files(
        tmp_path,
        'legacy_floor',
    )

    manager.select_map_callback(
        map_selection_message('legacy_floor')
    )

    expected_yaml = (
        tmp_path / 'legacy_floor.yaml'
    ).resolve()

    assert manager.selected_map_name == 'legacy_floor'
    assert manager.selected_map_path == str(expected_yaml)
    assert manager.selected_map_environment == 'legacy'
    assert manager.published_statuses[-1]['status'] == 'success'


def test_select_map_without_environment_labels_root_map_legacy(
    tmp_path: Path,
) -> None:
    manager = make_map_selection_manager(
        tmp_path,
        selected_environment='',
    )

    create_map_files(
        tmp_path,
        'root_map',
    )

    manager.select_map_callback(
        map_selection_message('root_map')
    )

    assert manager.selected_map_name == 'root_map'
    assert manager.selected_map_environment == 'legacy'
    assert manager.published_statuses[-1]['status'] == 'success'


def test_select_map_missing_yaml_preserves_existing_state(
    tmp_path: Path,
) -> None:
    manager = make_map_selection_manager(
        tmp_path,
        selected_environment='hospital',
    )
    manager.selected_map_name = 'existing'
    manager.selected_map_path = '/tmp/existing.yaml'
    manager.selected_map_environment = 'hospital'

    manager.select_map_callback(
        map_selection_message('missing_map')
    )

    assert manager.selected_map_name == 'existing'
    assert manager.selected_map_path == '/tmp/existing.yaml'
    assert manager.selected_map_environment == 'hospital'
    assert manager.published_maps == []
    assert manager.published_statuses[-1]['status'] == 'error'
    assert 'YAML does not exist' in (
        manager.published_statuses[-1]['message']
    )


def test_select_map_missing_image_preserves_existing_state(
    tmp_path: Path,
) -> None:
    manager = make_map_selection_manager(
        tmp_path,
        selected_environment='hospital',
    )
    manager.selected_map_name = 'existing'
    manager.selected_map_path = '/tmp/existing.yaml'
    manager.selected_map_environment = 'hospital'

    create_map_files(
        tmp_path / 'hospital',
        'incomplete_map',
        create_image=False,
    )

    manager.select_map_callback(
        map_selection_message('incomplete_map')
    )

    assert manager.selected_map_name == 'existing'
    assert manager.selected_map_path == '/tmp/existing.yaml'
    assert manager.selected_map_environment == 'hospital'
    assert manager.published_maps == []
    assert manager.published_statuses[-1]['status'] == 'error'
    assert 'image does not exist' in (
        manager.published_statuses[-1]['message']
    )
