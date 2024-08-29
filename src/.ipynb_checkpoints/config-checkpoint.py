### IMPORTS
from dotenv import load_dotenv
import os

# Set up RIOT API key (NA1 Region Only)
load_dotenv('.env')
api_key = os.getenv("RIOT_API_KEY")

# Data 
csv_file = "game_data.csv"
override_and_create_new_data = False