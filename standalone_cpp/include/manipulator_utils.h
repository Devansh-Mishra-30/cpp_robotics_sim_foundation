#pragma once

#include <vector>

#include "joint_state.h"

void updateJoint(JointState& joint, double dt);
void updateAllJoints(std::vector<JointState>& joints, double dt);
double clampJointPosition(double value, double min_position, double max_position);