## Задание 1

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git
mkdir -p ~/pract2
cd ~/pract2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install matplotlib==3.10.7

python -m pip show matplotlib
cat .venv/lib/python*/site-packages/matplotlib-*.dist-info/METADATA

echo 'Name — имя; Version — версия; Summary — описание; Author — автор.'
echo 'License — лицензия; Requires-Python — версия Python; Requires-Dist — зависимости.'
echo 'Project-URL — ссылки на проект.'
echo 'SemVer: MAJOR — несовместимые изменения; MINOR — совместимые новые функции; PATCH — совместимые исправления.'
echo 'Менеджер пакетов устанавливает, обновляет и удаляет пакеты с их зависимостями.'
echo 'Встроенные менеджеры: Emacs — package.el, VS Code — Extensions.'

git clone --depth 1 --branch v3.10.7 https://github.com/matplotlib/matplotlib.git matplotlib-src
cat matplotlib-src/pyproject.toml
```

## Задание 2

```bash
cd ~/pract2
sudo apt-get install -y nodejs npm
npm init -y
npm install express@5.1.0
cat node_modules/express/package.json

echo 'name — имя; version — версия; description — описание; license — лицензия.'
echo 'main — входной модуль; engines — требования к Node.js.'
echo 'dependencies — зависимости; devDependencies — зависимости для разработки.'
echo 'scripts — команды проекта; repository — репозиторий.'

git clone --depth 1 --branch v5.1.0 https://github.com/expressjs/express.git express-src
cat express-src/package.json
```

## Задание 3

```bash
cd ~/pract2
source .venv/bin/activate
sudo apt-get install -y graphviz
python -m pip install pipdeptree==2.30.0 graphviz
pipdeptree --packages matplotlib --graph-output dot > matplotlib.dot
npm ls --all --omit=dev --json > express.json

cat > express_graph.py <<'PY'
import json

with open('express.json') as file:
    tree = json.load(file)

def visit(name, package):
    parent = name + '@' + package['version']
    print(f'"{parent}";')
    for child_name, child_package in package.get('dependencies', {}).items():
        child = child_name + '@' + child_package['version']
        print(f'"{parent}" -> "{child}";')
        visit(child_name, child_package)

print('strict digraph express {')
print('rankdir=LR;')
visit('express', tree['dependencies']['express'])
print('}')
PY

python express_graph.py > express.dot
cat matplotlib.dot
cat express.dot
dot -Tpng matplotlib.dot -o matplotlib.png
dot -Tpng express.dot -o express.png
ls -lh matplotlib.png express.png
```

## Задание 4

```bash
cd ~/pract2
sudo apt-get install -y minizinc minizinc-ide
minizinc --version
minizinc --solvers

cat > lucky.mzn <<'MZN'
include "all_different.mzn";
array[1..6] of var 0..9: digit;
var 0..27: total;
constraint sum(i in 1..3)(digit[i]) = total;
constraint sum(i in 4..6)(digit[i]) = total;
constraint all_different(digit);
solve minimize total;
output [
  "ticket = " ++ concat([show(digit[i]) | i in 1..6]) ++ "\n",
  "sum = " ++ show(total) ++ "\n"
];
MZN

minizinc --solver gecode lucky.mzn
minizinc-ide lucky.mzn &
```

## Задание 5

```bash
cd ~/pract2

cat > pubgrub.mzn <<'MZN'
array[1..6] of string: menu_versions =
  ["1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0", "1.5.0"];
array[1..5] of string: dropdown_versions =
  ["1.8.0", "2.0.0", "2.1.0", "2.2.0", "2.3.0"];
array[1..2] of string: icons_versions = ["1.0.0", "2.0.0"];
% Индексы выбирают версии из массивов выше.
var 1..6: menu;
var 1..5: dropdown;
var 1..2: icons;
constraint icons = 1;
constraint menu = 1 -> dropdown = 1;
constraint menu >= 2 -> dropdown >= 2;
constraint dropdown >= 2 -> icons = 2;
solve satisfy;
output [
  "menu = " ++ menu_versions[fix(menu)] ++ "\n",
  "dropdown = " ++ dropdown_versions[fix(dropdown)] ++ "\n",
  "icons = " ++ icons_versions[fix(icons)] ++ "\n"
];
MZN

