#pragma once

#include "robot_command.h"

struct WheelCommand {
	double leftWheelSpeed{};
	double rightWheelSpeed{};
};

RobotCommand convertWheelCommandToRobotCommand(
	const WheelCommand& wheelCommand,
	double wheelRadius,
	double wheelBase
);

WheelCommand convertRobotCommandToWheelCommand(
	const RobotCommand& robotCommand,
	double wheelRadius,
	double wheelBase
);
