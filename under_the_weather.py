#!/usr/bin/python3

from time import sleep

from mastodon import Mastodon, StreamListener
from openweathermap import try_city, get_winnipeg

cities = {} # mega-list of all the most popular cities
try:
    with open("largest_cities.txt") as fd:
        for line in fd:
            (city, country) = line.rstrip().split(',')
            cities[city] = country
except FileNotFoundError:
    print("error: could not load largest cities")

common_words = [] # populate a list of common words that are likely not names
try:
    with open("common_words.txt") as fd:
        for word in fd:
            common_words.append(word.strip())
except FileNotFoundError:
    print("error: could not load list of common words.")

class StreamListenerWeather(StreamListener):
    def on_update(self, status):
        name = status.get("account", {}).get("acct")
        print(f"received status from {name}.")
        if name == "UnderTheWeather":
            print("this is just feedback!")

    def on_notification(self, notification):
        print("new notification!")
        acct = notification.get("account").get("acct")
        notif_type = notification.get("type")
        if notif_type == "reblog":
            print(f"post was reblogged by @{acct}")
            return
        elif notif_type == "favourite":
            print(f"post was favourited by @{acct}")
            return
        elif notif_type == "follow":
            print(f"new follower: @{acct}")
            return
        elif notif_type != "mention":
            print("weird, unknown notification type.")
            return

        status = notification.get("status")
        if status == None:
            print("status was none.")
            return
        content = cleanup(status.get("content"))
        if content == None:
            print("content was none.")
            return
        if content == "":
            mastodon.status_post(f"what do you want?", in_reply_to_id=status)
            return
        # first try to find something in the dict, then just guess every word
        words = sorted(content.split(), key=len, reverse=True)
        print("words is: " + str(words))
        for word in words:
            if word in cities:
                print("TRYING: " + f"{word},{cities[word]}")
                report = try_city(f"{word},{cities[word]}")
                break
        else: # found nothing in the largest cities dict
            for word in words:
                if word in common_words: # this could be way less inefficient
                    continue
                # here it tries to guess which of the other words might be a
                # city by trying them in order of length until it gets a
                # hit. is this even a good idea at all?
                sleep(0.5)
                print("GUESSING: " + word)
                report = try_city(word)
                if report != None:
                    break
        # finally, toot the report if we have one!
        if report != None:
            print(report)
            mastodon.status_post(f"@{acct}\n{report}", in_reply_to_id=status)
        else:
            print("error 404") # report was None
            mastodon.status_post(f"sorry @{acct}, i didn't find your city :^(",
                                 in_reply_to_id = status)

def cleanup(content):
    if content == None:
        return None
    # there must be a better way to de-HTML this string...
    content = content.replace("<p>", "").replace("</p>", "")
    content = content.replace("&apos;", "'").split()
    content = (' '.join([word.lower() for word in content if
        set(word).isdisjoint(set("@<>\""))]))
    return content

mastodon = Mastodon(client_id = 'undertheweather.secret',
                    access_token = 'mastodon_credential.secret',
                    api_base_url = 'https://mastodon.social')

def main():
    mastodon.account_update_credentials(note="prickly weather reporter")
    print("online.")
    try:
        weatherListener = StreamListenerWeather()
        mastodon.stream_user(listener=weatherListener)
    except KeyboardInterrupt:
        print("interrupt received, signing off...")
        mastodon.account_update_credentials(note="status: offline.\nask @danso.")
        print("signed off successfully.")
    except:
        print("error:")
        raise

if __name__ == "__main__":
    main()
