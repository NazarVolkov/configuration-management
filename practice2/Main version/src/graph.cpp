#include "app.h"

#include <fstream>
#include <stdexcept>

#include <json.hpp>

namespace {
void visit(const std::string& node, const Fetch& fetch, Graph& graph) {
    if (graph.find(node) != graph.end()) {
        return;
    }
    // Register the node before following its outgoing edges: cycles end here.
    const auto& children = graph.emplace(node, fetch(node)).first->second;
    for (const auto& child : children) {
        visit(child, fetch, graph);
    }
}

void check_links(const Graph& graph) {
    for (const auto& [name, children] : graph) {
        if (!valid_name(name, true)) {
            throw std::runtime_error("Test package needs uppercase Latin letters: " + name);
        }
        for (const auto& child : children) {
            if (graph.find(child) == graph.end()) {
                throw std::runtime_error("No definition for test package: " + child);
            }
        }
    }
}
}  // namespace

Graph load_test_graph(const Settings& settings) {
    std::ifstream input(settings.test_file, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Cannot open test repository.");
    }
    const auto data = nlohmann::json::parse(input);
    if (!data.is_object() || data.empty()) {
        throw std::runtime_error("Test repository needs a nonempty JSON object.");
    }
    auto graph = data.get<Graph>();
    check_links(graph);
    if (graph.find(settings.package) == graph.end()) {
        throw std::runtime_error("Package not in the test repository: " + settings.package);
    }
    return graph;
}

Graph build_graph(const std::string& root, const Fetch& fetch) {
    Graph graph;
    visit(root, fetch, graph);
    return graph;
}

void print_graph(const Graph& graph, std::ostream& output) {
    for (const auto& [name, children] : graph) {
        output << name << " ->";
        if (children.empty()) {
            output << " -";
        }
        for (const auto& child : children) {
            output << " " << child;
        }
        output << '\n';
    }
}

Graph reverse_graph(const Graph& graph, const std::string& target) {
    if (graph.find(target) == graph.end()) {
        throw std::runtime_error("Reverse target not in graph: " + target);
    }
    Graph reversed;
    for (const auto& [name, children] : graph) {
        reversed.try_emplace(name);
        for (const auto& child : children) {
            reversed[child].push_back(name);
        }
    }
    return build_graph(target, [&](const std::string& node) { return reversed.at(node); });
}
