#include <vector>
#include "reporter.h"
#include <iostream>
#include "manipulator_utils.h"
#include "joint_state.h"

int main() {
	const double dt = 0.1;
	double duration = 10.0;
	std::vector<JointState> threeJointArm = { {"shoulder",0.0,0.5}, {"elbow", 0.0,0.3}, {"wrist",0.0,0.2} };
	const int stepCount = static_cast<int>(duration / dt);

	std::cout << "Day 26 Manipulator Mini-Sim\n";
	std::cout << "--------------------------------\n\n";

	std::cout << "Initial joint states:\n";
	printJointStates(threeJointArm);

	for (int step = 0; step < stepCount; ++step) {
		updateAllJoints(threeJointArm, dt);
	}

	std::cout << "Final joint states:\n";
	printJointStates(threeJointArm);

	std::cout << "\n Simulation Setup: \n";
	std::cout << "dt: " << dt << "s\n";
	std::cout << "duration: " << duration << " s\n";
	std::cout << "step count: " << stepCount << "\n";

	return 0;
}




