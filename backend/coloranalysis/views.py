from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ColorAnalysisResult
from .serializers import ColorAnalysisResultSerializer


class ColorAnalysisCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Creează o analiză cromatică nouă pentru userul logat.
        Deocamdată sezonul vine din request (season), mai târziu îl calculează AI-ul.
        """
        serializer = ColorAnalysisResultSerializer(data=request.data)
        if serializer.is_valid():
            # aici, pe viitor, vei apela modelul AI și seta season/confidence
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ColorAnalysisHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Returnează istoricul analizelor cromatice pentru userul logat.
        """
        analyses = ColorAnalysisResult.objects.filter(
            user=request.user
        ).order_by("-created_at")
        serializer = ColorAnalysisResultSerializer(analyses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
