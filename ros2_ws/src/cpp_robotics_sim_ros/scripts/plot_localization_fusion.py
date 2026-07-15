#!/usr/bin/env python3
# Copyright 2026 Devansh Mishra
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.


import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


def load_csv(path: Path) -> dict[str, list[float]]:
    columns: dict[str, list[float]] = {}

    with path.open(newline='', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError('CSV file has no header.')

        for field in reader.fieldnames:
            columns[field] = []

        for row in reader:
            for field in reader.fieldnames:
                columns[field].append(float(row[field]))

    if not columns or not columns['time_sec']:
        raise ValueError('CSV contains no recorded data rows.')

    return columns


def rmse(values: list[float]) -> float:
    if not values:
        return math.nan

    return math.sqrt(
        sum(value * value for value in values) / len(values)
    )


def mean_absolute(values: list[float]) -> float:
    if not values:
        return math.nan

    return sum(abs(value) for value in values) / len(values)


def relative_time(values: list[float]) -> list[float]:
    initial_time = values[0]

    return [
        value - initial_time
        for value in values
    ]


def calculate_metrics(
    data: dict[str, list[float]],
) -> dict[str, float]:
    return {
        'samples': float(len(data['time_sec'])),

        'raw_position_rmse': rmse(
            data['raw_position_error']
        ),
        'noisy_position_rmse': rmse(
            data['noisy_position_error']
        ),
        'ekf_position_rmse': rmse(
            data['ekf_position_error']
        ),

        'raw_position_max': max(
            data['raw_position_error']
        ),
        'noisy_position_max': max(
            data['noisy_position_error']
        ),
        'ekf_position_max': max(
            data['ekf_position_error']
        ),

        'raw_yaw_rmse': rmse(
            data['raw_yaw_error']
        ),
        'noisy_yaw_rmse': rmse(
            data['noisy_yaw_error']
        ),
        'ekf_yaw_rmse': rmse(
            data['ekf_yaw_error']
        ),

        'raw_yaw_mae': mean_absolute(
            data['raw_yaw_error']
        ),
        'noisy_yaw_mae': mean_absolute(
            data['noisy_yaw_error']
        ),
        'ekf_yaw_mae': mean_absolute(
            data['ekf_yaw_error']
        ),
    }


def save_trajectory_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    plt.figure(figsize=(9, 8))

    plt.plot(
        data['amcl_x'],
        data['amcl_y'],
        linewidth=2.5,
        label='AMCL',
    )

    plt.plot(
        data['raw_x'],
        data['raw_y'],
        linewidth=1.8,
        label='Raw wheel odometry',
    )

    plt.plot(
        data['noisy_x'],
        data['noisy_y'],
        linewidth=1.0,
        alpha=0.65,
        label='Noisy odometry',
    )

    plt.plot(
        data['ekf_x'],
        data['ekf_y'],
        linewidth=2.0,
        label='EKF filtered odometry',
    )

    plt.scatter(
        data['amcl_x'][0],
        data['amcl_y'][0],
        marker='o',
        s=80,
        label='Start',
    )

    plt.xlabel('X position [m]')
    plt.ylabel('Y position [m]')
    plt.title(
        'Localization fusion: Raw, Noisy, AMCL and EKF Trajectories'
    )
    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def save_position_error_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    time_sec = relative_time(data['time_sec'])

    plt.figure(figsize=(10, 6))

    plt.plot(
        time_sec,
        data['raw_position_error'],
        label='Raw wheel odometry',
    )

    plt.plot(
        time_sec,
        data['noisy_position_error'],
        label='Noisy odometry',
    )

    plt.plot(
        time_sec,
        data['ekf_position_error'],
        label='EKF filtered odometry',
    )

    plt.xlabel('Elapsed recording time [s]')
    plt.ylabel('Position error relative to AMCL [m]')
    plt.title('Localization fusion: Position Error Relative to AMCL')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def save_yaw_error_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    time_sec = relative_time(data['time_sec'])

    raw_degrees = [
        math.degrees(value)
        for value in data['raw_yaw_error']
    ]

    noisy_degrees = [
        math.degrees(value)
        for value in data['noisy_yaw_error']
    ]

    ekf_degrees = [
        math.degrees(value)
        for value in data['ekf_yaw_error']
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        time_sec,
        raw_degrees,
        label='Raw wheel odometry',
    )

    plt.plot(
        time_sec,
        noisy_degrees,
        label='Noisy odometry',
    )

    plt.plot(
        time_sec,
        ekf_degrees,
        label='EKF filtered odometry',
    )

    plt.xlabel('Elapsed recording time [s]')
    plt.ylabel('Yaw error relative to AMCL [degrees]')
    plt.title('Localization fusion: Heading Error Relative to AMCL')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=220)
    plt.close()


