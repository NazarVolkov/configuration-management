#pragma once

#include "model.h"
#include "value.h"

Number read_number(const Expression& expression);
Number calculate_binary(Kind kind, const Number& left, const Number& right, Position position);
Number calculate_root(const Number& operand, Position position);
Number maximum(const Number& left, const Number& right);
