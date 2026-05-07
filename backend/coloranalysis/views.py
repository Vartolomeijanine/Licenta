from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import ColorAnalysisResult
from .serializers import ColorAnalysisResultSerializer
from coloranalysis.ai.predictor import SeasonPredictorService


predictor_service = SeasonPredictorService()


class ColorAnalysisCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """
        Creează o analiză cromatică nouă pentru userul logat.
        """
        image_file = request.FILES.get("image")
        serializer = ColorAnalysisResultSerializer(data={"image": image_file})
        if serializer.is_valid():
            is_hair_visible = request.data.get("is_hair_visible", "yes")
            is_hair_natural = request.data.get("is_hair_natural", "yes")
            natural_hair_color = request.data.get("natural_hair_color")

            # Save the uploaded image first so the predictor can read it from disk.
            instance = serializer.save(user=request.user, season="spring", confidence=None)

            analysis_result = predictor_service.predict_from_image(
                instance.image.path,
                is_hair_visible=is_hair_visible,
                is_hair_natural=is_hair_natural,
                natural_hair_color=natural_hair_color,
            )

            if not analysis_result.get("success"):
                return Response(analysis_result, status=status.HTTP_400_BAD_REQUEST)

            prediction = analysis_result["prediction"]
            instance.season = prediction["predicted_season"]
            instance.confidence = prediction.get("confidence")
            instance.save(update_fields=["season", "confidence"])
            
            response_data = {
                "id": instance.id,
                "image": request.build_absolute_uri(instance.image.url) if instance.image else None,
                "season": instance.season,
                "confidence": instance.confidence,
                "created_at": instance.created_at,
                "predicted_season_label": prediction.get("predicted_season_label"),
                "message": f"Analiză completă! Sezonul detectat: {instance.season.upper()} (confidence: {instance.confidence})",
                "features": analysis_result.get("features"),
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


class ColorAnalysisDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        analysis = get_object_or_404(ColorAnalysisResult, pk=pk, user=request.user)
        analysis.delete()
        return Response({"message": "Analysis deleted successfully."}, status=status.HTTP_200_OK)
