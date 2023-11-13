#!/usr/bin/python3

from time import sleep

from mastodon import Mastodon, StreamListener

from openweathermap import try_city, load_apikey


class StreamListenerWeather(StreamListener):
    def __init__(self, mastodon: Mastodon):
        self.cities = {}  # mega-list of all the most popular cities
        try:
            with open("largest_cities.txt") as fd:
                for line in fd:
                    (city, country) = line.rstrip().split(",")
                    self.cities[city] = country
        except FileNotFoundError:
            print("error: could not load largest cities")

        self.common_words = []  # populate a list of common words that are likely not names
        try:
            with open("common_words.txt") as fd:
                for word in fd:
                    self.common_words.append(word.strip())
        except FileNotFoundError:
            print("error: could not load list of common words.")

        self.apikey = load_apikey("/private/openweathermaps_api_key")

        self.mastodon = mastodon
        super().__init__()

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
        if status is None:
            print("status was none.")
            return

        content = status.get("content")
        if content is None:
            print("content was none.")
            return
        else:
            # there must be a better way to de-HTML this string...
            print("content is: " + content.encode())
            content = content.replace("<p>", "").replace("</p>", "")
            content = content.replace("&apos;", "'").split()
            content = " ".join(
                [word.lower() for word in content if set(word).isdisjoint(set('@<>"'))]
            )

        if content == "":
            self.mastodon.status_post(f"what do you want?", in_reply_to_id=status)
            return
        # first try to find something in the dict, then just guess every word
        words = sorted(content.split(), key=len, reverse=True)
        print("words is: " + str(words))
        report = None
        for word in words:
            if word in self.cities:
                print("TRYING: " + f"{word},{self.cities[word]}")
                report = try_city(f"{word},{self.cities[word]}", self.apikey)
                break
        else:  # found nothing in the largest cities dict
            for word in words:
                if word in self.common_words:  # this could be way less inefficient
                    continue
                # here it tries to guess which of the other words might be a
                # city by trying them in order of length until it gets a
                # hit. is this even a good idea at all?
                sleep(0.5)
                print("GUESSING: " + word)
                report = try_city(word, self.apikey)
                if report is not None:
                    break
        # finally, toot the report if we have one!
        if report is not None:
            print(report)
            self.mastodon.status_post(f"@{acct}\n{report}", in_reply_to_id=status)
        else:
            print("error 404")  # report was None
            self.mastodon.status_post(
                f"sorry @{acct}, i didn't find your city :^(", in_reply_to_id=status
            )


def main():
    mastodon = Mastodon(
        client_id="pytooter_clientcred.secret",
        #access_token="mastodon_credential.secret",
        #api_base_url="https://mastodon.social",
    )

    mastodon.account_update_credentials(note="prickly weather reporter")
    print("online.")
    try:
        mastodon.stream_user(listener=StreamListenerWeather(mastodon))
    except KeyboardInterrupt:
        print("interrupt received, signing off...")
        mastodon.account_update_credentials(note="status: offline.\nask @danso.")
        print("signed off successfully.")


if __name__ == "__main__":
    main()
