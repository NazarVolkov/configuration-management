#include "interpreter.h"
#include "machine_code.h"

#include <cmath>
#include <fstream>
#include <iomanip>
#include <limits>
#include <locale>
#include <stdexcept>
#include <string>
#include <vector>

namespace uvm {
namespace {

constexpr auto last_address = bit_mask(address_width);
using Memory = std::vector<double>;
using Stack = std::vector<double>;

double pop(Stack& stack) {
    if (stack.empty()) {
        throw std::runtime_error("stack underflow");
    }
    const auto value = stack.back();
    stack.pop_back();
    return value;
}

std::uint32_t resolve_address(double base, std::uint32_t offset) {
    if (!std::isfinite(base) || base < 0 || base > last_address - offset || std::trunc(base) != base) {
        throw std::runtime_error("sqrt requires a whole base address with base + offset in 0..65535");
    }
    return static_cast<std::uint32_t>(base) + offset;
}

void execute(const Instruction& instruction, Memory& memory, Stack& stack) {
    switch (instruction.opcode) {
    case Opcode::push:
        stack.push_back(instruction.operand);
        break;
    case Opcode::load:
        stack.push_back(memory[instruction.operand]);
        break;
    case Opcode::store:
        memory[instruction.operand] = pop(stack);
        break;
    case Opcode::sqrt: {
        const auto operand = pop(stack);
        const auto address = resolve_address(pop(stack), instruction.operand);
        memory[address] = std::sqrt(operand);
        break;
    }
    }
}

Memory execute_program(const std::filesystem::path& binary) {
    std::ifstream input(binary, std::ios::binary);
    if (!input) {
        throw std::runtime_error("cannot open binary file '" + binary.u8string() + "'");
    }
    Memory memory(last_address + 1);
    Stack stack;
    std::size_t offset = 0;
    try {
        while (const auto instruction = read_instruction(input)) {
            execute(*instruction, memory, stack);
            offset += instruction_size;
        }
    } catch (const std::runtime_error& error) {
        throw std::runtime_error("at byte " + std::to_string(offset) + ": " + error.what());
    }
    return memory;
}

void write_dump(const std::filesystem::path& dump, const Memory& memory, AddressRange range) {
    std::ofstream output(dump);
    if (!output) {
        throw std::runtime_error("cannot open memory dump '" + dump.u8string() + "'");
    }
    output.imbue(std::locale::classic());
    output << "address,value\n" << std::setprecision(std::numeric_limits<double>::max_digits10);
    for (auto address = range.first; address <= range.last; ++address) {
        output << address << ',' << memory[address] << '\n';
    }
    output.close();
    if (!output) {
        throw std::runtime_error("cannot write memory dump '" + dump.u8string() + "'");
    }
}

}

void interpret(const std::filesystem::path& binary, const std::filesystem::path& dump, AddressRange range) {
    if (range.first > range.last || range.last > last_address) {
        throw std::runtime_error("expected an increasing or single-address range within 0..65535");
    }
    write_dump(dump, execute_program(binary), range);
}

}
