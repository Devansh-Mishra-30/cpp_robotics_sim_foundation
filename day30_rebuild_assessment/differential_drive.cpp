#include "differential_drive.h"

RobotCommand convertWheelCommandToRobotCommand(const WheelCommand& wheelCommand, 
	double wheelRadius,
	double wheelBase
) {
	 
	const double v = 
		 wheelRadius * (wheelCommand.leftWheelSpeed + wheelCommand.rightWheelSpeed) / 2.0;
	 
	const double omega = 
		 wheelRadius * (wheelCommand.rightWheelSpeed - wheelCommand.leftWheelSpeed) / wheelBase;
	 
	return { v, omega };
}