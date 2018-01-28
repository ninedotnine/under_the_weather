#!/usr/bin/python3

import urllib.request
import json
from datetime import datetime

useragent = "undertheweather version 0.1"

def loadPosts(url):
    req = urllib.request.Request(url)
    req.add_header("User-agent", useragent)
    with urllib.request.urlopen(req) as httpresponse:
        print(httpresponse.geturl())
        assert httpresponse.getcode() == 200
        loaded = json.load(httpresponse)
    return loaded['data']['children']

def get_cute_thing():
    url = "https://www.reddit.com/r/aww/top/.json?t=today&limit=35"
    posts = loadPosts(url);
    for post in posts:
        if post['data']['stickied']:
            continue
        print("{url} \n {title}".format(**post['data']))
        if int(post['data']['score']) < 500:
            print("post below score threshold")
            continue
#         return  (post['data']['url'], post['data']['title'])
        return post['data']['url']

def main():
    print( "----------------------------------------")
    print(get_cute_thing())

if __name__ == "__main__":
    main()
