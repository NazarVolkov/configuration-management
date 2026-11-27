#pragma once

#include "model.h"

#include <string_view>

std::vector<Declaration> parse_document(std::string_view source);
