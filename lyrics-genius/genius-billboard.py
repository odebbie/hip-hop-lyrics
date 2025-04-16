import api_key
import requests
import lyricsgenius

import json
from datetime import date, time, datetime, timedelta
import numpy as np
import re

import time

client_access_token = api_key.your_client_access_token
LyricsGenius = lyricsgenius.Genius(client_access_token, timeout=15, sleep_time=3)

LyricsGenius.verbose = False # Turn off status messages
LyricsGenius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
LyricsGenius.skip_non_songs = True # Include hits thought to be non-songs (e.g. track lists)
LyricsGenius.excluded_terms = ["(Remix)", "(Live)"] # Exclude songs with these words in their title

with open('lyrics_singles.json', 'w') as json_file:
    with open(f'singles-rev.json') as chart_data:

        for row in chart_data: #each row is a dictionary

            row = json.loads(row)

            retries = 0

            while retries < 3:
                try:
                    song = LyricsGenius.search_song(row['title'], #title of the song
                                            row['main']) #first main artist name                

                    if song:
                        
                        print(f"Song found on retry {retries}: {song.title}, {song.artist}")

                        d = {
                                "album": row['album'],
                                "title": row['title'],
                                "main": row['main'],
                                "year": row['year'],
                                "date_fmt": row['date_fmt'],
                                "lyrics": song.lyrics
                            }

                        json.dump(d, json_file)
                        json_file.write('\n')
                        
                        retries = 3
                        
                        break

                except Exception as e:
                    print(f"Error on retry {retries}: {e}")
                    
                    retries += 1
                    
                    time.sleep(2) #Wait before retrying
                    
                    continue
                

