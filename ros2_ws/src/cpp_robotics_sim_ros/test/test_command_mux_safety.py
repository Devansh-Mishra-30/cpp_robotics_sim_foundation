#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

"""Unit tests for velocity-command arbitration and safety behavior."""

import importlib.util
import math
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from typing import Optional

from geometry_msgs.msg import TwistStamped


def load_command_mux_module() -> ModuleType:
    """Load command_mux_node.py as an importable test module."""
    script_path = (
        Path(__file__).resolve().parents[1]
        / 'scripts'
        / 'command_mux_node.py'
    )

    specification = importlib.util.spec_from_file_location(
        'command_mux_node',
        script_path,
    )

    if (
        specification is None
        or specification.loader is None
    ):
        raise RuntimeError(
            'Unable to load command multiplexer module'
        )

    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


MODULE = load_command_mux_module()
CommandMuxNode = MODULE.CommandMuxNode
CommandSource = MODULE.CommandSource


class FakeTime:
    """Provide a controllable ROS-like timestamp."""

    def __init__(self, nanoseconds: int) -> None:
        """Initialize the fake timestamp."""
        self.nanoseconds = nanoseconds

    def to_msg(self):
        """Return a minimal timestamp-like object."""
        return SimpleNamespace(
            sec=self.nanoseconds // 1_000_000_000,
            nanosec=self.nanoseconds % 1_000_000_000,
        )


class FakeClock:
    """Provide a controllable ROS-like clock."""

    def __init__(self, nanoseconds: int) -> None:
        """Initialize the controllable fake clock."""
        self.nanoseconds = nanoseconds

    def now(self) -> FakeTime:
        """Return the current fake time."""
        return FakeTime(self.nanoseconds)


class FakeLogger:
    """Capture log messages emitted by the node."""

    def __init__(self) -> None:
        """Initialize captured logger messages."""
        self.messages = []

    def info(self, message: str) -> None:
        """Capture an informational message."""
        self.messages.append(('info', message))

    def warn(self, message: str) -> None:
        """Capture a warning message."""
        self.messages.append(('warn', message))


class FakePublisher:
    """Capture published messages."""

    def __init__(self) -> None:
        """Initialize captured publisher messages."""
        self.messages = []

    def publish(self, message) -> None:
        """Store a published message."""
        self.messages.append(message)


def make_command(
    *,
    linear_x: float = 0.0,
    linear_y: float = 0.0,
    angular_z: float = 0.0,
) -> TwistStamped:
    """Create a TwistStamped command for testing."""
    message = TwistStamped()
    message.twist.linear.x = linear_x
    message.twist.linear.y = linear_y
    message.twist.angular.z = angular_z
    return message


def make_source(
    *,
    name: str,
    priority: int,
    order: int,
    timeout: float = 0.5,
    command: Optional[TwistStamped] = None,
    received_time_ns: Optional[int] = None,
) -> CommandSource:
    """Create one command source with optional runtime state."""
    return CommandSource(
        name=name,
        topic=f'/cmd_vel/{name}',
        priority=priority,
        timeout=timeout,
        order=order,
        latest_command=command,
        last_received_time_ns=received_time_ns,
    )


def make_mux(
    *,
    clock_ns: int = 1_000_000_000,
) -> CommandMuxNode:
    """Construct a multiplexer without initializing ROS interfaces."""
    mux = object.__new__(CommandMuxNode)

    mux.max_linear_velocity = 0.3
    mux.max_angular_velocity = 1.0
    mux.frame_id = 'base_link'
    mux.sources = []
    mux.emergency_stop_active = False
    mux.last_reported_source = None

    mux.command_publisher = FakePublisher()
    mux.active_source_publisher = FakePublisher()

    clock = FakeClock(clock_ns)
    logger = FakeLogger()

    mux.get_clock = lambda: clock
    mux.get_logger = lambda: logger

    mux.test_clock = clock
    mux.test_logger = logger

    return mux


def test_selects_highest_priority_active_source() -> None:
    """The highest-priority non-expired source must win."""
    mux = make_mux()

    keyboard = make_source(
        name='keyboard',
        priority=90,
        order=0,
        command=make_command(linear_x=0.1),
        received_time_ns=900_000_000,
    )
    navigation = make_source(
        name='navigation',
        priority=50,
        order=1,
        command=make_command(linear_x=0.2),
        received_time_ns=900_000_000,
    )

    mux.sources = [navigation, keyboard]

    assert mux.select_active_source() is keyboard


