from django.contrib import admin
from .models import AIAnalysis, AIRecommendation, AIInteraction

@admin.register(AIAnalysis)
class AIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis_type', 'status', 'created_at', 'completed_at')
    list_filter = ('analysis_type', 'status')
    search_fields = ('user__email', 'analysis_type')
    readonly_fields = ('created_at', 'completed_at', 'processing_time_ms')

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_type', 'priority', 'status', 'created_at')
    list_filter = ('recommendation_type', 'priority', 'status')
    search_fields = ('user__email', 'recommendation_type')

@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'interaction_type', 'created_at', 'tokens_consumed')
    list_filter = ('interaction_type', 'created_at')
    search_fields = ('user__email',)