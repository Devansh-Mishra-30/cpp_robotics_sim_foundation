#pragma once
#include<vector>
#include"pose2d.h"
#include"joint_state.h"
#include"robot_command.h"
#include"robot_utils.h"

void printSimulationHeader();
void printSimulationSetup(const double dt, int commandCount);
void printPose(const Pose2D& pose);
void printInitialPose(const std::vector<Pose2D>& trajectory);
void printFinalPose(const std::vector<Pose2D>& trajectory);
void printTrajectoryCount(const std::vector<Pose2D>& trajectory);
void printSelectedTrajectory(const std::vector<Pose2D>& trajectory, int sampleInterval);
void printValidationReport(const SimInput& inputCheck, double dt, const std::vector<RobotCommand>& commands, const std::vector<Pose2D>& trajectory);
void printSimulationSummary(double dt, const std::vector<RobotCommand>& commands,const std::vector<Pose2D>& trajectory, const Pose2D& targetPose);
void printJointStates(const std::vector<JointState>& joints);
