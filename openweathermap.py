#!/usr/bin/python3

import json
import os
import sys
import urllib.parse
import urllib.request

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?q="
DEFAULT_CITY = "montreal"


def load_apikey(filename):
    with open(os.environ.get("HOME") + filename) as fd:
        return fd.read().strip()


def try_city(city_name, apikey):
    city_name = city_name.strip().rstrip("!?").replace("&apos;", "'").strip()

    full_api_url = BASE_URL + urllib.parse.quote(city_name) + "&mode=json&units=metric&APPID=" + apikey

    with urllib.request.urlopen(full_api_url) as url:
        json_data = json.loads(url.read().decode("utf-8"))

    city = json_data.get("name")
    country = json_data.get("sys").get("country")
    weather = json_data.get("weather")[0].get("description")
    temp = json_data.get("main").get("temp")

    return f"Current weather in {city}, {country}:\n{weather}, {temp} \xb0C"


if __name__ == "__main__":
    print(
        try_city(
            sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CITY,
            load_apikey("/private/openweathermaps_api_key"),
        )
    )
