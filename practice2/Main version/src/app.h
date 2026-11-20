#pragma once

#include <filesystem>
#include <functional>
#include <iosfwd>
#include <map>
#include <string>
#include <vector>


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


using Packages = std::vector<std::string>;
using Requirements = std::vector<std::pair<std::string, std::string>>;

std::string download(const std::string& url);
std::string lower_name(std::string value);
std::string choose_version(const Packages& versions, const std::string& range, bool latest = false);
Requirements read_dependencies(const std::string& xml, const std::string& framework);

class Nuget {
public:
    explicit Nuget(const Settings& settings);
    std::string root(const Settings& settings);
    Packages dependencies(const std::string& package);

private:
    std::string base_;
    std::string framework_;
    std::map<std::string, Packages> versions_;
    std::map<std::string, Packages> dependencies_;
    const Packages& versions(const std::string& id);
};


using Graph = std::map<std::string, Packages>;
using Fetch = std::function<Packages(const std::string&)>;

Graph load_test_graph(const Settings& settings);
Graph build_graph(const std::string& root, const Fetch& fetch);
void print_graph(const Graph& graph, std::ostream& output);

Graph reverse_graph(const Graph& graph, const std::string& target);

std::string ascii_tree(const Graph& graph, const std::string& root);
std::string plantuml(const Graph& graph);
std::filesystem::path save_diagram(const Graph& graph, const std::string& root);
void render_png(const std::filesystem::path& source, bool open_image);
