#pragma once

#include <cstddef>
#include <stdexcept>
#include <string>
#include <vector>

struct Position {
    std::size_t line;
    std::size_t column;
};

class SourceError : public std::runtime_error {
public:
    SourceError(Position position, const std::string& message) : std::runtime_error(message), position(position) {}

    const Position position;
};

enum class Kind {
    number, string, array, reference, addition, subtraction, multiplication, maximum, square_root,
};

struct Expression {
    Kind kind;
    Position position;
    std::string text;
    std::vector<Expression> children;
};

struct Declaration {
    std::string name;
    Position position;
    Expression expression;
};
