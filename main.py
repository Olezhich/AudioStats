import sys

def main() -> int:
    if len(sys.argv) < 2:
        print(f'{sys.argv[0]}: too few arguments')
        return 0
    if sys.argv[1] == 'update': #plst get | poetry run python main.py update
        for line in sys.stdin:
            print(line)

    return 0

if __name__ == '__main__':
    main()
