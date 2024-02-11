import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time

def get_imdb_data(id):
    '''
    gets the data from imdbd
    '''
    url = "https://www.imdb.com/title/"
    response = requests.get(url+id, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # extracting budget
    box_office = soup.find_all('div', class_='sc-f65f65be-0 fVkLRr')

    for i in range(1,len(box_office)):
        text = box_office[i].find(class_="ipc-metadata-list-item__list-content-item")
        if text is None:
            continue
        else:
            text = text.text
            if '$' in text or '£' in text:
                budget = text.split(' ')[0]
                break
            else: 
                budget = 'NA'
            
    # extracting header IDS
    header = soup.find('div', class_='sc-dffc6c81-3 jFHENY').find_all('li', class_="ipc-inline-list__item")

    # initialize empty list
    data = {}

    # create a dictionary of ids within the list
    for item in header:
        data[item.text.title()] = item.find('a').get('href').split('/')[2]
        
    return budget, data

def get_omdb_data(id, data):
    '''
    gets the data from omdb
    '''
    # extract data from ombd using API
    api_key = '&apikey=6cf40218'
    url = 'http://www.omdbapi.com/?i='
    response = requests.get(url+id+api_key)
    
    # create a temporary dataframe - only want the first rwo
    temp = pd.DataFrame.from_dict(response.json()).head(1)
    
    # create ActorID column
    if ',' not in temp['Actors'][0]:
        temp['ActorID'] = temp['Actors'].map(data)
    else:
        temp['ActorID'] = [[data[actor.strip().title()] for actor in actors] for actors in temp['Actors'].str.split(',')]
    
    # create DirectorID column
    if ',' not in temp['Director'][0]:
        temp['DirectorID'] = temp['Director'].map(data)
    else:
        temp['DirectorID'] = [[data[director.strip().title()] for director in directors] for directors in temp['Director'].str.split(',')]

    return temp
    

def movie_data(ids):
    '''
    takes a list of imdb movie IDs, collects data from IMDb and OMDb, and returns a dataframe
    '''
    
    # initialize dataframe
    cols = ['Title', 'Year', 'Rated', 'Released', 'Runtime', 'Genre', 'Director',
       'Writer', 'Actors', 'Plot', 'Language', 'Country', 'Awards', 'Poster',
       'Ratings', 'Metascore', 'imdbRating', 'imdbVotes', 'imdbID', 'Type',
       'DVD', 'BoxOffice', 'Production', 'Website', 'Response', 'DirectorID',
       'ActorID','Budget']
    df = pd.DataFrame(columns = cols)
    
    counter = 1
    total = len(ids)
    
    for id in ids:
        try:
            budget, data = get_imdb_data(id)
            temp = get_omdb_data(id, data)
            temp['Budget'] = budget
            df = pd.concat([df, temp], ignore_index=True)
            print(f"{(counter)/total*100:.2f}% complete", end='\r')
            counter += 1
            time.sleep(0.4)
        except Exception as e:
            try:
                time.sleep(5)
                budget, data = get_imdb_data(id)
                temp = get_omdb_data(id, data)
                temp['Budget'] = budget
                df = pd.concat([df, temp], ignore_index=True)
                print(f"{(counter)/total*100:.2f}% complete", end='\r')
                counter += 1
            except Exception:
                continue
        
    return df