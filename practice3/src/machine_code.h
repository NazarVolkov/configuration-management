#pragma once

#include "instruction.h"

#include <cstddef>
#include <filesystem>
#include <iosfwd>
#include <optional>
#include <vector>

namespace uvm {

constexpr std::size_t instruction_size = 4;

void write_machine_code(const std::filesystem::path& path, const std::vector<Instruction>& program,
                        std::ostream* trace);
std::optional<Instruction> read_instruction(std::istream& input);

}
