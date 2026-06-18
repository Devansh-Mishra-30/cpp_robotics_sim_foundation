#include "manipulator_utils.h"

#include <algorithm>
#include <stdexcept>

double clampJointPosition(double value, double min_position, double max_position) {
	return std::clamp(value, min_position, max_position);
}

void updateJoint(JointState& joint, double dt) {

	if (dt <= 0.0) {
		throw std::runtime_error("UpdateJoint error: dt must be > 0");
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

