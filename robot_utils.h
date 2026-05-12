#pragma once
#include"robot_command.h"
#include <vector>

struct SimInput {
	bool commandbool;
	int commandsindex;
};

double wrapToPi(double angle_rad);
bool isValidDt(double dt);
bool isValidCommand(const RobotCommand& command);
SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands);
double computeTotalDistance(const std::vector<Pose2D>& trajectory);
double computeFinalPositionError(const std::vector<Pose2D>& trajectory, const Pose2D& targetPose);
double computeMaxSpeed(const std::vector<Pose2D>& trajectory, double dt);