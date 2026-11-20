#include "app.h"

#include <array>
#include <cctype>
#include <regex>
#include <sstream>
#include <stdexcept>

namespace {
using Version = std::array<unsigned long, 4>;

struct Range {
    std::string lower;
    std::string upper;
    bool include_lower;
    bool include_upper;
};

Version key(const std::string& value) {
    if (!stable_version(value)) {
        throw std::runtime_error("Unsupported version: " + value);
    }
    Version result{};
    std::istringstream stream(value);
    std::string part;
    for (auto& number : result) {
        if (std::getline(stream, part, '.')) {
            number = std::stoul(part);
        }
    }
    return result;
}

std::string compact(const std::string& value) {
    std::string result;
    for (const unsigned char character : value) {
        if (!std::isspace(character)) {
            result += static_cast<char>(character);
        }
    }
    return result;
}

bool valid_bound(const std::string& bound) {
    return bound.empty() || stable_version(bound);
}

Range parse_interval(const std::string& text, std::size_t comma) {
    if ((text.front() != '[' && text.front() != '(') ||
        (text.back() != ']' && text.back() != ')')) {
        throw std::runtime_error("Unsupported version range: " + text);
    }
    const auto lower = text.substr(1, comma - 1);
    const auto upper = text.substr(comma + 1, text.size() - comma - 2);
    if (!valid_bound(lower) || !valid_bound(upper)) {
        throw std::runtime_error("Unsupported version range: " + text);
    }
    return {lower, upper, text.front() == '[', text.back() == ']'};
}

Range parse_range(const std::string& raw) {
    const auto text = compact(raw);
    if (text.empty() || stable_version(text)) {
        return {text, {}, true, false};
    }
    const auto comma = text.find(',');
    if (comma != std::string::npos) {
        return parse_interval(text, comma);
    }
    if (text.front() == '[' && text.back() == ']') {
        const auto exact = text.substr(1, text.size() - 2);
        key(exact);
        return {exact, exact, true, true};
    }
    throw std::runtime_error("Unsupported version range: " + raw);
}

bool matches(const Version& version, const Range& range) {
    if (!range.lower.empty()) {
        const auto minimum = key(range.lower);
        if (version < minimum || (version == minimum && !range.include_lower)) {
            return false;
        }
    }
    if (!range.upper.empty()) {
        const auto maximum = key(range.upper);
        if (version > maximum || (version == maximum && !range.include_upper)) {
            return false;
        }
    }
    return true;
}
}  // namespace

bool stable_version(const std::string& version) {
    static const std::regex pattern(R"([0-9]{1,9}(\.[0-9]{1,9}){0,3})");
    return std::regex_match(version, pattern);
}

std::string choose_version(const std::vector<std::string>& versions, const std::string& range, bool latest) {
    const auto bounds = parse_range(range);
    std::string selected;
    for (const auto& candidate : versions) {
        if (!stable_version(candidate) || !matches(key(candidate), bounds)) {
            continue;
        }
        if (selected.empty() || (latest ? key(candidate) > key(selected) : key(candidate) < key(selected))) {
            selected = candidate;
        }
    }
    if (selected.empty()) {
        throw std::runtime_error("No stable version matches: " + range);
    }
    return selected;
}
