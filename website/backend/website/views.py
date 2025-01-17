from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from .utils import *
import numpy as np
import pandas as pd

class Predict(APIView):
    def post(self, request):
        '''
            something here
        '''

        name = (request.data['username'])

        # Check formatting is correct for the RIOT game name and tag
        if not is_correctly_formatted(name):
            return Response({"error": "Please ensure game name and tag line is valid"})
        
        # todo: rate limit
        # Use RIOT API to get info on this person's live game
        get_features(name)

        # Check if there is a game & get feature details
        features = np.array([[0.52, 0.4, 8.0, 0, 0, 0,0, 4, 3, 0, 4, 3,0, 1, 1, 3, 0,0]])
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