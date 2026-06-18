#pragma once

#include <string>

#include "differential_drive/differential_drive.h"
#include "differential_drive/pose2d.h"

struct SimulationScenario {
	std::string name;
	Pose2D initialPose;
	Pose2D targetPose;
	WheelCommand wheelCommand;
	double duration{};
};