#pragma once

#include <vector>
#include <string>

#include "differential_drive/pose2d.h"
#include "differential_drive/robot_command.h"
#include "differential_drive/robot_utils.h"
#include "differential_drive/trajectory_metrics.h"
#include "differential_drive/simulation_scenario.h"
#include "differential_drive/validation_result.h"

void printSimulationHeader();
void printSimulationSetup(const double dt, int commandCount);
void printPose(const Pose2D& pose);
void printInitialPose(const std::vector<Pose2D>& trajectory);
void printFinalPose(const std::vector<Pose2D>& trajectory);
void printTrajectoryCount(const std::vector<Pose2D>& trajectory);
void printSelectedTrajectory(const std::vector<Pose2D>& trajectory, int sampleInterval);
void printValidationReport(const SimInput& inputCheck, 
	double dt, 
	const std::vector<RobotCommand>& commands, 
	const std::vector<Pose2D>& trajectory);
void printSimulationSummary(double dt, 
	const std::vector<RobotCommand>& commands,
	const std::vector<Pose2D>& trajectory, 
	const Pose2D& targetPose);
bool writeTrajectoryToCsv(const std::string& filename,
	const std::vector<Pose2D>& trajectory, double dt);
void printTrajectoryMetrics(const TrajectoryMetrics& metrics);
void printScenarioResult(
	const SimulationScenario& scenario,
	const Pose2D& finalPose,
	const TrajectoryMetrics& metrics);
void printValidationResult(const ValidationResult& result);