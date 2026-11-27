#pragma once

#include "instruction.h"

#include <filesystem>
#include <vector>

namespace uvm {

std::vector<Instruction> read_assembly(const std::filesystem::path& source);

}
