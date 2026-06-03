#include "reporter.h"

#include <iostream>
#include <fstream>

void printSimulationHeader() {
	std::cout << "---------------------------------------------------\n"
		<< "------------- STARTING THE SIMULATION -------------\n"
		<< "---------------------------------------------------" << std::endl;
}

void printSimulationSetup(const double dt, int commandCount) {
	std::cout << "\nSimulation Setup: \n"
		<< "Time step: " << dt << " s\n"
		<< "Command count: " << commandCount << "\n"
		<< "Expected simulation time: " << dt * commandCount << " s\n" << std::endl;
}

void printPose(const Pose2D& pose) {
	std::cout << "x: " << pose.x
		<< " m; y: " << pose.y
		<< " m; theta: " << pose.theta << " rad" << std::endl;
}
void printJointStates(const std::vector<JointState>& joints) {
	for (const JointState& joint : joints) {
		std::cout << joint.name
			<< " | position: " << joint.position
			<< " rad; velocity: " << joint.velocity
			<< " rad/s" << std::endl;
	}
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
	std::cout << "\nSaved trajectory points: " << trajectory.size() << "\n";
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


void printValidationReport(const SimInput& inputCheck, double dt, const std::vector<RobotCommand>& commands, const std::vector<Pose2D>& trajectory) {

	std::cout << "\nValidation Report\n";
	std::cout << "Command count checked: " << commands.size() << "\n";
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

void printTargetPose(const Pose2D& targetPose) {
	printPose(targetPose);
}

void printTotalDistance(const std::vector<Pose2D>& trajectory) {
	std::cout << "Total distance traveled: " << computeTotalDistance(trajectory) << " m" << std::endl;

}

void printFinalPositionError(const std::vector<Pose2D>& trajectory, const Pose2D& targetPose) {
	std::cout << "Final position error: " << computeFinalPositionError(trajectory, targetPose) << " m" << std::endl;
}

void printMaxSpeed(const std::vector<Pose2D>& trajectory, double dt) {
	std::cout << "Maximum speed: " << computeMaxSpeed(trajectory, dt) << " m/s" << std::endl;
}


void printSimulationSummary(double dt, const std::vector<RobotCommand>& commands, const std::vector<Pose2D>& trajectory, const Pose2D& targetPose) {
	std::cout << "Simulation Summary: \n" << std::endl;
	printSimulationHeader();
	printSimulationSetup(dt, static_cast<int>(commands.size()));
	printValidationReport(validateSimulationInput(dt, commands), dt, commands, trajectory);
	printInitialPose(trajectory);
	printFinalPose(trajectory);
	std::cout << "Target Pose: \n";
	printTargetPose(targetPose);

	printTrajectoryCount(trajectory);
	printSelectedTrajectory(trajectory, 5);
	
	printTotalDistance(trajectory);
	printFinalPositionError(trajectory, targetPose);
	printMaxSpeed(trajectory, dt);

}

bool writeTrajectoryToCsv(const std::string& filename, 
	const std::vector<Pose2D>& trajectory, double dt) {
	std::ofstream file(filename);
	if (!file.is_open()) {
		return false;
	}

	file << "time,x,y,theta\n";
	for (size_t i = 0; i < trajectory.size(); i++)
	{
		const double time = static_cast<double>(i) * dt;
		const Pose2D& pose = trajectory[i];

		file << time << "," 
			<< pose.x << ","
			<< pose.y << ","
			<< pose.theta << "\n";
	}
	return true;
}

void printTrajectoryMetrics(const TrajectoryMetrics& metrics) {
	std::cout << "\nTrajectory Metrics\n";
	std::cout << "--------------------\n";
	std::cout << "Total distance traveled: "
		<< metrics.totalDistance << " m\n";
	std::cout << "Final position error: "
		<< metrics.finalPositionError << " m\n";
	std::cout << "Maximum speed: "
		<< metrics.maxSpeed << " m/s\n";
}

void printScenarioResult(
	const SimulationScenario& scenario,
	const Pose2D& finalPose,
	const TrajectoryMetrics& metrics) {
	std::cout << "\nScenario: " << scenario.name << "\n";
	std::cout << "-------------------------\n";
	std::cout << "Final pose: ";
	printPose(finalPose);
	std::cout << "Total distance: " << metrics.totalDistance << " m\n";
	std::cout << "Final position error: " << metrics.finalPositionError << " m\n";
	std::cout << "Maximum speed: " << metrics.maxSpeed << " m/s\n";
}
