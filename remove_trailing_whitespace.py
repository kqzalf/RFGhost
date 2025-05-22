"""Script to remove trailing whitespace from Python files in the current directory."""

import os


def remove_trailing_whitespace_from_file(filename: str) -> None:
    """Remove trailing whitespace from each line in the given file."""
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(filename, 'w', encoding='utf-8') as file:
        for line in lines:
            file.write(line.rstrip() + '\n')


def main() -> None:
    """Remove trailing whitespace from all .py files in the current directory."""
    for fname in os.listdir('.'):
        if fname.endswith('.py'):
            print(f'Removing trailing whitespace from {fname}')
            remove_trailing_whitespace_from_file(fname)


if __name__ == '__main__':
    main()
