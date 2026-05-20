#pragma once

#include <vector>

#include "joint_state.h"
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"

void printSimulationHeader();
void printSimulationSetup(double dt, int commandCount);
void printPose(const Pose2D& pose);
void printInitialPose(const std::vector<Pose2D>& trajectory);
void printFinalPose(const std::vector<Pose2D>& trajectory);
void printTrajectoryCount(const std::vector<Pose2D>& trajectory);
void printSelectedTrajectory(const std::vector<Pose2D>& trajectory,
	int sampleInterval
);
void printTotalDistance(const std::vector<Pose2D>& trajectory);
void printValidationReport(const SimInput& inputCheck,
	double dt,
	const std::vector<RobotCommand>& commands,
	const std::vector<Pose2D>& trajectory
);
void printFinalPositionError(const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
);
void printMaxSpeed(
	const std::vector<Pose2D>& trajectory,
	double dt
);
void printSimulationSummary(double dt,
	const std::vector<RobotCommand>& commands,
	const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
);
void printJointStates(const std::vector<JointState>& joints);

