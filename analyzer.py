#!/usr/bin/python3

import json
from pprint import pprint
from sys import argv

from watson_api import fetch_json, build_url
from get_creds import get_creds

default_text = "It is cold and rainy, what a great day we're having..."

def get_strongest_emotion(json_data):
    emotions = json_data.get('emotion').get('document').get('emotion')
    strongest_emotion = max(emotions, key=(lambda x: x[1]))
    print(strongest_emotion, emotions[strongest_emotion])
    return strongest_emotion

def main():
    if len(argv) > 1:
        text = argv[1]
    else:
        text = default_text
    (username, password) = get_creds("credentials")
    full_url = build_url(text)
    json_data = fetch_json(full_url, username, password)
    strongest_emotion = get_strongest_emotion(json_data)
    print("strongest emotion is : " + strongest_emotion)

if __name__ == "__main__":
    main()
