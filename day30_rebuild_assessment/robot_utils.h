#pragma once

#include "robot_command.h"
#include "pose2d.h"
#include <vector>

struct SimInput {
	bool commandbool{};
	int commandsindex{};
};

double wrapToPi(double angleRad);
bool isValidCommand(const RobotCommand& command);

bool isValidDt(double dt);
SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands);
double computeTotalDistance(const std::vector<Pose2D>& trajectory);
double computeFinalPositionError(const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
);
double computeMaxSpeed(const std::vector<Pose2D>& trajectory, double dt
);

