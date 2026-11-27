function Test-Evaluator {
    $source = @'
first: -4
offset: 5
sum: !{+ first offset}
difference: !{- sum -2}
product: !{* difference 2.5}
root: !{sqrt !{+ 9 7}}
max: !{max first -6 !{* root 2} product}
reading: [!{max}, [!{+ sum 1}, !{sqrt .25}], 'done']
copy: !{reading}
word: 'text'
alias: !{word}
'@
    $expected = @'
first = -4
offset = 5
sum = 1
difference = 3
product = 7.5
root = 4.0
max = 8.0
reading = [8.0, [2, 0.5], "done"]
copy = [8.0, [2, 0.5], "done"]
word = "text"
alias = "text"
'@
    Assert-Translation 'all operations and references' $source $expected

    $bounds = @'
low: -9223372036854775808
high: 9223372036854775807
product: !{* low 1}
sum: !{+ high low}
diff: !{- low low}
max: !{max 9007199254740992.0 9007199254740993}
fraction: !{max -.5 -1 0}
'@
    $expected = @'
low = -9223372036854775808
high = 9223372036854775807
product = -9223372036854775808
sum = -1
diff = 0
max = 9007199254740993
fraction = 0
'@
    Assert-Translation 'integer endpoints and mixed maximum' $bounds $expected

    Assert-InputError 'unknown reference' 'a: !{missing}' 'undefined constant .missing.'
    Assert-InputError 'forward reference' "a: !{b}`nb: 1" ':1:6: error: undefined constant .b.'
    Assert-InputError 'duplicate declaration' "a: 1`na: 2" ':2:1: error: duplicate constant .a.'
    Assert-InputError 'string operand' "a: !{+ 1 'x'}" 'numeric operand required'
    Assert-InputError 'array operand' "a: [2]`nb: !{max 1 a}" ':2:12: error: numeric operand required'
    Assert-InputError 'invalid square root' "ok: 1`na: !{sqrt -1}" 'sqrt requires a non-negative number'
    Assert-InputError 'integer literal overflow' 'a: 9223372036854775808' 'number out of range'
    Assert-InputError 'real literal overflow' 'a: 1e999' 'number out of range'
    Assert-InputError 'real result overflow' 'a: !{* 1e308 2}' 'floating-point result out of range'
    Assert-InputError 'addition overflow' 'a: !{+ 9223372036854775807 1}' 'integer result out of range'
    Assert-InputError 'subtraction overflow' 'a: !{- -9223372036854775808 1}' 'integer result out of range'
    Assert-InputError 'multiplication overflow' 'a: !{* -9223372036854775808 -1}' 'integer result out of range'
}
