
import pandas as pd
import re
import requests
import numpy as np
from bs4 import BeautifulSoup
#needed to speed up the scraping
import concurrent.futures

'''This script takes a Letterboxd username, scrapes the user's logged films and ratings. 
Then, it exports the resulting dataframe as a csv'''
#####################################################################


username_request = input("Please Enter the username: ")


#####################################################################
def getNumPages(username):
    baseurl = 'https://letterboxd.com/{}/films'.format(username)
    r = requests.get(baseurl)
    sp = BeautifulSoup(r.text, 'html.parser')
    try:
        page = int(sp.select("li.paginate-page")[-1].text)
    except:
        page = int() # for those users whose logged films span just one page
    return page

def the_filmlinks(url):#
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'html.parser')
    lbxbaseurl = "https://letterboxd.com/"
    return [
        lbxbaseurl + thing.get("data-target-link") for thing in sp.select(".really-lazy-load")
    ]

def getAllLinks(username): #
    pages = getNumPages(username)
    baseurl = "https://letterboxd.com/{}/films/page/".format(username)
    #links = [] This is slower, so use ThreadPoolExecutor below
    #for page in range(pages+1):
    #    for item in get_film_links(baseurl+str(page)):
    #      links.append(item)
    
    pagelinks = [baseurl+str(i) for i in range(pages+1)]
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for pagelink in pagelinks:
            futures.append(executor.submit(the_filmlinks, url=pagelink))
        links = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    return [link for llink in links for link in llink]

def the_details(url): #independent of the rest, lots of BeautifulSoup code went into this
    r = requests.get(url)
    sp = BeautifulSoup(r.text, 'html.parser')
    ratingblob = sp.select("head > meta:nth-child(20)")[0]
    
    if ratingblob.get("content").split()[0] == 'Letterboxd':
        rating_c = np.nan
    else:
        try: 
            rating_c = float(ratingblob.get("content").split()[0])
        except:
            rating_c = np.nan
        
    tmdbblob = sp.find('a', attrs={'data-track-action': 'TMDb'})
    directors = [name.text for name in sp.select("span.prettify")]
    
    res = re.search(r'\/movie\/(\d+)\/', tmdbblob.get("href")) # This grabs the TMDB
    #link; entries that aren't movies do not have a TMDB link, so we give them id 0
    if res:
        id = int(sp.find(class_="really-lazy-load").get("data-film-id"))
    else:
        id = np.nan

    ### Stubs    
    genrestub = sp.select('a[href^="/films/genre/"]')

    try:
        countrystub = sp.select('a[href^="/films/country/"]')[0] #/films/country/usa/
        country = re.search(r"/country/(\w+)/", countrystub.get("href")).group(1)
    except:
        country = np.nan

    try:
        languagestub = sp.select('a[href^="/films/language/"]')
        langs = {languagestub[i].text for i in range(len(languagestub))} 
        #use set because original language, spoken languages repetition 
    except:
        langs = np.nan
        
    try:
        runtime = int(re.search(r'\d+', sp.select_one("p.text-link").text).group())
    except:
        runtime = np.nan

    
    film ={
        'film_id': id, #will be used to exclude tv shows
        'film_title': sp.select_one("h1.headline-1").text,
        'film_year': int(sp.select_one("small.number").text),
        'director': [name.text for name in sp.select("span.prettify")],
        'average_rating': rating_c,
        'runtime': runtime,
        'country': country,
        'genres': [genrestub[i].text for i in range(len(genrestub))],
        'languages': langs #sp.select('a[href^="/films/language/"]')[0].text
        #'actors': []
    }
    return film

def getLoggedFilmDetails(username): #non-user related details
#film_details = []
    urls = getAllLinks(username)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for url in urls:
            futures.append(executor.submit(the_details,url))
        results = [future.result()
                for future in concurrent.futures.as_completed(futures)]
    return results

def getRatings(username):
    pages = getNumPages(username)
    baseurl = "https://letterboxd.com/{}/films/page/".format(username)
    rateid = []
    stars = {
        "★": 1, "★★": 2, "★★★": 3, "★★★★": 4, "★★★★★": 5, "½": 0.5, "★½": 1.5, "★★½": 2.5, 
        "★★★½": 3.5, "★★★★½": 4.5
      }

    for page in range(pages+1):
        film_p = baseurl+str(page)
        soup_p = BeautifulSoup(requests.get(film_p).text,'html.parser')
        for thing in soup_p.find_all('li', class_="poster-container"):
            try:
                userrating=stars[thing.find(class_="rating").get_text().strip()]
            except:
                userrating=np.nan
            
            filmp = {
                'film_id':int(thing.find(class_="really-lazy-load").get("data-film-id")),
                'user_rating': userrating
            }
            rateid.append(filmp)
  
    return rateid

def mergerFunc(myuser):
    try:
        df_films = pd.DataFrame(getLoggedFilmDetails(myuser))
    except:
        print('something wrong with list of films')

    try:
        df_ratings = pd.DataFrame(getRatings(myuser))
    except:
        print('issue getting ratings')

    try:
        df_films['director'] = [tuple(item) for item in df_films['director']]
        df_films['genres'] = [tuple(item) for item in df_films['genres']]
        df_films['languages'] = [tuple(item) for item in df_films['languages']]
    except:
        print('how do you get this error?')
        
    try:
        grouped_df = df_ratings.groupby('film_id').agg({'user_rating': 'mean'}).reset_index()
        ratings_df = pd.DataFrame(grouped_df)
    except:
        print('problem performing groupby')

    df = pd.merge(df_films, ratings_df).drop_duplicates()
    df['user_rating'] = df['user_rating'].fillna(df['average_rating'])
    return df
    #except:
    #    print('invalid username')

#Give the final (would have been the csv export)
films = mergerFunc(username_request)

films.to_csv(f'./{username_request}_letterboxd_export.csv')

try:
    films.to_csv(f'./{username_request}_letterboxd_export.csv', mode='x')
except FileExistsError:
    films.to_csv('unique_name.csv')