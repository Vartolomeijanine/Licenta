from rest_framework import serializers
from .models import ColorAnalysisResult


class ColorAnalysisResultSerializer(serializers.ModelSerializer):
    originalImageUrl = serializers.SerializerMethodField()
    tryOnImages = serializers.SerializerMethodField()
    tryOnError = serializers.SerializerMethodField()

    class Meta:
        model = ColorAnalysisResult
        fields = (
            "id",
            "image",
            "season",
            "confidence",
            "created_at",
            "originalImageUrl",
            "tryOnImages",
            "tryOnError",
        )
        read_only_fields = (
            "confidence",
            "created_at",
            "season",
            "originalImageUrl",
            "tryOnImages",
            "tryOnError",
        )
        extra_kwargs = {
            'image': {'required': True}
        }

    def get_originalImageUrl(self, obj):
        if not obj.image:
            return None

        request = self.context.get("request") if hasattr(self, "context") else None

        if request:
            return request.build_absolute_uri(obj.image.url)

        return obj.image.url

    def get_tryOnImages(self, obj):
        return obj.try_on_images

    def get_tryOnError(self, obj):
        return obj.try_on_error
