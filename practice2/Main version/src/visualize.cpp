#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <shellapi.h>
#include <process.h>

#include "app.h"

#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <set>
#include <stdexcept>

namespace {
struct Tree {
    const Graph& graph;
    std::ostringstream output;
    std::set<std::string> active;
    std::set<std::string> shown;

    explicit Tree(const Graph& data) : graph(data) {}

    void draw(const std::string& name, const std::string& indent, const std::string& branch) {
        output << indent << branch << name;
        if (active.count(name)) {
            output << " [cycle]\n";
            return;
        }
        if (!shown.insert(name).second) {
            output << " [shown]\n";
            return;
        }

        output << '\n';
        active.insert(name);
        auto next_indent = indent;
        if (!branch.empty()) {
            next_indent += branch == "`-- " ? "    " : "|   ";
        }
        const auto& children = graph.at(name);
        for (auto it = children.begin(); it != children.end(); ++it) {
            draw(*it, next_indent, it + 1 == children.end() ? "`-- " : "+-- ");
        }
        active.erase(name);
    }
};

std::string diagram_label(const std::string& node) {
    const auto at = node.find('@');
    if (at == std::string::npos) {
        return node;
    }
    constexpr std::size_t line_limit = 24;
    std::istringstream words(node.substr(0, at));
    std::string label;
    std::string word;
    std::size_t width = 0;
    while (std::getline(words, word, '.')) {
        if (width && width + word.size() > line_limit) {
            label += "\\n";
            width = 0;
        }
        label += word;
        width += word.size();
        if (!words.eof()) {
            label += '.';
            ++width;
        }
    }
    return label + "\\n" + node.substr(at + 1);
}
}  // namespace

std::string ascii_tree(const Graph& graph, const std::string& root) {
    Tree result(graph);
    result.draw(root, "", "");
    return result.output.str();
}

std::string plantuml(const Graph& graph) {
    std::ostringstream text;
    text << "@startuml\n!pragma layout smetana\nleft to right direction\n";
    text << "skinparam backgroundColor white\nskinparam defaultFontName Arial\nskinparam padding 10\n";
    std::map<std::string, std::string> aliases;
    std::size_t index = 0;
    for (const auto& node : graph) {
        const auto alias = "P" + std::to_string(index++);
        aliases.emplace(node.first, alias);
        text << "rectangle \"" << diagram_label(node.first) << "\" as " << alias << '\n';
    }
    for (const auto& [node, children] : graph) {
        for (const auto& child : children) {
            text << aliases.at(node) << " --> " << aliases.at(child) << '\n';
        }
    }
    text << "@enduml\n";
    return text.str();
}

std::filesystem::path save_diagram(const Graph& graph, const std::string& root) {
    auto name = root;
    std::replace(name.begin(), name.end(), '@', '_');
    std::filesystem::create_directories("output");
    const auto source = std::filesystem::path("output") / ("graph_" + name + ".puml");
    std::ofstream output(source, std::ios::binary);
    output << plantuml(graph);
    output.close();
    if (!output) {
        throw std::runtime_error("Cannot write PlantUML file.");
    }
    return source;
}

namespace {
std::filesystem::path find_java() {
    wchar_t buffer[32768];
    auto size = GetEnvironmentVariableW(L"JAVA_HOME", buffer, 32768);
    if (size > 0 && size < 32768) {
        const auto java = std::filesystem::path(buffer) / L"bin" / L"java.exe";
        if (std::filesystem::is_regular_file(java)) {
            return java;
        }
    }
    size = SearchPathW(nullptr, L"java.exe", nullptr, 32768, buffer, nullptr);
    if (size > 0 && size < 32768) {
        return buffer;
    }
    throw std::runtime_error("Java not found. Install Java or use --no-image.");
}

void prepare_plantuml() {
    const auto jar = std::filesystem::path("build/deps/plantuml.jar");
    if (std::filesystem::is_regular_file(jar)) {
        return;
    }
    const auto data = download("https://github.com/plantuml/plantuml/releases/"
                               "download/v1.2024.8/plantuml-1.2024.8.jar");
    std::filesystem::create_directories(jar.parent_path());
    std::ofstream file("build/deps/plantuml.tmp", std::ios::binary);
    file.write(data.data(), static_cast<std::streamsize>(data.size()));
    file.close();
    if (!file) {
        throw std::runtime_error("Cannot save PlantUML.");
    }
    std::filesystem::rename("build/deps/plantuml.tmp", jar);
}
}  // namespace

void render_png(const std::filesystem::path& source, bool open_image) {
    const auto java = find_java();
    prepare_plantuml();
    const wchar_t* arguments[] = {L"java.exe", L"-Djava.awt.headless=true", L"-jar",
        L"build/deps/plantuml.jar", L"-charset", L"UTF-8", L"-tpng", source.c_str(), nullptr};
    const auto status = _wspawnv(_P_WAIT, java.c_str(), arguments);
    auto image = source;
    image.replace_extension(".png");
    if (status != 0 || !std::filesystem::is_regular_file(image)) {
        throw std::runtime_error("PlantUML failed. Check Java installation.");
    }
    std::cout << "PNG: " << image.u8string() << '\n';
    if (open_image) {
        const auto full = std::filesystem::absolute(image);
        const auto result = ShellExecuteW(nullptr, L"open", full.c_str(), nullptr, nullptr, SW_SHOWNORMAL);
        if (reinterpret_cast<INT_PTR>(result) <= 32) {
            throw std::runtime_error("Cannot open graph image. Open the PNG from output.");
        }
    }
}
