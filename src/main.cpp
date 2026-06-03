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
#include "trajectory_metrics.h"

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
			<< " rad/s, wr: " << testCommand.rightWheelSpeed
			<< " rad/s -> v: " << result.v
			<< " m/s, omega: " << result.omega
			<< " rad/s\n";
	}

	std::cout << "\nDifferential Drive Demo\n";
	std::cout << "-----------------------------------\n";
	std::cout << "Left wheel speed: " << wheelCommand.leftWheelSpeed << " rad/s\n";
	std::cout << "Right wheel speed: " << wheelCommand.rightWheelSpeed << " rad/s\n";
	std::cout << "Computed v: " << robotCommand.v << " m/s\n";
	std::cout << "Computed omega: " << robotCommand.omega << " rad/s\n";

	printSimulationSummary(dt, commands, robot.getTrajectory(), targetPose);
	
	const TrajectoryMetrics metrics = computeTrajectoryMetrics(
		robot.getTrajectory(),
		targetPose,
		dt
	);

	printTrajectoryMetrics(metrics);

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

void runScenarioRunnerDemo() {
	const double dt = 0.1;
	const double wheelRadius = 0.1;
	const double wheelBase = 0.5;

	const std::vector<SimulationScenario> scenarios = createDefaultScenarios();

	std::cout << "\nDay 41 Scenario Runner Demo\n";
	std::cout << "------------------------------\n";

	for (const SimulationScenario& scenario : scenarios) {
		DifferentialDriveRobot robot(scenario.initialPose,
			wheelRadius, wheelBase
		);
		const int stepCount = static_cast<int> (scenario.duration / dt);

		for (int step = 0; step < stepCount; ++step) {
			robot.update(scenario.wheelCommand, dt);
		}

		const TrajectoryMetrics metrics = computeTrajectoryMetrics(
			robot.getTrajectory(),
			scenario.targetPose,
			dt
		);

		printScenarioResult(
			scenario,
			robot.getPose(),
			metrics
		);
	}
}

