#include "instruction.h"

namespace uvm {
namespace {

constexpr Operation operations[] = {
    {"push", Opcode::push, constant_width},
    {"load", Opcode::load, address_width},
    {"store", Opcode::store, address_width},
    {"sqrt", Opcode::sqrt, address_width}
};

}

const Operation* find_operation(std::string_view name) {
    for (const auto& operation : operations) {
        if (operation.name == name) {
            return &operation;
        }
    }
    return nullptr;
}

}
