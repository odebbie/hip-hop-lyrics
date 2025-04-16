import api_key
import requests
import lyricsgenius

import json
import csv
from datetime import date, time, datetime, timedelta
import numpy as np
import re

import time

import os

client_access_token = api_key.your_client_access_token
LyricsGenius = lyricsgenius.Genius(client_access_token, timeout=15, sleep_time=3)

LyricsGenius.verbose = False # Turn off status messages
LyricsGenius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
LyricsGenius.skip_non_songs = True # Include hits thought to be non-songs (e.g. track lists)
LyricsGenius.excluded_terms = ["(Live)"] # Exclude songs with these words in their title

with open('singles_lyrics.json', 'w') as json_file:
    with open("ego_trip_revised.json") as fd:
        href = [json.loads(line) for line in fd]

        for i in href:
            print(i['link'])

            retries = 0
            song = None

            while retries < 3:
                try:
                    # Extract the song URL
                    if 'https://' in i['link']:
                        url = i['link'].split('https://genius.com/', 1)[1]
                    elif 'http://' in i['link']:
                        url = i['link'].split('http://genius.com/', 1)[1]
                        
                    url = url.split('-lyrics', 1)[0]
                    url = re.sub('-', ' ', url)  # Clean up the song name for Genius search

                    # Search for the song using the Genius API
                    song = LyricsGenius.search_song(url)
                    print(f"Retry {retries}, Song found: {song.title_with_featured}")

                    # If the song is found, break out of the loop
                    if song:
                        d = {
                            "id": i["id"],
                            "date": i["date"],
                            "title_with_featured": song.title_with_featured,
                            "title": i['title'],
                            "title_g": song.title,
                            "main": i['main'],
                            "main_g": song.artist,
                            "lyrics": song.lyrics,
                        }

                        # Write the result to the file
                        json.dump(d, json_file)
                        json_file.write('\n')
                        break  # Exit the retry loop once the song is successfully fetched

                except Exception as e:
                    print(f"Error on retry {retries}: {e}")
                    retries += 1
                    time.sleep(2)  # Wait before retrying to avoid hitting rate limits

                        
                

