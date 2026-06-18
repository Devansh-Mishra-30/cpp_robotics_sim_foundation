#pragma once

#include <vector>
#include <string>
#include "differential_drive/pose2d.h"
#include "differential_drive/robot_command.h"
#include "differential_drive/trajectory_metrics.h"
#include "differential_drive/simulation_scenario.h"
#include "differential_drive/validation_result.h"

struct SimInput {
	bool commandbool;
	int commandsindex;
};

std::vector<SimulationScenario> createDefaultScenarios();

bool areAllCommandsValid(const std::vector<RobotCommand>& commands);

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