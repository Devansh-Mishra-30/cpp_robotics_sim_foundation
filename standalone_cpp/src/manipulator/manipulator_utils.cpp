#include "manipulator/manipulator_utils.h"

#include <algorithm>
#include <stdexcept>

double clampJointPosition(double value, double min_position, double max_position) {
	return std::clamp(value, min_position, max_position);
}

void updateJoint(JointState& joint, double dt) {

	if (dt <= 0.0) {
		throw std::runtime_error("updateJoint error: dt must be > 0");
	}

	if (joint.min_position > joint.max_position) {
		throw std::runtime_error("updateJoint error: invalid joint limits");
	}

	const double next_position = joint.position + joint.velocity * dt;

	joint.position = clampJointPosition(
		next_position,
		joint.min_position,
		joint.max_position
	);
}

void updateAllJoints(std::vector<JointState>& joints, double dt) {
	for (JointState& joint : joints) {
		updateJoint(joint, dt);
	}
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