#include "machine_code.h"

#include <array>
#include <fstream>
#include <stdexcept>
#include <string>

namespace uvm {
namespace {

constexpr unsigned bits_per_byte = 8;
using Bytes = std::array<unsigned char, instruction_size>;

Bytes encode(const Instruction& instruction) {
    const auto word = static_cast<std::uint32_t>(instruction.opcode) | (instruction.operand << opcode_width);
    Bytes bytes{};
    for (std::size_t index = 0; index < bytes.size(); ++index) {
        bytes[index] = static_cast<unsigned char>(word >> (index * bits_per_byte));
    }
    return bytes;
}

Instruction decode(const Bytes& bytes) {
    std::uint32_t word = 0;
    for (std::size_t index = 0; index < bytes.size(); ++index) {
        word |= static_cast<std::uint32_t>(bytes[index]) << (index * bits_per_byte);
    }
    const auto opcode = static_cast<Opcode>(word & bit_mask(opcode_width));
    const auto* operation = find_operation(opcode);
    if (operation == nullptr) {
        throw std::runtime_error("unknown opcode " + std::to_string(static_cast<std::uint32_t>(opcode)));
    }
    const auto operand = word >> opcode_width;
    if (operand > bit_mask(operation->operand_width)) {
        throw std::runtime_error("nonzero reserved bits");
    }
    return {opcode, operand};
}

void print_bytes(std::ostream& output, const Bytes& bytes) {
    constexpr char hex[] = "0123456789ABCDEF";
    const char* separator = "";
    for (const auto byte : bytes) {
        output << separator << "0x" << hex[byte >> 4] << hex[byte & 0x0F];
        separator = ", ";
    }
    output << '\n';
}

}

void write_machine_code(const std::filesystem::path& path, const std::vector<Instruction>& program,
                        std::ostream* trace) {
    std::ofstream output(path, std::ios::binary);
    if (!output) {
        throw std::runtime_error("cannot open binary output '" + path.u8string() + "'");
    }
    for (const auto& instruction : program) {
        const auto bytes = encode(instruction);
        output.write(reinterpret_cast<const char*>(bytes.data()), instruction_size);
        if (trace != nullptr) {
            print_bytes(*trace, bytes);
        }
    }
    output.close();
    if (!output) {
        throw std::runtime_error("cannot write binary output '" + path.u8string() + "'");
    }
}

std::optional<Instruction> read_instruction(std::istream& input) {
    Bytes bytes{};
    if (input.read(reinterpret_cast<char*>(bytes.data()), instruction_size)) {
        return decode(bytes);
    }
    if (input.bad() || !input.eof()) {
        throw std::runtime_error("cannot read binary file");
    }
    if (input.gcount() != 0) {
        throw std::runtime_error("truncated instruction");
    }
    return std::nullopt;
}

}
