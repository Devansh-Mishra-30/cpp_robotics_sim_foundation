#include "robot_utils.h"
#include <cmath>

double wrapToPi(double angleRad) {
	return std::atan2(std::sin(angleRad), std::cos(angleRad));
}

bool isValidCommand(const RobotCommand& command) {
	return std::isfinite(command.v) && std::isfinite(command.omega);
}

bool isValidDt(double dt) {
	return std::isfinite(dt) && dt > 0.0;
}

SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands) {
	SimInput result;
	result.commandbool = true;
	result.commandsindex = -1;

	if (!isValidDt(dt)) {
		result.commandbool = false;
		result.commandsindex = -2;
		return result;
	}

	if (commands.empty()) {
		result.commandbool = false;
		result.commandsindex = -3;
		return result;
	}

	for (size_t i = 0; i < commands.size(); ++i) {
		if (!isValidCommand(commands[i])) {
			result.commandbool = false;
			result.commandsindex = static_cast<int>(i);
			return result;
		}
	}
	return result;
}

double computeTotalDistance(const std::vector<Pose2D>& trajectory) {
	double totalDistance = 0.0;
	for (size_t i = 1; i < trajectory.size(); ++i)
	{
		const double dx = trajectory[i].x - trajectory[i - 1].x;
		const double dy = trajectory[i].y - trajectory[i - 1].y;
		totalDistance += std::sqrt(dx * dx + dy * dy);
	}
	return totalDistance;
}

double computeFinalPositionError(const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
) {
	if (trajectory.empty()) {
		return 0.0;
	}

	const Pose2D& finalPose = trajectory.back();

	const double dx = targetPose.x - finalPose.x;
	const double dy = targetPose.y - finalPose.y;

	return std::sqrt(dx * dx + dy * dy);
}


double computeMaxSpeed(const std::vector<Pose2D>& trajectory, double dt
) {
	double maxSpeed = 0.0;

	if (!isValidDt(dt)) {
		return maxSpeed;
	}

	for (size_t i = 1; i < trajectory.size(); ++i)
	{
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

