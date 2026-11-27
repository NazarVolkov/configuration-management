#include "assembler.h"

#include <charconv>
#include <fstream>
#include <stdexcept>
#include <string>

namespace uvm {
namespace {

std::string_view trim(std::string_view text) {
    const auto first = text.find_first_not_of(" \t\r");
    if (first == std::string_view::npos) {
        return {};
    }
    return text.substr(first, text.find_last_not_of(" \t\r") - first + 1);
}

std::string_view remove_comment(std::string_view line) {
    const auto marker = line.find('#');
    if (marker == 0 || (marker != std::string_view::npos && (line[marker - 1] == ' ' || line[marker - 1] == '\t'))) {
        return line.substr(0, marker);
    }
    return line;
}

std::uint32_t parse_operand(std::string_view text, const Operation& operation) {
    if (text.empty()) {
        throw std::runtime_error("missing operand for " + std::string(operation.name));
    }
    std::uint32_t operand = 0;
    const auto end = text.data() + text.size();
    const auto result = std::from_chars(text.data(), end, operand);
    if (result.ec != std::errc{} || result.ptr != end || operand > bit_mask(operation.operand_width)) {
        throw std::runtime_error("expected an integer in 0.." + std::to_string(bit_mask(operation.operand_width)));
    }
    return operand;
}

Instruction parse_instruction(std::string_view line) {
    if (line.substr(0, 2) != "- ") {
        throw std::runtime_error("expected a YAML sequence item starting with '- '");
    }
    line.remove_prefix(2);
    const auto separator = line.find(':');
    if (separator == std::string_view::npos || line.substr(separator + 1, 1) != " ") {
        throw std::runtime_error("expected 'operation: operand'");
    }
    const auto name = trim(line.substr(0, separator));
    const auto* operation = find_operation(name);
    if (operation == nullptr) {
        throw std::runtime_error("unknown operation '" + std::string(name) + "'");
    }
    return {operation->opcode, parse_operand(trim(line.substr(separator + 1)), *operation)};
}

}

std::vector<Instruction> read_assembly(const std::filesystem::path& source) {
    std::ifstream input(source);
    if (!input) {
        throw std::runtime_error("cannot open source file '" + source.u8string() + "'");
    }
    std::vector<Instruction> program;
    std::string line;
    std::size_t line_number = 0;
    while (std::getline(input, line)) {
        ++line_number;
        std::string_view content = line;
        constexpr std::string_view utf8_bom = "\xEF\xBB\xBF";
        if (line_number == 1 && content.substr(0, utf8_bom.size()) == utf8_bom) {
            content.remove_prefix(utf8_bom.size());
        }
        content = remove_comment(content);
        if (trim(content).empty()) {
            continue;
        }
        try {
            program.push_back(parse_instruction(content));
        } catch (const std::runtime_error& error) {
            throw std::runtime_error(source.u8string() + ":" + std::to_string(line_number) + ": " + error.what());
        }
    }
    if (input.bad()) {
        throw std::runtime_error("cannot read source file '" + source.u8string() + "'");
    }
    if (program.empty()) {
        throw std::runtime_error("source file must contain at least one instruction");
    }
    return program;
}

}
