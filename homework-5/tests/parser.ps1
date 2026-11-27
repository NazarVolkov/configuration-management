function Test-Parser {
    $source = @'
values: [0, -2, 003, 4.5, 6., .75, -.125, 2e3, 3E+2, -2.e-1]
text: ['two words', '', '"quoted" C:\tmp # text']
matrix: [[],
  [1, ['x', 2]], 3
]
z: [] empty: ''
'@
    $expected = @'
values = [0, -2, 3, 4.5, 6.0, 0.75, -0.125, 2000.0, 300.0, -0.2]
text = ["two words", "", "\"quoted\" C:\\tmp # text"]
matrix = [[], [1, ["x", 2]], 3]
z = []
empty = ""
'@
    Assert-Translation 'literals and recursive arrays' $source $expected
    Assert-Translation 'empty document' "`t `r`n" ''

    $invalid = [ordered]@{
        'uppercase name'       = 'Name: 1'
        'digit in name'        = 'namea1: 1'
        'incorrect assignment' = 'name = 1'
        'missing value'        = 'a:'
        'missing comma'        = 'a: [1 2]'
        'trailing comma'       = 'a: [1,]'
        'unclosed array'      = 'a: [[1], 2'
        'unterminated string' = "a: 'text"
        'newline in string'   = "a: 'one`ntwo'"
        'double quoted input' = 'a: "text"'
        'leading plus'        = 'a: +1'
        'incomplete exponent' = 'a: 3e-'
        'missing mantissa'    = 'a: .'
        'bare reference'      = 'a: b'
        'adjacent statements' = 'a: 1b: 2'
        'unclosed expression' = 'a: !{+ 1 2'
        'unsupported operator' = 'a: !{/ 1 2}'
        'binary arity'        = 'a: !{* 1 2 3}'
        'sqrt arity'          = 'a: !{sqrt 1 2}'
        'max arity'           = 'a: !{max 1}'
    }
    foreach ($case in $invalid.GetEnumerator()) {
        Assert-InputError $case.Key $case.Value ':1:\d+: error: syntax error'
    }
    Assert-InputError 'error position' "a: 1`r`nb: [1 2]" ':2:7: error: syntax error'

    $value = '[' * 128 + '1' + ']' * 128
    Assert-Translation 'maximum supported depth' "a: $value" "a = $value"
    $value = '!{sqrt ' * 129 + '1' + '}' * 129
    Assert-InputError 'excessive depth' "a: $value" 'nesting exceeds 128 levels'
}
