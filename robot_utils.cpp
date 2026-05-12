#include <cmath>
#include <vector>
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"

double wrapToPi(double angle_rad) {
	return std::atan2(std::sin(angle_rad), std::cos(angle_rad));
}

bool isValidCommand(const RobotCommand& command) {
	return std::isfinite(command.v) && std::isfinite(command.omega);
}

bool isValidDt(double dt) {
	return std::isfinite(dt) && dt > 0.0;
}

double computeTotalDistance(const std::vector<Pose2D>& trajectory) {
	double totalDistance = 0.0;
	for (size_t i = 1; i < trajectory.size(); ++i) {
		const double dx = trajectory[i].x - trajectory[i - 1].x;
		const double dy = trajectory[i].y - trajectory[i - 1].y;
		totalDistance += sqrt(dx * dx + dy * dy);
	}
	return totalDistance;
}

double computeFinalPositionError(const std::vector<Pose2D>& trajectory, const Pose2D& targetPose) {
	if (trajectory.empty()) {
		return 0.0;
	}
	Pose2D finalPose = trajectory.back();
	const double dx = targetPose.x - finalPose.x;
	const double dy = targetPose.y - finalPose.y;
	return std::sqrt(dx * dx + dy * dy);
}

double computeMaxSpeed(const std::vector<Pose2D>& trajectory, double dt) {
	
	double maxSpeed = 0.0;
	for (size_t i = 1; i < trajectory.size(); ++i) {
		const double dx = trajectory[i].x - trajectory[i - 1].x;
		const double dy = trajectory[i].y - trajectory[i - 1].y;
		const double stepDistance = std::sqrt(dx * dx + dy * dy);
		const double stepSpeed = stepDistance / dt;
		if (stepSpeed > maxSpeed) {
			maxSpeed = stepSpeed;
		}
	}

	return maxSpeed;
}

SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands) 
{
	SimInput commandboolandIndex;
	commandboolandIndex.commandbool = true;
	commandboolandIndex.commandsindex = -1;

	if (!isValidDt(dt)) {
		commandboolandIndex.commandbool = false;
		commandboolandIndex.commandsindex = -2; //placeholder for error numbering
		return commandboolandIndex;
	}

	if (commands.empty()) {
		commandboolandIndex.commandbool = false;
		commandboolandIndex.commandsindex = -3; //placeholder for error numbering
		return commandboolandIndex;
	}

	for (size_t i = 0; i < commands.size(); i++) {
		if (!isValidCommand(commands[i])) {
			commandboolandIndex.commandbool = false;
			commandboolandIndex.commandsindex = static_cast<int>(i);
			return commandboolandIndex;
		}
	}
	return commandboolandIndex;
}

