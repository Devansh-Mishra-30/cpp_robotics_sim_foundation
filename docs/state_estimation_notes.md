# Day 82 — State Estimation Notes

## Goal

Understand state estimation for robotics simulation and interview readiness.

Main concepts:

* odometry
* IMU
* sensor fusion
* covariance
* EKF
* localization drift
* noisy measurements

This is a concept day. The project does not implement a full EKF yet.

---

## 1. What Is State Estimation?

State estimation means estimating the robot's current state using imperfect sensor data.

For a mobile robot, the state usually includes:

```txt
x position
y position
yaw angle
linear velocity
angular velocity
```

A simple 2D robot state can be written as:

```txt
state = [x, y, yaw, linear_velocity, yaw_rate]
```

Interview answer:

```txt
State estimation is the process of estimating where the robot is and how it is moving using noisy sensor measurements.
```

---

## 2. Why State Estimation Is Needed

Robots do not know their perfect position automatically.

Sensors are noisy.

Wheel odometry can drift.
IMUs can have bias.
Lidar can have measurement noise.
Cameras can fail in low light or low texture.
Simulation can be too perfect unless noise is added.

So the robot needs a way to estimate its best current state from imperfect data.

Interview answer:

```txt
State estimation is needed because real robot sensors are noisy, incomplete, and uncertain.
```

---

## 3. Odometry

Odometry estimates robot motion over time.

For a differential-drive robot, wheel odometry comes from wheel rotation.

The controller or simulator estimates how far each wheel moved, then computes the robot's change in position.

Typical odometry output:

```txt
x
y
yaw
linear velocity
angular velocity
```

In this project, Gazebo controller odometry comes from:

```txt
/diff_drive_controller/odom
```

Interview answer:

```txt
Odometry is smooth and useful for short-term motion, but it drifts over time because small errors accumulate.
```

---

## 4. Why Odometry Drifts

Odometry is usually integrated over time.

That means the current pose depends on the previous pose.

Small errors keep accumulating.

Common causes of odometry drift:

* wheel slip
* inaccurate wheel radius
* inaccurate wheel separation
* encoder noise
* uneven ground
* simulation/model mismatch
* timing error

Interview answer:

```txt
Odometry drifts because small motion errors are integrated over time.
```

---

## 5. IMU

An IMU means Inertial Measurement Unit.

It usually measures:

```txt
linear acceleration
angular velocity
orientation estimate
```

For a ground robot, the most useful IMU signal is often:

```txt
angular velocity around z axis
```

That is the yaw rate.

Interview answer:

```txt
An IMU helps estimate angular motion, especially yaw rate, but it also has noise and bias.
```

---

## 6. Sensor Fusion

Sensor fusion means combining multiple sensor sources to get a better estimate.

Example:

```txt
wheel odometry + IMU -> fused odometry
```

Wheel odometry may be good for short-term translation.

IMU may be good for short-term angular velocity.

Together, they can produce a better estimate than either one alone.

Interview answer:

```txt
Sensor fusion combines multiple imperfect measurements into a better estimate of the robot state.
```

---

## 7. EKF

EKF means Extended Kalman Filter.

It is used when the robot motion model is nonlinear.

A mobile robot is nonlinear because x and y motion depend on yaw:

```txt
x_next = x + v * cos(yaw) * dt
y_next = y + v * sin(yaw) * dt
yaw_next = yaw + yaw_rate * dt
```

The EKF has two main steps:

```txt
prediction
correction
```

Interview answer:

```txt
An EKF estimates the robot state by predicting motion using a model and correcting that prediction using sensor measurements.
```

---

## 8. Prediction Step

The prediction step uses the robot motion model.

Example:

```txt
previous state + velocity command -> predicted next state
```

For a differential-drive robot:

```txt
linear velocity + angular velocity -> predicted x, y, yaw
```

The prediction step increases uncertainty because the motion model is not perfect.

Interview answer:

```txt
The prediction step estimates where the robot should be after applying the motion model.
```

---

## 9. Correction Step

The correction step uses sensor measurements.

Example:

```txt
predicted state + odometry measurement + IMU measurement -> corrected state
```

If a sensor is trusted, the correction pulls the estimate closer to that sensor.

If a sensor is noisy, the correction has less influence.

Interview answer:

```txt
The correction step updates the predicted state using sensor measurements.
```

---

## 10. Covariance

Covariance represents uncertainty.

Small covariance means:

```txt
I trust this measurement more.
```

Large covariance means:

```txt
I trust this measurement less.
```

In ROS 2 odometry messages, covariance appears in:

