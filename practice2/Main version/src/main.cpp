#include "app.h"

#include <iostream>
#include <stdexcept>
#include <string_view>

int wmain(int argc, wchar_t* argv[]) {
    try {
        if (argc > 2) {
            throw std::runtime_error("Usage: run.bat [config.json]");
        }
        const auto file = argc == 2 ? std::filesystem::path(argv[1]) : std::filesystem::path(L"config.json");
        print_settings(load_settings(file), std::cout);
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
