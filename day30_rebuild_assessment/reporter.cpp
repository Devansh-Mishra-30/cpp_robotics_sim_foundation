
#include "reporter.h"

#include <iostream>

void printSimulationHeader() {
	std::cout << "----------------------------------\n"
		<< "----------------------STARTING SIMULATION----------------------\n"
		<< "----------------------------------\n";
}

void printSimulationSetup(double dt, int commandCount) {
	std::cout << "\nSimulation Setup:\n"
		<< "Time step: " << dt << " s\n"
		<< "Command count: " << commandCount << "\n"
		<< "Expected simulation time: " << dt * commandCount << " s\n";
} 
void printPose(const Pose2D& pose) {
	std::cout << "x: " << pose.x
		<< " m; y: " << pose.y
		<< " m; theta: " << pose.theta << " rad\n";
}
void printInitialPose(const std::vector<Pose2D>& trajectory) {
	std::cout << "Initial pose:\n";

	if (trajectory.empty()) {
		std::cout << "Initial pose not available. Trajectory is empty.\n";
		return;
	}
	printPose(trajectory.front());
}

void printFinalPose(const std::vector<Pose2D>& trajectory) {
	std::cout << "Final pose:\n";

	if (trajectory.empty()) {
		std::cout << "Final pose not available. Trajectory is empty.\n";
		return;
	}

	printPose(trajectory.back());
}
void printTrajectoryCount(const std::vector<Pose2D>& trajectory) {
	std::cout << "\nSaved trajectory points: " << trajectory.size() << "\n";
}
void printSelectedTrajectory(const std::vector<Pose2D>& trajectory,
	int sampleInterval
) {
	std::cout << "Selected Trajectory Samples:\n";

	if (trajectory.empty()) {
		std::cout << "Selected poses not available. Trajectory is empty.\n";
		return;
	}

	if (sampleInterval <= 0) {
		std::cout << "Invalid sample interval. It must be greater than 0.\n";
		return;
	}

	const size_t interval = static_cast<size_t>(sampleInterval);

	for (size_t i = 0; i < trajectory.size(); i += interval) {
		std::cout << "Step: " << i << ": ";
		printPose(trajectory[i]);
	}

	const size_t finalIndex = trajectory.size() - 1;

	if (finalIndex % interval != 0) {
		std::cout << "Step: " << finalIndex << ": ";
		printPose(trajectory.back());
	}
}
void printValidationReport(const SimInput& inputCheck,
	double dt,
	const std::vector<RobotCommand>& commands,
	const std::vector<Pose2D>& trajectory
) {
	std::cout << "\nValidation Report\n";

	int errorCount = 0;

	if (!inputCheck.commandbool && inputCheck.commandsindex == -2) {
		std::cout << "Error: dt must be finite and greater than 0. Current time step: "
			<< dt << "\n";
		++errorCount;
	}

	if (!inputCheck.commandbool && inputCheck.commandsindex == -3) {
		std::cout << "Error: Command list is empty.\n";
		++errorCount;
	}

	if (!inputCheck.commandbool && inputCheck.commandsindex >= 0) {
		std::cout << "Error: Invalid command at index: "
			<< inputCheck.commandsindex << "\n";
		++errorCount;
	}

	if (trajectory.empty()) {
		std::cout << "Error: Trajectory is empty.\n";
		++errorCount;
	}
	else if (trajectory.size() == 1) {
		std::cout << "No additional trajectory points saved. Check steps or code logic.\n";
	}

	if (errorCount == 0) {
		std::cout << "Validation passed. No critical input or trajectory errors found.\n";
	}
	else {
		std::cout << "Validation completed with " << errorCount << " error(s).\n";
	}
}

void printFinalPositionError(const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
) {
	std::cout << "Final position error: "
		<< computeFinalPositionError(trajectory, targetPose) << " m\n";
}

void printTotalDistance(const std::vector<Pose2D>& trajectory) {
	std::cout << "Total distance traveled: "
		<< computeTotalDistance(trajectory) << " m\n";
}

void printMaxSpeed(
	const std::vector<Pose2D>& trajectory,
	double dt
) {
	std::cout << "Maximum speed: "
		<< computeMaxSpeed(trajectory, dt) << " m/s\n";
}
void printSimulationSummary(double dt,
	const std::vector<RobotCommand>& commands,
	const std::vector<Pose2D>& trajectory,
	const Pose2D& targetPose
) {
	std::cout << "Simulation Summary:\n\n";

	printSimulationHeader();
	printSimulationSetup(dt, static_cast<int>(commands.size()));

	printValidationReport(
		validateSimulationInput(dt, commands),
		dt,
		commands,
		trajectory
	);

	printInitialPose(trajectory);
	printFinalPose(trajectory);

	std::cout << "Target Pose:\n";
	printPose(targetPose);

	printTrajectoryCount(trajectory);
	printSelectedTrajectory(trajectory, 5);

	printTotalDistance(trajectory);
	printFinalPositionError(trajectory, targetPose);
	printMaxSpeed(trajectory, dt);
}

void printJointStates(const std::vector<JointState>& joints) {
	for (const JointState& joint : joints) {
		std::cout << joint.name
			<< " | position: " << joint.position
			<< " rad; velocity: " << joint.velocity
			<< " rad/s\n";
	}
}