minizinc --solver gecode pubgrub.mzn
```

## Задание 6

```bash
cd ~/pract2

cat > dependencies.mzn <<'MZN'
% foo: 1 = 1.0.0, 2 = 1.1.0; 0 у остальных пакетов = не установлен.
var 1..2: foo;
var 0..1: left;
var 0..1: right;
var 0..2: shared;
var 1..2: target;
constraint target = 2;
constraint (foo = 2) <-> (left = 1);
constraint (foo = 2) <-> (right = 1);
constraint (shared > 0) <-> (left = 1 \/ right = 1);
constraint left = 1 -> shared >= 1;
constraint right = 1 -> shared = 1;
constraint shared = 1 -> target = 1;
solve satisfy;
output [
  "root = 1.0.0\n",
  "foo = " ++ (if fix(foo) = 1 then "1.0.0" else "1.1.0" endif) ++ "\n",
  "left = " ++ (if fix(left) = 0 then "not installed"
               else "1.0.0" endif) ++ "\n",
  "right = " ++ (if fix(right) = 0 then "not installed"
                else "1.0.0" endif) ++ "\n",
  "shared = " ++ (if fix(shared) = 0 then "not installed"
                 else show(shared) ++ ".0.0" endif) ++ "\n",
  "target = " ++ show(target) ++ ".0.0\n"
];
MZN

minizinc --solver gecode dependencies.mzn
```

## Задание 7

```bash
cd ~/pract2
source .venv/bin/activate
python -m pip install semantic-version

cat > packages.json <<'JSON'
{
  "root": {"1.0.0": {"foo": "^1.0.0", "target": "^2.0.0"}},
  "foo": {
    "1.1.0": {"left": "^1.0.0", "right": "^1.0.0"},
    "1.0.0": {}
  },
  "left": {"1.0.0": {"shared": ">=1.0.0"}},
  "right": {"1.0.0": {"shared": "<2.0.0"}},
  "shared": {"2.0.0": {}, "1.0.0": {"target": "^1.0.0"}},
  "target": {"2.0.0": {}, "1.0.0": {}}
}
JSON

cat > resolve.py <<'PY'
import json
import subprocess
import sys
from pathlib import Path
from semantic_version import NpmSpec, Version

filename, root, root_version = sys.argv[1:]
packages = json.loads(Path(filename).read_text())
names = list(packages)
ids = {name: i for i, name in enumerate(names, 1)}
versions = {
    name: sorted(packages[name], key=Version, reverse=True)
    for name in names
}

# 0 — пакет не установлен; 1, 2, ... — номера версий.
size = max(len(items) for items in versions.values())
model = [f'array[1..{len(names)}] of var 0..{size}: selected;']
root_choice = versions[root].index(root_version) + 1
model.append(f'constraint selected[{ids[root]}] = {root_choice};')

for name in names:
    i = ids[name]
    model.append(f'constraint selected[{i}] <= {len(versions[name])};')
    for choice, version in enumerate(versions[name], 1):
        for dependency, requirement in packages[name][version].items():
            if dependency not in ids:
                model.append(f'constraint selected[{i}] != {choice};')
                continue
            allowed = []
            for j, candidate in enumerate(versions[dependency], 1):
                if Version(candidate) in NpmSpec(requirement):
                    allowed.append(str(j))
            choices = '{' + ','.join(allowed) + '}'
            model.append(
                f'constraint selected[{i}] = {choice} -> '
                f'selected[{ids[dependency]}] in {choices};'
            )

model.append('solve :: int_search(selected, input_order, indomain_min) satisfy;')
model.append('output [show(selected)];')
Path('generated.mzn').write_text('\n'.join(model))
result = subprocess.check_output(
    ['minizinc', '--solver', 'gecode', 'generated.mzn'], text=True
)
if 'UNSATISFIABLE' in result:
    print('No compatible versions')
    sys.exit(1)
selected = json.loads(result.splitlines()[0])

# Выводим только корневой пакет и его зависимости.
solution = {}
def collect(name):
    if name in solution:
        return
    version = versions[name][selected[ids[name] - 1] - 1]
    solution[name] = version
    for dependency in packages[name][version]:
        collect(dependency)

collect(root)
print(json.dumps(solution, indent=2))
PY

python resolve.py packages.json root 1.0.0
cat generated.mzn
```
