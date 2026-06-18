#include "manipulator/manipulator_reporter.h"

#include <iostream>

void printJointStates(const std::vector<JointState>& joints) {
	for (const JointState& joint : joints) {
		std::cout << joint.name
			<< " | position: " << joint.position
			<< " rad; velocity: " << joint.velocity
			<< " rad/s" << " | limits: ["
			<< joint.min_position
			<< ", " << joint.max_position << "] rad"
			<< std::endl;
	}
}