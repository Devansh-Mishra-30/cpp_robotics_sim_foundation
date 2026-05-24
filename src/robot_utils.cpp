#include "robot_utils.h"
#include "joint_state.h"
#include <algorithm>
#include <cmath>

bool areAllCommandsValid(const std::vector<RobotCommand>& commands) {
	return std::all_of(
		commands.begin(),
		commands.end(),
		[](const RobotCommand& command) {
			return isValidCommand(command);
		}
	);
}

size_t countMovingJoints(const std::vector<JointState>& joints) {
	return static_cast<size_t>(
		std::count_if(
			joints.begin(),
			joints.end(),
			[](const JointState& joint) {
				return std::abs(joint.velocity) > 0.0;
			}
		)
		);
}

double computeMaxJointPositionMagnitude(const std::vector<JointState>& joints) {
	if (joints.empty()) {
		return 0.0;
	}

	const auto maxIt = std::max_element(
		joints.begin(),
		joints.end(),
		[](const JointState& a, const JointState& b) {
			return std::abs(a.position) < std::abs(b.position);
		}
	);
	return std::abs(maxIt->position);
}

const Pose2D* findClosestPoseToTarget(
	const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
) {
	if (trajectory.empty()) {
		return nullptr;
	}

	const auto closestIt = std::min_element(
		trajectory.begin(),
		trajectory.end(),
		[&targetPose](const Pose2D& a, const Pose2D& b) {
			const double dxA = targetPose.x - a.x;
			const double dyA = targetPose.y - a.y;
			const double distanceA = dxA * dxA + dyA * dyA;

			const double dxB = targetPose.x - b.x;
			const double dyB = targetPose.y - b.y;
			const double distanceB = dxB * dxB + dyB * dyB;

			return distanceA < distanceB;
		}
	);
	return &(*closestIt);
}

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
		totalDistance += std::sqrt(dx * dx + dy * dy);
	}
	return totalDistance;
}

double computeFinalPositionError(const std::vector<Pose2D>& trajectory, const Pose2D& targetPose) {
	if (trajectory.empty()) {
		return 0.0;
	}
	const Pose2D& finalPose = trajectory.back();
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

SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands) {
	SimInput result;
	result.commandbool = true;
	result.commandsindex = -1;

	if (!isValidDt(dt)) {
		result.commandbool = false;
		result.commandsindex = -2; //placeholder for error numbering
		return result;
	}

	if (commands.empty()) {
		result.commandbool = false;
		result.commandsindex = -3; //placeholder for error numbering
		return result;
	}

	for (size_t i = 0; i < commands.size(); i++) {
		if (!isValidCommand(commands[i])) {
			result.commandbool = false;
			result.commandsindex = static_cast<int>(i);
			return result;
		}
	}
	return result;
}

