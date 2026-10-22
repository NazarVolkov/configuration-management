## Задание 1

```bash
mkdir -p ~/pract1
cd ~/pract1
grep -o '^[^:]*' /etc/passwd | sort
```

## Задание 2

```bash
grep -v '^[[:space:]]*#' /etc/protocols | awk 'NF >= 2 {print $2, $1}' | sort -nr | head -n 5
```

## Задание 3

```bash
sudo apt-get update
sudo apt-get install -y shellcheck

cat > banner <<'EOF'
#!/bin/bash
text="$*"
length=${#text}
line=$(printf '%*s' "$((length + 2))" '' | tr ' ' '-')
echo "+$line+"
echo "| $text |"
echo "+$line+"
EOF

chmod +x banner
shellcheck banner
./banner "Hello from RTU MIREA!"
./banner "Short"
```

## Задание 4

```bash
cat > idents <<'EOF'
#!/bin/bash
grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | paste -sd ' '
EOF

cat > hello.c <<'EOF'
#include <stdio.h>
int main(void) {
    printf("hello world\n");
    return 0;
}
EOF

chmod +x idents
./idents hello.c
```

## Задание 5

```bash
cat > reg <<'EOF'
#!/bin/bash
chmod 755 "$1" || exit 1
cp -- "$1" /usr/local/bin/
EOF

chmod +x reg
sudo ./reg banner
banner "Hello from RTU MIREA!"
```

## Задание 6

```bash
cat > chkcomment <<'EOF'
#!/bin/bash
find "$1" -type f \( -name '*.c' -o -name '*.js' -o -name '*.py' \) |
while IFS= read -r file; do
    case "$file" in
        *.py) pattern='#' ;;
        *.c|*.js) pattern='//|/\*' ;;
    esac
    if head -n 1 "$file" | grep -qE "$pattern"; then
        echo "Есть комментарий: $file"
    else
        echo "Нет комментария: $file"
    fi
done
EOF

mkdir -p comments
printf '/* comment */\nint value;\n' > comments/example.c
printf 'const value = 1; // comment\n' > comments/example.js
printf '# comment\nvalue = 1\n' > comments/example.py
printf 'value = 1\n' > comments/plain.py
chmod +x chkcomment
./chkcomment comments
```

## Задание 7

```bash
cat > dups <<'EOF'
#!/bin/bash
find "$1" -type f -exec md5sum {} + | sort | uniq -w 32 -D
EOF

mkdir -p duplicates/subdir
echo 'same contents' > duplicates/first.txt
cp duplicates/first.txt duplicates/subdir/copy.txt
echo 'other contents' > duplicates/other.txt
chmod +x dups
./dups duplicates
```

## Задание 8

```bash
cat > packext <<'EOF'
#!/bin/bash
find . -maxdepth 1 -type f -name "*.$1" ! -name 'archive.tar' -print0 |
    tar -cvf archive.tar --null -T -
EOF

chmod +x packext
./packext c
tar -tf archive.tar
```

## Задание 9

```bash
cat > tabify <<'EOF'
#!/bin/bash
if [[ $1 -ef $2 ]]; then
    echo 'Укажите разные входной и выходной файлы' >&2
    exit 1
fi
sed 's/    /\t/g' "$1" > "$2"
EOF

printf '    int value = 1;\n        return value;\n' > in.txt
chmod +x tabify
./tabify in.txt out.txt
cat -T out.txt
```

## Задание 10

```bash
cat > emptyfiles <<'EOF'
#!/bin/bash
find "$1" -maxdepth 1 -type f -name '*.txt' -empty -printf '%f\n'
EOF

mkdir -p empty_cases
touch empty_cases/empty.txt empty_cases/empty.bin
echo 'not empty' > empty_cases/filled.txt
chmod +x emptyfiles
./emptyfiles empty_cases
```
