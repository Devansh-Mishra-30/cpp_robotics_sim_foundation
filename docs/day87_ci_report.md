# Day 87 - GitHub Actions CI Report

## Purpose

Day 87 added continuous integration to the robotics simulation project using GitHub Actions.

The goal was to make the project automatically build and test on GitHub instead of only relying on local validation.

## Workflow File

```txt
.github/workflows/ros2_jazzy_ci.yml
CI Environment

The workflow runs on:

ubuntu-24.04
ROS 2 Jazzy
colcon
ament_cmake
GoogleTest
CI Trigger

The workflow runs on:

push to main
pull request to main
manual workflow dispatch
CI Steps

The workflow performs the following steps:

Checks out the repository.
Installs ROS 2 Jazzy dependencies.
Initializes and updates rosdep.
Installs package dependencies.
Builds the ROS 2 workspace.
Runs the GoogleTest test suite.
Uploads colcon test logs as an artifact.
Successful GitHub Actions Result

The GitHub Actions workflow completed successfully.

Workflow: ROS 2 Jazzy CI
Status: Success
Total duration: 3m 55s
Artifacts: 1
Local Test Result

The local Day 86 GoogleTest result before CI was:

Summary: 17 tests, 0 errors, 0 failures, 0 skipped
Engineering Significance

Before Day 87, the project could be built and tested locally.

After Day 87, the project is checked automatically on GitHub. This means every push can verify that the ROS 2 workspace still builds and that the GoogleTest unit tests still pass.

This is an important step toward professional software quality, reproducibility, and portfolio credibility.

Interview Explanation

I added a GitHub Actions CI workflow for my ROS 2 Jazzy robotics simulation workspace. The workflow runs on Ubuntu 24.04, installs ROS 2 Jazzy dependencies, builds the colcon workspace, runs the GoogleTest unit tests, and uploads the test logs. This gives the project automated build and test verification on every push or pull request.