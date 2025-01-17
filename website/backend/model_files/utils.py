import requests

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
        "X-Riot-Token": api_key 
    }
    
    response = requests.get(request_url, headers=headers)

    numFailedRetries = 0
    while response.status_code != 200: # while loop here for later when we want to ignore error 429
        # Retry limiter
        if(numFailedRetries >= 2):
            print(f"Exceeded retry limit of 2")
            return None
            
        if(response.status_code == 429):
            # Not success but is 429 API limit error
            print("Status 429 detected")
            return None
        elif(response.status_code == 404):
            # Data not found
            print("Error: Data not found")
            return None
        else:
            # Not success and not 429 API limit error
            print(f"Failed to fetch data: {response.status_code}")
            print(f'Request url: {request_url}')
            return None
        
    # (finally) status of 200
    #debug2 = response.headers.get("X-App-Rate-Limit-Count")
    #print(f"app-rate-count: {debug2}")
    return response.json()

def get_live_features(summoner_id, rate_limiter):
    
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
    match_info = apiCallHandler(f'https://na1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{summoner_id}', [rate_limiter])
    if match_info == None:
        return None
    participants = match_info['participants']

    # Get ally team
    team = -1
    for participant in participants:
        if(participant['puuid'] == summoner_id):
            team = participant['teamId']
    if team == -1:
        return None
    
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
        team_cmapping = champ_mapping.map[team_champions[i]]
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