void runValidationTestsDemo() {
	const double dt = 0.1;
	const int stepCount = 100;
	const double duration = static_cast<double>(stepCount) * dt;
	const double wheelRadius = 0.1;
	const double wheelBase = 0.5;
	const double tolerance = 1e-6;
	const double curveTolerance = 1e-4;

	std::cout << "\nDay 42 Validation Tests Demo\n";
	std::cout << "--------------------------------\n";
	{
		// Straight motion validation
		const Pose2D initialPose{ 0.0, 0.0, 0.0 };
		const Pose2D targetPose{ 5.0, 0.0, 0.0 };
		const WheelCommand wheelCommand{ 5.0, 5.0 };

		DifferentialDriveRobot robot(initialPose, wheelRadius, wheelBase);

		for (int step = 0; step < stepCount; ++step) {
			robot.update(wheelCommand, dt);
		}

		const Pose2D& finalPose = robot.getPose();

		const TrajectoryMetrics metrics = computeTrajectoryMetrics(
			robot.getTrajectory(),
			targetPose,
			dt
		);

		printValidationResult(validateScalar(
			"Straight final x",
			finalPose.x,
			5.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Straight final y",
			finalPose.y,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Straight final theta",
			finalPose.theta,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Straight total distance",
			metrics.totalDistance,
			5.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Straight final position error",
			metrics.finalPositionError,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Straight maximum speed",
			metrics.maxSpeed,
			0.5,
			tolerance
		));
	}
	{
		// No motion validation
		const Pose2D initialPose{ 0.0, 0.0, 0.0 };
		const Pose2D targetPose{ 0.0,0.0,0.0 };
		const WheelCommand wheelCommand{ 0.0, 0.0 };

		DifferentialDriveRobot robot(initialPose, wheelRadius, wheelBase);

		for (int step = 0; step < stepCount; ++step) {
			robot.update(wheelCommand, dt);
		}

		const Pose2D& finalPose = robot.getPose();

		const TrajectoryMetrics metrics = computeTrajectoryMetrics(
			robot.getTrajectory(),
			targetPose,
			dt
		);

		printValidationResult(validateScalar(
			"No motion final x",
			finalPose.x,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"No motion final y",
			finalPose.y,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"No motion final theta",
			finalPose.theta,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"No motion total distance",
			metrics.totalDistance,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"No motion final position error",
			metrics.finalPositionError,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"No motion maximum speed",
			metrics.maxSpeed,
			0.0,
			tolerance
		));
	}
	{
		// Rotate in place validation
		const Pose2D initialPose{ 0.0, 0.0, 0.0 };
		const Pose2D targetPose{ 0.0, 0.0, 0.0 };
		const WheelCommand wheelCommand{ -5.0, 5.0 };

		DifferentialDriveRobot robot(initialPose, wheelRadius, wheelBase);

		for (int step = 0; step < stepCount; ++step) {
			robot.update(wheelCommand, dt);
		}

		const RobotCommand robotCommand = convertWheelCommandToRobotCommand(
			wheelCommand,
			wheelRadius,
			wheelBase
		);

		const double expectedTheta = wrapToPi(robotCommand.omega * duration);

		const Pose2D& finalPose = robot.getPose();

		const TrajectoryMetrics metrics = computeTrajectoryMetrics(
			robot.getTrajectory(),
			targetPose,
			dt
		);

		printValidationResult(validateScalar(
			"Rotate final x",
			finalPose.x,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Rotate final y",
			finalPose.y,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Rotate final theta",
			finalPose.theta,
			expectedTheta,
			tolerance
		));

		printValidationResult(validateScalar(
			"Rotate total distance",
			metrics.totalDistance,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Rotate final position error",
			metrics.finalPositionError,
			0.0,
			tolerance
		));

		printValidationResult(validateScalar(
			"Rotate maximum speed",
			metrics.maxSpeed,
			0.0,
			tolerance
		));
	}
	{
		// Curve-left and Curve-right symmetry validation

		const Pose2D initialPose{ 0.0,0.0,0.0 };
		const Pose2D targetPose{ 0.0,0.0,0.0 };
		const WheelCommand leftCommand{ 3.0, 5.0 };
		const WheelCommand rightCommand{ 5.0, 3.0 };

		DifferentialDriveRobot leftRobot(initialPose, wheelRadius, wheelBase);
		DifferentialDriveRobot rightRobot(initialPose, wheelRadius, wheelBase);

		for (int step = 0; step < stepCount; ++step) {
			leftRobot.update(leftCommand, dt);
			rightRobot.update(rightCommand, dt);
		}

		const Pose2D& leftFinal = leftRobot.getPose();
		const Pose2D& rightFinal = rightRobot.getPose();

		const TrajectoryMetrics leftMetrics = computeTrajectoryMetrics(
			leftRobot.getTrajectory(),
			targetPose,
			dt
		);

		const TrajectoryMetrics rightMetrics = computeTrajectoryMetrics(
			rightRobot.getTrajectory(),
			targetPose,
			dt
		);

		printValidationResult(validateScalar(
			"Curve symmetry x",
			leftFinal.x,
			rightFinal.x,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve symmetry y",
			leftFinal.y,
			-rightFinal.y,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve symmetry theta",
			leftFinal.theta,
			-rightFinal.theta,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve right total distance",
			rightMetrics.totalDistance,
			4.0,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve left total distance",
			leftMetrics.totalDistance,
			4.0,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve distance symmetry",
			leftMetrics.totalDistance,
			rightMetrics.totalDistance,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve left maximum speed",
			leftMetrics.maxSpeed,
			0.4,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve right maximum speed",
			rightMetrics.maxSpeed,
			0.4,
			curveTolerance
		));

		printValidationResult(validateScalar(
			"Curve maximum speed symmetry",
			leftMetrics.maxSpeed,
			rightMetrics.maxSpeed,
			curveTolerance
		));

	}
}

int main() {
	std::cout << "Day 42 Robotics Simulation Project\n";
	std::cout << "=============================================\n";

	runDifferentialDriveDemo();
	runManipulatorDemo();
	runScenarioRunnerDemo();
	runValidationTestsDemo();
	return 0;
}







