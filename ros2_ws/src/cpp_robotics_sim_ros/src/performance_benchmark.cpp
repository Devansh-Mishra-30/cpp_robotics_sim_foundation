// Copyright 2026 Devansh Mishra
//
// Use of this source code is governed by an MIT-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/MIT.

#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "cpp_robotics_sim_ros/core_math.hpp"

namespace
{

using cpp_robotics_sim_ros::Pose2D;
using cpp_robotics_sim_ros::integratePose;

struct BenchmarkConfig
{
  std::vector<double> dt_values{0.1, 0.01, 0.001};
  double simulated_duration_sec{10.0};
  int virtual_robot_count{1000};
  int trials{5};
  std::string output_csv{"data/day88_performance_results.csv"};
  std::string output_report{"docs/performance_report.md"};
};

struct BenchmarkResult
{
  double dt{0.0};
  double simulated_duration_sec{0.0};
  int steps{0};
  int virtual_robot_count{0};
  int trials{0};
  std::int64_t total_updates{0};

  double mean_total_wall_ms{0.0};
  double mean_avg_step_us{0.0};
  double max_step_us{0.0};
  double mean_realtime_factor{0.0};

  double checksum{0.0};
};

double parseDouble(const std::string & value, const std::string & argument_name)
{
  try {
    return std::stod(value);
  } catch (const std::exception &) {
    throw std::invalid_argument("Invalid double for " + argument_name + ": " + value);
  }
}

int parseInt(const std::string & value, const std::string & argument_name)
{
  try {
    return std::stoi(value);
  } catch (const std::exception &) {
    throw std::invalid_argument("Invalid integer for " + argument_name + ": " + value);
  }
}

BenchmarkConfig parseArguments(int argc, char ** argv)
{
  BenchmarkConfig config;

  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];

    auto require_next_value = [&](const std::string & name) {
        if (i + 1 >= argc) {
          throw std::invalid_argument("Missing value after " + name);
        }
        return std::string(argv[++i]);
      };

    if (arg == "--output") {
      config.output_csv = require_next_value(arg);
    } else if (arg == "--report") {
      config.output_report = require_next_value(arg);
    } else if (arg == "--sim-duration") {
      config.simulated_duration_sec = parseDouble(require_next_value(arg), arg);
    } else if (arg == "--virtual-robots") {
      config.virtual_robot_count = parseInt(require_next_value(arg), arg);
    } else if (arg == "--trials") {
      config.trials = parseInt(require_next_value(arg), arg);
    } else if (arg == "--help") {
      std::cout
        << "Performance Benchmark\n\n"
        << "Options:\n"
        << "  --output <path>          Output CSV path\n"
        << "  --report <path>          Output Markdown report path\n"
        << "  --sim-duration <sec>     Simulated duration per run\n"
        << "  --virtual-robots <count> Number of virtual robot states\n"
        << "  --trials <count>         Trials per dt value\n";
      std::exit(0);
    } else {
      throw std::invalid_argument("Unknown argument: " + arg);
    }
  }

  if (config.simulated_duration_sec <= 0.0) {
    throw std::invalid_argument("simulated duration must be positive");
  }

  if (config.virtual_robot_count <= 0) {
    throw std::invalid_argument("virtual robot count must be positive");
  }

  if (config.trials <= 0) {
    throw std::invalid_argument("trial count must be positive");
  }

  return config;
}

std::vector<Pose2D> createInitialPoses(int count)
{
  std::vector<Pose2D> poses;
  poses.reserve(static_cast<std::size_t>(count));

  for (int i = 0; i < count; ++i) {
    Pose2D pose;
    pose.x = 0.001 * static_cast<double>(i % 100);
    pose.y = 0.001 * static_cast<double>((i / 100) % 100);
    pose.theta = 0.01 * static_cast<double>(i % 50);
    poses.push_back(pose);
  }

  return poses;
}