```txt
pose.covariance
twist.covariance
```

Each covariance array has 36 values because it represents a 6x6 matrix.

The 6 variables are usually:

```txt
x
y
z
roll
pitch
yaw
```

For a 2D ground robot, the important ones are:

```txt
x
y
yaw
linear velocity x
angular velocity z
```

Interview answer:

```txt
Covariance tells the filter how uncertain a pose or velocity measurement is.
```

---

## 11. Noise vs Covariance

Noise is the actual random error in a signal.

Covariance is the reported uncertainty of that signal.

Example:

```txt
x_noisy = x_actual + random_noise
```

If the noise standard deviation is:

```txt
0.02 m
```

Then the variance is:

```txt
0.02^2 = 0.0004
```

That value can be used in the covariance matrix.

Interview answer:

```txt
Noise is the actual error added to the signal, while covariance describes how uncertain that signal is.
```

---

## 12. Why Add Noise in Simulation?

Perfect simulation is not realistic.

A robot in simulation may behave better than a real robot because there is no sensor noise, no slip, and no model mismatch.

Adding noise helps test:

* controller robustness
* localization readiness
* EKF readiness
* trajectory validation
* Sim2Real behavior
* sensor uncertainty handling

Interview answer:

```txt
Noise makes simulation more realistic and helps test whether the robot system is robust to uncertainty.
```

---

## 13. Relationship to This Project

This project already has actual Gazebo odometry:

```txt
/diff_drive_controller/odom
```

Day 83 will create a noisy version:

```txt
/diff_drive_controller/odom -> noisy_odom_node.py -> /odom_noisy
```

The noisy odometry node will add controlled Gaussian noise to:

```txt
x
y
yaw
linear velocity
angular velocity
```

Important:

```txt
/odom_noisy does not move the robot.
It is only a noisy measurement stream for validation and future localization work.
```

---

## 14. Custom Simulator vs Gazebo State Estimation

This project has two stacks.

### Custom kinematic simulator stack

```txt
/cmd_vel
    -> sim_node
    -> /robot_pose
    -> /odom
    -> /tf
    -> /diagnostics
```

This stack is useful for learning custom motion integration and odometry publishing.

### Gazebo ros2_control stack

```txt
/diff_drive_controller/cmd_vel
    -> diff_drive_controller
    -> ros2_control
    -> gz_ros2_control
    -> Gazebo wheel joints
    -> /diff_drive_controller/odom
    -> /tf
    -> /joint_states
```

Day 83 uses the Gazebo odometry topic:

```txt
/diff_drive_controller/odom
```

Then it publishes:

```txt
/odom_noisy
```

Interview answer:

```txt
The noisy odometry node does not control Gazebo. It subscribes to Gazebo odometry, adds measurement noise, and republishes a noisy odometry stream.
```

---

## 15. Interview Answer: What Is an EKF?

An EKF is a state estimator used when the robot model is nonlinear.

It predicts the robot's next state using a motion model, then corrects that prediction using sensor measurements.

The filter uses covariance to decide how much it should trust each prediction or measurement.

Strong answer:

```txt
An EKF combines a motion model and noisy sensor measurements to estimate the robot's best current state. It has a prediction step and a correction step, and covariance controls how much each source is trusted.
```

---

## 16. Interview Answer: Why Does Odometry Drift?

Odometry drifts because it integrates motion over time.

Small wheel, encoder, timing, or slip errors accumulate.

Strong answer:

```txt
Odometry drift happens because every pose estimate depends on the previous pose estimate, so small errors accumulate over time.
```

---

## 17. Interview Answer: What Does Covariance Mean?

Covariance describes uncertainty in a measurement.

Low covariance means the measurement is trusted more.

High covariance means the measurement is trusted less.

Strong answer:

```txt
Covariance tells localization and sensor-fusion algorithms how reliable a pose or velocity measurement is.
```

---

## 18. Interview Answer: Why Add Noise to Odometry?

Adding noise makes simulation more realistic.

It helps test whether the robot system can handle imperfect measurements.

Strong answer:

```txt
Adding noise to odometry helps simulate real sensor uncertainty and prepares the system for EKF, localization, validation, and Sim2Real testing.
```

---

## 19. Day 82 Completion Criteria

Day 82 is complete when I can explain:

* what state estimation means
* why odometry drifts
* what an IMU contributes
* what sensor fusion means
* what an EKF does
* prediction vs correction
* what covariance means
* noise vs covariance
* why `/odom_noisy` is useful
* why `/odom_noisy` does not move Gazebo
