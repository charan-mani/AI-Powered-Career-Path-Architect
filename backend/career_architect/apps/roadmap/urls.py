from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoadmapViewSet, RoadmapStepViewSet, LearningResourceViewSet,
    ProgressUpdateViewSet, SkillDevelopmentViewSet
)

router = DefaultRouter()
router.register(r'roadmaps', RoadmapViewSet, basename='roadmap')
router.register(r'steps', RoadmapStepViewSet, basename='step')
router.register(r'resources', LearningResourceViewSet, basename='resource')
router.register(r'updates', ProgressUpdateViewSet, basename='update')
router.register(r'skill-development', SkillDevelopmentViewSet, basename='skill-development')

urlpatterns = [
    path('', include(router.urls)),
]