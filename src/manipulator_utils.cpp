#include "manipulator_utils.h"

void updateJoint(JointState& joint, double dt) {
	joint.position += joint.velocity * dt;
}

void updateAllJoints(std::vector<JointState>& joints, double dt) {
	for (JointState& joint : joints) {
		updateJoint(joint, dt);
	}
}