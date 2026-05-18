#include <vector>
#include "pose2d.h"
#include "robot_command.h"
#include "robot_utils.h"
#include "simulator.h"
#include "reporter.h"
#include <string>
#include <iostream>

int main() {
	const double dt = 0.1;

	struct Scenario {
		std::string name;
		Pose2D initialPose;
		RobotCommand command;
		double duration{};
	};

	const Pose2D targetPose{ 2.0, 0.0, 0.0 };

	std::vector<Scenario> scenarios = { { "straight motion",{0.0,0.0,0.0},{0.5, 0.0},10.0 },
	{"rotate in one place", { 0.0,0.0,0.0 }, { 0.0, 0.5 }, 12.0},
	{ "rotation + translation trajectory", { 0.0,0.0,0.0 }, { 0.5, 0.5 }, 15.0 },
	{ "offset straight motion", { 0.2,0.2,0.2 }, { 0.5, 0.0 }, 10.0 },
	{ "zero command test", { 0.0,0.0,0.0 }, { 0.0, 0.0 }, 5.0 },
	};

	for (const Scenario& scenario : scenarios) {
		std::cout << "\nScenario : " << scenario.name << std::endl;
		const int commandCount = static_cast<int>(scenario.duration / dt);

		const std::vector<RobotCommand> commands(commandCount, scenario.command);		
		
		const SimInput inputCheck = validateSimulationInput(dt, commands);

		if (!inputCheck.commandbool) {
			const std::vector<Pose2D> emptyTrajectory;
			printValidationReport(inputCheck, dt, commands, emptyTrajectory);
			continue;
		}

		Simulator simulator(dt, scenario.initialPose);

		for (const RobotCommand& currentCommand : commands) {
			simulator.step(currentCommand);
		}

		printSimulationSummary(dt, commands, simulator.getTrajectory(), targetPose);
	}
	return 0;
}