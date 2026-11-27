#pragma once

inline constexpr auto grammar = R"PEG(
Document       <- Space (Declaration (Gap Declaration)*)? Space !.
Declaration    <- Name Space ':' Space Value
Value          <- Number / String / Array / Expression
Array          <- '[' Nesting Space (Value (Space ',' Space Value)*)? Space ']'
Expression     <- '!{' Nesting Space (Addition / Subtraction / Multiplication / Maximum / SquareRoot / Name) Space '}'
Addition       <- '+' Gap Operand Gap Operand
Subtraction    <- '-' Gap Operand Gap Operand
Multiplication <- '*' Gap Operand Gap Operand
Maximum        <- 'max' Gap Operand Gap Operand (Gap Operand)*
SquareRoot     <- 'sqrt' Gap Operand
Operand        <- Value / Name
Name           <- < [a-z]+ >
Number         <- < '-'? ([0-9]+ ('.' [0-9]*)? / '.' [0-9]+) ([eE] [+-]? [0-9]+)? >
String         <- "'" < (!['\r\n] .)* > "'"
~Nesting       <- ''
~Space         <- [ \t\r\n]*
~Gap           <- [ \t\r\n]+
)PEG";
