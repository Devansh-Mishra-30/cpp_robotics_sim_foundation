#!/usr/bin/env python3

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


def load_csv(path: Path) -> dict[str, list[float]]:
    columns: dict[str, list[float]] = {}

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")

        for field in reader.fieldnames:
            columns[field] = []

        for row in reader:
            for field in reader.fieldnames:
                columns[field].append(float(row[field]))

    if not columns["time_sec"]:
        raise ValueError("CSV contains no data rows.")

    return columns


def calculate_metrics(data: dict[str, list[float]]) -> dict[str, float]:
    position_errors = data["position_error_m"]
    absolute_yaw_errors = [
        abs(error)
        for error in data["yaw_error_rad"]
    ]

    position_rmse = math.sqrt(
        sum(error * error for error in position_errors)
        / len(position_errors)
    )

    yaw_rmse = math.sqrt(
        sum(error * error for error in absolute_yaw_errors)
        / len(absolute_yaw_errors)
    )

    return {
        "samples": float(len(position_errors)),
        "mean_position_error": (
            sum(position_errors) / len(position_errors)
        ),
        "max_position_error": max(position_errors),
        "position_rmse": position_rmse,
        "mean_absolute_yaw_error": (
            sum(absolute_yaw_errors)
            / len(absolute_yaw_errors)
        ),
        "max_absolute_yaw_error": max(absolute_yaw_errors),
        "yaw_rmse": yaw_rmse,
    }


def save_trajectory_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    plt.figure(figsize=(8, 7))

    plt.plot(
        data["amcl_x"],
        data["amcl_y"],
        marker="o",
        label="AMCL",
    )

    plt.plot(
        data["odom_aligned_x"],
        data["odom_aligned_y"],
        marker="x",
        label="Aligned wheel odometry",
    )

    plt.xlabel("X position [m]")
    plt.ylabel("Y position [m]")
    plt.title("Day 104: AMCL vs Wheel Odometry Trajectory")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_position_error_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    initial_time = data["time_sec"][0]

    relative_time = [
        time_value - initial_time
        for time_value in data["time_sec"]
    ]

    plt.figure(figsize=(9, 5))

    plt.plot(
        relative_time,
        data["position_error_m"],
        marker="o",
    )

    plt.xlabel("Elapsed recording time [s]")
    plt.ylabel("Position error [m]")
    plt.title("Day 104: Position Error")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_yaw_error_plot(
    data: dict[str, list[float]],
    output_path: Path,
) -> None:
    initial_time = data["time_sec"][0]

    relative_time = [
        time_value - initial_time
        for time_value in data["time_sec"]
    ]

    yaw_error_degrees = [
        math.degrees(error)
        for error in data["yaw_error_rad"]
    ]

    plt.figure(figsize=(9, 5))

    plt.plot(
        relative_time,
        yaw_error_degrees,
        marker="o",
    )

    plt.xlabel("Elapsed recording time [s]")
    plt.ylabel("Yaw error [degrees]")
    plt.title("Day 104: Heading Error")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def write_report(
    metrics: dict[str, float],
    output_path: Path,
) -> None:
    report = f"""# Day 104 Localization Comparison Results

## Samples

{int(metrics["samples"])}

## Position Error

- Mean position error: {metrics["mean_position_error"]:.4f} m
- Maximum position error: {metrics["max_position_error"]:.4f} m
- Position RMSE: {metrics["position_rmse"]:.4f} m

## Heading Error

- Mean absolute yaw error: {metrics["mean_absolute_yaw_error"]:.4f} rad
- Maximum absolute yaw error: {metrics["max_absolute_yaw_error"]:.4f} rad
- Yaw RMSE: {metrics["yaw_rmse"]:.4f} rad
- Yaw RMSE: {math.degrees(metrics["yaw_rmse"]):.2f} degrees

## Interpretation

Wheel odometry and AMCL were aligned at the first synchronized sample.

The fixed initial alignment was preserved throughout the experiment.
This prevents the continuously updated AMCL map-to-odom correction from
artificially forcing the two trajectories to overlap.

The measured error increased as the robot rotated and translated. This
demonstrates the difference between dead-reckoned wheel odometry and
scan-corrected map-frame localization.
"""

    output_path.write_text(report, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plot Day 104 AMCL and wheel-odometry comparison data."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to the Day 104 CSV file.",
    )

    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory for plots and the summary report.",
    )

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Input CSV does not exist: {input_path}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    data = load_csv(input_path)
    metrics = calculate_metrics(data)

    trajectory_path = (
        output_dir / "day104_amcl_vs_odom_trajectory.png"
    )

    position_error_path = (
        output_dir / "day104_position_error.png"
    )

    yaw_error_path = (
        output_dir / "day104_yaw_error.png"
    )

    report_path = (
        output_dir / "day104_localization_comparison_report.md"
    )

    save_trajectory_plot(data, trajectory_path)
    save_position_error_plot(data, position_error_path)
    save_yaw_error_plot(data, yaw_error_path)
    write_report(metrics, report_path)

    print(f"Samples: {int(metrics['samples'])}")
    print(
        "Position RMSE: "
        f"{metrics['position_rmse']:.4f} m"
    )
    print(
        "Yaw RMSE: "
        f"{metrics['yaw_rmse']:.4f} rad "
        f"({math.degrees(metrics['yaw_rmse']):.2f} degrees)"
    )

    print(f"Saved: {trajectory_path}")
    print(f"Saved: {position_error_path}")
    print(f"Saved: {yaw_error_path}")
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
