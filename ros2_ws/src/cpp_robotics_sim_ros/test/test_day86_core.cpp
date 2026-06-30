#include <cmath>
#include <stdexcept>

#include "gtest/gtest.h"
#include "cpp_robotics_sim_ros/day86_testable_core.hpp"

/*
  Day 86 - GoogleTest Unit Tests

  What this file tests:
  ---------------------
  1. clamp()
  2. wrapToPi()
  3. integratePose()

  Why these tests matter:
  -----------------------
  In robotics simulation, many bugs come from small math errors:
    - wrong angle wrapping
    - wrong timestep handling
    - wrong velocity integration
    - unsafe command limits
    - sign mistakes in x/y motion

  These tests give us automated confidence that the core math behaves correctly.
*/

namespace
{

    constexpr double kTolerance = 1e-9;
    constexpr double kPi = 3.14159265358979323846;

}  // namespace

using cpp_robotics_sim_ros::Pose2D;
using cpp_robotics_sim_ros::clamp;
using cpp_robotics_sim_ros::integratePose;
using cpp_robotics_sim_ros::wrapToPi;

// -----------------------------------------------------------------------------
// clamp() tests
// -----------------------------------------------------------------------------

TEST(Day86ClampTest, KeepsValueInsideRange)
{
    EXPECT_DOUBLE_EQ(clamp(0.5, -1.0, 1.0), 0.5);
}

TEST(Day86ClampTest, LimitsValueAboveMaximum)
{
    EXPECT_DOUBLE_EQ(clamp(2.0, -1.0, 1.0), 1.0);
}

TEST(Day86ClampTest, LimitsValueBelowMinimum)
{
    EXPECT_DOUBLE_EQ(clamp(-2.0, -1.0, 1.0), -1.0);
}

TEST(Day86ClampTest, WorksWithNonSymmetricRange)
{
    EXPECT_DOUBLE_EQ(clamp(15.0, 0.0, 10.0), 10.0);
    EXPECT_DOUBLE_EQ(clamp(-5.0, 0.0, 10.0), 0.0);
    EXPECT_DOUBLE_EQ(clamp(7.0, 0.0, 10.0), 7.0);
}

TEST(Day86ClampTest, ThrowsWhenMinGreaterThanMax)
{
    EXPECT_THROW(clamp(0.0, 2.0, 1.0), std::invalid_argument);
}

// -----------------------------------------------------------------------------
// wrapToPi() tests
// -----------------------------------------------------------------------------

TEST(Day86WrapToPiTest, ZeroStaysZero)
{
    EXPECT_NEAR(wrapToPi(0.0), 0.0, kTolerance);
}

TEST(Day86WrapToPiTest, TwoPiWrapsToZero)
{
    EXPECT_NEAR(wrapToPi(2.0 * kPi), 0.0, kTolerance);
    EXPECT_NEAR(wrapToPi(-2.0 * kPi), 0.0, kTolerance);
}

TEST(Day86WrapToPiTest, PiMapsToNegativePiByConvention)
{
    EXPECT_NEAR(wrapToPi(kPi), -kPi, kTolerance);
}

TEST(Day86WrapToPiTest, ThreePiMapsToNegativePi)
{
    EXPECT_NEAR(wrapToPi(3.0 * kPi), -kPi, kTolerance);
}

TEST(Day86WrapToPiTest, OutputAlwaysWithinRange)
{
    const double test_angles[] = {
      -10.0 * kPi,
      -3.5 * kPi,
      -2.0 * kPi,
      -1.0 * kPi,
      -0.5 * kPi,
      0.0,
      0.5 * kPi,
      1.0 * kPi,
      2.0 * kPi,
      3.5 * kPi,
      10.0 * kPi
    };

    for (double angle : test_angles) {
        const double wrapped = wrapToPi(angle);

        EXPECT_GE(wrapped, -kPi);
        EXPECT_LT(wrapped, kPi);
    }
}

// -----------------------------------------------------------------------------
// integratePose() tests
// -----------------------------------------------------------------------------

TEST(Day86PoseIntegrationTest, MovesForwardAlongXWhenHeadingIsZero)
{
    Pose2D pose;
    pose.x = 0.0;
    pose.y = 0.0;
    pose.theta = 0.0;

    const Pose2D next_pose = integratePose(pose, 1.0, 0.0, 1.0);

    EXPECT_NEAR(next_pose.x, 1.0, kTolerance);
    EXPECT_NEAR(next_pose.y, 0.0, kTolerance);
    EXPECT_NEAR(next_pose.theta, 0.0, kTolerance);
}

TEST(Day86PoseIntegrationTest, MovesForwardAlongYWhenHeadingIsPiOverTwo)
{
    Pose2D pose;
    pose.x = 0.0;
    pose.y = 0.0;
    pose.theta = kPi / 2.0;

    const Pose2D next_pose = integratePose(pose, 1.0, 0.0, 1.0);

    EXPECT_NEAR(next_pose.x, 0.0, 1e-8);
    EXPECT_NEAR(next_pose.y, 1.0, 1e-8);
    EXPECT_NEAR(next_pose.theta, kPi / 2.0, kTolerance);
}

TEST(Day86PoseIntegrationTest, RotationOnlyChangesTheta)
{
    Pose2D pose;
    pose.x = 2.0;
    pose.y = 3.0;
    pose.theta = 0.0;

    const Pose2D next_pose = integratePose(pose, 0.0, 1.0, 0.5);

    EXPECT_NEAR(next_pose.x, 2.0, kTolerance);
    EXPECT_NEAR(next_pose.y, 3.0, kTolerance);
    EXPECT_NEAR(next_pose.theta, 0.5, kTolerance);
}

TEST(Day86PoseIntegrationTest, ThetaIsWrappedAfterUpdate)
{
    Pose2D pose;
    pose.x = 0.0;
    pose.y = 0.0;
    pose.theta = kPi - 0.1;

    const Pose2D next_pose = integratePose(pose, 0.0, 1.0, 0.2);

    EXPECT_GE(next_pose.theta, -kPi);
    EXPECT_LT(next_pose.theta, kPi);
    EXPECT_NEAR(next_pose.theta, -kPi + 0.1, 1e-8);
}

TEST(Day86PoseIntegrationTest, RepeatedForwardStepsAreDeterministic)
{
    Pose2D pose;
    pose.x = 0.0;
    pose.y = 0.0;
    pose.theta = 0.0;

    const double linear_velocity = 1.0;
    const double angular_velocity = 0.0;
    const double dt = 0.01;
    const int steps = 100;

    for (int i = 0; i < steps; ++i) {
        pose = integratePose(pose, linear_velocity, angular_velocity, dt);
    }

    EXPECT_NEAR(pose.x, 1.0, 1e-8);
    EXPECT_NEAR(pose.y, 0.0, 1e-8);
    EXPECT_NEAR(pose.theta, 0.0, 1e-8);
}

TEST(Day86PoseIntegrationTest, NegativeDtThrowsException)
{
    Pose2D pose;
    EXPECT_THROW(integratePose(pose, 1.0, 0.0, -0.01), std::invalid_argument);
}