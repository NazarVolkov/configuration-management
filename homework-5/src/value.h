#pragma once

#include <cstdint>
#include <string>
#include <variant>
#include <vector>

using Integer = std::int64_t;
using Number = std::variant<Integer, double>;

struct Value {
    using Array = std::vector<Value>;
    std::variant<Number, std::string, Array> data;
};

struct Binding {
    std::string name;
    Value value;
};
