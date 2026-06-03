#include <iostream>
#include <vector>

#include "differential_drive.h"
#include "joint_state.h"
#include "manipulator_utils.h"
#include "pose2d.h"
#include "reporter.h"
#include "robot_command.h"
#include "robot_utils.h"
#include "differential_drive_robot.h"

void runDifferentialDriveDemo() {
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
		return;
	}

	DifferentialDriveRobot robot(initialPose, wheelRadius, wheelBase);

	for (int step = 0; step < commandCount; ++step) {
		robot.update(wheelCommand, dt);
	}

	std::cout << "\nDay 38 Differential Drive Kinematics Tests\n";
	std::cout << "---------------------------------------------\n";

	const std::vector<WheelCommand> wheelTests = {
		{5.0,5.0},
		{-5.0, 5.0},
		{3.0, 5.0},
		{5.0, 3.0},
		{0.0,0.0}
	};

	for (const WheelCommand& testCommand : wheelTests) {
		const RobotCommand result = convertWheelCommandToRobotCommand(
			testCommand,
			wheelRadius,
			wheelBase
		);

		std::cout << "wl: " << testCommand.leftWheelSpeed
			<< "rad/s, wr: " << testCommand.rightWheelSpeed
			<< "rad/s -> v: " << result.v
			<< "m/s, omega: " << result.omega
			<< "rad/s\n";
	}

	std::cout << "\nDifferential Drive Demo\n";
	std::cout << "-----------------------------------\n";
	std::cout << "Left wheel speed: " << wheelCommand.leftWheelSpeed << " rad/s\n";
	std::cout << "Right wheel speed: " << wheelCommand.rightWheelSpeed << " rad/s\n";
	std::cout << "Computed v: " << robotCommand.v << " m/s\n";
	std::cout << "Computed omega: " << robotCommand.omega << " rad/s\n";

	printSimulationSummary(dt, commands, robot.getTrajectory(), targetPose);
	
	std::cout << "\nSTL analysis:\n";
	std::cout << "All commands valid: "
		<< (areAllCommandsValid(commands) ? "true" : "false") << "\n";

	const Pose2D* closestPose =
		findClosestPoseToTarget(robot.getTrajectory(), targetPose);

	if (closestPose != nullptr) {
		std::cout << "Closest pose to target: \n";
		printPose(*closestPose);
	}

	std::string filename = "trajectory.csv";
	if (!writeTrajectoryToCsv(filename, robot.getTrajectory(), dt)) {
		std::cout << "Error: trajectory.csv was not written\n";
		return;
	}
		std::cout << "Data logged successfully to trajectory.csv\n";

		robot.reset(initialPose);
		std::cout << "\nAfter reset pose:\n";
		printPose(robot.getPose());

}

void runManipulatorDemo() {
	const double dt = 0.1;
	const double duration = 10.0;
	const int stepCount = static_cast<int>(duration / dt);
	std::vector<JointState> threeJointArm = {
		{"shoulder", 0.0, 0.5},
		{"elbow", 0.0, 0.3},
		{"wrist", 0.0, 0.2},
	};

	std::cout << "\nManipulator Joint-Space Demo\n";
	std::cout << "--------------------------------\n";

	std::cout << "Initial joint states: \n";
	printJointStates(threeJointArm);

	for (int step = 0; step < stepCount; ++step) {
		updateAllJoints(threeJointArm, dt);
	}
	std::cout << "Final joint states: \n";
	printJointStates(threeJointArm);

	std::cout << "\nManipulator setup:\n";
	std::cout << "dt: " << dt << " s\n";
	std::cout << "duration: " << duration << " s\n";
	std::cout << "step count: " << stepCount << "\n";
}

int main() {
	std::cout << "Day 29 Integrated Robotics Simulation Project\n";
	std::cout << "=============================================\n";

	runDifferentialDriveDemo();
	runManipulatorDemo();
	return 0;
}







