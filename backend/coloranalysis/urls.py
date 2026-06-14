from django.urls import path
from .views import ColorAnalysisCreateView, ColorAnalysisHistoryView, ColorAnalysisDeleteView

urlpatterns = [
    path("analyze/", ColorAnalysisCreateView.as_view(), name="color_analysis_create"),
    path("history/", ColorAnalysisHistoryView.as_view(), name="color_analysis_history"),
    path("<int:pk>/delete/", ColorAnalysisDeleteView.as_view(), name="color_analysis_delete"),
]
