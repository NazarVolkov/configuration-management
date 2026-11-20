#include "app.h"

#include <fstream>
#include <regex>
#include <stdexcept>

#include <json.hpp>

using nlohmann::json;

bool valid_name(const std::string& name, bool test_mode) {
    static const std::regex test_pattern("[A-Z]+");
    static const std::regex nuget_pattern("[A-Za-z0-9_]+([.-][A-Za-z0-9_]+)*");
    return std::regex_match(name, test_mode ? test_pattern : nuget_pattern);
}

bool valid_url(const std::string& url) {
    static const std::regex pattern(R"(https?://[A-Za-z0-9.-]+(:[0-9]+)?([/?][^\s#]*)?)");
    return std::regex_match(url, pattern);
}

template <typename T>
T field(const json& data, const char* name) {
    if (!data.contains(name)) {
        throw std::runtime_error(std::string("Missing setting: ") + name);
    }
    try {
        return data.at(name).get<T>();
    } catch (const json::exception&) {
        throw std::runtime_error(std::string("Invalid type for setting: ") + name);
    }
}

void check_source(Settings& settings, const std::filesystem::path& folder) {
    if (!valid_name(settings.package, settings.test_mode)) {
        throw std::runtime_error("Invalid package name.");
    }
    if (!settings.test_mode) {
        if (!valid_url(settings.repository)) {
            throw std::runtime_error("repository must be an HTTP(S) URL.");
        }
        return;
    }
    settings.test_file = folder / std::filesystem::u8path(settings.repository);
    if (!std::filesystem::is_regular_file(settings.test_file)) {
        throw std::runtime_error("Test repository file not found: " + settings.repository);
    }
}

Settings load_settings(const std::filesystem::path& file) {
    std::ifstream input(file, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Cannot open configuration: " + file.u8string());
    }
    const auto data = json::parse(input);
    if (!data.is_object()) {
        throw std::runtime_error("Configuration must be a JSON object.");
    }
    Settings settings{field<std::string>(data, "package"),
                      field<std::string>(data, "repository"), {},
                      field<bool>(data, "test_mode"), field<bool>(data, "ascii_tree"),
                      data.value("version", std::string{}), data.value("framework", std::string{"net8.0"})};
    for (const auto& item : data.items()) {
        const auto& name = item.key();
        if (name != "package" && name != "repository" && name != "test_mode" &&
            name != "ascii_tree" && name != "version" && name != "framework") {
            throw std::runtime_error("Unknown setting: " + name);
        }
    }
    check_source(settings, file.parent_path());
    if (!settings.version.empty() && !stable_version(settings.version)) {
        throw std::runtime_error("version must be a stable numeric version.");
    }
    if (settings.framework.find_first_not_of(" \r\n\t") == std::string::npos) {
        throw std::runtime_error("framework must not be empty.");
    }
    return settings;
}

void print_settings(const Settings& settings, std::ostream& output) {
    output << "package = " << settings.package << '\n'
           << "repository = " << settings.repository << '\n'
           << "test_mode = " << std::boolalpha << settings.test_mode << '\n'
           << "ascii_tree = " << settings.ascii_tree << '\n'
           << "version = " << settings.version << '\n'
           << "framework = " << settings.framework << '\n';
}
