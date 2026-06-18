#include "differential_drive/differential_drive.h"

RobotCommand convertWheelCommandToRobotCommand(
	const WheelCommand& wheelCommand,
	double wheelRadius,
	double wheelBase
) {
	const double v = 
		wheelRadius * (wheelCommand.rightWheelSpeed + wheelCommand.leftWheelSpeed) / 2.0;
	const double omega = 
		wheelRadius * (wheelCommand.rightWheelSpeed - wheelCommand.leftWheelSpeed) / wheelBase;
	return { v, omega };
}

WheelCommand convertRobotCommandToWheelCommand(
	const RobotCommand& robotCommand,
	double wheelRadius,
	double wheelBase
) {
	const double leftWheelSpeed =
		(robotCommand.v - (robotCommand.omega * wheelBase / 2.0)) / wheelRadius;
	const double rightWheelSpeed =
		(robotCommand.v + (robotCommand.omega * wheelBase / 2.0)) / wheelRadius;

	return { leftWheelSpeed, rightWheelSpeed };
}