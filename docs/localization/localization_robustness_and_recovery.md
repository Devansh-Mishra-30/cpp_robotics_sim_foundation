# Localization Robustness and Recovery

## Objective

Evaluate AMCL behavior after deliberately assigning an incorrect initial
pose and verify recovery through manual reinitialization.

## Initial state

AMCL and wheel odometry both started near:

- X: 0 m
- Y: 0 m
- Yaw: 0 rad

## Incorrect localization hypothesis

A deliberately incorrect initial pose was published:

- X: 2.5 m
- Y: 1.5 m
- Yaw: approximately 180 degrees

AMCL accepted the incorrect hypothesis and reported approximately:

- X: 2.492 m
- Y: 1.514 m
- Yaw: 3.124 rad

After rotating the robot, AMCL remained near the incorrect map location,
while wheel odometry correctly showed that the robot remained near the
local origin.

After the rotation, wheel odometry reported approximately:

- X: 0 m
- Y: 0 m
- Yaw: 1.326 rad
- Yaw: 75.974 degrees

AMCL was still localized near the incorrect map position:

- X: 2.206 m
- Y: 1.497 m

This confirmed that AMCL did not automatically recover during the short
rotation test.

## Recovery

A corrected initial pose was published using the wheel-odometry position
and heading.

AMCL recovered to approximately:

- X: -0.0121 m
- Y: -0.0043 m
- Yaw: 1.326 rad

The recovered position error was approximately 0.0128 m, and the yaw
error was negligible.

The `map -> base_link` transform also returned to approximately:

- X: -0.012 m
- Y: -0.004 m
- Yaw: 1.326 rad

## Post-recovery motion

After recovery, the robot was commanded to move forward while facing
approximately 1.326 rad.

The final AMCL estimate was approximately:

- X: 0.0692 m
- Y: 0.2939 m
- Yaw: approximately 1.30 rad

The displacement was primarily in the positive Y direction, which was
consistent with the robot's recovered heading. This confirmed that AMCL
remained stable and continued tracking the robot after recovery.

## Conclusion

AMCL did not automatically recover from the deliberately incorrect pose
during the short rotation test. Manual reinitialization through
`/initialpose` restored localization successfully.

This experiment demonstrates:

- sensitivity to a poor initial pose
- separation between local wheel odometry and global map localization
- recovery using a corrected initial hypothesis
- restoration of the map-to-robot transform chain
- stable localization after recovery and subsequent motion
