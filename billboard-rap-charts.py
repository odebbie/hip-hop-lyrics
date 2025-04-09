import billboard
from datetime import date, time, datetime, timedelta
import numpy as np
import re
import json

ignore_ands = ['Mamdo & She','KC Of KC & The Sunshine Band', 'Magoo And Timbaland',
               'Disco And The City Boyz', 'Patra And Terri', 'The Young and The Restless',
               'Young and Restless', 'Nice & Smooth', 'Heavy D & the Boyz',
               'Dr. Jeckyll & Mr. Hyde', 'Grandmaster Flash & the Furious 5',
               'Grandmaster Flash & The Furious Five',
               'Afrika Bambaataa & the Soul Sonic Force','Grandmixer D.ST & the Infinity Rappers',
               'Rickey G & the Everlasting Five', 'Freddy B & the Mighty Mic Masters',
               'Doug E. Fresh & The Get Fresh Crew', 'Rock Master Scott & the Dynamic Three',
               'Grandmaster Melle Mel and The Furious Five', 'Freddy B and The Mighty Mic Masters', 'Rickey G. & The Everloving Five',
               'Afrika Bambaataa & the Soulsonic Force', "Grand Mixer D.St. & The Infinity Rappers"]
ignore_exes = ['X Ambassadors', 'XXX Tentacion', 'Lil Nas X']

#  Write to JSON
def get_chart_data_js(file_name = "charts-songs", chart_name = "rap-song", current = '1989-03-11'):

    with open(file_name, 'w') as json_file:
        format_start = "%Y-%m-%d"
        current_as_date = datetime.strptime(current, format_start)

        while current_as_date.year < 2025:
            print(current)
            chart = billboard.ChartData(chart_name, date = current) # each year takes abt a minute to traverse

            # Initialize lists and dictionaries
            #songs = defaultdict(list)

            for n, i in enumerate(chart):
                #main_artists = []
                #featuring = []
                #featuring_artists = []

                #check specific cases
                if "Memphis Bleek (& Jay-Z)" == i.artist:
                    main_artists = ['Memphis Bleek']
                    featuring_artists = ['Jay-Z']

                elif ignore_ands == i.artist or ignore_exes == i.artist:
                    main_artists = i.artist
                    featuring_artists = []

                elif 'Heltah Skeltah And O.G.C. As The Fab 5' in i.artist:
                    main_artists = ['The Fab 5', 'Heltah Skeltah', 'Originoo Gunn Clappaz']
                    featuring_artists = []

                elif i.title == "Been Around The World/It's All About The Benjamins":
                    main_artists = ['Puff Daddy']
                    featuring_artists = ['The Notorious B.I.G.', 'Mase']

                # Separate main and featuring artists
                elif 'Featuring' in i.artist:
                    print(i.artist)
                    main_artists, featuring = i.artist.split('Featuring')
                    #main_artists_list = re.split(' & ', main_artists)
                    featuring_artists = re.split(' & |, ', featuring)
                
                elif ' With ' in i.artist:
                    print(i.artist)
                    main_artists, featuring = i.artist.split(' With ')
                    featuring_artists = re.split(' & |, ', featuring)

                elif ' Feat. ' in i.artist:
                    print(i.artist)
                    main_artists, featuring = i.artist.split(' Feat. ')
                    featuring_artists = re.split(' & |, ', featuring)

                elif ' Duet With ' in i.artist:
                    print(i.artist)
                    main_artists, featuring = i.artist.split(' Duet With ')
                    featuring_artists = re.split(' & |, ', featuring)
                
                elif ' With ' in i.artist:
                    print(i.artist)
                    main_artists, featuring = i.artist.split(' With ')
                    featuring_artists = re.split(' & |, ', featuring)

                elif ' + ' in i.artist:
                    print(i.artist)
                    main_artists = i.artist.split(' + ')
                    featuring_artists = []

                elif ' X ' in i.artist: #risky
                    print(i.artist)
                    main_artists = i.artist.split(' X ')
                    featuring_artists = []

                else: #no featuring artist
                    main_artists = i.artist
                    #main_artists_list = re.split(' & |, ', main_artists)
                    featuring_artists = []

                if type(main_artists) ==str:
                    main_artists_list = re.split(' & ', main_artists) #.split(' X ', main_artists)
                
                #remove parenthesis
                main_artists_list = [x.replace("(", "").replace(")", "").strip() for x in main_artists_list]
                featuring_artists = [x.replace("(", "").replace(")", "").strip() for x in featuring_artists]

                d = {
                "date": chart.date, #week
                "week_rank": n + 1, #week_rank
                "title": i.title, #title
                "main": main_artists_list, #main artists
                "featuring": featuring_artists, #featuring artists
                "peakPos": i.peakPos, #peakPosition
                "lastPos": i.lastPos, #previousPosition
                "weeks": i.weeks } #total number of weeks on the chart
                #weeks at one
                #weeks in top ten, maybe ill do these at the end? aggregate later?

                json.dump(d, json_file)
                json_file.write('\n')

            current_as_date = current_as_date + timedelta(days = 7) #increment by week
            current = current_as_date.strftime(format_start)
            #print(current)

get_chart_data_js()