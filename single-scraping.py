from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import HTTPError
import urllib.request
import urllib.parse
import os
import codecs
from datetime import datetime
import json
import requests

header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia

path = 'wiki-hip-hop-'
year = 1980

def fetch_wikipedia_url(search_term):
    """Helper function to fetch URL from Wikipedia search."""
    search_term = urllib.parse.quote_plus(search_term)
    url = f'https://en.wikipedia.org/w/api.php?action=opensearch&format=json&limit=1&namespace=0&search="{search_term}"'
    
    response = requests.get(url)
    response.raise_for_status()

    if response.ok:
        #print(response.json())
        if response.json()[3]:  # Checks if there's a URL
            return response.json()
    return None

def query(main, album):
    search_terms = [
        f'{album} album', 
        f'{album} mixtape', 
        f'{album} ({main} album)', 
        album
    ]
    
    for term in search_terms:
        result = fetch_wikipedia_url(term)
        if result:  # If a valid URL is found, return the response
            return result
    
    return 'NA'  # Return 'NA' if no valid result is found

def get_songs(q):
    if q != 'NA' and q != []:
        try:
            wiki = q[3][0]
            req = urllib.request.Request(wiki,headers=header)
            page = urlopen(req)
            soup = BeautifulSoup(page, 'html.parser')

        except:
            return None
        
        if soup:
            try:
                song_names = soup.find_all('span', class_='fn')
                
            except:
                return None
            
            if song_names:
                try:
                    release = soup.find_all(string=lambda text: text and 'Released' in text)
                    #print(release)

                    if song_names and release:
                        songs = [song.get_text(strip=True).replace('"', '') for song in song_names]
                        release_dates = [r.strip().replace('Released:', '').strip() for r in release]
                        try:
                            assert len(songs) == len(release_dates[1:])
                            return list(zip(songs, release_dates[1:]))
                        except AssertionError:
                            release_dates = []
                            return songs
                except:
                    release_dates = []
                    return songs