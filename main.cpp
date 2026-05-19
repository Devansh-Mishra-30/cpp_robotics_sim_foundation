#include <iostream>
#include <vector>

#include "differential_drive.h"
#include "pose2d.h"
#include "reporter.h"
#include "robot_command.h"
#include "robot_utils.h"
#include "simulator.h"

int main() {
	const double dt = 0.1;
	const double duration = 10.0;
	const int commandCount = static_cast<int>(duration / dt);
	const double wheelRadius = 0.1;
	const double wheelBase = 0.5;

	const Pose2D initialPose{ 0.0,0.0,0.0 };
	const Pose2D targetPose{ 5.0,0.0,0.0 };

	const WheelCommand wheelCommand{ 5.0,5.0 };
	const RobotCommand robotCommand = convertWheelCommandToRobotCommand(
		wheelCommand,
		wheelRadius,
		wheelBase
	);

	const std::vector<RobotCommand> commands(commandCount, robotCommand);
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

	std::cout << "Day 27 Differential Drive Mini-Sim\n";
	std::cout << "-----------------------------------\n";
	std::cout << "Left wheel speed: " << wheelCommand.leftWheelSpeed << " rad/s\n";
	std::cout << "Right wheel speed: " << wheelCommand.rightWheelSpeed << " rad/s\n";
	std::cout << "Computed v: " << robotCommand.v << " m/s\n";
	std::cout << "Computed omega: " << robotCommand.omega << " rad/s\n";

	printSimulationSummary(dt, commands, simulator.getTrajectory(), targetPose);
	return 0;
}




