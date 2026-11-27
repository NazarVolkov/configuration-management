#include "parser.h"

#include "grammar.h"

#include <peglib.h>

#include <map>

namespace {

Position position_of(const peg::Ast& node) {
    return {node.line, node.column};
}

Expression read_expression(const peg::Ast& node) {
    if (node.name == "Expression" || node.name == "Value" || node.name == "Operand") {
        return read_expression(*node.nodes.at(0));
    }

    static const std::map<std::string, Kind> kinds = {
        {"Number", Kind::number}, {"String", Kind::string}, {"Array", Kind::array},
        {"Name", Kind::reference}, {"Addition", Kind::addition}, {"Subtraction", Kind::subtraction},
        {"Multiplication", Kind::multiplication}, {"Maximum", Kind::maximum}, {"SquareRoot", Kind::square_root},
    };
    Expression expression{kinds.at(node.name), position_of(node), std::string(node.token), {}};
    for (const auto& child : node.nodes) {
        expression.children.push_back(read_expression(*child));
    }
    return expression;
}

}  // namespace

std::vector<Declaration> parse_document(std::string_view source) {
    peg::parser parser(grammar);
    if (!parser) {
        throw std::logic_error("invalid internal grammar");
    }

    const std::string_view utf8_bom = "\xEF\xBB\xBF";
    if (source.substr(0, utf8_bom.size()) == utf8_bom) {
        source.remove_prefix(utf8_bom.size());
    }

    Position error_position{1, 1};
    std::string diagnostic = "invalid input";
    parser.set_logger([&](std::size_t line, std::size_t column, const std::string& message) {
        error_position = {line, column};
        diagnostic = message;
    });
    parser.enable_ast();
    std::shared_ptr<peg::Ast> document;
    if (!parser.parse(source, document)) {
        throw SourceError(error_position, diagnostic);
    }

    std::vector<Declaration> declarations;
    for (const auto& declaration : document->nodes) {
        const auto& name = *declaration->nodes.at(0);
        declarations.push_back({name.token_to_string(), position_of(name), read_expression(*declaration->nodes.at(1))});
    }
    return declarations;
}
