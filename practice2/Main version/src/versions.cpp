#include "app.h"
#include <regex>

bool stable_version(const std::string& version) {
    static const std::regex pattern(R"([0-9]{1,9}(\.[0-9]{1,9}){0,3})");
    return std::regex_match(version, pattern);
}
