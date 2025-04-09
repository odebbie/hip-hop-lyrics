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

def clean_wikipedia_tables_p2016(year, file_name = 'wiki-hip-hop.json'):

    with open(file_name, 'w') as json_file:
        format_start = "%Y-%m-%d"
        
        wiki = f"https://en.wikipedia.org/wiki/{year}_in_hip-hop"
        header = {'User-Agent': 'Mozilla/5.0'} #Needed to prevent 403 error on Wikipedia
        req = urllib.request.Request(wiki,headers=header)
        page = urlopen(req)
        soup = BeautifulSoup(page, 'html.parser')
        
        tables = soup.findAll("table", { "class" : "wikitable" })

        for n, table in enumerate(tables):
            n = n + 1

            if n < 13: #from jan to dec
                # preinit list of lists
                rows=table.findAll("tr")
                row_lengths=[len(r.findAll(['th','td'])) for r in rows]
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
                    cells = row.findAll(["td","th"]) #get all the info in the table selectors
                    for j in range(len(cells)):
                        cell=cells[j]
                        
                        #lots of cells span cols and rows so lets deal with that
                        cspan=int(cell.get('colspan',1))
                        rspan=int(cell.get('rowspan',1))

                        for k in range(rspan):
                            if n == 4: #fixing edge case
                                for l in range(cspan - 1):
                                    data[i+k][j+l]+=cell.text #go from top to bottom, left to right
                            else:
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
                        current_as_date = convert(str(n) + " " + data[row][0][0] + " " + str(year), '%m %d %Y').strftime("%Y-%m-%d") #in case of Unknown
                    except: #catch unknown
                        current_as_date = year

                    #print(data[row])

                    if data[row] == []:
                        continue
                    elif data[row][0] == []:
                        continue
                    elif len(data[row][0]) == 2: #date and artist are together
                        d = {'release_date': current_as_date,
                            'main': data[row][0][1],
                            'album': data[row][1][0]}
                    elif len(data[row][0]) == 3: #date and artist and album are together
                        d = {'release_date': current_as_date,
                            'main': data[row][0][1],
                            'album': data[row][0][2]}
                    elif len(data[row][1]) == 2: #date and artist and album are together
                        d = {'release_date': current_as_date,
                            'main': data[row][1][0],
                            'album': data[row][1][1]}
                    else: #make new dictionary
                        #print(data[row])
                        d = {'release_date': current_as_date,
                            'main': data[row][1][0],
                            'album': data[row][2][0]}
                        
                    #data2.append(d)
                    
                    json.dump(d, json_file)
                    json_file.write('\n')

#after 2016
year = 2017
while year < 2025: 
    print(year)
    clean_wikipedia_tables_p2016(year, f'wiki-hip-hop-{year}.json')
    year += 1
