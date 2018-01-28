#!/usr/bin/python3

import urllib.request
import json
import pprint
from sys import argv

from get_creds import get_creds

default_text = "It is cold and rainy, what a great day we're having..."
# default_text = "I still have a dream, a dream deeply rooted in the American dream %E2%80%93 one day this nation will rise up and live up to its creed. We hold these truths to be self evident, that all men are created equal."

def build_url(text):
    baseurl = "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27&text=" + text + "&features=sentiment,emotion,concepts,keywords"
    return baseurl.replace(" ", "%20")

def fetch_json(full_api_url, username, password):
    passman = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passman.add_password(None,
                              uri=full_api_url,
                              user=username,
                              passwd=password)
    authhandler =  urllib.request.HTTPBasicAuthHandler(passman)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
    with urllib.request.urlopen(full_api_url) as url:
        output = url.read().decode('utf-8')
    return json.loads(output)

def main():
    if len(argv) > 1:
        text = argv[1]
    else:
        text = default_text
    (username, password) = get_creds("credentials")
    full_url = build_url(text)
    json_data = fetch_json(full_url, username, password)
    pprint.pprint(json_data)

if __name__ == "__main__":
    main()
