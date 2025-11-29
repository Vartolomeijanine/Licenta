from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..permissions import IsAdmin, IsColleague,IsPassenger

class AdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": f"Hello, Admin {request.user.email}!"})

class ColleagueView(APIView):
    permission_classes = [IsAuthenticated, IsColleague]

    def get(self, request):
        return Response({"message": f"Hello, Colleague {request.user.email}!"})

class PassengerView(APIView):
    permission_classes = [IsAuthenticated, IsPassenger]

    def get(self, request):
        return Response({"message": f"Hello, Passenger {request.user.email}!"})