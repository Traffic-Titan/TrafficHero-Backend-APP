import os
import json
from urllib import request, parse

def geocode(item:str):
    url = "https://maps.googleapis.com/maps/api/geocode/json?address=" + parse.quote(item) + "&key=" + os.getenv('Google_Maps_Key')
    response = request.urlopen(url)
    result = json.load(response)["results"]

    for item in result:
        return item['geometry']['location']