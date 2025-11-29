from rest_framework import serializers
from .models import ColorAnalysisResult


class ColorAnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorAnalysisResult
        fields = ("id", "image", "season", "confidence", "created_at")
        read_only_fields = ("confidence", "created_at")
