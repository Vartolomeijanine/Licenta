from django.urls import path
from .views import ColorAnalysisCreateView, ColorAnalysisHistoryView

urlpatterns = [
    path("analyze/", ColorAnalysisCreateView.as_view(), name="color_analysis_create"),
    path("history/", ColorAnalysisHistoryView.as_view(), name="color_analysis_history"),
]
