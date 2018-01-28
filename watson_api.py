import urllib.request
import json
import pprint

from get_creds import get_creds

text = "It is cold and rainy, what a great day we're having..."

def builder(text):
    baseurl = "https://gateway.watsonplatform.net/natural-language-understanding/api/v1/analyze?version=2017-02-27&text=" + text + "&features=sentiment,keywords"
    return baseurl.replace(" ", "%20")

def fetcher(full_api_url, username, password):
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
    (username, password) = get_creds("credentials")
    full_url = builder(text)
    json_data = fetcher(full_url, username, password)
    pprint.pprint(json_data)

if __name__ == "__main__":
    main()
