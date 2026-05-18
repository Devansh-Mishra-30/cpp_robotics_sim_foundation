#pragma once
#include <string>
struct JointState {
	std::string name;
	double position{};
	double velocity{};
};