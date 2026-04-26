from django.db import models
from users.models import User
from django.utils import timezone

class Roadmap(models.Model):
    """Career roadmap model"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    target_role = models.CharField(max_length=100)
    target_industry = models.CharField(max_length=100, blank=True, null=True)
    generated_by_ai = models.BooleanField(default=True)
    
    # Roadmap settings
    total_duration_months = models.IntegerField(default=12)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    
    # Metrics
    current_step_index = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    
    # AI Analysis
    skill_gap_analysis = models.JSONField(default=dict)
    market_insights = models.JSONField(default=dict)
    salary_projection = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmaps'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['target_role']),
            models.Index(fields=['is_completed']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"
    
    def update_progress(self):
        """Update completion percentage based on completed steps"""
        total_steps = self.steps.count()
        if total_steps == 0:
            self.completion_percentage = 0.0
        else:
            completed_steps = self.steps.filter(is_completed=True).count()
            self.completion_percentage = (completed_steps / total_steps) * 100
            self.is_completed = self.completion_percentage >= 100
        self.save()


class RoadmapStep(models.Model):
    """Individual steps within a roadmap"""
    STEP_TYPE_CHOICES = [
        ('learning', 'Learning'),
        ('project', 'Project'),
        ('certification', 'Certification'),
        ('networking', 'Networking'),
        ('job_application', 'Job Application'),
        ('interview_prep', 'Interview Preparation')
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='steps')
    step_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Step details
    step_type = models.CharField(max_length=50, choices=STEP_TYPE_CHOICES, default='learning')
    
    # Duration
    estimated_duration_hours = models.IntegerField(default=40)
    actual_duration_hours = models.IntegerField(null=True, blank=True)
    recommended_timeline = models.CharField(max_length=100, blank=True, null=True)
    
    # Resources and skills
    resources = models.JSONField(default=list)
    skills_to_develop = models.JSONField(default=list)
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    # Progress tracking
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    user_notes = models.TextField(blank=True, null=True)
    difficulty_rating = models.IntegerField(null=True, blank=True)
    satisfaction_score = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmap_steps'
        ordering = ['roadmap', 'step_number']
        unique_together = ['roadmap', 'step_number']
        indexes = [
            models.Index(fields=['roadmap', 'step_number']),
            models.Index(fields=['is_completed']),
        ]

    def __str__(self):
        return f"{self.roadmap.title} - Step {self.step_number}: {self.title}"


class LearningResource(models.Model):
    """Learning resources associated with steps"""
    RESOURCE_TYPE_CHOICES = [
        ('course', 'Online Course'),
        ('book', 'Book'),
        ('article', 'Article'),
        ('video', 'Video'),
        ('tutorial', 'Tutorial'),
        ('documentation', 'Documentation'),
        ('podcast', 'Podcast'),
        ('tool', 'Tool/Software'),
    ]

    COMPLETION_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]

    step = models.ForeignKey(RoadmapStep, on_delete=models.CASCADE, related_name='learning_resources')
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    url = models.URLField()
    description = models.TextField(blank=True, null=True)
    duration_estimate = models.CharField(max_length=50, blank=True, null=True)
    difficulty_level = models.CharField(max_length=20, blank=True, null=True)
    is_free = models.BooleanField(default=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    completion_status = models.CharField(max_length=20, choices=COMPLETION_CHOICES, default='not_started')
    user_rating = models.IntegerField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'learning_resources'
        indexes = [
            models.Index(fields=['step', 'completion_status']),
        ]

    def __str__(self):
        return f"{self.title} ({self.resource_type})"


class ProgressUpdate(models.Model):
    """Track user progress updates"""
    UPDATE_TYPE_CHOICES = [
        ('step_completed', 'Step Completed'),
        ('step_started', 'Step Started'),
        ('note_added', 'Note Added'),
        ('resource_completed', 'Resource Completed'),
        ('roadmap_created', 'Roadmap Created'),
        ('roadmap_modified', 'Roadmap Modified'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='progress_updates')
    step = models.ForeignKey(RoadmapStep, on_delete=models.CASCADE, null=True, blank=True)
    update_type = models.CharField(max_length=50, choices=UPDATE_TYPE_CHOICES)
    description = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'progress_updates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['roadmap', '-created_at']),
        ]

    def __str__(self):
        return f"{self.roadmap.title} - {self.update_type}"


class SkillDevelopment(models.Model):
    """Track skill development progress"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_development')
    skill_name = models.CharField(max_length=100)
    current_level = models.CharField(max_length=20)
    target_level = models.CharField(max_length=20)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, null=True, blank=True)
    progress_percentage = models.FloatField(default=0.0)
    resources_completed = models.IntegerField(default=0)
    total_resources = models.IntegerField(default=0)
    last_practiced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'skill_development'
        unique_together = ['user', 'skill_name', 'roadmap']
        indexes = [
            models.Index(fields=['user', 'skill_name']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.skill_name}"
