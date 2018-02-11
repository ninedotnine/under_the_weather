import sys

from os import environ

def get_api_key():
    homedir = environ.get("HOME")
    try:
        with open(homedir + "/private/openweathermaps_api_key") as fd:
            return fd.read().strip()
    except:
        print("error loading openweathermaps API key.")
        raise

def get_creds(credential_file_path):
    with open(credential_file_path) as creds:
        username = creds.readline().strip()
        password = creds.readline().strip()
    return (username, password)

if __name__ == "__main__":
    get_creds(sys.argv[1])
