# Day 85 — Trajectory Validation Report

## Purpose

This report validates the Gazebo `ros2_control` differential-drive stack by comparing commanded velocity, actual odometry, and noisy odometry.

The validation data comes from:

```txt
data/day84_trajectory_validation.csv
```

The generated plot is:

```txt
plots/trajectory_validation.png
```

---

## System Under Test

The robot is moved by the Gazebo `ros2_control` stack:

```txt
/diff_drive_controller/cmd_vel
    -> diff_drive_controller
    -> ros2_control
    -> gz_ros2_control
    -> Gazebo wheel joints
    -> /diff_drive_controller/odom
```

The noisy odometry stream is produced by:

```txt
/diff_drive_controller/odom
    -> noisy_odom_node.py
    -> /odom_noisy
```

Important:

```txt
/odom_noisy does not move Gazebo.
It is a noisy feedback stream for validation and future localization work.
```

---

## Validation Metrics

| Metric | Value |
|---|---:|
| samples | 981 |
| duration | 48.120000 s |
| actual path length | 7.729966 m |
| final actual x | -0.123778 m |
| final actual y | 0.006144 m |
| final actual yaw | -0.099185 rad |
| mean position noise error | 0.024892 m |
| max position noise error | 0.066334 m |
| mean yaw noise error | 0.015597 rad |
| max yaw noise error | 0.063535 rad |
| max commanded linear velocity | 0.250000 m/s |
| max actual linear velocity | 0.256755 m/s |
| max commanded yaw rate | 0.200000 rad/s |
| max actual yaw rate | 0.205404 rad/s |

---

## Interpretation

The commanded velocity columns show the desired robot motion.

The actual odometry columns show the executed robot motion reported by the Gazebo `diff_drive_controller`.

The noisy odometry columns show a controlled noisy measurement stream created from actual odometry.

The actual and noisy trajectories should be close but not identical. The difference between them represents simulated measurement uncertainty.

---

## Interview Explanation

Day 85 converts raw validation data into engineering evidence.

Instead of only saying the robot moves in Gazebo, this report shows that the system can record command signals, actual odometry feedback, noisy measurement feedback, and quantitative trajectory metrics.

This is important for robotics simulation engineering because simulation behavior must be measurable, repeatable, and comparable.

---

## Key Takeaways

- The robot was commanded through `/diff_drive_controller/cmd_vel`.
- Actual executed motion was recorded from `/diff_drive_controller/odom`.
- Noisy feedback was recorded from `/odom_noisy`.
- Position and yaw noise errors were computed.
- Commanded velocity and actual velocity were compared.
- A portfolio-ready validation plot was generated.

---

## Day 85 Completion Criteria

Day 85 is complete when:

- `plots/trajectory_validation.png` exists.
- `docs/trajectory_validation_report.md` exists.
- The report contains path length, final pose, noise error, and velocity metrics.
- Day 68 regression still passes.
