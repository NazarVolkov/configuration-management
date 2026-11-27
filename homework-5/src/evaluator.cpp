#include "evaluator.h"

#include "numbers.h"

#include <unordered_map>

namespace {

class Evaluator {
public:
    std::vector<Binding> evaluate(const std::vector<Declaration>& declarations);

private:
    Value evaluate_expression(const Expression& expression) const;
    Value::Array evaluate_array(const Expression& expression) const;
    Value resolve_reference(const Expression& expression) const;
    Number numeric_value(const Expression& operand) const;
    Number evaluate_operation(const Expression& expression) const;

    std::unordered_map<std::string, std::size_t> bindings_by_name;
    std::vector<Binding> bindings;
};

std::vector<Binding> Evaluator::evaluate(const std::vector<Declaration>& declarations) {
    bindings.reserve(declarations.size());
    for (const auto& declaration : declarations) {
        if (bindings_by_name.count(declaration.name)) {
            throw SourceError(declaration.position, "duplicate constant '" + declaration.name + "'");
        }
        auto value = evaluate_expression(declaration.expression);
        bindings_by_name.emplace(declaration.name, bindings.size());
        bindings.push_back({declaration.name, std::move(value)});
    }
    return std::move(bindings);
}

Value Evaluator::evaluate_expression(const Expression& expression) const {
    switch (expression.kind) {
    case Kind::number: return {read_number(expression)};
    case Kind::string: return {expression.text};
    case Kind::array: return {evaluate_array(expression)};
    case Kind::reference: return resolve_reference(expression);
    default: return {evaluate_operation(expression)};
    }
}

Value::Array Evaluator::evaluate_array(const Expression& expression) const {
    Value::Array values;
    values.reserve(expression.children.size());
    for (const auto& child : expression.children) {
        values.push_back(evaluate_expression(child));
    }
    return values;
}

Value Evaluator::resolve_reference(const Expression& expression) const {
    const auto found = bindings_by_name.find(expression.text);
    if (found == bindings_by_name.end()) {
        throw SourceError(expression.position, "undefined constant '" + expression.text + "'");
    }
    return bindings.at(found->second).value;
}

Number Evaluator::numeric_value(const Expression& operand) const {
    const auto value = evaluate_expression(operand);
    if (const auto number = std::get_if<Number>(&value.data)) {
        return *number;
    }
    throw SourceError(operand.position, "numeric operand required");
}

Number Evaluator::evaluate_operation(const Expression& expression) const {
    const auto& operands = expression.children;
    auto result = numeric_value(operands.at(0));
    if (expression.kind == Kind::square_root) {
        return calculate_root(result, expression.position);
    }
    if (expression.kind == Kind::maximum) {
        for (std::size_t index = 1; index < operands.size(); ++index) {
            result = maximum(result, numeric_value(operands[index]));
        }
        return result;
    }
    return calculate_binary(expression.kind, result, numeric_value(operands.at(1)), expression.position);
}

}  // namespace

std::vector<Binding> evaluate_document(const std::vector<Declaration>& declarations) {
    return Evaluator{}.evaluate(declarations);
}
