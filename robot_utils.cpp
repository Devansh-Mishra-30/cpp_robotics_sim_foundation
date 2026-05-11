#include <cmath>
#include "robot_command.h"
#include "robot_utils.h"

double wrapToPi(double angle_rad) {
	return std::atan2(std::sin(angle_rad), std::cos(angle_rad));
}

bool isValidCommand(const RobotCommand& command) {
	return std::isfinite(command.v) && std::isfinite(command.omega);
}

bool isValidDt(double dt) {
	return std::isfinite(dt) && dt > 0.0;
}

SimInput validateSimulationInput(double dt, const std::vector<RobotCommand>& commands) 
{
	SimInput commandboolandIndex;
	commandboolandIndex.commandbool = true;
	commandboolandIndex.commandsindex = -1;

	if (!isValidDt(dt)) {
		commandboolandIndex.commandbool = false;
		commandboolandIndex.commandsindex = -2; //placeholder for error numbering
		return commandboolandIndex;
	}

	if (commands.empty()) {
		commandboolandIndex.commandbool = false;
		commandboolandIndex.commandsindex = -3; //placeholder for error numbering
		return commandboolandIndex;
	}

	for (size_t i = 0; i < commands.size(); i++) {
		if (!isValidCommand(commands[i])) {
			commandboolandIndex.commandbool = false;
			commandboolandIndex.commandsindex = static_cast<int>(i);
			return commandboolandIndex;
		}
	}
	return commandboolandIndex;
}

