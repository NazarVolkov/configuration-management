#pragma once

#include <cstdint>
#include <filesystem>

namespace uvm {

struct AddressRange {
    std::uint32_t first;
    std::uint32_t last;
};

void interpret(const std::filesystem::path& binary, const std::filesystem::path& dump, AddressRange range);

}
