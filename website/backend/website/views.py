from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from .utils import *
import numpy as np
import pandas as pd

# Rate limiter
# TODO: switch to single rate limit calls later
rate_limiter = RateLimiter_Method([(97, 160)])

class Predict(APIView):
    def post(self, request):
        '''
            Takes in a prediction request and either returns Rate Limit error, Player not found error, or Match not started error
        '''

        name = (request.data['username'])

        # Check formatting is correct for the RIOT game name and tag
        if not is_correctly_formatted(name):
            return Response({"error": "Please ensure game name and tag line is valid"})
        
        # Rate limit check
        try:
            rate_limiter.acquire()
        except Exception as e:
            return Response({"error": e}, status=429)

        # Use RIOT API to get info on this person's live game
        try:
            features_tuple = get_features(name)
        except Exception as e:
            return Response({"error": str(e)})
        features = np.array(features_tuple, ndmin=2)

        # Check if there is a game & get feature details
        # features = np.array([[0.52, 0.4, 8.0, 0, 0, 0,0, 4, 3, 0, 4, 3,0, 1, 1, 3, 0,0]])
        features.reshape(1,-1)
        feature_names = [
            "adap_ratio", "balance_ratio", "cc_sum", "tank", "engage", "disengage",
            "adc", "mage", "assassin", "support", "mid", "top",
            "jungle", "bruiser", "duelist", "poke", "hs", "bot"
        ]
        features_df = pd.DataFrame(features, columns=feature_names)

        # Get prediction based on features
        outcome = predict_game(features_df)
        return Response({"result": True if outcome[0] == 1 else False})