def test_ignores_expired_source() -> None:
    """Commands older than their timeout must be ignored."""
    mux = make_mux(clock_ns=2_000_000_000)

    expired = make_source(
        name='keyboard',
        priority=100,
        order=0,
        timeout=0.5,
        command=make_command(linear_x=0.2),
        received_time_ns=1_000_000_000,
    )

    active = make_source(
        name='navigation',
        priority=50,
        order=1,
        timeout=0.5,
        command=make_command(linear_x=0.1),
        received_time_ns=1_750_000_000,
    )

    mux.sources = [expired, active]

    assert mux.select_active_source() is active


def test_equal_priority_uses_configured_order() -> None:
    """Equal priorities must resolve deterministically by source order."""
    mux = make_mux()

    first = make_source(
        name='keyboard',
        priority=90,
        order=0,
        command=make_command(),
        received_time_ns=900_000_000,
    )
    second = make_source(
        name='gui',
        priority=90,
        order=1,
        command=make_command(),
        received_time_ns=900_000_000,
    )

    mux.sources = [second, first]

    assert mux.select_active_source() is first


def test_clock_rollback_invalidates_source() -> None:
    """A future receive timestamp must be discarded after clock rollback."""
    mux = make_mux(clock_ns=1_000_000_000)

    source = make_source(
        name='keyboard',
        priority=90,
        order=0,
        command=make_command(),
        received_time_ns=2_000_000_000,
    )

    mux.sources = [source]

    assert mux.select_active_source() is None
    assert source.latest_command is None
    assert source.last_received_time_ns is None


def test_rejects_non_finite_source_command() -> None:
    """A non-finite command must invalidate the source."""
    mux = make_mux()

    source = make_source(
        name='keyboard',
        priority=90,
        order=0,
        command=make_command(linear_x=0.1),
        received_time_ns=900_000_000,
    )

    message = make_command(linear_x=math.nan)

    mux.command_callback(source, message)

    assert source.latest_command is None
    assert source.last_received_time_ns is None
    assert mux.test_logger.messages == [
        (
            'warn',
            "Rejected non-finite command from 'keyboard'",
        )
    ]


def test_sanitize_clamps_supported_components() -> None:
    """Supported planar components must respect velocity limits."""
    mux = make_mux()

    output = mux.sanitize_command(
        make_command(
            linear_x=0.8,
            angular_z=-2.0,
        )
    )

    assert output.twist.linear.x == 0.3
    assert output.twist.angular.z == -1.0


def test_sanitize_zeroes_unsupported_components() -> None:
    """Unsupported velocity components must remain zero."""
    mux = make_mux()

    output = mux.sanitize_command(
        make_command(
            linear_x=0.1,
            linear_y=0.5,
            angular_z=0.2,
        )
    )

    assert output.twist.linear.x == 0.1
    assert output.twist.linear.y == 0.0
    assert output.twist.linear.z == 0.0
    assert output.twist.angular.x == 0.0
    assert output.twist.angular.y == 0.0
    assert output.twist.angular.z == 0.2


def test_sanitize_non_finite_command_returns_zero() -> None:
    """Non-finite commands must produce a safe zero command."""
    mux = make_mux()

    output = mux.sanitize_command(
        make_command(linear_x=math.inf)
    )

    assert output.twist.linear.x == 0.0
    assert output.twist.angular.z == 0.0


def test_no_active_source_publishes_zero() -> None:
    """No valid source must result in a zero command."""
    mux = make_mux()
    mux.sources = []

    mux.publish_command()

    assert len(mux.command_publisher.messages) == 1
    output = mux.command_publisher.messages[0]
    assert output.twist.linear.x == 0.0
    assert output.twist.angular.z == 0.0
    assert mux.active_source_publisher.messages[-1].data == 'none'


def test_emergency_stop_overrides_active_source() -> None:
    """Emergency stop must override every active command source."""
    mux = make_mux()
    mux.emergency_stop_active = True

    mux.sources = [
        make_source(
            name='keyboard',
            priority=100,
            order=0,
            command=make_command(linear_x=0.2),
            received_time_ns=900_000_000,
        )
    ]

    mux.publish_command()

    assert len(mux.command_publisher.messages) == 1
    output = mux.command_publisher.messages[0]
    assert output.twist.linear.x == 0.0
    assert output.twist.angular.z == 0.0
    assert (
        mux.active_source_publisher.messages[-1].data
        == 'emergency_stop'
    )


def test_positive_finite_validation() -> None:
    """Positive finite validation must reject unsafe values."""
    CommandMuxNode.require_positive_finite('value', 0.1)

    for invalid_value in (
        0.0,
        -1.0,
        math.nan,
        math.inf,
        -math.inf,
    ):
        try:
            CommandMuxNode.require_positive_finite(
                'value',
                invalid_value,
            )
        except ValueError:
            continue

        raise AssertionError(
            f'Expected ValueError for {invalid_value}'
        )
