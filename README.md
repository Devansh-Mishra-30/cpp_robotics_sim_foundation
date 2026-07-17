# C++ Robotics Simulation Foundation

[![ROS 2 Jazzy CI](https://github.com/Devansh-Mishra-30/cpp_robotics_sim_foundation/actions/workflows/ros2_jazzy_ci.yml/badge.svg)](https://github.com/Devansh-Mishra-30/cpp_robotics_sim_foundation/actions/workflows/ros2_jazzy_ci.yml)
![ROS 2](https://img.shields.io/badge/ROS%202-Jazzy-22314E)
![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04-E95420)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-FF6F00)
![License](https://img.shields.io/badge/License-MIT-green)

A browser-controlled ROS 2 autonomous mobile robot simulation platform for **manual control, SLAM mapping, map management, AMCL localization, Nav2 navigation, lifecycle orchestration, and repeatable validation**.

The project began as a C++ robotics-learning exercise and evolved into a managed simulation workflow that reduces repeated terminal setup, coordinates multiple ROS 2 subsystems, and provides one interface for operating and validating an autonomous mobile robot stack.

> **Release status:** `v0.1.0` stable release
> **Primary environment:** Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic
> **Validation baseline:** 357 automated tests, native and Docker validation, launch regression, dashboard integration, and launcher lifecycle tests

---

## Overview

The platform brings together:

- a differential-drive mobile robot modeled in URDF/Xacro;
- Gazebo Harmonic simulation;
- `ros2_control` and `diff_drive_controller`;
- simulated LiDAR, odometry, TF, and joint states;
- SLAM Toolbox mapping;
- environment-aware map storage;
- AMCL localization;
- Nav2 planning, control, goal execution, and cancellation;
- browser-based simulation and mode management;
- runtime safety, command arbitration, and clean shutdown;
- native, CI, and Docker-based validation.

The primary user workflow is controlled from the browser dashboard rather than by repeatedly launching individual nodes and commands manually.

---

## Demo and Media

The `v0.1.0` release media includes a Warehouse teaser and a complete workflow demonstration covering manual control, mapping, localization, navigation, validation, and clean shutdown.

Public video links and selected screenshots will be added here after the release media is published.

Recommended repository media layout:

```text
docs/media/
├── dashboard.png
├── warehouse.png
├── hospital.png
├── mapping.png
├── localization.png
├── navigation.png
└── architecture.png
```

---

## Current Capabilities

### Simulation lifecycle

- Select Warehouse or Hospital simulation environments.
- Launch Gazebo and the complete robot-control stack.
- Stop and reset the simulation from the dashboard.
- Prevent environment changes while a simulation is active.
- Detect unexpected simulator exits.
- Recover environment selection after an external Gazebo close.
- Clean up managed processes during stop and shutdown.

### Manual control

- Browser-based velocity commands.
- Keyboard and supported dashboard control paths.
- Command-source tracking.
- Velocity routing through a controlled command pipeline.
- Safe zero-velocity output when control ends.

### Mapping

- Start and stop SLAM Toolbox from the dashboard.
- Build a map from LiDAR and odometry.
- Save maps under an environment-specific map directory.
- Validate and sanitize map names.
- List available saved maps.
- Preserve map metadata and image files.

### Localization

- Select an environment-specific saved map.
- Launch `map_server` and AMCL.
- Publish an initial pose.
- Maintain the `map → odom → base_link` transform chain.
- Recover cleanly when switching environments or stopping modes.

### Navigation

- Launch the Nav2 stack from the dashboard.
- Submit map-frame navigation goals.
- Monitor goal state and feedback.
- Cancel active goals.
- Stop the robot after success or cancellation.
- Prevent conflicting command sources.

### Validation and release engineering

- Python, JavaScript, and Bash syntax checks.
- C++ GoogleTest coverage.
- Python unit and behavior tests.
- ROS 2 linting through ament.
- Simulator launch regression.
- Headless dashboard integration testing.
- Public launcher lifecycle testing.
- Docker build and full container test gate.
- GitHub Actions CI for ROS 2 Jazzy.

---

## Environments

| Environment | Purpose |
|---|---|
| **Warehouse** | Aisles, obstacles, loading areas, and navigation corridors |
| **Hospital** | Corridors, rooms, reception areas, and indoor navigation scenarios |

Environment definitions are registered in:

```text
ros2_ws/src/cpp_robotics_sim_ros/config/environment_registry.yaml
```

World files are stored in:

```text
ros2_ws/src/cpp_robotics_sim_ros/worlds/
```

Saved maps are stored outside the repository by default:

```text
~/.ros/cpp_robotics_sim/maps/<environment>/
```

Example:

```text
~/.ros/cpp_robotics_sim/maps/hospital/hospital.yaml
~/.ros/cpp_robotics_sim/maps/hospital/hospital.pgm
```

---

## Architecture

```text
Browser Dashboard
        │
        │ rosbridge WebSocket
        ▼
Simulation / Mode / Mapping / Localization / Navigation Managers
        │
        ├── Simulation lifecycle and environment selection
        ├── Command-source arbitration and safe stop
        ├── SLAM Toolbox and map management
        ├── Map server and AMCL localization
        └── Nav2 goal execution and cancellation
        │
        ▼
ROS 2 Runtime
        │
        ├── robot_state_publisher
        ├── controller_manager
        ├── joint_state_broadcaster
        ├── diff_drive_controller
        ├── ros_gz_bridge
        ├── SLAM Toolbox
        ├── AMCL
        ├── map_server
        └── Nav2
        │
        ▼
Gazebo Harmonic
        │
        ├── Differential-drive robot
        ├── Wheel joints
        ├── LiDAR
        └── Warehouse / Hospital worlds
```

Detailed architecture:

- [`docs/installation.md`](docs/installation.md)
- [`docs/system_architecture.md`](docs/system_architecture.md)
- [`docs/topic_interface_reference.md`](docs/topic_interface_reference.md)
- [`docs/debugging_and_validation.md`](docs/debugging_and_validation.md)

---

## Repository Structure

```text
cpp_robotics_sim_foundation/
├── .github/
│   └── workflows/
│       └── ros2_jazzy_ci.yml
├── docs/
│   ├── debugging_and_validation.md
│   ├── installation.md
│   ├── system_architecture.md
│   └── topic_interface_reference.md
├── ros2_ws/
│   └── src/
│       └── cpp_robotics_sim_ros/
│           ├── config/
│           ├── launch/
│           ├── maps/
│           ├── nav2/
│           ├── rviz/
│           ├── scripts/
│           ├── src/
│           ├── test/
│           ├── urdf/
│           ├── web/
│           ├── worlds/
│           └── xacro/
├── scripts/
│   ├── check_syntax.sh
│   ├── launch_regression.sh
│   ├── run.sh
│   └── test.sh
├── Dockerfile
├── LICENSE
└── README.md
```

Generated build products, logs, bags, and local maps should remain outside version control unless intentionally added.

---

## Requirements

### Supported development environment

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Python 3.12
- CMake and a C++17-compatible compiler
- `colcon`
- Docker Desktop or Docker Engine for container validation

WSL2 can be used when GUI forwarding and Docker integration are configured correctly.

### Core ROS packages

The workspace depends on packages including:

```text
nav2_bringup
nav2_amcl
nav2_map_server
nav2_controller
nav2_planner
nav2_bt_navigator
nav2_behaviors
nav2_waypoint_follower
nav2_velocity_smoother
nav2_lifecycle_manager
slam_toolbox
robot_localization
ros_gz_sim
ros_gz_bridge
gz_ros2_control
ros2_control
ros2_controllers
controller_manager
diff_drive_controller
robot_state_publisher
xacro
rosbridge_server
tf2_ros
```

Use `rosdep` to resolve package dependencies rather than installing them manually one by one.

---

## Clone and Install

Clone the repository:

```bash
git clone https://github.com/Devansh-Mishra-30/cpp_robotics_sim_foundation.git
cd cpp_robotics_sim_foundation
```

Install ROS 2 Jazzy before running the project setup script. The current
release setup supports Ubuntu 24.04.

From the repository root:

```bash
./scripts/setup.sh
```

The setup script:

- verifies that the host is Ubuntu 24.04;
- verifies that the configured ROS 2 installation exists;
- installs `python3-rosdep` when necessary;
- initializes and updates rosdep;
- resolves dependencies from `ros2_ws/src`;
- verifies that `colcon` and `ros2` are available.

The script may request administrator privileges while installing packages.

After setup completes:

```bash
./scripts/build.sh
./scripts/test.sh
```

## Build

From the repository root:

```bash
source /opt/ros/jazzy/setup.bash

cd ros2_ws

colcon build \
  --packages-select cpp_robotics_sim_ros \
  --cmake-args -DBUILD_TESTING=ON

source install/setup.bash
```

Expected result:

```text
Summary: 1 package finished
```

For development with symlinked Python and resource files:

```bash
colcon build \
  --packages-select cpp_robotics_sim_ros \
  --symlink-install \
  --cmake-args -DBUILD_TESTING=ON
```

---

## Run the Platform

From the repository root:

```bash
./scripts/run.sh
```

The launcher starts:

- the browser dashboard HTTP server;
- rosbridge WebSocket;
- simulation manager;
- mode manager;
- mapping manager;
- localization manager;
- navigation goal manager.

Default ports:

| Service | Port |
|---|---|
| Dashboard HTTP server | `8080` |
| rosbridge WebSocket | `9090` |

On native Linux, the dashboard is normally available at
`http://localhost:8080`. Under WSL2, `run.sh` detects the WSL network address,
prints the complete dashboard URL, and opens it in the Windows browser when
browser launching is enabled.

The dashboard does not automatically start Gazebo. Select an environment and
use **Start**.

---

## Dashboard Workflow

### 1. Start the platform

```bash
./scripts/run.sh
```

Open:

```text
http://localhost:8080
```

Confirm that the dashboard shows:

```text
ROS connected
Safety state: READY
Simulation: stopped
```

### 2. Select an environment

Choose:

- Warehouse; or
- Hospital.

Environment selection is locked while the simulation is running.

### 3. Start the simulation

Press **Start**.

Expected runtime components include:

```text
Gazebo
robot_state_publisher
controller_manager
joint_state_broadcaster
diff_drive_controller
LiDAR bridge
command routing
```

### 4. Choose an operating mode

The supported user modes are:

```text
Manual
Mapping
Localization
Navigation
```

Only one auxiliary mode should be active at a time.

### 5. Stop cleanly

Use **Stop Mode** before changing high-level operating modes when appropriate.

Use **Stop Simulation** before switching environments.

Stop the dashboard launcher with `Ctrl+C` after the simulation has stopped.

---

## Manual Control

1. Start the simulation.
2. Select **Manual**.
3. Use the dashboard controls to drive the robot.
4. Observe linear and angular command values.
5. Release control and verify that the command returns to zero.
6. Select **Stop Mode** when finished.

Safety behavior:

- the active command source is tracked;
- stale or inactive control should not continue moving the robot;
- a zero command is issued when manual control ends.

---

## Mapping Workflow

1. Start the selected simulation environment.
2. Select **Mapping**.
3. Drive the robot through unexplored areas.
4. Monitor live map growth.
5. Enter a valid map name.
6. Save the map.
7. Stop Mapping before starting Localization or Navigation.

Map output:

```text
~/.ros/cpp_robotics_sim/maps/<environment>/<map_name>.yaml
~/.ros/cpp_robotics_sim/maps/<environment>/<map_name>.pgm
```

Map names are validated to prevent invalid or unsafe paths.

---

## Localization Workflow

1. Stop Mapping.
2. Select a saved map for the current environment.
3. Start **Localization**.
4. Set the initial pose from the dashboard.
5. Confirm that AMCL becomes active.
6. Verify the map-based TF chain:

```text
map → odom → base_link
```

Useful checks:

```bash
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map base_link
ros2 topic info /map
ros2 topic info /scan
```

---

## Navigation Workflow

1. Complete or load a valid map.
2. Select the saved map for the current environment.
3. Select **Navigation**.
4. Set the initial pose from the dashboard.
5. Confirm that the map, AMCL, TF, and Nav2 servers are active.
6. Enter a map-frame goal:
   - `x`
   - `y`
   - `yaw`
7. Select **Send Goal**.
8. Monitor distance, estimated time, elapsed time, and recovery count.
9. Allow the goal to complete or select **Cancel Goal**.

Navigation mode launches its own map-server, AMCL, and Nav2 stack. Because
operating modes are mutually exclusive, Localization mode does not remain
active while Navigation mode is running.

Expected safety behavior:

- the command source changes to navigation while a goal is active;
- the robot stops after success;
- the robot stops after cancellation;
- the active source returns to none;
- the simulation remains running until explicitly stopped.

---

## ROS 2 Interfaces

### Dashboard and manager interfaces

#### Topics

| Interface | Type | Purpose |
|---|---|---|
| `/cmd_vel/gui` | `geometry_msgs/msg/TwistStamped` | Dashboard manual-velocity command |
| `/control/emergency_stop` | `std_msgs/msg/Bool` | Engage or release emergency stop |
| `/control/active_source` | `std_msgs/msg/String` | Current velocity-command source |
| `/simulation/status` | `std_msgs/msg/String` | High-level simulation state |
| `/simulation/environment_status` | `std_msgs/msg/String` | Environment state, selection, world, and lock status |
| `/simulation/environment_request` | `std_msgs/msg/String` | Requested simulation environment |
| `/mode/status` | `std_msgs/msg/String` | Active operating-mode state |
| `/mapping/save_request` | `std_msgs/msg/String` | Requested map name |
| `/mapping/save_status` | `std_msgs/msg/String` | JSON map-save result |
| `/mapping/saved_maps` | `std_msgs/msg/String` | JSON saved-map inventory |
| `/localization/select_map_request` | `std_msgs/msg/String` | JSON map-selection request |
| `/localization/initial_pose_request` | `std_msgs/msg/String` | JSON initial-pose request |
| `/localization/status` | `std_msgs/msg/String` | JSON localization-manager status |
| `/localization/selected_map` | `std_msgs/msg/String` | JSON selected-map metadata |
| `/navigation/goal_request` | `std_msgs/msg/String` | JSON map-frame goal request |
| `/navigation/cancel_request` | `std_msgs/msg/String` | JSON goal-cancellation request |
| `/navigation/status` | `std_msgs/msg/String` | JSON navigation state and final result |
| `/navigation/feedback` | `std_msgs/msg/String` | JSON navigation-progress feedback |

#### Services

| Interface | Type | Purpose |
|---|---|---|
| `/simulation/start` | `std_srvs/srv/Trigger` | Start the selected simulation environment |
| `/simulation/stop` | `std_srvs/srv/Trigger` | Stop the managed simulation |
| `/simulation/reset` | `std_srvs/srv/Trigger` | Stop and restart the selected environment |
| `/mode/manual` | `std_srvs/srv/Trigger` | Activate Manual mode |
| `/mode/mapping` | `std_srvs/srv/Trigger` | Launch Mapping mode |
| `/mode/localization` | `std_srvs/srv/Trigger` | Launch Localization mode |
| `/mode/navigation` | `std_srvs/srv/Trigger` | Launch Navigation mode |
| `/mode/stop` | `std_srvs/srv/Trigger` | Stop the active operating mode |

### Robot and autonomy interfaces

| Interface | Type | Purpose |
|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | Simulated LiDAR |
| `/joint_states` | `sensor_msgs/msg/JointState` | Robot joint states |
| `/diff_drive_controller/odom` | `nav_msgs/msg/Odometry` | Controller odometry |
| `/diff_drive_controller/cmd_vel` | `geometry_msgs/msg/TwistStamped` | Controller command input |
| `/map` | `nav_msgs/msg/OccupancyGrid` | SLAM or map-server map |
| `/amcl_pose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | AMCL pose estimate |
| `/initialpose` | `geometry_msgs/msg/PoseWithCovarianceStamped` | Initial pose published to AMCL |
| `/navigate_to_pose` | `nav2_msgs/action/NavigateToPose` | Nav2 single-goal action |
| `/tf` | `tf2_msgs/msg/TFMessage` | Dynamic transforms |
| `/tf_static` | `tf2_msgs/msg/TFMessage` | Static transforms |
| `/clock` | `rosgraph_msgs/msg/Clock` | Simulation time |

See [`docs/topic_interface_reference.md`](docs/topic_interface_reference.md) for the full contract.

---

## Transform Ownership

### Mapping

```text
SLAM Toolbox:
  map → odom

diff_drive_controller:
  odom → base_link

robot_state_publisher:
  base_link → robot links and sensors
```

### Localization and Navigation

```text
AMCL:
  map → odom

diff_drive_controller:
  odom → base_link

robot_state_publisher:
  base_link → robot links and sensors
```

Avoid running multiple publishers for the same TF edge.

---

## Testing

Build the workspace and run the complete native release gate:

```bash
./scripts/build.sh
./scripts/test.sh
```

`test.sh` expects an existing built workspace and exits with an error when
`ros2_ws/install/setup.bash` is missing.

The current validated baseline is:

```text
357 tests
0 errors
0 failures
0 skipped
```

The combined build and test gate includes:

1. Python syntax checks
2. JavaScript syntax checks
3. Bash syntax checks
4. ROS 2 package build
5. registered ROS 2 tests
6. ament lint checks
7. GoogleTest
8. simulator launch regression
9. headless dashboard integration
10. public launcher lifecycle validation

### Targeted ROS 2 test execution

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

cd ros2_ws

colcon test \
  --packages-select cpp_robotics_sim_ros \
  --event-handlers console_direct+

colcon test-result --verbose
```

---

## Docker

Build the development and test image:

```bash
docker build \
  --tag cpp-robotics-sim:v0.1.0 \
  .
```

Run the full test gate:

```bash
docker run --rm \
  --name cpp-robotics-sim-v010-test \
  cpp-robotics-sim:v0.1.0 \
  bash -lc './scripts/test.sh'
```

The Docker gate validates the same source tree in a clean Ubuntu 24.04 / ROS 2 Jazzy environment.

GUI simulation is normally run on the host. The container is primarily intended for build, lint, and automated test reproducibility.

---

## Continuous Integration

Workflow:

```text
.github/workflows/ros2_jazzy_ci.yml
```

CI validates:

- source syntax;
- dependency installation;
- ROS 2 package build;
- unit and behavior tests;
- ament linting;
- test-result collection.

GUI-dependent Gazebo scenarios are validated locally because hosted CI environments do not provide the same desktop and graphics stack.

---

## Validation Evidence

Validated release-candidate scenarios include:

- Warehouse startup and shutdown;
- Hospital startup and shutdown;
- manual drive and safe stop;
- mapping and map save;
- map selection;
- AMCL localization;
- Nav2 goal success;
- Nav2 goal cancellation;
- environment switching in both directions;
- stale-process cleanup;
- launcher port release;
- recovery after closing Gazebo externally;
- native full test gate;
- Docker full test gate.

Release evidence should be reproduced against the exact commit used for the GitHub tag.

---

## Troubleshooting

### Dashboard opens but ROS is disconnected

Check:

```bash
ss -ltnp | grep -E ':8080|:9090'
ros2 node list
```

Restart the launcher if rosbridge or the manager nodes are missing.

### Gazebo closes and the dashboard shows an error

An externally closed simulator is treated as an unexpected process exit.

Expected behavior:

- simulation status becomes `error`;
- environment selection unlocks;
- the user can choose another environment;
- the simulation can be restarted without restarting the dashboard.

### Environment selection is locked

Stop the simulation first. Selection is intentionally locked during:

```text
starting
running
stopping
```

### Navigation does not start

Verify:

```bash
ros2 topic info /map
ros2 topic info /scan
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map base_link
ros2 action list | grep navigate_to_pose
```

Navigation requires a valid map, localization, TF, LiDAR, odometry, and active Nav2 servers.

### Generated build state needs to be refreshed

Use the normal dashboard and launcher shutdown paths for runtime processes.

The repository cleanup script removes generated workspace artifacts and Python caches. It does not terminate ROS 2 or Gazebo processes.

```bash
./scripts/clean.sh
```

After cleaning, rebuild the workspace before launching the platform again.
---

## Known Limitations

`v0.1.0` is a validated first public release, not a production deployment platform.

Current limitations:

- RViz is not integrated into the browser dashboard.
- GUI Gazebo scenarios are not executed in hosted CI.
- Custom robots are not yet loadable through the dashboard.
- Custom user maps and worlds require configuration changes.
- Algorithm selection is fixed by the current configuration.
- Parameter tuning is configuration-file based rather than dashboard-driven.
- Dynamic-obstacle benchmarking is not part of the first release.
- Hardware deployment is outside the `v0.1.0` scope.
- PS4 controller support is deferred.
- Performance comparisons are not yet exposed as a complete experiment pipeline.

---

## Roadmap

Planned post-`v0.1.0` work includes:

- custom robot import;
- custom map and world selection;
- dashboard-based parameter tuning;
- selectable planners, controllers, and localization methods;
- RViz integration;
- experiment orchestration;
- automated parameter sweeps;
- plot and report generation;
- spreadsheet-driven test definitions;
- algorithm and configuration comparison;
- rosbag replay regression;
- dynamic-obstacle scenarios;
- sensor and physics noise sweeps;
- simulation-to-hardware workflows;
- improved portfolio and teaching material.

The long-term goal is an instructional and experimentation platform for autonomous mobile robot development rather than a single fixed demo.

---

## Security and Safety Notes

- Map names and filesystem paths are validated before use.
- Environment changes are allowlisted.
- Mutually exclusive modes prevent conflicting autonomy stacks.
- Velocity sources are tracked and deactivated on stop.
- Navigation success and cancellation trigger a safe stop.
- Shutdown attempts normal process-group termination before escalation.
- Generated maps, bags, build products, and logs are not committed by default.

---

## Development Guidelines

Before submitting changes:

```bash
./scripts/test.sh
```

Also verify:

```bash
git diff --check
git status --short
```

Changes to lifecycle, command routing, mapping, localization, navigation, or filesystem handling should include targeted regression tests.

Do not add new runtime behavior without documenting:

- the user workflow;
- ROS 2 interfaces;
- safety behavior;
- failure recovery;
- validation evidence.

---

## Contributing

Issues and focused pull requests are welcome after the first public release.

A useful contribution should include:

- a clear problem statement;
- reproduction steps;
- minimal implementation scope;
- tests;
- documentation updates;
- validation evidence.

For larger features, open an issue before implementation to align on architecture and release scope.

---

## License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE).

---

## Author

**Devansh Mishra**

- GitHub: [Devansh-Mishra-30](https://github.com/Devansh-Mishra-30)
- LinkedIn: [linkedin.com/in/dvm](https://linkedin.com/in/dvm)
- Portfolio: [devanshportfolio.bubbleapps.io/version-test/](https://devanshportfolio.bubbleapps.io/version-test/)

---

## Release Summary

`v0.1.0` establishes a reproducible baseline for:

```text
Environment selection
Managed simulation lifecycle
Browser-based manual control
SLAM mapping
Environment-aware map management
AMCL localization
Nav2 navigation
Goal cancellation
Command-source safety
Native and Docker validation
Clean shutdown and recovery
```

The first release is intended to provide a stable foundation for continued robotics simulation, experimentation, teaching, and autonomous mobile robot development.
