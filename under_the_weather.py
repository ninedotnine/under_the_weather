#!/usr/bin/python3

from pprint import pprint
from time import sleep

from mastodon import Mastodon, StreamListener
from get_creds import get_creds
from openweathermap import try_city, get_winnipeg
from watson_api import get_strongest_emotion
from redditaww import get_cute_thing

cities = {} # mega-list of all the most popular cities
with open("world_largest_cities.txt") as fd:
    for line in fd:
        (city, country) = line.split(',')
        cities[city] = country

mastodon = Mastodon(
    client_id = 'undertheweather_mastodon.secret',
    access_token = 'mastodon_credential.secret',
    api_base_url = 'https://mastodon.social'
)

class StreamListenerWeather(StreamListener):
    def on_update(self, status):
        print("-----------received status.------------------")
        print("i don't really care about these.")
        if status.get("account").get("acct") == "UnderTheWeather":
            print("this is just feedback!")
#         pprint(status)

    def on_notification(self, notification):
        print("-----------NOTIFICATION------------------")
#         pprint(notification)
        if notification.get('type') != 'mention':
            print("type wasn't mentioned.")
            return
        status = notification.get('status')
#         pprint(status)
        if status == None:
            print("status was none.")
            return
        print((status.get('content')))
        content = cleanup(status.get('content'))
        if content == None:
            print("content was none.")
            return
        if content == "":
            mastodon.status_post(f"what do you want?", in_reply_to_id=status)
            return
        acct = notification.get('account').get('acct')
        emotion = get_strongest_emotion(content)
        print("THE POSTER IS FEELING: " + emotion)
        if emotion == "joy":
            if status.get('visibility') != 'direct':
                mastodon.status_reblog(status)
            else:
                print("can't reblog a direct message.")
        elif emotion == "disgust":
            mastodon.status_post("you could try being less rude.",
                                 in_reply_to_id=status)
            return
        elif emotion == "anger":
            mastodon.status_post(get_winnipeg(), in_reply_to_id=status)
            return
        elif emotion == "emoji":
            mastodon.status_post("Current weather in your house: \U0001f4a9",
                                 in_reply_to_id=status)
            return
        for city in cities:
            if city in content:
                print("TRYING: " + city)
                report = try_city(f"{city},{cities[city]}")
                break
        else:
            for word in sorted(content.split(), key=len, reverse=True):
                # here it tries to guess which of the other words might be a
                # city by trying them in order of length until it gets a
                # hit. is this even a good idea at all?
                sleep(0.5)
                print("GUESSING: " + word)
                report = try_city(word)
                if report != None:
                    break
        if report != None:
            print(report)
            mastodon.status_post(f"@{acct} {report}", in_reply_to_id=status)
            if emotion == "sadness":
                sleep(1)
                cute_url = get_cute_thing()
                mastodon.status_post("aw, don't be sad, @" + acct +
                                     ".\nmaybe this will cheer you up!\n" +
                                     cute_url, in_reply_to_id=status)
            return
        print("error 404") # report was None
        mastodon.status_post(f"sorry @{acct}, i didn't find your city :^(",
                             in_reply_to_id = status)

def cleanup(content):
    if content == None:
        return None
#     print("----- 1 content is: ", content)
    content = content.replace("<p>", "").replace("</p>", "")
    content = content.replace("&apos;", "'").split()
#     print("----- 2 content is: ", content)
    content = (' '.join([word.lower() for word in content if
        set(word).isdisjoint(set("@<>\""))]))
    print("----- cleaned content is: ", content)
    return content

def main():
    weather = StreamListenerWeather()
    mastodon.stream_user(listener=weather)

if __name__ == "__main__":
    main()
