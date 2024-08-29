### IMPORTS

import importlib
import os
import requests
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
import threading
from datetime import datetime
from typing import NamedTuple
import pandas as pd
import config
importlib.reload(config)
from app import lib
importlib.reload(lib)

### GLOBAL VARIABLES

CSV_FILE = "./data/game_data.csv" #test_data.csv
MATCH_ID_FILE = "./data/match_ids.csv" # test_ids.csv

OVERRIDE_AND_CREATE_NEW_DATA = config.override_and_create_new_data

# Knobs for grabbing data
SAMPLE_SIZE_SCALE = 10 # X for each rank & division (X*3*4*3), (X*num_sample_ranks*divisions*num_for_each_player)
NUM_SAMPLE_FOR_EACH_PLAYER = 3 # Too much will result in data skewed based on particular player performance, Capped at 20

# Filler Data if API returns NONE or WR
DEFAULT_WR = 0.45
DEFAULT_MATCH_HISTORY = 19
DEFAULT_CHAMP_MASTERY = 200000

# Ranks used for grabbing data from
SAMPLE_RANKS = {
    # Casual players are usually from silver to platinum
    "SILVER",
    "GOLD",
    "PLATINUM"
}
DIVISIONS = {
    "I",
    "II",
    "III",
    "IV"
}

# Features, includes the label 
class Features(NamedTuple):
    match_id: object
    time: object
    avg_summoner_lvl_team_1: float
    avg_match_history_length_team_1: float
    avg_win_rate_team_1: float
    sum_champ_mastery_team_1: int
    avg_summoner_lvl_team_2: float
    avg_match_history_length_team_2: float
    avg_win_rate_team_2: float
    sum_champ_mastery_team_2: int
    winner: int

# Can use later for getting better avg/accounting for other gamemodes
EXCLUDED_QUEUE_IDS = {
    0,    # Custom games
    830,  # Co-op vs. AI: Intro bots
    840,  # Co-op vs. AI: Beginner bots
    850,  # Co-op vs. AI: Intermediate bots
    450,  # ARAM
    900,  # ARURF
    920,  # Nexus Blitz
    1300  # Nexus Blitz (old)
    # Add more queue IDs to exclude other game modes
}

UPDATED = 97

### FUNCTIONS

def updateCheck():
    """
        Simple function for checking if file content has been successfully reloaded
    """
    return UPDATED
    
def apiCallHandler(request_url, rate_limiters):
    """
        Function for handling API calls

        Args:
            request url: A string representing an url API call
            rate_limiters: A list of RateLimiter objects

        Returns:
            object: If API status 200 response
            None: If API status 404 no data response

        Raises:
            RuntimeError: If a status other than 404 or 429 is returned
    """
    # Make sure all rate_limiters are O.K
    for rate_limiter in rate_limiters:
        rate_limiter.acquire()

    headers = {
        "X-Riot-Token": config.api_key 
    }
    
    response = requests.get(request_url, headers=headers)

    numFailedRetries = 0
    while response.status_code != 200: # while loop here for later when we want to ignore error 429
        # Retry limiter
        if(numFailedRetries >= 2):
            sys.exit(f"Exceeded retry limit of {numRetries}")
            
        if(response.status_code == 429):
            # Not success but is 429 API limit error
            print("Status 429 detected")
            retry_after = int(response.headers.get("Retry-After", 0))
            # 429, retry
            print(f"Retrying in {retry_after}")
            time.sleep(retry_after)
            numFailedRetries += 1
            rate_limiter.acquire()
            response = requests.get(request_url, headers=headers)
        elif(response.status_code == 404):
            # Data not found
            print("Error: Data not found")
            return None
        else:
            # Not success and not 429 API limit error
            print(f"Failed to fetch data: {response.status_code}")
            print(f'Request url: {request_url}')
            sys.exit("Stopping all execution")
        
    # (finally) status of 200
    return response.json()

