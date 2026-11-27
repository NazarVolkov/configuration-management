#include "assembler.h"
#include "interpreter.h"
#include "machine_code.h"

#include <charconv>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using Arguments = std::vector<std::filesystem::path>;

void print_help(std::ostream& output) {
    output << "Usage:\n"
           << "  uvm assemble <source.yaml> <output.bin> [--test | --test-fields]\n"
           << "  uvm interpret <input.bin> <dump.csv> <first-address> <last-address>\n"
           << "  uvm --help\n";
}

void assemble(const Arguments& args) {
    if (args.size() < 3 || args.size() > 4) {
        throw std::runtime_error("invalid arguments for assemble");
    }
    const auto mode = args.size() == 4 ? args[3] : std::filesystem::path{};
    if (args.size() == 4 && mode != "--test" && mode != "--test-fields") {
        throw std::runtime_error("expected --test or --test-fields");
    }
    const auto program = uvm::read_assembly(args[1]);
    uvm::write_machine_code(args[2], program, mode == "--test" ? &std::cout : nullptr);
    if (mode == "--test-fields") {
        for (const auto& instruction : program) {
            std::cout << "A=" << static_cast<std::uint32_t>(instruction.opcode) << ", B="
                      << instruction.operand << '\n';
        }
    }
    std::cout << "Binary size: " << program.size() * uvm::instruction_size << " bytes\n";
}

std::uint32_t parse_address(const std::filesystem::path& arg) {
    const auto text = arg.u8string();
    const auto end = text.data() + text.size();
    std::uint32_t address = 0;
    const auto result = std::from_chars(text.data(), end, address);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw std::runtime_error("invalid address '" + text + "'");
    }
    return address;
}

int run(const Arguments& args) {
    if (args.size() == 1 && args[0] == "--help") {
        print_help(std::cout);
        return 0;
    }
    if (!args.empty() && args[0] == "assemble") {
        assemble(args);
        return 0;
    }
    if (!args.empty() && args[0] == "interpret") {
        if (args.size() != 5) {
            throw std::runtime_error("interpret requires input file, dump file, first and last addresses");
        }
        uvm::interpret(args[1], args[2], {parse_address(args[3]), parse_address(args[4])});
        return 0;
    }
    print_help(std::cerr);
    return 1;
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
