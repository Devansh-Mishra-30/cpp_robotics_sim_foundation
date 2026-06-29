#!/usr/bin/env python3

import argparse
import csv
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt


REQUIRED_COLUMNS = [
    'time_sec',
    'cmd_linear_x',
    'cmd_angular_z',
    'actual_x',
    'actual_y',
    'actual_yaw',
    'actual_linear_x',
    'actual_angular_z',
    'noisy_x',
    'noisy_y',
    'noisy_yaw',
]


def find_repo_root():
    cwd = Path.cwd().resolve()

    for path in [cwd] + list(cwd.parents):
        if (path / 'ros2_ws' / 'src' / 'cpp_robotics_sim_ros').exists():
            return path

        if path.name == 'ros2_ws' and (path / 'src' / 'cpp_robotics_sim_ros').exists():
            return path.parent

    return cwd


def resolve_repo_path(path_text):
    path = Path(path_text).expanduser()

    if path.is_absolute():
        return path

    return find_repo_root() / path


def safe_float(value):
    if value is None:
        return float('nan')

    value = str(value).strip()

    if value == '':
        return float('nan')

    return float(value)


def is_valid(value):
    return not math.isnan(value)


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def mean(values):
    values = [value for value in values if is_valid(value)]

    if not values:
        return float('nan')

    return sum(values) / len(values)


def max_value(values):
    values = [value for value in values if is_valid(value)]

    if not values:
        return float('nan')

    return max(values)


def max_abs(values):
    values = [abs(value) for value in values if is_valid(value)]

    if not values:
        return float('nan')

    return max(values)


def fmt(value, unit=''):
    if math.isnan(value):
        return 'not available'

    if unit:
        return f'{value:.6f} {unit}'

    return f'{value:.6f}'


