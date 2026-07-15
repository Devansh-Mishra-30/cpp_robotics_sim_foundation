# Localization Validation Report

## 1. Executive summary

This report summarizes the localization phase of the ROS 2 differential
drive simulation project.

The localization stack was developed and validated using:

- ROS 2 Jazzy
- Gazebo Sim
- ros2_control
- SLAM Toolbox
- Nav2 Map Server
- AMCL
- robot_localization EKF
- simulated wheel odometry
- simulated lidar
- simulated IMU
- artificial odometry noise
- quantitative trajectory and covariance analysis

The completed system supports:

- map generation
- map persistence
- known-map localization
- wheel-odometry tracking
- IMU measurement publishing
- EKF-based sensor fusion
- covariance inspection
- trajectory comparison
- localization failure injection
- manual localization recovery

The localization pipeline operated successfully end to end.

The final experiments also demonstrated an important engineering result:
sensor fusion does not automatically guarantee lower global position
error. AMCL and EKF solve different localization problems and should be
used together rather than treated as interchangeable estimators.

---

## 2. System architecture

The localization architecture consists of two complementary estimation
layers.

### Local estimation

Wheel odometry and IMU measurements are processed by an Extended Kalman
Filter.

The local estimation chain is:

```text
wheel encoders / ros2_control odometry
                    +
               simulated IMU
                    |
                    v
          robot_localization EKF
                    |
                    v
           /odometry/filtered

The EKF provides a locally continuous estimate of robot motion.

Global localization

AMCL uses the saved occupancy-grid map and lidar scans to estimate the
robot pose in the map frame.

The global localization chain is:

saved occupancy-grid map
          +
       lidar scans
          +
 odometry motion prediction
          |
          v
         AMCL
          |
          v
      map -> odom

The complete transform relationship is:

map -> odom -> base_link

AMCL provides global map correction.

Odometry and EKF provide smooth local motion estimation.

3. SLAM and map generation

SLAM Toolbox was used to generate an occupancy-grid map of the simulated
environment.

The robot was driven through the environment while lidar measurements
and odometry were processed by SLAM Toolbox.

The completed map was saved for later localization.

The mapping phase validated:

lidar integration
odometry integration
map-frame creation
occupancy-grid generation
map persistence
map reload compatibility

The saved map was subsequently loaded through the Nav2 map server.

4. AMCL localization

AMCL was launched using the saved occupancy-grid map.

The localization stack successfully provided:

/amcl_pose
map -> odom
particle-based pose estimation
covariance estimates
scan-based pose corrections

At the normal simulation start, AMCL and wheel odometry agreed near:

X: 0 m
Y: 0 m
Yaw: 0 rad

This confirmed that the initial map, odometry and robot frames were
aligned correctly.

5. AMCL and wheel-odometry comparison

A fixed initial transform was used to align wheel odometry with AMCL in
the map frame.

The alignment was captured once and then frozen.

This avoided using AMCL's continuously updated map -> odom correction
to artificially force the wheel-odometry trajectory to match AMCL.

The comparison demonstrated:

wheel odometry remained locally continuous
AMCL applied scan-based map corrections
odometry error increased during longer motion
heading and position differences became visible after turns
AMCL and odometry solved different estimation problems

The comparison plots and metrics were generated during the localization comparison experiment.

6. Simulated IMU integration

A simulated IMU sensor was added to the robot model.

The IMU published:

angular velocity
linear acceleration
measurement covariance
sensor frame information

The stationary IMU yaw-rate measurements showed measurable Gaussian-like
noise.

Observed stationary yaw-rate behavior included approximately:

mean: 0.000233 rad/s
standard deviation: 0.001988 rad/s
minimum: -0.005770 rad/s
maximum: 0.007008 rad/s

The sensor also responded correctly during commanded robot rotation.

7. EKF sensor fusion

The robot_localization EKF was configured to fuse wheel-odometry and
IMU measurements.

The baseline EKF configuration fused:

wheel forward velocity
wheel yaw rate
IMU yaw rate

The EKF published:

/odometry/filtered

with:

frame_id: odom
child_frame_id: base_link

The EKF was configured with:

publish_tf: false

This prevented duplicate publication of odom -> base_link, which
remained owned by the differential-drive controller.

The EKF diagnostic system reported:

The robot_localization state estimation node appears to be functioning
properly.

The observed filtered output frequency was approximately:

28.5 to 28.8 Hz

for a configured target of 30 Hz.

This was within the accepted diagnostic range.

8. Covariance tuning

Explicit process-noise and initial-estimate covariance matrices were
added to the EKF configuration.

The EKF state order was:

x, y, z,
roll, pitch, yaw,
vx, vy, vz,
vroll, vpitch, vyaw,
ax, ay, az

The covariance analysis compared:

raw wheel-odometry velocity
raw wheel-odometry yaw rate
IMU yaw rate
EKF-filtered velocity
EKF-filtered yaw rate

During the stationary test:

wheel odometry showed effectively zero simulated noise
IMU yaw-rate standard deviation was approximately 0.001988 rad/s
EKF yaw-rate standard deviation was approximately 0.001364 rad/s

This represented approximately a 31 percent reduction in stationary
yaw-rate variation.

During commanded motion, the EKF preserved the expected response:

commanded forward velocity: 0.08 m/s
filtered maximum forward velocity: approximately 0.0819 m/s
commanded yaw rate: 0.20 rad/s
filtered maximum yaw rate: approximately 0.2035 rad/s

This showed that the filter reduced short-term IMU noise without
significantly suppressing valid motion.

9. Fusion comparison

The localization fusion analysis compared:

raw wheel odometry
artificially noisy odometry
EKF-filtered odometry
AMCL localization

The artificially noisy odometry source added independent noise to:

X position
Y position
yaw
linear velocity
angular velocity

The final fusion-analysis EKF configuration fused:

noisy X position
noisy Y position
noisy yaw
noisy forward velocity
IMU yaw rate

All trajectories were transformed into the map frame using one frozen
initial alignment.

The final comparison produced:

Position RMSE relative to AMCL
Raw wheel odometry: 0.284043 m
Noisy odometry: 0.284686 m
EKF-filtered odometry: 0.284960 m
Yaw RMSE relative to AMCL
Raw wheel odometry: 0.131918 rad
Noisy odometry: 0.131989 rad
EKF-filtered odometry: 0.133052 rad

The EKF result was nearly identical to the noisy-odometry result:

position difference: approximately 0.10 percent worse
yaw difference: approximately 0.81 percent worse

These differences were too small to claim a meaningful improvement or
degradation.

The EKF remained smoother and locally continuous, but AMCL-relative RMSE
did not improve materially.

This result occurred because the artificial noisy odometry added
bounded independent noise to an otherwise nearly ideal simulated pose.
It did not reproduce persistent wheel slip, calibration bias, encoder
scale error or accumulating hardware drift.

10. Localization robustness and recovery

AMCL robustness was tested by deliberately publishing an incorrect
initial pose.

The incorrect hypothesis was approximately:

X: 2.5 m
Y: 1.5 m
Yaw: 180 degrees

AMCL accepted the incorrect hypothesis and initially reported:

X: 2.492 m
Y: 1.514 m
Yaw: 3.124 rad

The robot was then rotated while remaining near the wheel-odometry
origin.

Wheel odometry reported approximately:

X: 0 m
Y: 0 m
Yaw: 1.326 rad

AMCL remained near the wrong map location:

X: 2.206 m
Y: 1.497 m

This demonstrated that AMCL did not automatically recover during the
short rotation test.

A corrected pose was then published through /initialpose.

AMCL recovered to approximately:

X: -0.0121 m
Y: -0.0043 m
Yaw: 1.326 rad

The recovered position error was approximately:

0.0128 m

The recovered yaw error was negligible.

After recovery, the robot moved forward and AMCL continued tracking the
motion correctly.

The final AMCL pose was approximately:

X: 0.0692 m
Y: 0.2939 m
Yaw: approximately 1.30 rad

This confirmed stable localization after recovery.

11. Validation summary
Validation item	Result
SLAM map generation	Pass
Map save and reload	Pass
AMCL startup localization	Pass
Lidar frame integration	Pass
Wheel odometry publication	Pass
IMU publication	Pass
EKF startup	Pass
EKF diagnostics	Pass
EKF output rate	Pass
Covariance matrix validation	Pass
Stationary noise analysis	Pass
Motion-response analysis	Pass
Raw/noisy/EKF/AMCL comparison	Pass
Incorrect initial-pose injection	Pass
AMCL recovery through /initialpose	Pass
Post-recovery localization	Pass
12. Key engineering conclusions
AMCL and EKF are complementary

AMCL and EKF should not be treated as competing localization systems.

The EKF produces a high-rate, locally continuous estimate using odometry
and IMU measurements.

AMCL provides scan-corrected global localization relative to a known
map.

The recommended architecture is:

wheel odometry + IMU
          |
          v
         EKF
          |
          v
    odom -> base_link

lidar + map + motion prediction
          |
          v
         AMCL
          |
          v
       map -> odom
Sensor fusion does not guarantee better global accuracy

An EKF only improves the estimate when:

the sensor models are appropriate
measurement covariance is realistic
process noise is realistic
fused measurements contain complementary information
sensor errors are not strongly correlated
the test metric matches the filter objective

The fusion experiment showed that smoothing and continuity can improve
without producing lower AMCL-relative RMSE.

Simulation has important limitations

The raw wheel odometry in this simulation was unusually accurate.

A physical robot would introduce:

wheel slip
encoder quantization
wheel-radius mismatch
track-width calibration error
motor deadband
mechanical backlash
timing jitter
transport delay
sensor bias
non-Gaussian disturbances

Future validation should model these effects.

13. Known limitations

Current limitations include:

no persistent encoder bias model
no explicit wheel-slip model
no time-varying IMU bias
no sensor dropout testing
no delayed-message testing
no out-of-order message testing
no kidnapped-robot automatic recovery
no automated covariance optimization
no hardware validation
no ground-truth simulator pose comparison in the final fusion report

These limitations are appropriate targets for future development.

14. Future work

Recommended next improvements include:

ground-truth pose recorder
wheel-slip injection
encoder scale-factor error
persistent IMU bias
sensor dropout scenarios
delayed and stale message tests
automated localization regression tests
global-local EKF architecture
Nav2 integration using filtered odometry
automatic relocalization workflows
hardware comparison
repeatable benchmark scenarios
15. Interview-level explanation

The localization stack uses wheel odometry and IMU measurements for local
motion estimation, while AMCL performs global localization against a
known lidar map.

Wheel odometry is smooth and locally continuous but accumulates drift.

The IMU provides independent angular-rate information but contains
measurement noise and bias.

The EKF combines these measurements using their covariance estimates to
produce a filtered local state.

AMCL compares live lidar scans against the occupancy-grid map and updates
the map -> odom transform.

This allows the robot to maintain:

a continuous local odometry frame
a globally corrected map frame
a valid map -> odom -> base_link transform chain

The validation phase demonstrated correct startup, sensor fusion,
covariance behavior, global correction, localization failure and manual
recovery.

The main lesson is that filtering, smoothing, local continuity and global
accuracy are different objectives. A robust localization architecture
assigns each estimator a clearly defined role.
