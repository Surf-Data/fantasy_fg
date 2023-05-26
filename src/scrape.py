import requests
#from bs4 import BeautifulSoup
import json
import os
import time
from analyze import analyzer,league
from dotenv import load_dotenv
import subprocess

load_dotenv()  # take environment variables from .env.


current = int(time.time())
def scraper(player_type='bat'):
    try:
        cached_dir = f'cache/{player_type}/'
        cached_files = os.listdir(cached_dir)
        if len(cached_files) > 1:
            status_code = subprocess.run( "rm "+cached_dir+'*',shell=True,check=True)
            raise Exception("Error: multiple files in cache")
        elif len(cached_files) == 0:
            raise Exception("Error: No cached files")
        else:
            cached = cached_files[0]
            cached_int = int(cached)
            if cached_int < (current-3600*24):
                raise Exception("Error: File more than 24 hours old")
            with open(cached_dir+cached, "r") as cache: 
                data  = json.load(cache)
            return {"statusCode": 200,"message":"data loaded","data":data}

    except Exception as e:
        print(e)
        data  = requests.get(f'https://www.fangraphs.com/api/projections?type=rfangraphsdc&stats={player_type}&pos=all&team=0&players=0&lg=all').content
        with open(cached_dir+str(current), "wb") as cache:
            cache.write(data)
        return {"statusCode": 200,"message":"new data cached and loaded","data":json.loads(data)}
    
    
if __name__ == '__main__':
    player_type = 'sta'
    results = scraper(player_type)
    A = analyzer(results['data'],player_type)
    #sub = A.df.loc[A.df.PlayerName.isin(['Kodai Senga','Tony Gonsolin','Sonny Gray','Zack Wheeler'])]
    #sub = A.df.loc[A.df.PlayerName.isin(['Mike Trout','Bryce Harper','Brandon Lowe','Tim Anderson','Paul Dejong','Bryson Stott','Matt McLain','Royce Lewis','Hunter Renfroe','Steven Kwan'])][['PlayerName','PA','R','RBI','points']]
    #print(sub[['PlayerName','points']])

    l = league(league_id=os.environ['league_id']
               , year=2023
                ,espn_s2=os.environ['espn_s2']
                ,swid=os.environ['swid']
                )
    fas = l.free_agents(size=100,position_id=14)
    fa_names = []
    for fa in fas:
       fa_names.append(fa.name)
    fa_data = A.df.loc[A.df.PlayerName.isin(fa_names)].copy()
    print(fa_data[['PlayerName','points']])

    

    