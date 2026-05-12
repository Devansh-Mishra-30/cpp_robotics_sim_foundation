#include <vector>
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"
#include "simulator.h"
#include "reporter.h"

int main() {
	const double dt = 0.1;
	const int commandCount = 20;
	
	const Pose2D initialPose{ 0.0, 0.0, 0.0 };
	const Pose2D targetPose{ 2.0, 0.0, 0.0 };

	const RobotCommand command{ 1.0, 0.2 };
	const std::vector<RobotCommand> commands(commandCount, command);

	const SimInput inputCheck = validateSimulationInput(dt, commands);

	if (!inputCheck.commandbool) {
		const std::vector<Pose2D> emptyTrajectory;
		printValidationReport(inputCheck, dt, commands, emptyTrajectory);
		return 1;
	}

	Simulator simulator(dt, initialPose);

	for (const RobotCommand& currentCommand : commands) {
		simulator.step(currentCommand);
	}

	printSimulationSummary(dt,commands, simulator.getTrajectory(), targetPose);

	return 0;
}