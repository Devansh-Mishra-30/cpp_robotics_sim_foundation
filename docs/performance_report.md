# Day 88 - Performance Benchmark Report

## Purpose

This report benchmarks the deterministic pose-update layer of the C++ robotics simulation stack.

The benchmark compares three simulation timesteps: `dt=0.1`, `dt=0.01`, and `dt=0.001`.

## Benchmark Configuration

| Parameter | Value |
|---|---:|
| Simulated duration per run | 10 sec |
| Virtual robot states | 1000 |
| Trials per dt | 5 |

## Results

| dt | Steps | Total updates | Mean wall time (ms) | Mean step time (us) | Max step time (us) | Mean real-time factor |
|---:|---:|---:|---:|---:|---:|---:|
| 0.100000 | 100 | 100000 | 1.825736 | 18.257358 | 96.457000 | 5684.978549 |
| 0.010000 | 1000 | 1000000 | 17.402707 | 17.402707 | 365.555000 | 574.992884 |
| 0.001000 | 10000 | 10000000 | 174.740537 | 17.474054 | 1061.030000 | 57.229905 |

## Interpretation

Smaller timestep values require more simulation steps for the same amount of simulated time. This increases computational cost, even though it can improve numerical resolution.

The `mean_avg_step_us` column estimates the average time spent in one update-step batch. The `max_step_us` column captures the slowest observed update-step batch across all trials.

The `mean_realtime_factor` estimates how many simulated seconds were processed per real wall-clock second for this deterministic update layer. A value greater than 1.0 means this core update loop is faster than real time.

## Scope

This benchmark does not include Gazebo physics, rendering, ROS 2 middleware, controller manager overhead, TF broadcasting, sensor simulation, rosbag logging, or RViz visualization.

This is the first performance layer: deterministic C++ kinematic update timing. Later benchmark phases can add ROS callback timing, launch-level regression, Gazebo real-time factor, Nav2 behavior, and rosbag/logging overhead.

## Interview Explanation

I added a C++ performance benchmark for the deterministic pose-update layer of my robotics simulator. The benchmark compares different simulation timesteps, measures average and maximum update time, and reports an estimated real-time factor. This gives the project a timing baseline before deeper ROS 2, Gazebo, and Nav2 performance testing.
