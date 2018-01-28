#!/usr/bin/python3

import datetime
import json
import urllib.request
from sys import argv
from time import strftime, localtime, time

from pprint import pprint

apikey_filename = "openweathermap_apikey"
default_city = 'montreal'

def load_apikey(filename):
    try:
        with open(filename) as fd:
            apikey = fd.read().strip()
    except FileNotFoundError:
        print("no openweathermap api key provided.")
        exit(2)
    return apikey

def build_url(city_name, apikey):
    baseurl = 'http://api.openweathermap.org/data/2.5/weather?q='
    return baseurl + str(city_name) + '&mode=json&units=metric&APPID=' + apikey

def fetch_data(full_api_url):
#     try:
    with urllib.request.urlopen(full_api_url) as url:
        output = url.read().decode('utf-8')
#     except urllib.request.HTTPError:
#         print("city not found (404).")
#         exit(1)
    return json.loads(output)

def sort_data(json_data):
    city = json_data.get('name')
    country = json_data.get('sys').get('country')
    weather = json_data.get('weather')[0].get('description')
    temp = json_data.get('main').get('temp')
    return (city, country, weather, temp)

def try_city(city_name):
    apikey = load_apikey(apikey_filename)
    url = build_url(city_name.strip(), apikey)
    try:
        json_data = fetch_data(url)
    except urllib.request.HTTPError:
        return None
    (city, country, weather, temp) = sort_data(json_data)
    print( f"current weather in {city}, {country}:\n{weather}, {temp} \xb0C")
    return f"current weather in {city}, {country}:\n{weather}, {temp} \xb0C"

def main():
    if len(argv) > 1:
        city = argv[1]
    else:
        city = default_city
    apikey = load_apikey(apikey_filename)
    url = build_url(city, apikey)
    json_data = fetch_data(url)
#     pprint(json_data)
    (city, country, weather, temp) = sort_data(json_data)
    print(f"current weather in {city}, {country}:")
    print(f"{weather}, {temp} \xb0C")

if __name__ == "__main__":
    main()
