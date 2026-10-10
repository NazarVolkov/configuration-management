"""Простой эмулятор командной строки: этап 1."""


def main():
    while True:
        try:
            line = input("demo:/$ ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        parts = line.split()
        if not parts:
            continue

        command, args = parts[0], parts[1:]
        if command == "exit":
            if args:
                print("exit: неверные аргументы")
            else:
                break
        elif command in ("ls", "cd"):
            print(f"{command}: {args}")
        else:
            print(f"Ошибка: неизвестная команда: {command}")


if __name__ == "__main__":
    main()
