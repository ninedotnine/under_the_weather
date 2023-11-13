#!/usr/bin/python3

import unicodedata

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

        # there must be a better way to de-HTML this string...
        print("message is: " + content)
        content = content.replace("<p>", "").replace("</p>", "")
        content = content.replace("&apos;", "'")
        msg = " ".join(
            [
                word.lower()
                for word in content.split()
                if set(word).isdisjoint(set('@<>"'))
            ]
        )

        if not msg:
            self.mastodon.status_post(f"what do you want?", in_reply_to_id=status)
            return

        report = None

        if "," in msg:  # assume the user passed 'city,country code'
            print("TRYING: " + msg)
            report = try_city(msg, self.apikey)
        else:
            # normalize the text
            msg = unicodedata.normalize("NFD", msg).encode("ascii", "ignore").decode()
            if msg in self.cities:
                print("TRYING: " + f"{msg},{self.cities[msg]}")
                report = try_city(f"{msg},{self.cities[msg]}", self.apikey)

        if report:
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
