from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
import random

from .models import ColorAnalysisResult
from .serializers import ColorAnalysisResultSerializer


class ColorAnalysisCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Creează o analiză cromatică nouă pentru userul logat.
        MOCK: Returnează sezon random + confidence score
        """
        serializer = ColorAnalysisResultSerializer(data=request.data)
        if serializer.is_valid():
            # MOCK AI - returnează sezon random cu confidence
            seasons = ["spring", "summer", "autumn", "winter"]
            mock_season = random.choice(seasons)
            mock_confidence = round(random.uniform(0.7, 0.99), 2)
            
            # Salvează cu sezonul mock și confidence
            instance = serializer.save(
                user=request.user,
                season=mock_season,
                confidence=mock_confidence
            )
            
            response_data = {
                "id": instance.id,
                "image": request.build_absolute_uri(instance.image.url) if instance.image else None,
                "season": instance.season,
                "confidence": instance.confidence,
                "created_at": instance.created_at,
                "message": f"Analiză completă! Sezonul detectat: {instance.season.upper()} (confidence: {instance.confidence})"
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

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
