#doesnt work!
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

#API Search
def fetch_discography_url(search_term):
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

def query_disc(main):
    search_terms = [
        f'{main} singles discography', 
        f'{main} discography', 
        f'{main} (rapper)',
        f'{main}'
    ]
    
    for term in search_terms:
        result = fetch_discography_url(term)
        if result:  # If a valid URL is found, return the response
            return result
    
    return 'NA'  # Return 'NA' if no valid result is found

#three types of artist discography pages
def scrape_singles_disc(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    lead_artist_header = soup.find('h2', id='As_lead_artist')

    next_element = lead_artist_header.find_parent('div').find_next_sibling()

    tables = []

    while next_element:
        if next_element.name == 'table' and 'wikitable' in next_element.get('class', []):
            tables.append(next_element)
        elif next_element.name == 'div' and 'mw-heading2' in next_element.get('class', []):
            #print('there')
            # Stop if we encounter another heading like <h2>
            break

        next_element = next_element.find_next_sibling()

    return tables #EX: https://en.wikipedia.org/wiki/Kendrick_Lamar_singles_discography
    

def scrape_singles(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    lead_artist_header = soup.find('h3', id='As_lead_artist')

    next_element = lead_artist_header.find_parent('div').find_next_sibling()

    tables = []

    while next_element:
        if next_element.name == 'table' and 'wikitable' in next_element.get('class', []):
            tables.append(next_element)
        elif next_element.name == 'div' and 'mw-heading3' in next_element.get('class', []):
            break
        
        next_element = next_element.find_next_sibling()

    return tables #EX: https://en.wikipedia.org/wiki/Smino_discography

def scrape_singles_main(url): #main page only
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # find relevant tag
    lead_artist_header = soup.find('h3', id='Singles')

    # div element
    next_element = lead_artist_header.find_parent('div').find_next_sibling()

    # store tables
    tables = []

    # until next div
    while next_element:
        if next_element.name == 'table' and 'wikitable' in next_element.get('class', []):
            #if wikitable
            #print('here')
            tables.append(next_element)
        elif next_element.name == 'div' and 'mw-heading3' in next_element.get('class', []):
            break
        
        # continue
        next_element = next_element.find_next_sibling()

    return tables #EX: https://en.wikipedia.org/wiki/N.E.R.D.


def extract_cell_data(cell):
    try:
        colspan = int(cell['colspan'])
    except:
        colspan = 1

    try:
        rowspan = int(cell['rowspan'])
    except:
        rowspan = 1
        
    return [cell.text] * colspan, rowspan

data = []

def multi_spanning(func, url, main): #for multispanning rows...doesnt work
    tables = func(url)

    for table in tables: 
        for row in table.find_all('tr'):
            row_data = []
            row_spans = []
            for cell in row.find_all(['th', 'td']):
                if cell == None:
                    continue
                cell_data, cell_rowspan = extract_cell_data(cell)
                row_data.extend(cell_data)
                row_spans.extend([cell_rowspan] * len(cell_data))

            for i, span in enumerate(row_spans): 
                print(i, span)  
                if span > 1: #if there is a rowspan greater than 1
                    row_spans[i] -= 1

                    if len(data) == 0:
                        continue

                    elif len(row_data) < len(data[0]) and len(row_data) < len(data[-1]):
                        row_data.insert(i, data[-1][i])
                #print(row_spans, i)

            data.append(row_data)

    return data

def format_tbl_data(func, url, main):
    tables = func(url)

    tags = tables[0].select('tr td[rowspan]')
    years = []
    for tag in tags:
        print(tag.attrs)
        years.append((tag.text.strip().isdigit(), tag['rowspan']))

    all_data = []

    for table in tables:
        #print(table)

        # Extract table rows
        rows = table.find_all('tr')
        #print(rows)

        # Initialize variables
        current_album = ""
        current_year = ""

        # Process table data
        data = []
        for row in rows[2:]:  # Skip header rows
            
            cols = row.find_all(['th', 'td'])
            
            if len(cols) == 0:
                continue

            elif len(cols) == 1:
                song_title = cols[0].text.strip()
            
            elif len(cols) == 2:
                song_title = cols[0].text.strip()

                if cols[1].text.strip().isdigit(): #the 2nd col is the year
                    current_year = cols[1].text.strip()

                elif cols[1].text.strip().isalnum(): #the 2nd col is the album title
                    current_album = cols[1].text.strip()
            
            else: #all columns are there

                song_title = cols[0].text.strip()
                year = cols[1].text.strip()

                # Handle album column using rowspan attribute when present
                if "rowspan" in cols[-1].attrs:
                    current_album = cols[-1].text.strip()
                    current_year = year if year else current_year

                # If the year column is not a digit, continue using the last known year
                if year.isdigit():
                    current_year = year
                
                # getalbum
                album_info = cols[-1].text.strip()
                if album_info:
                    current_album = album_info

            #print(len(cols), song_title, int(cols[0].get('colspan',1)))

            entry = {
                "artist": main,
                "song_title": song_title,
                "album": current_album,
                "year": current_year
            }
            data.append(entry)

        all_data.extend(data)
    return all_data

with open('unique_artists.json', 'r', encoding='utf8') as fd:
    unique_artists = [json.loads(line) for line in fd]

for i in unique_artists:
    url = query_disc(i)[3][0]

    if 'singles_discography' in url:
        multi_spanning(scrape_singles, 'https://en.wikipedia.org/wiki/Beyonc%C3%A9_singles_discography','Beyonce')
        
    elif 'discography' in url: #seperate page
        multi_spanning(scrape_singles_disc, 'https://en.wikipedia.org/wiki/Beyonc%C3%A9_singles_discography','Beyonce')

    else: #the person's wikipedia page
        format_tbl_data(scrape_singles_main, 'https://en.wikipedia.org/wiki/N.E.R.D.', 'N.E.R.D.')