def write_report(
    metrics: dict[str, float],
    output_path: Path,
) -> None:
    noisy_position_improvement = (
        100.0
        * (
            metrics['noisy_position_rmse']
            - metrics['ekf_position_rmse']
        )
        / metrics['noisy_position_rmse']
        if metrics['noisy_position_rmse'] > 0.0
        else math.nan
    )

    noisy_yaw_improvement = (
        100.0
        * (
            metrics['noisy_yaw_rmse']
            - metrics['ekf_yaw_rmse']
        )
        / metrics['noisy_yaw_rmse']
        if metrics['noisy_yaw_rmse'] > 0.0
        else math.nan
    )

    raw_yaw_row = (
        '| Raw wheel odometry | '
        f'{metrics["raw_yaw_rmse"]:.6f} | '
        f'{math.degrees(metrics["raw_yaw_rmse"]):.3f} | '
        f'{metrics["raw_yaw_mae"]:.6f} |'
    )
    noisy_yaw_row = (
        '| Noisy odometry | '
        f'{metrics["noisy_yaw_rmse"]:.6f} | '
        f'{math.degrees(metrics["noisy_yaw_rmse"]):.3f} | '
        f'{metrics["noisy_yaw_mae"]:.6f} |'
    )
    ekf_yaw_row = (
        '| EKF filtered odometry | '
        f'{metrics["ekf_yaw_rmse"]:.6f} | '
        f'{math.degrees(metrics["ekf_yaw_rmse"]):.3f} | '
        f'{metrics["ekf_yaw_mae"]:.6f} |'
    )

    report = f"""# Localization fusion Fusion Analysis

## Experiment

The comparison uses AMCL as the map-frame localization reference.

The other trajectories are transformed into the map frame using one
fixed initial map-to-odometry alignment. The alignment is captured once
and is not continuously updated.

The compared sources are:

- Raw wheel odometry
- Artificially noisy wheel odometry
- EKF-filtered noisy odometry and IMU yaw rate
- AMCL localization

## Samples

{int(metrics["samples"])}

## Position error relative to AMCL

| Estimate | RMSE [m] | Maximum error [m] |
|---|---:|---:|
| Raw wheel odometry | {metrics["raw_position_rmse"]:.6f} | {metrics["raw_position_max"]:.6f} |
| Noisy odometry | {metrics["noisy_position_rmse"]:.6f} | {metrics["noisy_position_max"]:.6f} |
| EKF filtered odometry | {metrics["ekf_position_rmse"]:.6f} | {metrics["ekf_position_max"]:.6f} |

EKF position-RMSE improvement relative to noisy odometry:
{noisy_position_improvement:.2f}%

## Yaw error relative to AMCL

| Estimate | RMSE [rad] | RMSE [deg] | Mean absolute error [rad] |
|---|---:|---:|---:|
{raw_yaw_row}
{noisy_yaw_row}
{ekf_yaw_row}

EKF yaw-RMSE improvement relative to noisy odometry:
{noisy_yaw_improvement:.2f}%

## Interpretation

The noisy odometry contains independent position, heading, linear
velocity and angular velocity disturbances.

The EKF fuses the noisy forward velocity and yaw rate with the simulated
IMU yaw-rate measurement. It therefore estimates a smoother motion state
than the noisy source alone.

Raw wheel odometry may perform unusually well in this simulation because
its motion is derived directly from the simulated wheel joints and does
not contain the same wheel slip, calibration error, encoder quantization
and mechanical uncertainty expected on physical hardware.

AMCL provides scan-corrected map-frame localization, while wheel
odometry and the EKF remain locally continuous dead-reckoning estimates.
"""

    output_path.write_text(report, encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate Localization fusion fusion-analysis plots.'
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input Localization fusion CSV path.',
    )

    parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory for plots and metrics report.',
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(
            f'Input CSV does not exist: {input_path}'
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_csv(input_path)
    metrics = calculate_metrics(data)

    trajectory_path = (
        output_dir / 'fusion_comparison.png'
    )

    position_error_path = (
        output_dir / 'fusion_position_error.png'
    )

    yaw_error_path = (
        output_dir / 'fusion_yaw_error.png'
    )

    report_path = (
        output_dir / 'localization_fusion_metrics.md'
    )

    save_trajectory_plot(data, trajectory_path)
    save_position_error_plot(data, position_error_path)
    save_yaw_error_plot(data, yaw_error_path)
    write_report(metrics, report_path)

    print(f"Samples: {int(metrics['samples'])}")

    print(
        'Raw position RMSE: '
        f"{metrics['raw_position_rmse']:.6f} m"
    )

    print(
        'Noisy position RMSE: '
        f"{metrics['noisy_position_rmse']:.6f} m"
    )

    print(
        'EKF position RMSE: '
        f"{metrics['ekf_position_rmse']:.6f} m"
    )

    print(
        'Raw yaw RMSE: '
        f"{metrics['raw_yaw_rmse']:.6f} rad"
    )

    print(
        'Noisy yaw RMSE: '
        f"{metrics['noisy_yaw_rmse']:.6f} rad"
    )

    print(
        'EKF yaw RMSE: '
        f"{metrics['ekf_yaw_rmse']:.6f} rad"
    )

    print(f'Saved: {trajectory_path}')
    print(f'Saved: {position_error_path}')
    print(f'Saved: {yaw_error_path}')
    print(f'Saved: {report_path}')


if __name__ == '__main__':
    main()
