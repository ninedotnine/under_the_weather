from pprint import pprint
import json

def read_data(filename):
    with open(filename) as fd: # i'm not sure this is really a file descriptor
        output = fd.read()
    return json.loads(output)

def main():
    filename = "out.json"
    data = read_data(filename)
    pprint(data)

if __name__ == "__main__":
    main()
