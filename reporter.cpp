#include"reporter.h"
#include<iostream>

void printSimulationHeader() {
	std::cout << "---------------------------------------------------"
		<< "------------- STARTING THE SIMULATION -------------"
		<< "---------------------------------------------------" << std::endl;
}

void printSimulationSetup(const double dt, int commandCount) {
	std::cout << "\nSimulation Setup: \n"
		<< "Time step: " << dt << " s\n"
		<< "Command count: " << commandCount << "\n"
		<< "Expected simulation time: " << dt * commandCount << " s\n" << std::endl;
}

void printPose(const Pose2D& robotPose) {
	std::cout << "x: " << robotPose.x
		<< " m; y: " << robotPose.y
		<< " m; theta: " << robotPose.theta << " rad" << std::endl;
}

void printInitialPose(const std::vector<Pose2D>& trajectory) {
	std::cout << "Initial pose: " << std::endl;
	if (trajectory.empty()) {
		std::cout << "\n Initial pose not available. Trajectory is empty. \n";
		return;
	}
	printPose(trajectory.front());
}
void printFinalPose(const std::vector<Pose2D>& trajectory) {
	std::cout << "Final pose: " << std::endl;
	if (trajectory.empty()) {
		std::cout << "\n Final pose not available. Trajectory is empty. \n";
		return;
	}
	printPose(trajectory.back());
}

void printTrajectoryCount(const std::vector<Pose2D>& trajectory) {
	std::cout << "\n Saved trajectory points: " << trajectory.size() << "\n";
}

void printSelectedTrajectory(const std::vector<Pose2D>& trajectory, int sampleInterval) {
	std::cout << "Selected Trajectory Samples: \n";

	if (trajectory.empty()) {
		std::cout << "\n Selected poses not available. Trajectory is empty. \n";
		return;
	}

	if (sampleInterval <= 0) {
		std::cout << "Invalid sample interval. It must be greater than 0.\n";
		return;
	}

	const size_t interval = static_cast<size_t>(sampleInterval);

	for (size_t i = 0; i < trajectory.size(); i += static_cast<size_t>(sampleInterval)) {
		std::cout << "Step: " << i << ": ";
		printPose(trajectory[i]);
	}

	const size_t finalIndex = trajectory.size() - 1;

	if (finalIndex% static_cast<int>(sampleInterval) != 0){
		std::cout << "Step " << finalIndex << ": ";
		printPose(trajectory.back());
 	}
}


void printValidationReport(const SimInput& inputCheck, double dt, const std::vector<RobotCommand>& commands, const std::vector<Pose2D>& trajectory) {

	std::cout << "\nValidation Report\n";
	int errorCount = 0;
	if (inputCheck.commandbool == false && inputCheck.commandsindex == -2) {
		std::cout << "Error. dt must be finite and greater than 0. Current time step: " << dt << std::endl;
		++errorCount;
	}
	if (inputCheck.commandbool == false && inputCheck.commandsindex == -3) {
		std::cout << "Error: Command list is empty" << std::endl;
		++errorCount;
	}
	if (inputCheck.commandbool == false && inputCheck.commandsindex >= 0) {
		std::cout << "Error: Invalid Command at index: " << inputCheck.commandsindex << std::endl;
		++errorCount;
	}
	if (trajectory.empty()) {
		std::cout << "\nError: Trajectory is empty. \n";
		++errorCount;
	}
	else if (trajectory.size() == 1) {
		std::cout << "No additional trajectory points saved. Check steps or code logic! \n";
	}
	if (errorCount == 0) {
		std::cout << "Validation passed. No critical input or trajectory errors found.\n";
	}
	else {
		std::cout << "Validation completed with " << errorCount << " error(s). \n";
	}
}


void printSimulationSummary(double dt, const std::vector<RobotCommand>& commands, const std::vector<Pose2D>& trajectory) {
	std::cout << "Simulation Summary: \n" << std::endl;
	printSimulationHeader();
	printSimulationSetup(dt, static_cast<int>(commands.size()));
	printValidationReport(validateSimulationInput(dt, commands), dt, commands, trajectory);
	printInitialPose(trajectory);
	printFinalPose(trajectory);
	printTrajectoryCount(trajectory);
	printSelectedTrajectory(trajectory, 5);
}

