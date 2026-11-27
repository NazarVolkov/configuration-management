#include "numbers.h"

#include <charconv>
#include <cmath>
#include <limits>

namespace {

constexpr auto integer_min = std::numeric_limits<Integer>::min();
constexpr auto integer_max = std::numeric_limits<Integer>::max();

template <typename Type>
Type read_numeric_literal(const Expression& expression) {
    Type number{};
    const auto begin = expression.text.data();
    const auto end = begin + expression.text.size();
    const auto result = std::from_chars(begin, end, number);
    if (result.ec != std::errc{} || result.ptr != end) {
        throw SourceError(expression.position, "number out of range: " + expression.text);
    }
    return number;
}

bool sum_overflows(Integer left, Integer right) {
    return (right > 0 && left > integer_max - right) || (right < 0 && left < integer_min - right);
}

bool difference_overflows(Integer left, Integer right) {
    return (right > 0 && left < integer_min + right) || (right < 0 && left > integer_max + right);
}

bool product_overflows(Integer left, Integer right) {
    if (left > 0) {
        return right > integer_max / left || right < integer_min / left;
    }
    if (left < 0 && right > 0) {
        return left < integer_min / right;
    }
    return left < 0 && right < 0 && left < integer_max / right;
}

Integer calculate_integer(Kind kind, Integer left, Integer right, Position position) {
    switch (kind) {
    case Kind::addition:
        if (!sum_overflows(left, right)) {
            return left + right;
        }
        break;
    case Kind::subtraction:
        if (!difference_overflows(left, right)) {
            return left - right;
        }
        break;
    case Kind::multiplication:
        if (!product_overflows(left, right)) {
            return left * right;
        }
        break;
    default:
        throw std::logic_error("invalid binary operator");
    }
    throw SourceError(position, "integer result out of range");
}

double as_double(const Number& number) {
    return std::visit([](auto value) { return static_cast<double>(value); }, number);
}

double calculate_real(Kind kind, double left, double right) {
    switch (kind) {
    case Kind::addition: return left + right;
    case Kind::subtraction: return left - right;
    case Kind::multiplication: return left * right;
    default: throw std::logic_error("invalid binary operator");
    }
}

int compare_integer_real(Integer integer, double real) {
    const auto upper_limit = std::ldexp(1.0, std::numeric_limits<Integer>::digits);
    if (real >= upper_limit) {
        return -1;
    }
    if (real < -upper_limit) {
        return 1;
    }
    const auto whole = static_cast<Integer>(real);
    if (integer != whole) {
        return integer < whole ? -1 : 1;
    }
    const auto fraction = real - static_cast<double>(whole);
    return (fraction < 0) - (fraction > 0);
}

bool less_than(const Number& left, const Number& right) {
    const auto left_integer = std::get_if<Integer>(&left);
    const auto right_integer = std::get_if<Integer>(&right);
    if (left_integer && right_integer) {
        return *left_integer < *right_integer;
    }
    if (left_integer) {
        return compare_integer_real(*left_integer, std::get<double>(right)) < 0;
    }
    if (right_integer) {
        return compare_integer_real(*right_integer, std::get<double>(left)) > 0;
    }
    return std::get<double>(left) < std::get<double>(right);
}

}  // namespace

Number read_number(const Expression& expression) {
    if (expression.text.find_first_of(".eE") == std::string::npos) {
        return read_numeric_literal<Integer>(expression);
    }
    return read_numeric_literal<double>(expression);
}

Number calculate_binary(Kind kind, const Number& left, const Number& right, Position position) {
    const auto left_integer = std::get_if<Integer>(&left);
    const auto right_integer = std::get_if<Integer>(&right);
    if (left_integer && right_integer) {
        return calculate_integer(kind, *left_integer, *right_integer, position);
    }
    const auto result = calculate_real(kind, as_double(left), as_double(right));
    if (!std::isfinite(result)) {
        throw SourceError(position, "floating-point result out of range");
    }
    return result;
}

Number calculate_root(const Number& operand, Position position) {
    const auto value = as_double(operand);
    if (value < 0) {
        throw SourceError(position, "sqrt requires a non-negative number");
    }
    return std::sqrt(value);
}

Number maximum(const Number& left, const Number& right) {
    return less_than(left, right) ? right : left;
}