def multithread_call(urls, work):
    """
         For using multithreading when calling multiple APIs

         Args:
             urls: List of tuples (url, [rate_limiters]) where url is a String that represent an API call url,
                 and [rate_limiters] is a list of RateLimiter objects specific to that URL
             work: A function that does "work" on each API call response

        Returns:
            objects[]: List of API responses that correspond to original order of urls
            objects[NONE]: List of API responses, where some can be None

        Raises:
            RuntimeError: If an odd exception happens when calling the API handler (API handler shouldn't return errors)
    """
    results = [None] * len(urls)
    # "Future" objects store the future value of the API call, it is mapped to an index
    future_to_index = {}
    # Threadpoolexecutor ensures max concurrent workers don't exceed
    with ThreadPoolExecutor(max_workers=lib.MAX_REQUESTS_PER_SECOND) as executor:
        # Go through list of URLs and their specific rate limiters
        for index, (url, url_rate_limiters) in enumerate(urls):
            # Submit API call to executor with its corresponding rate limiters
            future = executor.submit(apiCallHandler, url, url_rate_limiters)
            future_to_index[future] = index

        # as_completed takes "Future" objects in the order they complete
        for future in as_completed(future_to_index):
            # Get index which tells the correct order to return as
            index = future_to_index[future]
            try:
                result = work(future.result())
                results[index] = result
            except Exception as e:
                # This shouldn't ever happen, API error checking done in the API handler
                print(f"Odd Exception: {e}")
                sys.exit("Stopping all execution")
    return results

def avg_wr_summoner_draft(match_history, summoner_puuid, rate_limiter):
    """
        Function for manually calculating average win rate of a summoner for draft games
        *No longer supported
        *Extremely slow b/c of API rate limit
    """
    if(len(match_history) == 0):
        return DEFAULT_WR
    # Create the API URLS based on match_history
    urls = []
    for match in match_history:
        urls += [(f"https://americas.api.riotgames.com/lol/match/v5/matches/{match}", [rate_limiter])]
    results = multithread_call(urls, lambda x: x)
    total_matches = 0
    win_count = 0
    for response in results:
        try:
            # Finds the first participant's id who's equal to the summoner's puuid
            participant = next(p for p in response['info']['participants'] if p['puuid'] == summoner_puuid)
            if(participant['win'] == True):
                win_count+=1
            total_matches+=1
        except StopIteration:
            print("ERROR: StopIteration exception occured, Riot data incorrect?")
            print(response)
            print(f"Summoner PUUID: {summoner_puuid}")
            sys.exit("Stopping all execution")
        except:
            print("ERROR: Exception occured, shouldn't be here")
            sys.exit("Stopping all execution")
    return round(win_count/total_matches, 2)

def avg_wr_summoner_ranked(match_history_length, stats):
    """
        Function for calculating average win rate of a summoner for ranked games

        Args:
            match_history_length: Integer representing length of summoner match history
            stats: Object representing API response of summoner's overall statistics for each gamemode

        Returns:
            int: Number representing average winrate
    """
    if(match_history_length == 0 or stats == None):
        print(f"Inserting default WR, length: {match_history_length}, stats: {stats}")
        return DEFAULT_WR
        
    # Go through each gamemode and look for RANKED_SOLO_5x5
    for stat in stats:
        if(stat['queueType'] == "RANKED_SOLO_5x5"):
            wins = stat['wins']
            loses = stat['losses']
            total = wins+loses
            return round(wins/total, 2)

    # Found no ranked_solo games
    return DEFAULT_WR

def champ_mastery_summoner(stats):
    """
        Function for getting champion mastery of a summoner

        Args:
            stats: Object representing API response of summoner's champ mastery of the champion played

        Returns:
            int: Number representing mastery points in the champion played
    """
    if(stats == None):
        print(f"Inserting default champ_mastery, stats: {stats}")
        return DEFAULT_CHAMP_MASTERY
    champ_mastery = stats['championPoints']
    return champ_mastery

