from mastodon import Mastodon, StreamListener
from get_creds import get_creds
from openweathermap import try_city
from pprint import pprint


########################################
# old code! used only for initial setup. kept for posterity.
# Mastodon.create_app(
#      'undertheweather',
#      api_base_url = 'https://mastodon.social',
#      to_file = 'undertheweather_mastodon.secret'
# )
#
# mastodon = Mastodon(
#     client_id = 'undertheweather_mastodon.secret',
#     api_base_url = 'https://mastodon.social'
# )
#
# mastodon.log_in(
#     'userhuteoans@endrix.org',
#     '45iS2f0qeP78LJemZ57bTzZjI',
#     to_file = 'mastodon_credential.secret'
# )
########################################

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
        pprint("-----------STATUS------------------")
        print(status)

    def on_notification(self, notification):
        print("-----------NOTIFICATION------------------")
        pprint(notification)
        if notification.get('type') != 'mention':
            print("type wasn't mention.")
            return
        status = notification.get('status')
        if status == None:
            print("status was none.")
            return
        content = cleanup(status.get('content'))
        if content == None:
            print("content was none.")
            return
        for word in content:
            print("=============== WORDS:",  word)
        acct = status.get('account').get('acct')
        for city in cities:
            if city in (' '.join(content)):
                print("TRYING: " + city)
                weather = try_city(f"{city},{cities[city]}")
                break
        else:
            for word in content:
                print("GUESSING: " + word)
                weather = try_city(word)
        if weather != None:
            print("SAYING==========", acct, ", weather: ", weather)
            mastodon.status_post(f"@{acct} {weather}",
                                 in_reply_to_id=notification)
            return
        print(f"@{acct} SAYING========== error 404")
        mastodon.status_post("sorry @{acct}, i failed to find your city :^(",
                             in_reply_to_id = notification)

def cleanup(content):
    if content == None:
        return None
    content = content.rstrip("</p>").split()
    print("----- content is: ", content)
    content = [word.lower() for word in content if
        set(word).isdisjoint(set("@><()[]{}\""))]
    print("----- content is: ", content)
    return content

def main():
    weather = StreamListenerWeather()
    mastodon.stream_user(listener=weather)

if __name__ == "__main__":
    main()
