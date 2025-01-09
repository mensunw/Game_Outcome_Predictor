from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer
from .utils import *

class Predict(APIView):
    def post(self, request):
        '''
            something here
        '''

        name = (request.data['username'])

        # Check formatting is correct for the RIOT game name and tag
        if not is_correctly_formatted(name):
            return Response({"error": "Please ensure game name and tag line is valid"})
        
        # Use RIOT API to get info on this person's live game

        # Check if there is a game

        # Check if the game is at least 15mins in
        return Response({"result": True})