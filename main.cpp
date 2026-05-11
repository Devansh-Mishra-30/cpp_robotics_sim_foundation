#include <vector>
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"
#include "simulator.h"
#include "reporter.h"

int main() {
	const double dt = 0.1;
	const int commandCount = 20;
	// parameters
	Pose2D robotPose{0.0, 0.0, 0.0};
	// initial pose
	const RobotCommand command{1.0,0.2};
	std::vector<RobotCommand> commands{ commandCount, command };

	std::vector<Pose2D> trajectory;
	trajectory.push_back(robotPose);
	SimInput inputCheck = validateSimulationInput(dt, commands);

	if (!inputCheck.commandbool) {
		printValidationReport(inputCheck, dt, commands, trajectory);
		return 1;
	}

	Simulator simulator(dt);

	for (const RobotCommand& currentCommand : commands) {
		simulator.step(currentCommand);
	}

	printSimulationSummary(dt,commands, simulator.getTrajectory());

	return 0;
}