# Gets Data for a given summoner PUUID, and their champ played (for champ mastery)
# Data currently equals: Summoner Level, match history length (max 20), AVG win rate for past 20 matches, champ mastery
def get_summoner_features(summoner_puuid, champion_id, rate_limiter):
    """
        Get summoner's features, which are currently their level, match history length, average winrate, champ mastery

        Args:
            summoner_puuid: Integer representing summoner's PUUID
            champion_id: Integer representing champion played
            rate_limiter: RateLimiter object for API rate limits
        Returns:
            tuple(...): Tuple representing (success, level, match_history_length, avg_wr, champ_mastery) where success is boolean representing whether function returned successfully, level is number representing summoner's level, avg_wr is a float representing the average winrate, champ_mastery is an integer representing champion mastery
            tuple(success=False, ...): If summoner's match history API call returned None or summoner's data API call returned None
    """
    
    # Get summoners' match history & length using their PUUID, filters only for ranked games; max api_calls = 1 (No multithread)
    match_history_search_limiter = lib.RateLimiter_Method([(2000,10)])
    summoner_match_history = apiCallHandler(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner_puuid}/ids?queue=420&type=ranked&start=0&count=20', [rate_limiter, match_history_search_limiter])
    match_history_length = 0
    
    if (summoner_match_history == None):
        #API Handler returned None, something went wrong 
        print(f"summoner_match_history returned None for : {summoner_puuid}")
        return (False, 0,0,0,0)

    match_history_length = len(summoner_match_history)
        
    # All calls below can be multithreaded since prev info is not needed
    # urls = [] Future work: have all possible multi threaded calls do one call
    
    # Get summoners' level using their PUUID; max api_calls = 1
    summoner_search_limiter = lib.RateLimiter_Method([(2000,60)])
    summoner_data = apiCallHandler(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{summoner_puuid}', [rate_limiter, summoner_search_limiter])
    if(summoner_data == None):
        # API Handler returned None, cannot proceed without summoner_data
        print(f"summoner_data returned None for: {summoner_puuid}")
        return (False, 0,0,0,0)
    level = summoner_data['summonerLevel']
    summoner_id = summoner_data['id']
    
    # Get summoners' win rate using match history; max_api_calls = 20 
    # Future work: Ensure that no custom, bot, tutorial, or arena/limited game mode matches
    # Future work: If match count is < 20, THEN use quickplay and aram stats (assign weights to them)
    # Future work: add compatibility for predicting specifically gamemodes other than normal draft 
    #avg_wr = avg_wr_summoner_ranked(match_history_length, summoner_id, rate_limiter)

    # Parallize starting here
    urls = []
    # Get summoners' win rate using API
    summoner_performance_search_limiter = lib.RateLimiter_Method([(270,60)])
    urls += [(f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}', [rate_limiter, summoner_performance_search_limiter])]
    # Get summoners' champ mastery for the match 
    summoner_mastery_search_limiter = lib.RateLimiter_Method([(20000,10),(1200000,600)])
    urls += [(f'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{summoner_puuid}/by-champion/{champion_id}', [rate_limiter, summoner_mastery_search_limiter])]

    all_data_response = multithread_call(urls, lambda x: x)

    # Win rate
    avg_wr = avg_wr_summoner_ranked(match_history_length, all_data_response[0])

    # Champ mastery
    champ_mastery = champ_mastery_summoner(all_data_response[1])
    
    return (True, level, match_history_length, avg_wr, champ_mastery)

def get_features(match_id, rate_limiter):
    
    """
        Gets the features for the match/record given the match ID

        Args:
            match_id: Object representing a match id
            rate_limiter: RateLimiter Object for API rate limits

        Returns:
            tuple(...): Tuple representing (match_id, time, avg_lvl_1, avg_mhl_1, avg_wr_1, sum_cm_1, avg_lvl_2, avg_mhl_2, avg_wr_2, sum_cm_2, winner) where datatypes are (Object, Object, float, float, float, int, float, float, float, sum, int), winner represents the winning team with 3 meaning no one won
            tuple(..., winner=3): If match_info is None or match result is a draw
    """
    
    match_info = apiCallHandler(f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}', [rate_limiter])
    if(match_info == None):
        # API Handler returned None, couldn't get data on match
        return (match_id, datetime.now(), 0, 0, 0, 0, 0, 0, 0, 0, 3)
        
    players = match_info['metadata']['participants']
    
    # Team 1
    avg_lvl_1 = 0
    avg_mhl_1 = 0
    avg_wr_1 = 0
    sum_cm_1 = 0
    total_1 = 0
    
    # Team 2
    avg_lvl_2 = 0
    avg_mhl_2 = 0
    avg_wr_2 = 0
    sum_cm_2 = 0
    total_2 = 0
    
    # 1 means first 5 won, 2 means last 5 won, 3 means draw
    winner = 0
    if(match_info['info']['participants'][0]['win'] == True):
        winner = 1
    elif(match_info['info']['participants'][5]['win'] == True):
        winner = 2
    else:
        # Remake, no one won
        winner = 3
        print("REMADE")
    
    if winner != 3:
        for index in range(len(players)):
            # Get championID of each player
            champion_id = match_info['info']['participants'][index]['championId']
            
            status, level, match_history_length, wr, champ_mastery = get_summoner_features(players[index], champion_id, rate_limiter)

            if status == True:
                if(index < 5):
                    avg_lvl_1 += level
                    avg_mhl_1 += match_history_length
                    avg_wr_1 += wr
                    sum_cm_1 += champ_mastery
                    total_1 +=1
                elif(index >= 5):
                    avg_lvl_2 += level
                    avg_mhl_2 += match_history_length
                    avg_wr_2 += wr
                    sum_cm_2 += champ_mastery
                    total_2 +=1
                else:
                    print("Error: Shouldn't be here")
            else:
                # get_summoner_features returned None/False
                print("Warning: get_summoner_features returned None/False")
                if(index < 5):
                    total_1 -= 1
                else:
                    total_2 -= 1
                
        avg_lvl_1 = round(avg_lvl_1 / total_1, 2)
        avg_mhl_1 = round(avg_mhl_1 / total_1, 2)
        avg_wr_1 = round(avg_wr_1 / total_1, 2)
        
        avg_lvl_2 = round(avg_lvl_2 / total_2, 2)
        avg_mhl_2 = round(avg_mhl_2 / total_2, 2)
        avg_wr_2 = round(avg_wr_2 / total_2, 2)
        
        
    return (match_id, datetime.now(), avg_lvl_1, avg_mhl_1, avg_wr_1, sum_cm_1, avg_lvl_2, avg_mhl_2, avg_wr_2, sum_cm_2, winner)

# Converts a given match_id and its features into a dictionary
# Records will have format of dictionary(match_id, time, features...)
def features_to_dictionary(match_id, time, avg_lvl_1, avg_mhl_1, avg_wr_1, sum_cm_1, avg_lvl_2, avg_mhl_2, avg_wr_2, sum_cm_2, winner):
    """
        Converts a given match_id and its features into a dictionary record, records will have format of dictionary(match_id, time, features...)

        Args: 
            match_id: Object representing games' match id
            time: Object representing current time
            ...: Features for match
        Returns:
            dictionary(features): A dictionary with each feature mapped to the corresponding input feature
    """
    features_record = {
        "match_id": match_id,
        "time": time, 
        "avg_summoner_lvl_team_1": avg_lvl_1,
        "avg_match_history_length_team_1": avg_mhl_1,
        "avg_win_rate_team_1": avg_wr_1,
        "sum_champ_mastery_team_1": sum_cm_1,
        "avg_summoner_lvl_team_2": avg_lvl_2,
        "avg_match_history_length_team_2": avg_mhl_2,
        "avg_win_rate_team_2": avg_wr_2,
        "sum_champ_mastery_team_2": sum_cm_2,
        "winner": winner
    }
    return features_record

# Work function for grabbing (SAMPLE_SIZE_SCALE) amount for each players_info
def work_func_summonerID(players_info):
    """
        Work function for grabbing (SAMPLE_SIZE_SCALE) amount for each players_info

        Args:
            players_info: Object representing API response for a bunch of summoners' information

        Returns:
            list[Object]: List of objects with each object representing a summoner's summonerID
            list[]: Empty list if players_info is None
    """
    players_summonerID = []
    if(players_info == None):
        # API Handler returned none
        print("Error: API Handler returned None for players_info?")
        return players_summonerID
    for index in range(SAMPLE_SIZE_SCALE):
        player_summonerID = players_info[index]['summonerId']
        players_summonerID += [player_summonerID]
    return players_summonerID

def work_func_sample_matches(match_history):
    """
    Work function for grabbing (NUM_SAMPLE_FOR_EACH_PLAYER) from each player
        Args:
            match_history: Object representing API response for a player's match history

        Returns:
            list[Object]: List of objects representing match ids from the player
            list[]: Empty list if match_history is None
    """
    matches = []
    if(match_history == None):
        # API Handler returned None
        print("Error: API Handler returned None for match_history instead of []?")
        return matches
    index = 0
    while(index < len(match_history) and index < NUM_SAMPLE_FOR_EACH_PLAYER):
        matches += [match_history[index]]
        index += 1
    return matches

def work_func_puuid(info):
    """
    Work function for converting summonerID into PUUIDs
        Args:
            info: Object representing API response for a player's account info

        Returns:
            Object: Player's PUUID
            None: If info is None
    """
    if info == None:
        return None
    return info['puuid']

def twoD_to_oneD(list):
    """
    Helper function for turning 2D lists to 1D
        Args:
            list: Generic list

        Returns:
            list[T]: A list of anything
    """
    # Note: filters out empty lists [] created by work functions from "None's"
    res = []
    for i in range(len(list)):
        for j in list[i]:
            res += [j]
    return res

def match_ids_to_dictionary(match_ids_list):
    """
        Helper function for converting match_ids list into a list of dictionaries 

        Args:
            match_ids_list: A proper list of objects representing match ids

        Returns:
            list[dictionary(str)]: A list of dictionaries, each dictionary mapping "match_id" to a match_id
    """
    match_ids_dictionary = []
    for match_id in match_ids_list:
        record = {
            "match_id": match_id
        }
        match_ids_dictionary.append(record)
    return match_ids_dictionary

def get_random_players(rate_limiter):
    """
    Gets random players from a particular rank and division 
        Args:
            rate_limiter: Object representing RateLimiter for API call limits

        Returns:
            list[Objects]: List of objects each representing a player's PUUID
    """
    # Get all players' summonerIDs
    division_search_limiter = lib.RateLimiter_Method([(50,10)])
    urls = []
    for rank in SAMPLE_RANKS:
            for division in DIVISIONS:
                urls += [(f'https://na1.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/{rank}/{division}?page=1', [rate_limiter, division_search_limiter])]
    all_players_summonerID_twoD = multithread_call(urls, work_func_summonerID)
    all_players_summonerID = twoD_to_oneD(all_players_summonerID_twoD)

    # Convert summonerIds into PUUIDs
    summoner_search_limiter = lib.RateLimiter_Method([(2000,60)])
    urls = []
    for player_summonerID in all_players_summonerID:
        urls += [(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{player_summonerID}',[rate_limiter, summoner_search_limiter])]
    all_players_PUUID = multithread_call(urls, work_func_puuid)
    return all_players_PUUID

# Gets random match ids from SAMPLE_RANKS
def get_random_match_ids(rate_limiter):
    """
    Gets random match ids from SAMPLE_RANKS
        Args:
            rate_limiter: Object representing API call rate limits

        Returns:
            list[Objects]: List of objects, each representing a match id
    """
    # First get players from a particular rank and division (one page each)
    players_PUUID = get_random_players(rate_limiter)

    # Get [NUM_SAMPLE_FOR_EACH_PLAYER] matches from each player
    match_search_limiter = lib.RateLimiter_Method([(2000,10)])
    urls = []
    for player_PUUID in players_PUUID:
        # Check for None from work_func_puuid
        if not (player_PUUID == None):
            urls += [(f'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{player_PUUID}/ids?queue=420&type=ranked&start=0&count=20', [rate_limiter, match_search_limiter])]
    matches_twoD = multithread_call(urls, work_func_sample_matches)
    matches = twoD_to_oneD(matches_twoD)
    return matches

def read_match_ids():
    """
    Reads the match ids from the match_ids CSV file and returns a list of them

    Args:
        None

    Returns:
        objects[]: A list of objects containing match_ids

    Raises:
        RuntimeError: If match_ids CSV is not found
    """
    if not os.path.isfile(MATCH_ID_FILE):
        sys.exit("RuntimeError: match_ids CSV not found")

    match_ids = []
    df = pd.read_csv(MATCH_ID_FILE)
    for i in range(len(df)):
        match_ids += [df.iloc[i].values[0]]
    return match_ids

def is_duplicate_match_id(match_id):
    """
    Checks the CSV file to see if a given match_id is already there
        Args:
            match_id: Object representing the match's id
    """
    
    # Loading current CSV file if CSV already exists
    if(os.path.isfile(CSV_FILE)):
        df = pd.read_csv(CSV_FILE)
        if(match_id in df['match_id'].values):
            print("dupe: matchid already in CSV")
            return True
    return False

def get_data(match_ids, rate_limiter):
    """
        Retrieves data/features for the match ids
            Args:
                match_ids: List of objects representing match ids
                rate_limiter: RateLimiter object representing API call limits
            Returns:
                None
    """
    for match_id in match_ids:
        # Search current CSV file if match_id already exists
        print(f'On this match_id: {match_id}')
        if not(is_duplicate_match_id(match_id)):
            currData = []
            match_id, time, avg_lvl_1, avg_mhl_1, avg_wr_1, sum_cm_1, avg_lvl_2, avg_mhl_2, avg_wr_2, sum_cm_2, winner = get_features(match_id, rate_limiter)
            # Check if not remake or invalid match (3)
            if(winner != 3):
                record = features_to_dictionary(match_id, time, avg_lvl_1, avg_mhl_1, avg_wr_1, sum_cm_1, avg_lvl_2, avg_mhl_2, avg_wr_2, sum_cm_2, winner)
                currData.append(record)
                # Write to CSV/create a new one to save progress
                df = pd.DataFrame(currData)
                if(os.path.isfile(CSV_FILE)):
                    # Use this one if DataFrame/CSV already exists
                    df.to_csv(CSV_FILE, index=False, mode='a', header=False)
                else:
                    # Use this one to create CSV for the first time
                    df.to_csv(CSV_FILE, index=False)
    print(f"Finished retrieving data")
    return None
    