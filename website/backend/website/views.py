from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Item
from .serializers import ItemSerializer

class TestEndpoint(APIView):
    def get(self, request):
        return Response({"message": "Backend is working!"})