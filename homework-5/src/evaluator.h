#pragma once

#include "model.h"
#include "value.h"

std::vector<Binding> evaluate_document(const std::vector<Declaration>& declarations);
