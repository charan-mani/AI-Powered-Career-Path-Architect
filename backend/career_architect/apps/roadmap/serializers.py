from rest_framework import serializers
from .models import (
    Roadmap, RoadmapStep, LearningResource,
    ProgressUpdate, SkillDevelopment
)

class LearningResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningResource
        fields = [
            'id', 'resource_type', 'title', 'url', 'description',
            'duration_estimate', 'difficulty_level', 'is_free', 'platform',
            'completion_status', 'user_rating', 'completed_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoadmapStepSerializer(serializers.ModelSerializer):
    learning_resources = LearningResourceSerializer(many=True, read_only=True)
    depends_on_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=RoadmapStep.objects.all(), source='depends_on', 
        write_only=True, required=False
    )
    depends_on = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    skills_to_develop = serializers.JSONField(default=list, required=False)

    class Meta:
        model = RoadmapStep
        fields = [
            'id', 'step_number', 'title', 'description', 'step_type',
            'estimated_duration_hours', 'actual_duration_hours',
            'recommended_timeline', 'resources', 'skills_to_develop',
            'is_completed', 'completion_date', 'user_notes',
            'difficulty_rating', 'satisfaction_score', 'learning_resources',
            'depends_on', 'depends_on_ids', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'completion_date']

    def validate_skills_to_develop(self, value):
        """Ensure skills_to_develop is a list"""
        if value is None:
            return []
        return value


class RoadmapSerializer(serializers.ModelSerializer):
    steps = RoadmapStepSerializer(many=True, read_only=True)
    total_steps = serializers.IntegerField(read_only=True)
    completed_steps = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Roadmap
        fields = [
            'id', 'title', 'description', 'target_role', 'target_industry',
            'generated_by_ai', 'total_duration_months', 'difficulty_level',
            'current_step_index', 'completion_percentage', 'is_completed',
            'skill_gap_analysis', 'market_insights', 'salary_projection',
            'total_steps', 'completed_steps', 'steps',
            'created_at', 'updated_at', 'last_accessed'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_accessed',
            'total_steps', 'completed_steps'
        ]
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_steps'] = instance.steps.count()
        data['completed_steps'] = instance.steps.filter(is_completed=True).count()
        return data


class ProgressUpdateSerializer(serializers.ModelSerializer):
    step_title = serializers.CharField(source='step.title', read_only=True)
    roadmap_title = serializers.CharField(source='roadmap.title', read_only=True)

    class Meta:
        model = ProgressUpdate
        fields = [
            'id', 'update_type', 'description', 'metadata',
            'step', 'step_title', 'roadmap', 'roadmap_title',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SkillDevelopmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillDevelopment
        fields = [
            'id', 'skill_name', 'current_level', 'target_level',
            'progress_percentage', 'resources_completed', 'total_resources',
            'last_practiced', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoadmapCreateSerializer(serializers.Serializer):
    """Serializer for creating a new roadmap"""
    title = serializers.CharField(max_length=200, required=False)
    target_role = serializers.CharField(max_length=100, required=True)
    target_industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    timeframe_months = serializers.IntegerField(min_value=1, max_value=60, default=12)
    difficulty_level = serializers.ChoiceField(
        choices=['beginner', 'intermediate', 'advanced'],
        default='intermediate'
    )
    include_salary_data = serializers.BooleanField(default=True)
    include_market_insights = serializers.BooleanField(default=True)


class RoadmapGenerateSerializer(serializers.Serializer):
    """Serializer for AI-generated roadmap"""
    target_role = serializers.CharField(max_length=100, required=True)
    target_industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    timeframe_months = serializers.IntegerField(min_value=1, max_value=60, default=12)
    current_skills = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    experience_level = serializers.CharField(required=False, allow_blank=True)
    preferred_learning_style = serializers.CharField(required=False, allow_blank=True)
    include_salary_data = serializers.BooleanField(default=True)
    include_market_insights = serializers.BooleanField(default=True)