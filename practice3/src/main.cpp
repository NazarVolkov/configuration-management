#include "assembler.h"

#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {

using Arguments = std::vector<std::filesystem::path>;

void print_help(std::ostream& output) {
    output << "Usage:\n  uvm assemble <source.yaml> <output.bin> [--test]\n  uvm --help\n";
}

void assemble(const Arguments& args) {
    if (args.size() < 3 || args.size() > 4 || (args.size() == 4 && args[3] != "--test")) {
        throw std::runtime_error("invalid arguments for assemble");
    }
    const auto program = uvm::read_assembly(args[1]);
    if (args.size() == 4) {
        for (const auto& instruction : program) {
            std::cout << "A=" << static_cast<std::uint32_t>(instruction.opcode) << ", B="
                      << instruction.operand << '\n';
        }
    }
}

int run(const Arguments& args) {
    if (args.size() == 1 && args[0] == "--help") {
        print_help(std::cout);
        return 0;
    }
    if (args.empty() || args[0] != "assemble") {
        print_help(std::cerr);
        return 1;
    }
    assemble(args);
    return 0;
}

}

#ifdef _WIN32
int wmain(int argc, wchar_t* argv[]) {
#else
int main(int argc, char* argv[]) {
#endif
    try {
        return run(Arguments(argv + 1, argv + argc));
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }
}
