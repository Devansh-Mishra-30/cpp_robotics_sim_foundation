#pragma once

#include <string>

#include "differential_drive.h"
#include "pose2d.h"

struct SimulationScenario {
	std::string name;
	Pose2D initialPose;
	Pose2D targetPose;
	WheelCommand wheelCommand;
	double duration{};
};