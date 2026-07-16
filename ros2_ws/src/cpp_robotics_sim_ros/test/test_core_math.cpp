// Copyright 2026 Devansh Mishra
//
// Use of this source code is governed by an MIT-style
// license that can be found in the LICENSE file or at
// https://opensource.org/licenses/MIT.

#include <limits>
#include <stdexcept>

#include "cpp_robotics_sim_ros/core_math.hpp"
#include "gtest/gtest.h"

namespace
{

constexpr double kTolerance = 1e-9;
constexpr double kPi = 3.14159265358979323846;

}  // namespace

using cpp_robotics_sim_ros::Pose2D;
using cpp_robotics_sim_ros::clamp;
using cpp_robotics_sim_ros::integratePose;
using cpp_robotics_sim_ros::isFinitePose;
using cpp_robotics_sim_ros::wrapToPi;

TEST(ClampTest, KeepsValueInsideRange)
{
  EXPECT_DOUBLE_EQ(clamp(0.5, -1.0, 1.0), 0.5);
}

TEST(ClampTest, LimitsValueAboveMaximum)
{
  EXPECT_DOUBLE_EQ(clamp(2.0, -1.0, 1.0), 1.0);
}

TEST(ClampTest, LimitsValueBelowMinimum)
{
  EXPECT_DOUBLE_EQ(clamp(-2.0, -1.0, 1.0), -1.0);
}

TEST(ClampTest, SupportsNonSymmetricRange)
{
  EXPECT_DOUBLE_EQ(clamp(15.0, 0.0, 10.0), 10.0);
  EXPECT_DOUBLE_EQ(clamp(-5.0, 0.0, 10.0), 0.0);
  EXPECT_DOUBLE_EQ(clamp(7.0, 0.0, 10.0), 7.0);
}

TEST(ClampTest, AllowsEqualBounds)
{
  EXPECT_DOUBLE_EQ(clamp(3.0, 2.0, 2.0), 2.0);
}

TEST(ClampTest, RejectsReversedBounds)
{
  EXPECT_THROW(
    clamp(0.0, 2.0, 1.0),
    std::invalid_argument);
}

TEST(ClampTest, RejectsNonFiniteInputs)
{
  const double infinity =
    std::numeric_limits<double>::infinity();

  const double nan =
    std::numeric_limits<double>::quiet_NaN();

  EXPECT_THROW(
    clamp(nan, -1.0, 1.0),
    std::invalid_argument);

  EXPECT_THROW(
    clamp(0.0, -infinity, 1.0),
    std::invalid_argument);

  EXPECT_THROW(
    clamp(0.0, -1.0, infinity),
    std::invalid_argument);
}

TEST(WrapToPiTest, ZeroStaysZero)
{
  EXPECT_NEAR(wrapToPi(0.0), 0.0, kTolerance);
}

TEST(WrapToPiTest, TwoPiWrapsToZero)
{
  EXPECT_NEAR(
    wrapToPi(2.0 * kPi),
    0.0,
    kTolerance);

  EXPECT_NEAR(
    wrapToPi(-2.0 * kPi),
    0.0,
    kTolerance);
}

TEST(WrapToPiTest, PiMapsToNegativePi)
{
  EXPECT_NEAR(
    wrapToPi(kPi),
    -kPi,
    kTolerance);
}

TEST(WrapToPiTest, OutputAlwaysRemainsInRange)
{
  const double angles[] = {
    -10.0 * kPi,
    -3.5 * kPi,
    -2.0 * kPi,
    -kPi,
    -0.5 * kPi,
    0.0,
    0.5 * kPi,
    kPi,
    2.0 * kPi,
    3.5 * kPi,
    10.0 * kPi,
  };

  for (const double angle : angles) {
    const double wrapped = wrapToPi(angle);

    EXPECT_GE(wrapped, -kPi);
    EXPECT_LT(wrapped, kPi);
  }
}

TEST(WrapToPiTest, RejectsNonFiniteAngles)
{
  EXPECT_THROW(
    wrapToPi(
      std::numeric_limits<double>::infinity()),
    std::invalid_argument);

  EXPECT_THROW(
    wrapToPi(
      std::numeric_limits<double>::quiet_NaN()),
    std::invalid_argument);
}

TEST(PoseValidationTest, RecognizesFinitePose)
{
  EXPECT_TRUE(isFinitePose(Pose2D{1.0, 2.0, 0.5}));
}

