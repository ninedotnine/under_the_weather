#!/usr/bin/python3

import urllib.request
import json
import pprint
from sys import argv
from pprint import pprint

from get_creds import get_creds

default_text = "It is cold and rainy, what a great day we're having..."
# default_text = "I still have a dream, a dream deeply rooted in the American dream %E2%80%93 one day this nation will rise up and live up to its creed. We hold these truths to be self evident, that all men are created equal."

def build_url(text):
    baseurl = "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27&text=" + text + "&features=sentiment,emotion,concepts,keywords"
    return baseurl.replace(" ", "%20")

def fetch_json(full_api_url, username, password):
    passmgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    passmgr.add_password(None, uri=full_api_url,
                         user=username, passwd=password)
    authhandler =  urllib.request.HTTPBasicAuthHandler(passmgr)
    opener = urllib.request.build_opener(authhandler)
    urllib.request.install_opener(opener)
    with urllib.request.urlopen(full_api_url) as url:
        output = url.read().decode('utf-8')
    return json.loads(output)

def get_strongest_emotion(string):
#     emotion = json_data.get('emotion').get('document').get('emotion')
    (username, password) = get_creds("credentials")
    full_url = build_url(string)
#     print("full_url is " + full_url)
    try:
        json_data = fetch_json(full_url, username, password)
    except urllib.error.HTTPError:
        return 'unknown' # this often happens when the text is too short.
    except UnicodeEncodeError:
        return 'emoji'
#     pprint.pprint(json_data)
    emotions = json_data.get('emotion').get('document').get('emotion')
    for emote in (reversed(sorted(emotions, key=(lambda x : emotions[x])))):
        print(f"{emote}\t\t {emotions[emote]}")
    return max(emotions, key=(lambda x: emotions[x]))

def main():
    if len(argv) > 1:
        text = argv[1]
    else:
        text = default_text
    strongest_emotion = get_strongest_emotion(text)
    print("strongest emotion is : " + strongest_emotion)

if __name__ == "__main__":
    main()
