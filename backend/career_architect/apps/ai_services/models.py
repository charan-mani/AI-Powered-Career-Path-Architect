from django.db import models
from users.models import User

class AIAnalysis(models.Model):
    """AI analysis records"""
    ANALYSIS_TYPES = [
        ('roadmap', 'Roadmap Generation'),
        ('skill_gap', 'Skill Gap Analysis'),
        ('resume', 'Resume Analysis'),
        ('career_suggestion', 'Career Suggestion'),
        ('interview_prep', 'Interview Preparation'),
        ('market_insights', 'Market Insights'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    model_used = models.CharField(max_length=50, default='gemini-3-flash-preview')
    tokens_used = models.IntegerField(default=0)
    processing_time_ms = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_analyses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.analysis_type} - {self.status}"


class AIRecommendation(models.Model):
    """AI-generated recommendations"""
    RECOMMENDATION_TYPES = [
        ('skill', 'Skill Recommendation'),
        ('course', 'Course Recommendation'),
        ('job', 'Job Recommendation'),
        ('career', 'Career Path Recommendation'),
        ('resource', 'Resource Recommendation'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_recommendations')
    analysis = models.ForeignKey(AIAnalysis, on_delete=models.CASCADE, null=True, blank=True)
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPES)
    content = models.JSONField(default=dict)
    priority = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True)
    feedback_score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_recommendations'
        ordering = ['priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.recommendation_type}"


class AIInteraction(models.Model):
    """User interactions with AI"""
    INTERACTION_TYPES = [
        ('chat', 'Chat'),
        ('question', 'Question'),
        ('feedback', 'Feedback'),
        ('analysis_request', 'Analysis Request'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_interactions')
    interaction_type = models.CharField(max_length=50, choices=INTERACTION_TYPES)
    prompt = models.TextField()
    response = models.TextField()
    metadata = models.JSONField(default=dict)
    tokens_consumed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_interactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.interaction_type}"