BenchmarkResult runBenchmarkForDt(
  double dt,
  const BenchmarkConfig & config)
{
  const int steps = static_cast<int>(std::ceil(config.simulated_duration_sec / dt));

  BenchmarkResult result;
  result.dt = dt;
  result.simulated_duration_sec = config.simulated_duration_sec;
  result.steps = steps;
  result.virtual_robot_count = config.virtual_robot_count;
  result.trials = config.trials;
  result.total_updates =
    static_cast<std::int64_t>(steps) *
    static_cast<std::int64_t>(config.virtual_robot_count);

  double sum_total_wall_ms = 0.0;
  double sum_avg_step_us = 0.0;
  double sum_realtime_factor = 0.0;
  double max_step_us_across_trials = 0.0;
  double checksum = 0.0;

  for (int trial = 0; trial < config.trials; ++trial) {
    std::vector<Pose2D> poses = createInitialPoses(config.virtual_robot_count);

    double max_step_us_this_trial = 0.0;

    const auto trial_start = std::chrono::steady_clock::now();

    for (int step = 0; step < steps; ++step) {
      const auto step_start = std::chrono::steady_clock::now();

      for (int i = 0; i < config.virtual_robot_count; ++i) {
        const double linear_velocity = 0.25 + 0.001 * static_cast<double>(i % 5);
        const double angular_velocity = 0.20 + 0.001 * static_cast<double>(i % 3);

        poses[static_cast<std::size_t>(i)] =
          integratePose(
          poses[static_cast<std::size_t>(i)],
          linear_velocity,
          angular_velocity,
          dt);
      }

      const auto step_end = std::chrono::steady_clock::now();

      const double step_us =
        std::chrono::duration<double, std::micro>(step_end - step_start).count();

      if (step_us > max_step_us_this_trial) {
        max_step_us_this_trial = step_us;
      }
    }

    const auto trial_end = std::chrono::steady_clock::now();

    const double total_wall_ms =
      std::chrono::duration<double, std::milli>(trial_end - trial_start).count();

    const double avg_step_us = (total_wall_ms * 1000.0) / static_cast<double>(steps);
    const double realtime_factor = config.simulated_duration_sec / (total_wall_ms / 1000.0);

    sum_total_wall_ms += total_wall_ms;
    sum_avg_step_us += avg_step_us;
    sum_realtime_factor += realtime_factor;

    if (max_step_us_this_trial > max_step_us_across_trials) {
      max_step_us_across_trials = max_step_us_this_trial;
    }

    for (const auto & pose : poses) {
      checksum += pose.x + pose.y + pose.theta;
    }
  }

  result.mean_total_wall_ms = sum_total_wall_ms / static_cast<double>(config.trials);
  result.mean_avg_step_us = sum_avg_step_us / static_cast<double>(config.trials);
  result.max_step_us = max_step_us_across_trials;
  result.mean_realtime_factor = sum_realtime_factor / static_cast<double>(config.trials);
  result.checksum = checksum;

  return result;
}

void writeCsv(
  const std::string & output_path,
  const std::vector<BenchmarkResult> & results)
{
  std::ofstream file(output_path);

  if (!file.is_open()) {
    throw std::runtime_error("Failed to open CSV output file: " + output_path);
  }

  file
    << "dt,"
    << "simulated_duration_sec,"
    << "steps,"
    << "virtual_robot_count,"
    << "trials,"
    << "total_updates,"
    << "mean_total_wall_ms,"
    << "mean_avg_step_us,"
    << "max_step_us,"
    << "mean_realtime_factor,"
    << "checksum\n";

  file << std::fixed << std::setprecision(6);

  for (const auto & result : results) {
    file
      << result.dt << ","
      << result.simulated_duration_sec << ","
      << result.steps << ","
      << result.virtual_robot_count << ","
      << result.trials << ","
      << result.total_updates << ","
      << result.mean_total_wall_ms << ","
      << result.mean_avg_step_us << ","
      << result.max_step_us << ","
      << result.mean_realtime_factor << ","
      << result.checksum << "\n";
  }
}

