#pragma once

#include <vector>
#include "joint_state.h"
#include "pose2d.h"
#include "robot_command.h"
#include "trajectory_metrics.h"
#include "simulation_scenario.h"
#include "validation_result.h"

struct SimInput {
	bool commandbool;
	int commandsindex;
};

std::vector<SimulationScenario> createDefaultScenarios();

bool areAllCommandsValid(const std::vector<RobotCommand>& commands);
size_t countMovingJoints(const std::vector<JointState>& joints);
double computeMaxJointPositionMagnitude(const std::vector<JointState>& joints);

const Pose2D* findClosestPoseToTarget(
	const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
);

double wrapToPi(double angle_rad);
bool isValidDt(double dt);
bool isValidCommand(const RobotCommand& command);
SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands);
double computeTotalDistance(const std::vector<Pose2D>& trajectory);
double computeFinalPositionError(const std::vector<Pose2D>& trajectory, const Pose2D& targetPose);
double computeMaxSpeed(const std::vector<Pose2D>& trajectory, double dt);
TrajectoryMetrics computeTrajectoryMetrics(
	const std::vector <Pose2D>& trajectory,
	const Pose2D& targetPose,
	double dt
);
bool isNear(
	double actual,
	double expected,
	double tolerance
);

ValidationResult validateScalar(
	const std::string& testName,
	double actual,
	double expected,
	double tolerance
);