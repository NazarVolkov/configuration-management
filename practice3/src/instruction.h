#pragma once

#include <cstdint>
#include <string_view>

namespace uvm {

constexpr unsigned opcode_width = 4;
constexpr unsigned address_width = 16;
constexpr unsigned constant_width = 26;

constexpr std::uint32_t bit_mask(unsigned width) {
    return (std::uint32_t{1} << width) - 1;
}

enum class Opcode : std::uint32_t {
    push = 14,
    load = 6,
    store = 3,
    sqrt = 11
};

struct Operation {
    std::string_view name;
    Opcode opcode;
    unsigned operand_width;
};

struct Instruction {
    Opcode opcode;
    std::uint32_t operand;
};

const Operation* find_operation(std::string_view name);

}
