#pragma once

#include <string>

struct ValidationResult {
	std::string testName;
	bool passed{};
	double actualValue{};
	double expectedValue{};
	double tolerance{};
};
