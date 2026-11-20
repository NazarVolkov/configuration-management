#pragma once

#include <filesystem>
#include <iosfwd>
#include <string>

struct Settings {
    std::string package;
    std::string repository;
    std::filesystem::path test_file;
    bool test_mode;
    bool ascii_tree;
    std::string version;
    std::string framework;
};

bool valid_name(const std::string& name, bool test_mode);
bool valid_url(const std::string& url);
bool stable_version(const std::string& version);
Settings load_settings(const std::filesystem::path& file);
void print_settings(const Settings& settings, std::ostream& output);
