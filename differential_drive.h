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
