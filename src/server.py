import sys

def main():
    id = int(sys.argv[1])
    n = int(sys.argv[2])
    port = int(sys.argv[3])
    filename = 'log' + str(id) + '.txt'
    with open(filename, 'w+') as f:
        f.write("> server %d" % id)

if __name__ == "__main__":
    main()