TEST(PoseValidationTest, RejectsNonFinitePose)
{
  const double infinity =
    std::numeric_limits<double>::infinity();

  EXPECT_FALSE(isFinitePose(Pose2D{infinity, 0.0, 0.0}));
  EXPECT_FALSE(isFinitePose(Pose2D{0.0, infinity, 0.0}));
  EXPECT_FALSE(isFinitePose(Pose2D{0.0, 0.0, infinity}));
}

TEST(PoseIntegrationTest, MovesForwardAlongX)
{
  const Pose2D next_pose = integratePose(
    Pose2D{},
    1.0,
    0.0,
    1.0);

  EXPECT_NEAR(next_pose.x, 1.0, kTolerance);
  EXPECT_NEAR(next_pose.y, 0.0, kTolerance);
  EXPECT_NEAR(next_pose.theta, 0.0, kTolerance);
}

TEST(PoseIntegrationTest, MovesForwardAlongY)
{
  const Pose2D next_pose = integratePose(
    Pose2D{0.0, 0.0, kPi / 2.0},
    1.0,
    0.0,
    1.0);

  EXPECT_NEAR(next_pose.x, 0.0, 1e-8);
  EXPECT_NEAR(next_pose.y, 1.0, 1e-8);
  EXPECT_NEAR(
    next_pose.theta,
    kPi / 2.0,
    kTolerance);
}

TEST(PoseIntegrationTest, RotationOnlyChangesHeading)
{
  const Pose2D next_pose = integratePose(
    Pose2D{2.0, 3.0, 0.0},
    0.0,
    1.0,
    0.5);

  EXPECT_NEAR(next_pose.x, 2.0, kTolerance);
  EXPECT_NEAR(next_pose.y, 3.0, kTolerance);
  EXPECT_NEAR(next_pose.theta, 0.5, kTolerance);
}

TEST(PoseIntegrationTest, UsesCurrentHeadingForTranslation)
{
  const Pose2D next_pose = integratePose(
    Pose2D{},
    1.0,
    1.0,
    0.5);

  EXPECT_NEAR(next_pose.x, 0.5, kTolerance);
  EXPECT_NEAR(next_pose.y, 0.0, kTolerance);
  EXPECT_NEAR(next_pose.theta, 0.5, kTolerance);
}

TEST(PoseIntegrationTest, WrapsHeadingAfterUpdate)
{
  const Pose2D next_pose = integratePose(
    Pose2D{0.0, 0.0, kPi - 0.1},
    0.0,
    1.0,
    0.2);

  EXPECT_GE(next_pose.theta, -kPi);
  EXPECT_LT(next_pose.theta, kPi);
  EXPECT_NEAR(
    next_pose.theta,
    -kPi + 0.1,
    1e-8);
}

TEST(PoseIntegrationTest, ZeroTimestepPreservesPose)
{
  const Pose2D pose{2.0, -3.0, 0.75};

  const Pose2D next_pose = integratePose(
    pose,
    10.0,
    -10.0,
    0.0);

  EXPECT_DOUBLE_EQ(next_pose.x, pose.x);
  EXPECT_DOUBLE_EQ(next_pose.y, pose.y);
  EXPECT_DOUBLE_EQ(next_pose.theta, pose.theta);
}

TEST(PoseIntegrationTest, RepeatedStepsAreDeterministic)
{
  Pose2D pose;

  for (int index = 0; index < 100; ++index) {
    pose = integratePose(
      pose,
      1.0,
      0.0,
      0.01);
  }

  EXPECT_NEAR(pose.x, 1.0, 1e-8);
  EXPECT_NEAR(pose.y, 0.0, 1e-8);
  EXPECT_NEAR(pose.theta, 0.0, 1e-8);
}

TEST(PoseIntegrationTest, RejectsNegativeTimestep)
{
  EXPECT_THROW(
    integratePose(Pose2D{}, 1.0, 0.0, -0.01),
    std::invalid_argument);
}

TEST(PoseIntegrationTest, RejectsNonFiniteInputs)
{
  const double infinity =
    std::numeric_limits<double>::infinity();

  const double nan =
    std::numeric_limits<double>::quiet_NaN();

  EXPECT_THROW(
    integratePose(
      Pose2D{infinity, 0.0, 0.0},
      1.0,
      0.0,
      0.1),
    std::invalid_argument);

  EXPECT_THROW(
    integratePose(Pose2D{}, nan, 0.0, 0.1),
    std::invalid_argument);

  EXPECT_THROW(
    integratePose(Pose2D{}, 1.0, infinity, 0.1),
    std::invalid_argument);

  EXPECT_THROW(
    integratePose(Pose2D{}, 1.0, 0.0, nan),
    std::invalid_argument);
}
