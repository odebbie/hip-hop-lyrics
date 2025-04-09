from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import HTTPError
import urllib.request
import os
import codecs
from datetime import datetime
import json

# Function to convert string to datetime
def convert(date_time, fm = '%B %d %Y'):
    #format = '%B %d %Y'
    datetime_str = datetime.strptime(date_time, fm)

    return datetime_str

def clean_wikipedia_tables(year, file_name = 'wiki-hip-hop.json'):

    with open(file_name, 'w') as json_file:
        format_start = "%Y-%m-%d"
        
        wiki = f"https://en.wikipedia.org/wiki/{year}_in_hip-hop"
        header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
        req = urllib.request.Request(wiki,headers=header)
        page = urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        
        tables = soup.find_all("table", { "class" : "wikitable" })

        table = tables[0]

        # preinit list of lists
        rows=table.find_all("tr")
        row_lengths=[len(r.find_all(['th','td'])) for r in rows]
        ncols=max(row_lengths)
        nrows=len(rows)
        data=[]
        for i in range(nrows):
            rowD=[]
            for j in range(ncols):
                rowD.append('')
            data.append(rowD)

        # process html
        for i in range(len(rows)): #for each row
            row=rows[i]
            rowD=[] #row data
            cells = row.find_all(["td","th"]) #get all the info in the table selectors
            for j in range(len(cells)):
                cell=cells[j]
                
                #lots of cells span cols and rows so lets deal with that
                try:
                    cspan=int(cell.get('colspan',1))
                    rspan=int(cell.get('rowspan',1))
                except:
                    cspan=int(cell.get('colspan',1))
                    rspan=int(cell.get('rowspan',1)[0])

                for k in range(rspan):
                    for l in range(cspan):
                        data[i+k][j+l]+=cell.text #go from top to bottom, left to right

            data.append(rowD)
        for k in range(len(data)):
            for l in range(4):
                try:
                    data[k][l] = list(filter(None, data[k][l].split('\n')))         

                except:
                    continue

        #data2 = []
        data = data[1:]

        for row in range(len(data)):
            try:
                current_as_date = convert(data[row][0][0] + " " + str(year)).strftime("%Y-%m-%d") #in case of Unknown
            except: #catch unknown
                current_as_date = year

            #print(data[row])

            if data[row] == []:
                continue
            elif len(data[row][0]) == 2: #date and artist are together
                
                d = {'release_date': current_as_date,
                    'main': data[row][0][1],
                    'album': data[row][1][0]}
            elif len(data[row][0]) == 3: #date and artist and album are together
                d = {'release_date': current_as_date,
                    'main': data[row][0][1],
                    'album': data[row][0][2]}
                
            else: #make new dictionary
                #print(data[row])
                d = {'release_date': current_as_date,
                    'main': data[row][1][0],
                    'album': data[row][2][0]}
                
            #data2.append(d)
            
            json.dump(d, json_file)
            json_file.write('\n')

#before 2017
year = 1980
while year != 2001 and year < 2017: 
    print(year)
    clean_wikipedia_tables(year, f'wiki-hip-hop-{year}.json')
    year += 1
