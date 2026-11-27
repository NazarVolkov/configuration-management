#include "toml.h"

#include <charconv>
#include <stdexcept>
#include <string_view>

namespace {

void append_string(std::string& output, std::string_view text) {
    constexpr std::string_view hex = "0123456789ABCDEF";
    output += '"';
    for (const unsigned char character : text) {
        if (character == '"' || character == '\\') {
            output += '\\';
        }
        if (character < 0x20 || character == 0x7F) {
            output += "\\u00";
            output += hex[character >> 4];
            output += hex[character & 0x0F];
        } else {
            output += static_cast<char>(character);
        }
    }
    output += '"';
}

void append_number(std::string& output, const Number& number) {
    if (const auto integer = std::get_if<Integer>(&number)) {
        output += std::to_string(*integer);
        return;
    }
    char buffer[64];
    const auto result = std::to_chars(buffer, buffer + sizeof(buffer), std::get<double>(number));
    if (result.ec != std::errc{}) {
        throw std::logic_error("cannot format floating-point value");
    }
    const std::string_view spelling(buffer, result.ptr - buffer);
    output += spelling;
    if (spelling.find_first_of(".eE") == std::string_view::npos) {
        output += ".0";
    }
}

void append_value(std::string& output, const Value& value);

void append_array(std::string& output, const Value::Array& array) {
    output += '[';
    std::string_view separator;
    for (const auto& value : array) {
        output += separator;
        append_value(output, value);
        separator = ", ";
    }
    output += ']';
}

void append_value(std::string& output, const Value& value) {
    if (const auto number = std::get_if<Number>(&value.data)) {
        append_number(output, *number);
    } else if (const auto text = std::get_if<std::string>(&value.data)) {
        append_string(output, *text);
    } else {
        append_array(output, std::get<Value::Array>(value.data));
    }
}

}  // namespace

std::string render_toml(const std::vector<Binding>& bindings) {
    std::string output;
    for (const auto& binding : bindings) {
        output += binding.name;
        output += " = ";
        append_value(output, binding.value);
        output += '\n';
    }
    return output;
}
