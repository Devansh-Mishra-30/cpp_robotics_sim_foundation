# Day 104 Localization Comparison Results

## Samples

8

## Position Error

- Mean position error: 0.0307 m
- Maximum position error: 0.0514 m
- Position RMSE: 0.0354 m

## Heading Error

- Mean absolute yaw error: 0.0150 rad
- Maximum absolute yaw error: 0.0269 rad
- Yaw RMSE: 0.0175 rad
- Yaw RMSE: 1.00 degrees

## Interpretation

Wheel odometry and AMCL were aligned at the first synchronized sample.

The fixed initial alignment was preserved throughout the experiment.
This prevents the continuously updated AMCL map-to-odom correction from
artificially forcing the two trajectories to overlap.

The measured error increased as the robot rotated and translated. This
demonstrates the difference between dead-reckoned wheel odometry and
scan-corrected map-frame localization.
