import re
from django.conf import settings
import requests
import threading
import time
from collections import deque
from joblib import load
import urllib.parse
model = load("./exported_model.joblib")

def is_correctly_formatted(input_str):
    """
    Checks if the input string is correctly formatted.

    Correct format:
    - Contains a `#`.
    - Characters before `#` must be 3-16 characters (any character).
    - Characters after `#` must be 3-5 characters (any character).

    Args:
        input_str (str): The string to validate.

    Returns:
        bool: True if the input string is correctly formatted, False otherwise.
    """
    # Define the regular expression pattern
    pattern = r'^.{3,16}#.{3,5}$'
    # Use re.fullmatch to check if the string matches the pattern
    return bool(re.fullmatch(pattern, input_str))

def get_features(username):
    """
    Checks if there is a live game based on this username and returns its features if so
    """
    nameTag_split = username.split("#")
    gameName = nameTag_split[0]
    tagLine = nameTag_split[1]
    try:
        summoner_id = get_puuid(gameName, tagLine)
        features = get_live_features(summoner_id)
    except Exception as e:
        raise Exception(e)
    # Gets the live data
    return features

def predict_game(features):
    """
    Predict the outcome using the loaded model.
    Args:
        features (list): A list or numpy array of input features.
    Returns:
        bool: The model's prediction.
    """
    
    prediction = model.predict(features)
    return prediction

def get_puuid(name, tag):
    """
        Retrieves summoner_id given name#tag
            Args:
                name: String representing player name
                rate_limiter: RateLimiter object representing API call limits
            Returns:
                String: represents player's PUUID
    """
    parsed_name = urllib.parse.quote(name)
    try:
        player_info = apiCallHandler(f'https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{parsed_name}/{tag}')
    except Exception as e:
        raise Exception(e)
    return player_info['puuid']

def apiCallHandler(request_url):
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

    headers = {
        "X-Riot-Token": settings.RIOT_KEY
    }
    
    response = requests.get(request_url, headers=headers)

    if response.status_code != 200:        
        if(response.status_code == 429):
            # Not success but is 429 API limit error
            raise Exception("Rate limit detected from Riot")
        elif(response.status_code == 404):
            # Data not found
            print("Error: Data not found")
            raise Exception("No data found")
        else:
            # Not success and not 429 API limit error
            print(f"Failed to fetch data: {response.status_code}")
            print(f'Request url: {request_url}')
            raise Exception(f"Bad request")
        
    # (finally) status of 200
    #debug2 = response.headers.get("X-App-Rate-Limit-Count")
    #print(f"app-rate-count: {debug2}")
    return response.json()

