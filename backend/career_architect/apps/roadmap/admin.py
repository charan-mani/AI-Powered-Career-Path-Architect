from django.contrib import admin
from .models import (
    Roadmap, RoadmapStep, LearningResource,
    ProgressUpdate, SkillDevelopment
)

@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'target_role', 'completion_percentage', 
                   'is_completed', 'created_at')
    list_filter = ('is_completed', 'generated_by_ai', 'difficulty_level')
    search_fields = ('title', 'description', 'target_role', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'last_accessed')
    ordering = ('-created_at',)

@admin.register(RoadmapStep)
class RoadmapStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'step_number', 'step_type', 'is_completed')
    list_filter = ('step_type', 'is_completed')
    search_fields = ('title', 'description', 'roadmap__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'step', 'resource_type', 'is_free', 'completion_status')
    list_filter = ('resource_type', 'is_free', 'completion_status')
    search_fields = ('title', 'description', 'url')

@admin.register(ProgressUpdate)
class ProgressUpdateAdmin(admin.ModelAdmin):
    list_display = ('roadmap', 'update_type', 'created_at')
    list_filter = ('update_type', 'created_at')
    search_fields = ('roadmap__title', 'description')

@admin.register(SkillDevelopment)
class SkillDevelopmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill_name', 'current_level', 'progress_percentage')
    list_filter = ('current_level',)
    search_fields = ('user__email', 'skill_name')