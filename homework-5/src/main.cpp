#include "evaluator.h"
#include "parser.h"
#include "toml.h"

#include <Windows.h>

#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>

namespace {

constexpr auto usage = "Usage: cfg5.exe (--input | -i) <file>\n       cfg5.exe (--help | -h)\n";

void validate_utf8(const std::string& source) {
    if (source.empty()) {
        return;
    }
    if (source.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        throw std::runtime_error("input file is too large");
    }
    const auto size = static_cast<int>(source.size());
    if (!MultiByteToWideChar(CP_UTF8, MB_ERR_INVALID_CHARS, source.data(), size, nullptr, 0)) {
        throw std::runtime_error("input must be valid UTF-8");
    }
}

std::string read_input(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open input file: " + path.u8string());
    }
    std::string source(std::istreambuf_iterator<char>{input}, std::istreambuf_iterator<char>{});
    validate_utf8(source);
    return source;
}

int translate(const std::filesystem::path& path) {
    try {
        const auto source = read_input(path);
        const auto declarations = parse_document(source);
        const auto bindings = evaluate_document(declarations);
        std::cout << render_toml(bindings) << std::flush;
        if (!std::cout) {
            throw std::runtime_error("cannot write TOML to standard output");
        }
        return 0;
    } catch (const SourceError& error) {
        std::cerr << path.u8string() << ':' << error.position.line << ':' << error.position.column
                  << ": error: " << error.what() << '\n';
        return 1;
    }
}

int run(int argc, wchar_t* argv[]) {
    if (argc == 2 && (std::wstring_view(argv[1]) == L"--help" || std::wstring_view(argv[1]) == L"-h")) {
        std::cout << usage;
        return 0;
    }
    if (argc == 3 && (std::wstring_view(argv[1]) == L"--input" || std::wstring_view(argv[1]) == L"-i")) {
        return translate(argv[2]);
    }
    std::cerr << "error: expected --input <file>\n" << usage;
    return 2;
}

}  // namespace

int wmain(int argc, wchar_t* argv[]) {
    try {
        return run(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
