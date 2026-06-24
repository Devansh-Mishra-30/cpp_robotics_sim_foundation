# Standalone C++ Robotics Simulator

This folder contains the pure C++ simulation layer of the project. It does not depend on ROS 2.

The standalone simulator demonstrates:

* C++ project structure
* differential-drive mobile robot kinematics
* manipulator joint-state updates
* fixed-timestep simulation loops
* trajectory logging and metrics
* scenario validation
* target-tracking demo
* clean header/source separation

---

## Folder Structure

```txt
standalone_cpp/
├── include/
│   ├── differential_drive/
│   └── manipulator/
├── src/
│   ├── differential_drive/
│   ├── manipulator/
│   └── main.cpp
├── CMakeLists.txt
├── build.ps1
└── README.md
```

---

## Modules

### Differential-Drive Module

Location:

```txt
include/differential_drive/
src/differential_drive/
```

This module models a differential-drive mobile robot.

Main behavior:

```txt
wheel speeds -> linear/angular velocity -> pose update -> trajectory -> metrics
```

It includes:

* wheel-speed conversion
* pose integration
* trajectory storage
* validation scenarios
* target tracking
* trajectory metrics

---

### Manipulator Module

Location:

```txt
include/manipulator/
src/manipulator/
```

This module models basic joint-space motion for a manipulator.

Main behavior:

```txt
q_next = q_current + q_dot * dt
q_next = clamp(q_next, min_position, max_position)
```

It includes:

* joint state representation
* joint velocity integration
* joint limit clamping
* invalid limit checks

---

## Build on Linux / WSL

From this folder:

```bash
rm -rf build
mkdir build
cd build
cmake ..
cmake --build .
./robotics_sim
```

---

## Build on Windows PowerShell

From this folder:

```powershell
.\build.ps1
```

The PowerShell build script configures the project with Visual Studio 2022, builds the Debug executable, and runs:

```txt
build/Debug/robotics_sim.exe
```

---

## What This Layer Proves

The standalone C++ layer proves the core simulation logic before ROS 2 integration.

It shows that the project can:

* represent robot state cleanly
* update mobile robot pose using kinematics
* update manipulator joint state safely
* validate deterministic scenarios
* compute trajectory metrics
* keep simulation logic modular and testable

---

## Relationship to ROS 2 Layer

The ROS 2 simulator in `../ros2_ws/` builds on the same simulation concepts, but exposes them through ROS 2 topics, parameters, launch files, odometry, TF, YAML configuration, and QoS profiles.

The standalone layer focuses on the C++ simulation foundation.

The ROS 2 layer focuses on robotics middleware integration.
