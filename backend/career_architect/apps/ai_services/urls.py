from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIAnalysisViewSet, AIRecommendationViewSet,
    AIInteractionViewSet, AIDashboardViewSet
)

router = DefaultRouter()
router.register(r'analyses', AIAnalysisViewSet, basename='ai-analysis')
router.register(r'recommendations', AIRecommendationViewSet, basename='ai-recommendation')
router.register(r'interactions', AIInteractionViewSet, basename='ai-interaction')
router.register(r'dashboard', AIDashboardViewSet, basename='ai-dashboard')

urlpatterns = [
    path('', include(router.urls)),
    # Add explicit stats endpoint that matches frontend
    path('dashboard/stats/', AIDashboardViewSet.as_view({'get': 'stats'}), name='ai-dashboard-stats'),
]