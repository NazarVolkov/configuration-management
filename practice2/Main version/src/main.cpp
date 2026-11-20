#include "app.h"

#include <iostream>
#include <stdexcept>
#include <string_view>

namespace {
enum class Stage { settings, direct, graph, reverse, visualize };

constexpr const char* usage =
    "Usage: run.bat [config.json] [--stage 1|2|3|4|5] [--reverse package] [--no-image] [--no-open]";

struct Arguments {
    std::filesystem::path file = L"config.json";
    Stage stage = Stage::graph;
    std::string target;
    bool no_image = false;
    bool no_open = false;
};

Stage parse_stage(std::wstring_view value) {
    if (value == L"1") {
        return Stage::settings;
    }
    if (value == L"2") {
        return Stage::direct;
    }
    if (value == L"3") {
        return Stage::graph;
    }
    if (value == L"4") {
        return Stage::reverse;
    }
    if (value == L"5") {
        return Stage::visualize;
    }
    throw std::runtime_error("--stage requires 1, 2, 3, 4 or 5.");
}

struct Cursor {
    int count;
    wchar_t** values;
    int next = 1;

    bool more() const { return next < count; }

    const wchar_t* value() {
        if (!more() || values[next][0] == L'-' || !values[next][0]) {
            throw std::runtime_error("Option needs a value.");
        }
        return values[next++];
    }
};

void read_option(const std::wstring_view flag, Cursor& cursor, Arguments& args) {
    if (flag == L"--stage") {
        args.stage = parse_stage(cursor.value());
    } else if (flag == L"--reverse") {
        args.target = std::filesystem::path(cursor.value()).u8string();
    } else if (flag == L"--no-image") {
        args.no_image = true;
    } else if (flag == L"--no-open") {
        args.no_open = true;
    } else {
        throw std::runtime_error(usage);
    }
}

Arguments parse_arguments(int argc, wchar_t* argv[]) {
    Cursor cursor{argc, argv};
    Arguments result;
    if (cursor.more() && argv[cursor.next][0] != L'-') {
        result.file = cursor.value();
    }
    while (cursor.more()) {
        const std::wstring_view flag = argv[cursor.next++];
        read_option(flag, cursor, result);
    }
    if (!result.target.empty() && result.stage != Stage::reverse) {
        throw std::runtime_error("--reverse is only available at stage 4.");
    }
    return result;
}

void print_direct(const std::string& root, const Packages& dependencies) {
    std::cout << root << '\n';
    for (const auto& dependency : dependencies) {
        std::cout << "  " << dependency << '\n';
    }
}

void analyze(const Arguments& args, const std::string& root, const Fetch& fetch, const Graph* test_graph = nullptr) {
    if (args.stage == Stage::direct) {
        print_direct(root, fetch(root));
    } else if (args.stage == Stage::graph) {
        print_graph(build_graph(root, fetch), std::cout);
    } else if (args.stage == Stage::reverse) {
        const auto target = args.target.empty() ? root : args.target;
        const auto graph = test_graph ? reverse_graph(*test_graph, target)
                                      : reverse_graph(build_graph(root, fetch), lower_name(target));
        print_graph(graph, std::cout);
    } else {
        throw std::runtime_error("Stage not implemented yet.");
    }
}

void run(const Arguments& args) {
    const auto settings = load_settings(args.file);
    if (args.stage == Stage::settings) {
        print_settings(settings, std::cout);
    } else if (settings.test_mode) {
        const auto graph = load_test_graph(settings);
        analyze(args, settings.package, [&](const std::string& node) { return graph.at(node); }, &graph);
    } else {
        Nuget repository(settings);
        const auto root = repository.root(settings);
        analyze(args, root, [&](const std::string& node) { return repository.dependencies(node); });
    }
}
}  // namespace

int wmain(int argc, wchar_t* argv[]) {
    try {
        if (argc == 2 && std::wstring_view(argv[1]) == L"--help") {
            std::cout << usage << '\n';
            return 0;
        }
        run(parse_arguments(argc, argv));
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