def get_live_features(summoner_id):
    
    """
        Gets the live features for the match/record given the summoner ID

        Args:
            summoner_id: String representing a summoner id
            rate_limiter: RateLimiter Object for API rate limits

        Returns:
            tuple(...): Tuple representing (..., -1), win should be unknown outcome 
            tuple(..., win=3): If match_info is None 
    """

    # Each participant is a list of participants
    try:
        match_info = apiCallHandler(f'https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summoner_id}')
    except Exception as e:
        raise Exception(e)
    participants = match_info['participants']

    # Get ally team
    team = -1
    for participant in participants:
        if(participant['puuid'] == summoner_id):
            team = participant['teamId']
    if team == -1:
        raise Exception("Cat: TEAM NOT FOUND?")
    
    # Get champions played for team
    team_champions = []
    
    for participant in participants:
        champion_id = participant['championId'] 
        team_id = participant['teamId']  # Team ID: 100 (team1) or 200 (team2)
    
        if team_id == team:
            team_champions.append(champion_id)

    # AD-AP ratio
    team_adap_ratio = 0
    # Specific roles for each team
    team_roles_count = {
        "Tank": 0,
        "Engage": 0,
        "Disengage": 0,
        "ADC": 0,
        "Mage": 0,
        "Assassin": 0,
        "Support": 0,
        "Mid": 0,
        "Top": 0,
        "Jungle": 0,
        "Bruiser": 0,
        "Duelist": 0,
        "Poke": 0,
        "HS": 0 ,
        "Bot": 0
    }

    # Balanced ratio (Checks for certain important factors for deciding a balanced team)
    team_balance_ratio = 0
    # CC sum
    team_cc_sum = 0
    
    # Find the everything based on the champ mapping
    for i in range(5):
        try:
            team_cmapping = champ_map[team_champions[i]]
        except:
            team_cmapping = champ_map[1]
            print("Champion not listed under champion maps, defaulted to 1")
        # ADAP ratio
        team_adap_ratio += team_cmapping["adap"][0]
        # Roles
        for role in team_cmapping["roles"]:
            team_roles_count[role] += 1
        # CC ratio
        team_cc_sum += team_cmapping["cc"]

    team_adap_ratio = 2 * ((1 - abs((team_adap_ratio / 5) - 0.5)) - 0.5)
    
    # Assigns balance points based on certain criteria
    team_balance_points = 0
    # At least one tank
    if team_roles_count["Tank"] > 0:
        team_balance_points += 1
    # At least one engage/disengage
    if team_roles_count["Engage"] > 0 or team_roles_count["Disengage"] > 0:
        team_balance_points += 1
    # At least one backline damage dealer
    if team_roles_count["Mage"] > 0 or team_roles_count["ADC"] > 0:
        team_balance_points += 2
    # All roles filled
    if team_roles_count["Top"] > 0 and team_roles_count["Bot"] > 0 and team_roles_count["Mid"] > 0 and team_roles_count["Jungle"] > 0 and team_roles_count["Support"] > 0:
        team_balance_points += 1

    team_balance_ratio = team_balance_points / 5

    # Creates 2 separate records for each team
    record = (team_adap_ratio, team_balance_ratio, team_cc_sum, team_roles_count["Tank"], team_roles_count["Engage"], team_roles_count["Disengage"], team_roles_count["ADC"], team_roles_count["Mage"], team_roles_count["Assassin"], team_roles_count["Support"], team_roles_count["Mid"], team_roles_count["Top"], team_roles_count["Jungle"], team_roles_count["Bruiser"], team_roles_count["Duelist"], team_roles_count["Poke"], team_roles_count["HS"], team_roles_count["Bot"])
    return record

class RateLimiter_Method:
    """
        Generic Rate Limiter class for method rate limits
    """
    def __init__(self, limits):
        """
            Args:
                limits: A list of tuples, where each tuple contains (max_requests, period_in_seconds)
        """
        self.limits = limits
        self.lock = threading.Lock()
        self.request_times = {limit: deque() for limit in self.limits}

    def acquire(self):
        # Only one thread at a time
        with self.lock:
            while True:
                now = time.time()
                allowed = True

                # Go through every request and ensure rates are being followed
                for max_requests, time_window in self.limits:
                    q = self.request_times[(max_requests, time_window)]
                    # Remove timestamps older than the time window
                    while q and q[0] < now - time_window:
                        q.popleft()

                    if len(q) >= max_requests:
                        # Rate limit has been hit, will sleep for this one and then update all rates again / continue checking
                        allowed = False
                        print(f"Rate limit reached for {max_requests}/{time_window}s.")
                        raise Exception("Rate limit exceeded") 

                if allowed:
                    # If here that means got through every limit check
                    for max_requests, time_window in self.limits:
                        # For every limit, add this timestamp
                        self.request_times[(max_requests, time_window)].append(now)
                    break

