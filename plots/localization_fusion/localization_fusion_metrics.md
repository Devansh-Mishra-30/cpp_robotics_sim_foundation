# Day 108 Fusion Analysis

## Experiment

The comparison uses AMCL as the map-frame localization reference.

The other trajectories are transformed into the map frame using one
fixed initial map-to-odometry alignment. The alignment is captured once
and is not continuously updated.

The compared sources are:

- Raw wheel odometry
- Artificially noisy wheel odometry
- EKF-filtered noisy odometry and IMU yaw rate
- AMCL localization

## Samples

55

## Position error relative to AMCL

| Estimate | RMSE [m] | Maximum error [m] |
|---|---:|---:|
| Raw wheel odometry | 0.284043 | 0.532143 |
| Noisy odometry | 0.284686 | 0.560124 |
| EKF filtered odometry | 0.284960 | 0.553373 |

EKF position-RMSE improvement relative to noisy odometry:
-0.10%

## Yaw error relative to AMCL

| Estimate | RMSE [rad] | RMSE [deg] | Mean absolute error [rad] |
|---|---:|---:|---:|
| Raw wheel odometry | 0.131918 | 7.558 | 0.091946 |
| Noisy odometry | 0.131989 | 7.562 | 0.094329 |
| EKF filtered odometry | 0.133052 | 7.623 | 0.094562 |

EKF yaw-RMSE improvement relative to noisy odometry:
-0.81%

## Interpretation

The noisy odometry contains independent position, heading, linear
velocity and angular velocity disturbances.

The EKF fuses the noisy forward velocity and yaw rate with the simulated
IMU yaw-rate measurement. It therefore estimates a smoother motion state
than the noisy source alone.

Raw wheel odometry may perform unusually well in this simulation because
its motion is derived directly from the simulated wheel joints and does
not contain the same wheel slip, calibration error, encoder quantization
and mechanical uncertainty expected on physical hardware.

AMCL provides scan-corrected map-frame localization, while wheel
odometry and the EKF remain locally continuous dead-reckoning estimates.
