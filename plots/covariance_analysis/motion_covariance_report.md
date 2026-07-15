# Day 107 Covariance Analysis

## Purpose

Compare raw wheel odometry, IMU yaw-rate measurements, and
EKF-filtered odometry.

The report records observed measurement variation and the covariance
values published by each source.

### Raw wheel odometry linear velocity

- Samples: 1654
- Mean: 0.00876802 m/s
- Standard deviation: 0.02489048 m/s
- Minimum: -0.00000000 m/s
- Maximum: 0.08232323 m/s

### Raw wheel odometry yaw rate

- Samples: 1654
- Mean: 0.01733383 rad/s
- Standard deviation: 0.05600795 rad/s
- Minimum: -0.00000000 rad/s
- Maximum: 0.20343434 rad/s

### Raw IMU yaw rate

- Samples: 1627
- Mean: 0.01775982 rad/s
- Standard deviation: 0.05666855 rad/s
- Minimum: -0.00658747 rad/s
- Maximum: 0.20534417 rad/s

### Filtered linear velocity

- Samples: 998
- Mean: 0.00869904 m/s
- Standard deviation: 0.02485791 m/s
- Minimum: -0.00045709 m/s
- Maximum: 0.08193939 m/s

### Filtered yaw rate

- Samples: 998
- Mean: 0.01742840 rad/s
- Standard deviation: 0.05606577 rad/s
- Minimum: -0.00645830 rad/s
- Maximum: 0.20352113 rad/s

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
  0.0001456902
- Mean yaw-rate twist covariance:
  0.0000019486

## Initial interpretation

Wheel odometry supplies forward velocity and yaw rate.

The IMU supplies an independent noisy measurement of yaw rate.

The EKF combines both yaw-rate sources. The filtered output should retain
the robot's motion response while reducing sensitivity to individual IMU
noise samples.

A covariance value represents estimated uncertainty, not the measured
value itself. A smaller covariance gives that measurement greater weight
inside the Kalman filter.
