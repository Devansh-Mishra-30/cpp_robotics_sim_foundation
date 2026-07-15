# Day 107 Covariance Analysis

## Purpose

Compare raw wheel odometry, IMU yaw-rate measurements, and
EKF-filtered odometry.

The report records observed measurement variation and the covariance
values published by each source.

### Raw wheel odometry linear velocity

- Samples: 962
- Mean: 0.00000000 m/s
- Standard deviation: 0.00000000 m/s
- Minimum: -0.00000000 m/s
- Maximum: 0.00000000 m/s

### Raw wheel odometry yaw rate

- Samples: 962
- Mean: -0.00000000 rad/s
- Standard deviation: 0.00000000 rad/s
- Minimum: -0.00000000 rad/s
- Maximum: 0.00000000 rad/s

### Raw IMU yaw rate

- Samples: 928
- Mean: 0.00023298 rad/s
- Standard deviation: 0.00198844 rad/s
- Minimum: -0.00577037 rad/s
- Maximum: 0.00700816 rad/s

### Filtered linear velocity

- Samples: 578
- Mean: 0.00000000 m/s
- Standard deviation: 0.00000000 m/s
- Minimum: -0.00000000 m/s
- Maximum: 0.00000000 m/s

### Filtered yaw rate

- Samples: 578
- Mean: 0.00011333 rad/s
- Standard deviation: 0.00136361 rad/s
- Minimum: -0.00409260 rad/s
- Maximum: 0.00687074 rad/s

## Published covariance values

### Raw wheel odometry

- Mean linear-X twist covariance:
  0.0000000000
- Mean yaw-rate twist covariance:
  0.0000000000

### IMU

- Mean yaw-rate covariance:
  0.0000040000

### EKF-filtered odometry

- Mean linear-X twist covariance:
  0.0001462541
- Mean yaw-rate twist covariance:
  0.0000019508

## Initial interpretation

Wheel odometry supplies forward velocity and yaw rate.

The IMU supplies an independent noisy measurement of yaw rate.

The EKF combines both yaw-rate sources. The filtered output should retain
the robot's motion response while reducing sensitivity to individual IMU
noise samples.

A covariance value represents estimated uncertainty, not the measured
value itself. A smaller covariance gives that measurement greater weight
inside the Kalman filter.