def read_validation_csv(csv_path):
    with csv_path.open('r', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        fieldnames = reader.fieldnames

    if not rows:
        raise RuntimeError(f'CSV has no data rows: {csv_path}')

    if fieldnames is None:
        raise RuntimeError(f'CSV has no header: {csv_path}')

    for column in REQUIRED_COLUMNS:
        if column not in fieldnames:
            raise RuntimeError(f'Missing required CSV column: {column}')

    data = {}

    for column in fieldnames:
        data[column] = [safe_float(row.get(column, '')) for row in rows]

    return data, rows


def compute_path_length(x_values, y_values):
    total = 0.0

    for i in range(1, len(x_values)):
        if not all(is_valid(value) for value in [
            x_values[i - 1],
            y_values[i - 1],
            x_values[i],
            y_values[i],
        ]):
            continue

        dx = x_values[i] - x_values[i - 1]
        dy = y_values[i] - y_values[i - 1]

        total += math.sqrt(dx * dx + dy * dy)

    return total


def compute_noise_errors(actual_x, actual_y, actual_yaw, noisy_x, noisy_y, noisy_yaw):
    position_errors = []
    yaw_errors = []

    for ax, ay, ayaw, nx, ny, nyaw in zip(
        actual_x,
        actual_y,
        actual_yaw,
        noisy_x,
        noisy_y,
        noisy_yaw,
    ):
        if all(is_valid(value) for value in [ax, ay, nx, ny]):
            dx = nx - ax
            dy = ny - ay
            position_errors.append(math.sqrt(dx * dx + dy * dy))

        if all(is_valid(value) for value in [ayaw, nyaw]):
            yaw_errors.append(abs(wrap_angle(nyaw - ayaw)))

    return position_errors, yaw_errors


def make_plot(data, plot_path):
    time_sec = data['time_sec']

    cmd_linear_x = data['cmd_linear_x']
    cmd_angular_z = data['cmd_angular_z']

    actual_x = data['actual_x']
    actual_y = data['actual_y']
    actual_yaw = data['actual_yaw']
    actual_linear_x = data['actual_linear_x']
    actual_angular_z = data['actual_angular_z']

    noisy_x = data['noisy_x']
    noisy_y = data['noisy_y']
    noisy_yaw = data['noisy_yaw']

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    axes[0, 0].plot(actual_x, actual_y, label='actual odom')
    axes[0, 0].plot(noisy_x, noisy_y, label='noisy odom')
    axes[0, 0].set_title('Actual vs Noisy Trajectory')
    axes[0, 0].set_xlabel('x [m]')
    axes[0, 0].set_ylabel('y [m]')
    axes[0, 0].axis('equal')
    axes[0, 0].grid(True)
    axes[0, 0].legend()

    axes[0, 1].plot(time_sec, actual_yaw, label='actual yaw')
    axes[0, 1].plot(time_sec, noisy_yaw, label='noisy yaw')
    axes[0, 1].set_title('Yaw Over Time')
    axes[0, 1].set_xlabel('time [s]')
    axes[0, 1].set_ylabel('yaw [rad]')
    axes[0, 1].grid(True)
    axes[0, 1].legend()

    axes[1, 0].plot(time_sec, cmd_linear_x, label='commanded linear x')
    axes[1, 0].plot(time_sec, actual_linear_x, label='actual linear x')
    axes[1, 0].set_title('Commanded vs Actual Linear Velocity')
    axes[1, 0].set_xlabel('time [s]')
    axes[1, 0].set_ylabel('velocity [m/s]')
    axes[1, 0].grid(True)
    axes[1, 0].legend()

    axes[1, 1].plot(time_sec, cmd_angular_z, label='commanded yaw rate')
    axes[1, 1].plot(time_sec, actual_angular_z, label='actual yaw rate')
    axes[1, 1].set_title('Commanded vs Actual Yaw Rate')
    axes[1, 1].set_xlabel('time [s]')
    axes[1, 1].set_ylabel('yaw rate [rad/s]')
    axes[1, 1].grid(True)
    axes[1, 1].legend()

    fig.tight_layout()

    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(plot_path, dpi=160)
    plt.close(fig)


def write_report(data, rows, csv_path, plot_path, report_path):
    time_sec = data['time_sec']

    cmd_linear_x = data['cmd_linear_x']
    cmd_angular_z = data['cmd_angular_z']

    actual_x = data['actual_x']
    actual_y = data['actual_y']
    actual_yaw = data['actual_yaw']
    actual_linear_x = data['actual_linear_x']
    actual_angular_z = data['actual_angular_z']

    noisy_x = data['noisy_x']
    noisy_y = data['noisy_y']
    noisy_yaw = data['noisy_yaw']

    final_index = len(rows) - 1

    duration = time_sec[-1] - time_sec[0] if len(time_sec) >= 2 else 0.0
    path_length = compute_path_length(actual_x, actual_y)

    position_errors, yaw_errors = compute_noise_errors(
        actual_x,
        actual_y,
        actual_yaw,
        noisy_x,
        noisy_y,
        noisy_yaw,
    )

    lines = [
        '# Day 85 — Trajectory Validation Report',
        '',
        '## Purpose',
        '',
        'This report validates the Gazebo `ros2_control` differential-drive stack by comparing commanded velocity, actual odometry, and noisy odometry.',
        '',
        'The validation data comes from:',
        '',
        '```txt',
        'data/day84_trajectory_validation.csv',
        '```',
        '',
        'The generated plot is:',
        '',
        '```txt',
        'plots/trajectory_validation.png',
        '```',
        '',
        '---',
        '',
        '## System Under Test',
        '',
        'The robot is moved by the Gazebo `ros2_control` stack:',
        '',
        '```txt',
        '/diff_drive_controller/cmd_vel',
        '    -> diff_drive_controller',
        '    -> ros2_control',
        '    -> gz_ros2_control',
        '    -> Gazebo wheel joints',
        '    -> /diff_drive_controller/odom',
        '```',
        '',
        'The noisy odometry stream is produced by:',
        '',
        '```txt',
        '/diff_drive_controller/odom',
        '    -> noisy_odom_node.py',
        '    -> /odom_noisy',
        '```',
        '',
        'Important:',
        '',
        '```txt',
        '/odom_noisy does not move Gazebo.',
        'It is a noisy feedback stream for validation and future localization work.',
        '```',
        '',
        '---',
        '',
        '## Validation Metrics',
        '',
        '| Metric | Value |',
        '|---|---:|',
        f'| samples | {len(rows)} |',
        f'| duration | {fmt(duration, "s")} |',
        f'| actual path length | {fmt(path_length, "m")} |',
        f'| final actual x | {fmt(actual_x[final_index], "m")} |',
        f'| final actual y | {fmt(actual_y[final_index], "m")} |',
        f'| final actual yaw | {fmt(actual_yaw[final_index], "rad")} |',
        f'| mean position noise error | {fmt(mean(position_errors), "m")} |',
        f'| max position noise error | {fmt(max_value(position_errors), "m")} |',
        f'| mean yaw noise error | {fmt(mean(yaw_errors), "rad")} |',
        f'| max yaw noise error | {fmt(max_value(yaw_errors), "rad")} |',
        f'| max commanded linear velocity | {fmt(max_abs(cmd_linear_x), "m/s")} |',
        f'| max actual linear velocity | {fmt(max_abs(actual_linear_x), "m/s")} |',
        f'| max commanded yaw rate | {fmt(max_abs(cmd_angular_z), "rad/s")} |',
        f'| max actual yaw rate | {fmt(max_abs(actual_angular_z), "rad/s")} |',
        '',
        '---',
        '',
        '## Interpretation',
        '',
        'The commanded velocity columns show the desired robot motion.',
        '',
        'The actual odometry columns show the executed robot motion reported by the Gazebo `diff_drive_controller`.',
        '',
        'The noisy odometry columns show a controlled noisy measurement stream created from actual odometry.',
        '',
        'The actual and noisy trajectories should be close but not identical. The difference between them represents simulated measurement uncertainty.',
        '',
        '---',
        '',
        '## Interview Explanation',
        '',
        'Day 85 converts raw validation data into engineering evidence.',
        '',
        'Instead of only saying the robot moves in Gazebo, this report shows that the system can record command signals, actual odometry feedback, noisy measurement feedback, and quantitative trajectory metrics.',
        '',
        'This is important for robotics simulation engineering because simulation behavior must be measurable, repeatable, and comparable.',
        '',
        '---',
        '',
        '## Key Takeaways',
        '',
        '- The robot was commanded through `/diff_drive_controller/cmd_vel`.',
        '- Actual executed motion was recorded from `/diff_drive_controller/odom`.',
        '- Noisy feedback was recorded from `/odom_noisy`.',
        '- Position and yaw noise errors were computed.',
        '- Commanded velocity and actual velocity were compared.',
        '- A portfolio-ready validation plot was generated.',
        '',
        '---',
        '',
        '## Day 85 Completion Criteria',
        '',
        'Day 85 is complete when:',
        '',
        '- `plots/trajectory_validation.png` exists.',
        '- `docs/trajectory_validation_report.md` exists.',
        '- The report contains path length, final pose, noise error, and velocity metrics.',
        '- Day 68 regression still passes.',
        '',
    ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(
        description='Generate Day 85 trajectory validation plot and report.'
    )

    parser.add_argument(
        '--csv',
        default='data/day84_trajectory_validation.csv',
        help='Input CSV path.'
    )

    parser.add_argument(
        '--plot',
        default='plots/trajectory_validation.png',
        help='Output plot path.'
    )

    parser.add_argument(
        '--report',
        default='docs/trajectory_validation_report.md',
        help='Output markdown report path.'
    )

    args = parser.parse_args()

    csv_path = resolve_repo_path(args.csv)
    plot_path = resolve_repo_path(args.plot)
    report_path = resolve_repo_path(args.report)

    if not csv_path.exists():
        raise FileNotFoundError(f'CSV file not found: {csv_path}')

    data, rows = read_validation_csv(csv_path)

    make_plot(data, plot_path)
    write_report(data, rows, csv_path, plot_path, report_path)

    print(f'Input CSV:        {csv_path}')
    print(f'Generated plot:   {plot_path}')
    print(f'Generated report: {report_path}')
    print(f'Samples:          {len(rows)}')


if __name__ == '__main__':
    main()