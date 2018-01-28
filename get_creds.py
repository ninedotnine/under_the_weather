import sys

def get_creds(credential_file_path):
    with open(credential_file_path) as creds:
        username = creds.readline().strip()
        password = creds.readline().strip()
    return (username, password)

if __name__ == "__main__":
    get_creds(sys.argv[1])