champ_map = {
    1: {
        "name": "Annie",
        "adap": (0.05, 0.95),
        "roles": ("Mage", "Mid"),
        "cc": 4.5,
    },  
    2: {
        "name": "Olaf",
        "adap": (0.9, 0.1),
        "roles": ("Bruiser", "Jungle", "Top", "Tank"),
        "cc": 0.5,
    }, 
    3: {
        "name": "Galio",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Support", "Mid", "Engage", "Disengage"),
        "cc": 7.5,
    },
    4: {
        "name": "Twisted Fate",
        "adap": (0.3, 0.7),
        "roles": ("Mage", "Mid", "Poke"),
        "cc": 4,
    },  
    5: {
        "name": "Xin Zhao",
        "adap": (0.9, 0.1),
        "roles": ("Tank", "Jungle", "Bruiser"),
        "cc": 2.5,
    },   
    6: {
        "name": "Urgot",
        "adap": (0.8, 0.2),
        "roles": ("Tank", "Top", "Bruiser"),
        "cc": 2,
    },    
    7: {
        "name": "LeBlanc",
        "adap": (0.1, 0.9),
        "roles": ("Mage", "Assassin", "Mid", "Poke"),
        "cc": 2,
    },    
    8: {
        "name": "Vladimir",
        "adap": (0.05, 0.95),
        "roles": ("Mage", "Mid"),
        "cc": 0.5,
    },    
    9: {
        "name": "Fiddlesticks",
        "adap": (0.1, 0.9),
        "roles": ("Mage", "Jungle", "Support", "Engage"),
        "cc": 5,
    },
    10: {
        "name": "Kayle",
        "adap": (0.4, 0.6),
        "roles": ("Mage", "Top", "Mid"),
        "cc": 0.5,
    },
    11: {
        "name": "Master Yi",
        "adap": (0.9, 0.1),
        "roles": ("Assassin", "Jungle"),
        "cc": 0,
    }, 
    12: {
        "name": "Alistar",
        "adap": (0.2, 0.8),
        "roles": ("Tank", "Support", "Engage"),
        "cc": 7.5,
    }, 
    13: {
        "name": "Ryze",
        "adap": (0.1, 0.9),
        "roles": ("Mage", "Mid", "Top"),
        "cc": 2.5,
    }, 
    14: {
        "name": "Sion",
        "adap": (0.8, 0.2),
        "roles": ("Tank", "Top", "Engage"),
        "cc": 5.5,
    },
    15: {
        "name": "Sivir",
        "adap": (0.9, 0.1),
        "roles": ("ADC", "Bot"),
        "cc": 0,
    },
    16: {
        "name": "Soraka",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Disengage", "HS"),
        "cc": 3,
    },  
    17: {
        "name": "Teemo",
        "adap": (0.2, 0.8),
        "roles": ("Mage", "Top", "Poke"),
        "cc": 2,
    },   
    18: {
        "name": "Tristana",
        "adap": (0.9, 0.1),
        "roles": ("ADC", "Bot"),
        "cc": 2.5,
    },  
    19: {
        "name": "Warwick",
        "adap": (0.3, 0.7),
        "roles": ("Tank", "Jungle", "Top", "Bruiser"),
        "cc": 4.5,
    },   
    20: {
        "name": "Nunu",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Jungle", "Engage", "Mage"),
        "cc": 5,
    },   
   21: {
        "name": "Miss Fortune",
        "adap": (0.85, 0.15),
        "roles": ("ADC", "Bot", "Support"),
        "cc": 0.5,
    }, 
    22: {
        "name": "Ashe",
        "adap": (0.9, 0.1),
        "roles": ("ADC", "Engage", "Bot", "Support"),
        "cc": 5,
    }, 
    23: {
        "name": "Tryndamere",
        "adap": (0.9, 0.1),
        "roles": ("Top", "Jungle", "Assassin", "Duelist"),
        "cc": 0.5,
    },   
    24: {
        "name": "Jax",
        "adap": (0.7, 0.3),
        "roles": ("Top", "Jungle", "Bruiser", "Engage", "Duelist"),
        "cc": 3,
    },  
    25: {
        "name": "Morgana",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Mid", "Disengage", "HS"),
        "cc": 7,
    },   
    26: {
        "name": "Zilean",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Mid", "Disengage", "Poke"),
        "cc": 4.5,
    },   
    27: {
        "name": "Singed",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Top", "Disengage"),
        "cc": 4,
    },   
    28: {
        "name": "Evelynn",
        "adap": (0.1, 0.9),
        "roles": ("Assassin", "Jungle", "Mage"),
        "cc": 2.5,
    },   
    29: {
        "name": "Twitch",
        "adap": (0.75, 0.25),
        "roles": ("ADC", "Bot"),
        "cc": 0.5,
    },   
    30: {
        "name": "Karthus",
        "adap": (0.05, 0.95),
        "roles": ("Mage", "Jungle", "Mid"),
        "cc": 0.5,
    },   
    31: {
        "name": "Cho'Gath",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Top", "Mid"),
        "cc": 3.5,
    },   
    32: {
        "name": "Amumu",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Jungle", "Engage"),
        "cc": 8,
    },  
    33: {
        "name": "Rammus",
        "adap": (0.1, 0.9),
        "roles": ("Tank", "Jungle", "Engage"),
        "cc": 3.5,
    },   
    34: {
        "name": "Anivia",
        "adap": (0.05, 0.95),
        "roles": ("Mage", "Mid", "Disengage"),
        "cc": 3.5,
    },   
    35: {
        "name": "Shaco",
        "adap": (0.65, 0.35),
        "roles": ("Assassin", "Jungle", "Poke"),
        "cc": 3.5,
    },  
    36: {
        "name": "Dr. Mundo",
        "adap": (0.7, 0.3),
        "roles": ("Tank", "Top", "Jungle", "Engage"),
        "cc": 1,
    },   
    37: {
        "name": "Sona",
        "adap": (0.05, 0.95),
        "roles": ("Support", "Mage", "Disengage", "HS"),
        "cc": 4.5,
    },   
    38: {
        "name": "Kassadin",
        "adap": (0.1, 0.9),
        "roles": ("Assassin", "Mage", "Mid"),
        "cc": 0.5,
    },   
    39: {
        "name": "Irelia",
        "adap": (0.85, 0.15),
        "roles": ("Top", "Mid", "Duelist"),
        "cc": 2,
    }, 
    40: {
        "name": "Janna",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Disengage", "Mage", "HS"),
        "cc": 4,
    },   
    41: {
        "name": "Gangplank",
        "adap": (0.9, 0.1),
        "roles": ("Top", "Mid", "Duelist"),
        "cc": 1,
    },   
    42: {
        "name": "Corki",
        "adap": (0.65, 0.35),
        "roles": ("Mid", "ADC", "Mage", "Poke", "Bot"),
        "cc": 0,
    },  
    43: {
        "name": "Karma",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Mid", "Mage", "Disengage", "Poke", "HS"),
        "cc": 3.5,
    },   
    44: {
        "name": "Taric",
        "adap": (0.25, 0.75),
        "roles": ("Support", "Tank", "Disengage", "HS"),
        "cc": 4,
    },   
    45: {
        "name": "Veigar",
        "adap": (0.05, 0.95),
        "roles": ("Mid", "Mage"),
        "cc": 3,
    },   
    48: {
        "name": "Trundle",
        "adap": (0.85, 0.15),
        "roles": ("Top", "Jungle", "Tank", "Bruiser"),
        "cc": 1,
    },
    50: {
        "name": "Swain",
        "adap": (0.1, 0.9),
        "roles": ("Mid", "Support", "Mage", "Engage", "Tank"),
        "cc": 3.5,
    }, 
    51: {
        "name": "Caitlyn",
        "adap": (0.95, 0.05),
        "roles": ("ADC", "Poke", "Bot"),
        "cc": 1.5,
    }, 
    53: {
        "name": "Blitzcrank",
        "adap": (0.1, 0.9),
        "roles": ("Support", "Engage", "Tank"),
        "cc": 6,
    },   
    54: {
        "name": "Malphite",
        "adap": (0.3, 0.7),
        "roles": ("Top", "Tank", "Engage"),
        "cc": 4,
    },   
    55: {
        "name": "Katarina",
        "adap": (0.35, 0.65),
        "roles": ("Mid", "Assassin", "Mage"),
        "cc": 0,
    },  
    56: {
        "name": "Nocturne",
        "adap": (0.9, 0.1),
        "roles": ("Jungle", "Assassin", "Engage"),
        "cc": 2.5,
    },   
    57: {
        "name": "Maokai",
        "adap": (0.1, 0.9),
        "roles": ("Top", "Jungle", "Tank", "Engage", "Disengage"),
        "cc": 8.5,
    },  
    58: {
        "name": "Renekton",
        "adap": (0.9, 0.1),
        "roles": ("Top", "Duelist", "Bruiser", "Engage", "Tank"),
        "cc": 2.5,
    },   
    59: {
        "name": "Jarvan IV",
        "adap": (0.8, 0.2),
        "roles": ("Jungle", "Top", "Engage", "Bruiser", "Tank"),
        "cc": 3,
    },  
    60: {
        "name": "Elise",
        "adap": (0.05, 0.95),
        "roles": ("Jungle", "Mage", "Assassin", "Poke"),
        "cc": 2.5,
    },   
    61: {
        "name": "Orianna",
        "adap": (0.15, 0.85),
        "roles": ("Mid", "Mage"),
        "cc": 4.5,
    },   
    62: {
        "name": "Wukong",
        "adap": (0.9, 0.1),
        "roles": ("Top", "Jungle", "Bruiser", "Duelist", "Engage", "Assassin"),
        "cc": 4,
    },   
    63: {
        "name": "Brand",
        "adap": (0.05, 0.95),
        "roles": ("Support", "Mid", "Mage", "Poke"),
        "cc": 2.5,
    },   
    64: {
        "name": "Lee Sin",
        "adap": (0.85, 0.15),
        "roles": ("Jungle", "Top", "Assassin", "Bruiser"),
        "cc": 3,
    },   
    67: {
        "name": "Vayne",
        "adap": (0.95, 0.05),
        "roles": ("ADC", "Duelist", "Bot"),
        "cc": 2,
    }, 
    68: {
        "name": "Rumble",
        "adap": (0.05, 0.95),
        "roles": ("Top", "Mage"),
        "cc": 0.5,
    },   
    69: {
        "name": "Cassiopeia",
        "adap": (0.05, 0.95),
        "roles": ("Mid", "Mage", "Disengage"),
        "cc": 4.5,
    },   
    72: {
        "name": "Skarner",
        "adap": (0.7, 0.3),
        "roles": ["Jungle", "Tank", "Engage"],
        "cc": 6.5,
    },   
    74: {
        "name": "Heimerdinger",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Top", "Support", "Mage"],
        "cc": 2,
    },  
    75: {
        "name": "Nasus",
        "adap": (0.8, 0.2),
        "roles": ["Top", "Tank", "Bruiser"],
        "cc": 1.5,
    },   
    76: {
        "name": "Nidalee",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "Mage", "Assassin", "Poke"],
        "cc": 0,
    },   
    77: {
        "name": "Udyr",
        "adap": (0.6, 0.4),
        "roles": ["Jungle", "Top", "Bruiser"],
        "cc": 2,
    },   
    78: {
        "name": "Poppy",
        "adap": (0.8, 0.2),
        "roles": ["Top", "Jungle", "Support", "Tank", "Disengage"],
        "cc": 6,
    },  
    79: {
        "name": "Gragas",
        "adap": (0.05, 0.95),
        "roles": ["Jungle", "Mid", "Top", "Mage"],
        "cc": 5.5,
    },   
    80: {
        "name": "Pantheon",
        "adap": (0.95, 0.05),
        "roles": ["Mid", "Support", "Top", "Assassin", "Duelist"],
        "cc": 3.5,
    },   
    81: {
        "name": "Ezreal",
        "adap": (0.7, 0.3),
        "roles": ["ADC", "Bot"],
        "cc": 0,
    },   
    82: {
        "name": "Mordekaiser",
        "adap": (0.1, 0.9),
        "roles": ["Top", "Jungle", "Mage", "Duelist", "Bruiser"],
        "cc": 3,
    },  
    83: {
        "name": "Yorick",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Duelist", "Bruiser"],
        "cc": 0.5,
    },  
    84: {
        "name": "Akali",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Top", "Assassin"],
        "cc": 0,
    },   
    85: {
        "name": "Kennen",
        "adap": (0.05, 0.95),
        "roles": ["Top", "Mid", "Assassin", "Engage", "Mage"],
        "cc": 4.5,
    },   
    86: {
        "name": "Garen",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Tank", "Duelist", "Bruiser"],
        "cc": 1,
    },   
    89: {
        "name": "Leona",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Engage", "Tank"],
        "cc": 8,
    },  
    90: {
        "name": "Malzahar",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Mage"],
        "cc": 3.5,
    },   
    91: {
        "name": "Talon",
        "adap": (0.95, 0.05),
        "roles": ["Mid", "Assassin"],
        "cc": 0.5,
    },
    92: {
        "name": "Riven",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Duelist", "Bruiser"],
        "cc": 1,
    }, 
    96: {
        "name": "Kog'Maw",
        "adap": (0.7, 0.3),
        "roles": ["ADC", "Poke", "Bot"],
        "cc": 0.5,
    },  
    98: {
        "name": "Shen",
        "adap": (0.8, 0.2),
        "roles": ["Top", "Support", "Disengage", "HS"],
        "cc": 4,
    },   
    99: {
        "name": "Lux",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Support", "Mage", "Poke"],
        "cc": 4,
    },  
    101: {
        "name": "Xerath",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Support", "Mage", "Poke"],
        "cc": 3,
    },  
    102: {
        "name": "Shyvana",
        "adap": (0.3, 0.7),
        "roles": ["Jungle", "Top", "Poke", "Bruiser", "Engage"],
        "cc": 2.5,
    },  
    103: {
        "name": "Ahri",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Mage", "Assassin"],
        "cc": 3.5,
    },
    104: {
        "name": "Graves",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "ADC"],
        "cc": 1,
    },   
    105: {
        "name": "Fizz",
        "adap": (0.15, 0.85),
        "roles": ["Mid", "Assassin"],
        "cc": 1.5,
    },
    106: {
        "name": "Volibear",
        "adap": (0.3, 0.7),
        "roles": ["Top", "Jungle", "Engage", "Tank", "Bruiser"],
        "cc": 2.5,
    },
    107: {
        "name": "Rengar",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Top", "Assassin"],
        "cc": 1.5,
    }, 
    110: {
        "name": "Varus",
        "adap": (0.7, 0.3),
        "roles": ["ADC", "Poke", "Bot"],
        "cc": 3,
    }, 
    111: {
        "name": "Nautilus",
        "adap": (0.15, 0.85),
        "roles": ["Support", "Tank", "Engage"],
        "cc": 8.5,
    }, 
    112: {
        "name": "Viktor",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Poke", "Mage"],
        "cc": 3,
    },  
    113: {
        "name": "Sejuani",
        "adap": (0.2, 0.8),
        "roles": ["Jungle", "Top", "Tank", "Engage"],
        "cc": 8,
    }, 
    114: {
        "name": "Fiora",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Duelist", "Bruiser"],
        "cc": 1.5,
    },  
    115: {
        "name": "Ziggs",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Bot", "Mage", "Poke"],
        "cc": 2,
    },  
    117: {
        "name": "Lulu",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Mage", "HS", "Disengage"],
        "cc": 5.5,
    },  
    119: {
        "name": "Draven",
        "adap": (0.95, 0.05),
        "roles": ["ADC", "Bot"],
        "cc": 2,
    },
    120: {
        "name": "Hecarim",
        "adap": (0.8, 0.2),
        "roles": ["Jungle", "Bruiser", "Engage"],
        "cc": 5.5,
    }, 
    121: {
        "name": "Kha'Zix",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Assassin"],
        "cc": 0.5,
    },  
    122: {
        "name": "Darius",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Duelist", "Bruiser"],
        "cc": 2.5,
    },  
    126: {
        "name": "Jayce",
        "adap": (0.85, 0.15),
        "roles": ["Top", "Mid", "Poke"],
        "cc": 2,
    }, 
    127: {
        "name": "Lissandra",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Mage"],
        "cc": 5,
    },  
    131: {
        "name": "Diana",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "Mid", "Assassin", "Bruiser", "Engage"],
        "cc": 3.5,
    },  
    133: {
        "name": "Quinn",
        "adap": (0.9, 0.1),
        "roles": ["Top", "ADC"],
        "cc": 2,
    }, 
    134: {
        "name": "Syndra",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Mage"],
        "cc": 3,
    }, 
    136: {
        "name": "Aurelion Sol",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Mage"],
        "cc": 3.5,
    }, 
    141: {
        "name": "Kayn",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Assassin", "Bruiser"],
        "cc": 1,
    },  
    142: {
        "name": "Zoe",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Mage", "Poke"],
        "cc": 2.5,
    },
    143: {
        "name": "Zyra",
        "adap": (0.05, 0.95),
        "roles": ["Support", "Mid", "Poke", "Mage"],
        "cc": 5.5,
    }, 
    145: {
        "name": "Kai'Sa",
        "adap": (0.6, 0.4),
        "roles": ["ADC", "Bot"],
        "cc": 0,
    },  
    147: {
        "name": "Seraphine",
        "adap": (0.05, 0.95),
        "roles": ["Support", "Mid", "Mage", "HS", "Poke", "Bot"],
        "cc": 7.5,
    },  
    150: {
        "name": "Gnar",
        "adap": (0.85, 0.15),
        "roles": ["Top", "Bruiser", "Engage", "Tank"],
        "cc": 6,
    },  
    154: {
        "name": "Zac",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "Tank", "Engage", "Top"],
        "cc": 7,
    }, 
    157: {
        "name": "Yasuo",
        "adap": (0.9, 0.1),
        "roles": ["Mid", "Top", "Duelist"],
        "cc": 2,
    },  
    161: {
        "name": "Vel'Koz",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Support", "Mage", "Poke"],
        "cc": 3,
    },  
    163: {
        "name": "Taliyah",
        "adap": (0.05, 0.95),
        "roles": ["Mid", "Jungle", "Mage", "Disengage"],
        "cc": 4.5,
    },  
    164: {
        "name": "Camille",
        "adap": (0.85, 0.15),
        "roles": ["Top", "Duelist", "Engage", "Bruiser"],
        "cc": 3.5,
    },  
    166: {
        "name": "Akshan",
        "adap": (0.9, 0.1),
        "roles": ["Mid", "ADC", "Assassin"],
        "cc": 0,
    },   
    200: {
        "name": "Bel'Veth",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Bruiser"],
        "cc": 2,
    },  
    201: {
        "name": "Braum",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Tank", "Disengage"],
        "cc": 6,
    },  
    202: {
        "name": "Jhin",
        "adap": (0.9, 0.1),
        "roles": ["ADC", "Bot"],
        "cc": 3,
    },
    203: {
        "name": "Kindred",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "ADC"],
        "cc": 0.5,
    },  
    221: {
        "name": "Zeri",
        "adap": (0.8, 0.2),
        "roles": ["ADC", "Bot"],
        "cc": 0.5,
    },
    222: {
        "name": "Jinx",
        "adap": (0.9, 0.1),
        "roles": ["ADC", "Bot"],
        "cc": 2.5,
    },
    223: {
        "name": "Tahm Kench",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Top", "Tank", "Disengage"],
        "cc": 5.5,
    }, 
    233: {
        "name": "Briar",
        "adap": (0.8, 0.2),
        "roles": ["Jungle", "Bruiser", "Assassin"],
        "cc": 4,
    },  
    234: {
        "name": "Viego",
        "adap": (0.8, 0.2),
        "roles": ["Jungle"],
        "cc": 2,
    },  
    235: {
        "name": "Senna",
        "adap": (0.9, 0.1),
        "roles": ["Support", "ADC", "Bot", "HS"],
        "cc": 4,
    }, 
    236: {
        "name": "Lucian",
        "adap": (0.9, 0.1),
        "roles": ["ADC", "Mid", "Bot"],
        "cc": 0,
    },
    238: {
        "name": "Zed",
        "adap": (0.9, 0.1),
        "roles": ["Mid", "Jungle", "Assassin"],
        "cc": 0.5,
    },  
    240: {
        "name": "Kled",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Engage", "Bruiser"],
        "cc": 1.5,
    },  
    245: {
        "name": "Ekko",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "Mid", "Assassin"],
        "cc": 3,
    },  
    246: {
        "name": "Qiyana",
        "adap": (0.9, 0.1),
        "roles": ["Mid", "Jungle", "Assassin"],
        "cc": 3.5,
    },  
    254: {
        "name": "Vi",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Bruiser", "Engage"],
        "cc": 5.5,
    },  
    266: {
        "name": "Aatrox",
        "adap": (0.85, 0.15),
        "roles": ["Top", "Bruiser"],
        "cc": 2.5,
    },  
    267: {
        "name": "Nami",
        "adap": (0.05, 0.95),
        "roles": ["Support", "HS"],
        "cc": 7,
    },  
    268: {
        "name": "Azir",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Mage"],
        "cc": 3,
    },  
    350: {
        "name": "Yuumi",
        "adap": (0.05, 0.95),
        "roles": ["Support", "HS"],
        "cc": 0.5,
    },  
    360: {
        "name": "Samira",
        "adap": (0.95, 0.05),
        "roles": ["ADC", "Bot"],
        "cc": 0,
    },
    412: {
        "name": "Thresh",
        "adap": (0.2, 0.8),
        "roles": ["Support", "Tank", "Disengage"],
        "cc": 6.5,
    }, 
    420: {
        "name": "Illaoi",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Bruiser", "Tank"],
        "cc": 0.5,
    }, 
    421: {
        "name": "Rek'Sai",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Assassin", "Bruiser"],
        "cc": 2.5,
    },  
    427: {
        "name": "Ivern",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "HS"],
        "cc": 5.5,
    },  
    429: {
        "name": "Kalista",
        "adap": (0.9, 0.1),
        "roles": ["ADC", "Bot"],
        "cc": 3,
    }, 
    432: {
        "name": "Bard",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Engage", "Disengage", "HS"],
        "cc": 5.5,
    }, 
    497: {
        "name": "Rakan",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Engage", "Tank"],
        "cc": 7.5,
    },  
    498: {
        "name": "Xayah",
        "adap": (0.95, 0.05),
        "roles": ["ADC", "Bot"],
        "cc": 2.5,
    },
    516: {
        "name": "Ornn",
        "adap": (0.3, 0.7),
        "roles": ["Top", "Tank", "Engage"],
        "cc": 7,
    },  
    517: {
        "name": "Sylas",
        "adap": (0.25, 0.75),
        "roles": ["Mid", "Assassin", "Bruiser"],
        "cc": 4.5,
    },  
    518: {
        "name": "Neeko",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Support", "Engage", "Mage"],
        "cc": 6.5,
    }, 
    523: {
        "name": "Aphelios",
        "adap": (0.95, 0.05),
        "roles": ["ADC", "Bot"],
        "cc": 0.5,
    },
    526: {
        "name": "Rell",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Tank", "Engage"],
        "cc": 8.5,
    }, 
    555: {
        "name": "Pyke",
        "adap": (0.9, 0.1),
        "roles": ["Support", "Engage", "Assassin"],
        "cc": 4.5,
    },  
    711: {
        "name": "Vex",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Mage", "Assassin"],
        "cc": 4.5,
    }, 
    777: {
        "name": "Yone",
        "adap": (0.8, 0.2),
        "roles": ["Mid", "Top", "Bruiser", "Engage"],
        "cc": 5,
    },  
    799: {
        "name": "Ambessa",
        "adap": (0.9, 0.1),
        "roles": ["Jungle", "Top", "Bruiser", "Assassin"],
        "cc": 2.5,
    },  
    875: {
        "name": "Sett",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Engage", "Bruiser", "Tank"],
        "cc": 3.5,
    },  
    876: {
        "name": "Lillia",
        "adap": (0.1, 0.9),
        "roles": ["Jungle", "Engage", "Assassin"],
        "cc": 4.5,
    },  
    887: {
        "name": "Gwen",
        "adap": (0.1, 0.9),
        "roles": ["Top", "Bruiser", "Duelist"],
        "cc": 0.5,
    },  
    888: {
        "name": "Renata",
        "adap": (0.1, 0.9),
        "roles": ["Support", "HS", "Disengage"],
        "cc": 7,
    }, 
    893: {
        "name": "Aurora",
        "adap": (0.1, 0.9),
        "roles": ["Mid", "Mage", "Assassin"],
        "cc": 3.5,
    },  
    895: {
        "name": "Nilah",
        "adap": (0.95, 0.05),
        "roles": ["ADC", "Bot"],
        "cc": 3.5,
    },
    897: {
        "name": "K'Sante",
        "adap": (0.9, 0.1),
        "roles": ["Top", "Engage", "Tank"],
        "cc": 5.5,
    },  
    901: {
        "name": "Smolder",
        "adap": (0.9, 0.1),
        "roles": ["ADC", "Bot"],
        "cc": 0.5,
    }, 
    902: {
        "name": "Milio",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Disengage", "HS"],
        "cc": 3,
    },  
    910: {
        "name": "Hwei",
        "adap": (0.1, 0.9),
        "roles": ["Support", "Mid", "Mage"],
        "cc": 3,
    },  
    950: {
        "name": "Naafiri",
        "adap": (0.95, 0.05),
        "roles": ["Mid", "Jungle", "Top", "Assassin"],
        "cc": 0,
    },  
}