void writeMarkdownReport(
  const std::string & output_path,
  const BenchmarkConfig & config,
  const std::vector<BenchmarkResult> & results)
{
  std::ofstream file(output_path);

  if (!file.is_open()) {
    throw std::runtime_error("Failed to open Markdown report file: " + output_path);
  }

  file << "# Performance Benchmark Report\n\n";

  file << "## Purpose\n\n";
  file
    << "This report benchmarks the deterministic pose-update layer of the "
    << "C++ robotics simulation stack.\n\n";

  file
    << "The benchmark compares three simulation timesteps: `dt=0.1`, "
    << "`dt=0.01`, and `dt=0.001`.\n\n";

  file << "## Benchmark Configuration\n\n";
  file << "| Parameter | Value |\n";
  file << "|---|---:|\n";
  file << "| Simulated duration per run | " << config.simulated_duration_sec << " sec |\n";
  file << "| Virtual robot states | " << config.virtual_robot_count << " |\n";
  file << "| Trials per dt | " << config.trials << " |\n\n";

  file << "## Results\n\n";
  file
    << "| dt | Steps | Total updates | Mean wall time (ms) | "
    << "Mean step time (us) | Max step time (us) | Mean real-time factor |\n";
  file << "|---:|---:|---:|---:|---:|---:|---:|\n";

  file << std::fixed << std::setprecision(6);

  for (const auto & result : results) {
    file
      << "| " << result.dt
      << " | " << result.steps
      << " | " << result.total_updates
      << " | " << result.mean_total_wall_ms
      << " | " << result.mean_avg_step_us
      << " | " << result.max_step_us
      << " | " << result.mean_realtime_factor
      << " |\n";
  }

  file << "\n## Interpretation\n\n";
  file
    << "Smaller timestep values require more simulation steps for the same "
    << "amount of simulated time. This increases computational cost, even "
    << "though it can improve numerical resolution.\n\n";

  file
    << "The `mean_avg_step_us` column estimates the average time spent in one "
    << "update-step batch. The `max_step_us` column captures the slowest observed "
    << "update-step batch across all trials.\n\n";

  file
    << "The `mean_realtime_factor` estimates how many simulated seconds were "
    << "processed per real wall-clock second for this deterministic update layer. "
    << "A value greater than 1.0 means this core update loop is faster than real time.\n\n";

  file << "## Scope\n\n";
  file
    << "This benchmark does not include Gazebo physics, rendering, ROS 2 middleware, "
    << "controller manager overhead, TF broadcasting, sensor simulation, rosbag logging, "
    << "or RViz visualization.\n\n";

  file
    << "This is the first performance layer: deterministic C++ kinematic update timing. "
    << "Later benchmark phases can add ROS callback timing, launch-level regression, "
    << "Gazebo real-time factor, Nav2 behavior, and rosbag/logging overhead.\n\n";

  file << "## Interview Explanation\n\n";
  file
    << "I added a C++ performance benchmark for the deterministic pose-update layer "
    << "of my robotics simulator. The benchmark compares different simulation "
    << "timesteps, measures average and maximum update time, and reports an estimated "
    << "real-time factor. This gives the project a timing baseline before deeper "
    << "ROS 2, Gazebo, and Nav2 performance testing.\n";
}

void printSummary(const std::vector<BenchmarkResult> & results)
{
  std::cout << "\nPerformance Benchmark Results\n";
  std::cout << "------------------------------------\n";
  std::cout
    << std::setw(10) << "dt"
    << std::setw(12) << "steps"
    << std::setw(18) << "mean ms"
    << std::setw(18) << "avg step us"
    << std::setw(18) << "max step us"
    << std::setw(12) << "RTF"
    << "\n";

  std::cout << std::fixed << std::setprecision(6);

  for (const auto & result : results) {
    std::cout
      << std::setw(10) << result.dt
      << std::setw(12) << result.steps
      << std::setw(18) << result.mean_total_wall_ms
      << std::setw(18) << result.mean_avg_step_us
      << std::setw(18) << result.max_step_us
      << std::setw(12) << result.mean_realtime_factor
      << "\n";
  }

  std::cout << "\n";
}

}  // namespace

int main(int argc, char ** argv)
{
  try {
    const BenchmarkConfig config = parseArguments(argc, argv);

    std::vector<BenchmarkResult> results;
    results.reserve(config.dt_values.size());

    for (const double dt : config.dt_values) {
      results.push_back(runBenchmarkForDt(dt, config));
    }

    writeCsv(config.output_csv, results);
    writeMarkdownReport(config.output_report, config, results);
    printSummary(results);

    std::cout << "Generated CSV:    " << config.output_csv << "\n";
    std::cout << "Generated report: " << config.output_report << "\n";

    return 0;
  } catch (const std::exception & error) {
    std::cerr << "Performance benchmark failed: " << error.what() << "\n";
    return 1;
  }
}
