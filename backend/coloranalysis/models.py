from django.conf import settings
from django.db import models


class ColorAnalysisResult(models.Model):
    SEASONS = [
        ("spring", "Spring"),
        ("summer", "Summer"),
        ("autumn", "Autumn"),
        ("winter", "Winter"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="color_analyses"
    )

    image = models.ImageField(upload_to="color_analysis/")

    season = models.CharField(
        max_length=20,
        choices=SEASONS
    )

    confidence = models.FloatField(
        null=True,
        blank=True,
        help_text="Confidence score between 0 and 1."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.season} ({self.created_at.date()})"
