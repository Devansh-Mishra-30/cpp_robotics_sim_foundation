#pragma once

#include <vector>

#include "manipulator/joint_state.h"

void updateJoint(JointState& joint, double dt);
void updateAllJoints(std::vector<JointState>& joints, double dt);
size_t countMovingJoints(const std::vector<JointState>& joints);
double clampJointPosition(double value, double min_position, double max_position);
double computeMaxJointPositionMagnitude(const std::vector<JointState>& joints);