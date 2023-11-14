#!/usr/bin/python3

from lxml import etree
from mastodon import Mastodon, StreamListener

from openweathermap import try_city, load_apikey


class StreamListenerWeather(StreamListener):
    def __init__(self, mastodon: Mastodon, apikey_filename):
        self.apikey = load_apikey(apikey_filename)
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

        print("message is: " + content)
        # example content (line break added for readability):
        # <p><a href="https://bolha.one/@cadusilva" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@cadusilva</a>
        # <span> </span>
        # <a href="https://bolha.one/@clima" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@clima</a>
        # <span> São Paulo</span></p>

        content = etree.XML(content).xpath("string()")

        msg = " ".join((w for w in content.split() if not w.startswith("@")))

        if not msg:
            self.mastodon.status_post(f"what do you want?", in_reply_to_id=status)
            return

        print("TRYING: " + msg)
        report = try_city(msg, self.apikey)

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
        client_id="mastodon_credential.secret",
    )

    mastodon.account_update_credentials(note="prickly weather reporter")
    print("online.")
    try:
        mastodon.stream_user(
            listener=StreamListenerWeather(mastodon, "openweather_apikey.secret")
        )
    except KeyboardInterrupt:
        print("interrupt received, signing off...")
        mastodon.account_update_credentials(note="status: offline.\nask @danso.")
        print("signed off successfully.")


if __name__ == "__main__":
    main()
