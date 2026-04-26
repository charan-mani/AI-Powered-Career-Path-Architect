from rest_framework import serializers
from .models import AIAnalysis, AIRecommendation, AIInteraction

class AIAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIAnalysis
        fields = [
            'id', 'analysis_type', 'input_data', 'output_data',
            'status', 'model_used', 'tokens_used', 'processing_time_ms',
            'error_message', 'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class AIRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIRecommendation
        fields = [
            'id', 'recommendation_type', 'content', 'priority',
            'status', 'feedback', 'feedback_score', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AIInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInteraction
        fields = [
            'id', 'interaction_type', 'prompt', 'response',
            'metadata', 'tokens_consumed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class AIChatSerializer(serializers.Serializer):
    """Serializer for AI chat interactions"""
    message = serializers.CharField(required=True)
    context = serializers.JSONField(required=False, default=dict)


class SkillGapAnalysisSerializer(serializers.Serializer):
    """Serializer for skill gap analysis request"""
    target_role = serializers.CharField(required=True)
    current_skills = serializers.ListField(child=serializers.CharField(), required=True)
    experience_level = serializers.CharField(required=False, allow_blank=True)


class ResumeAnalysisSerializer(serializers.Serializer):
    """Serializer for resume analysis request"""
    resume_text = serializers.CharField(required=True)
    target_role = serializers.CharField(required=False, allow_blank=True)