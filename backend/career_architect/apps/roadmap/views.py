from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from .models import (
    Roadmap, RoadmapStep, LearningResource,
    ProgressUpdate, SkillDevelopment
)
from .serializers import (
    RoadmapSerializer, RoadmapStepSerializer, LearningResourceSerializer,
    ProgressUpdateSerializer, SkillDevelopmentSerializer,
    RoadmapCreateSerializer, RoadmapGenerateSerializer
)
from ai_services.gemini_client import GeminiClient
import re
import logging

logger = logging.getLogger(__name__)


class RoadmapViewSet(viewsets.ModelViewSet):
    """ViewSet for Roadmap model"""
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter roadmaps to current user"""
        user = self.request.user
        logger.info(f"Getting roadmaps for user: {user.email if user.is_authenticated else 'Anonymous'}")
        
        queryset = Roadmap.objects.filter(user=self.request.user)
        
        # Apply filters from query params
        status_filter = self.request.query_params.get('status')
        if status_filter == 'completed':
            queryset = queryset.filter(is_completed=True)
        elif status_filter == 'active':
            queryset = queryset.filter(is_completed=False)
        elif status_filter == 'paused':
            pass
        
        # Apply sorting
        sort_by = self.request.query_params.get('sortBy', 'created_at')
        sort_order = self.request.query_params.get('sortOrder', 'desc')
        if sort_order == 'desc':
            queryset = queryset.order_by(f'-{sort_by}')
        else:
            queryset = queryset.order_by(sort_by)
        
        return queryset

    def list(self, request, *args, **kwargs):
        """Override list to add logging"""
        logger.info(f"List roadmaps called by user: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def create_manual(self, request):
        """Create a manual roadmap"""
        serializer = RoadmapCreateSerializer(data=request.data)
        if serializer.is_valid():
            roadmap = Roadmap.objects.create(
                user=request.user,
                title=serializer.validated_data.get('title', 
                      f"Path to {serializer.validated_data['target_role']}"),
                description=serializer.validated_data.get('description', ''),
                target_role=serializer.validated_data['target_role'],
                target_industry=serializer.validated_data.get('target_industry', ''),
                total_duration_months=serializer.validated_data['timeframe_months'],
                difficulty_level=serializer.validated_data.get('difficulty_level', 'intermediate'),
                generated_by_ai=False
            )
            return Response(RoadmapSerializer(roadmap).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _parse_roadmap_steps(self, roadmap, full_text):
        """
        Parse the AI-generated text into individual steps with resources
        Returns the list of created steps
        """
        created_steps = []
        
        # Pattern to find step sections
        # Looks for "### Step X:" or "Step X:" and captures until next step or end
        step_pattern = r'(?:^|\n)(?:###?\s*)?Step\s+(\d+)[:\.]\s*([^\n]+)\n(.*?)(?=\n(?:###?\s*)?Step\s+\d+[:\.]|\Z)'
        step_matches = re.findall(step_pattern, full_text, re.DOTALL | re.IGNORECASE)
        
        if not step_matches:
            # Try alternative pattern with just "Step X:" without the ###
            step_pattern = r'(?:^|\n)Step\s+(\d+)[:\.]\s*([^\n]+)\n(.*?)(?=\nStep\s+\d+[:\.]|\Z)'
            step_matches = re.findall(step_pattern, full_text, re.DOTALL | re.IGNORECASE)
        
        logger.info(f"Found {len(step_matches)} steps in AI response")
        
        for step_num, title, content in step_matches:
            step_num = int(step_num)
            
            # Extract duration if present
            duration_match = re.search(r'\*\*Duration:\*\*\s*(\d+(?:-\d+)?)\s*hours?', content, re.IGNORECASE)
            duration = 40  # Default
            if duration_match:
                duration_str = duration_match.group(1)
                if '-' in duration_str:
                    duration = int(duration_str.split('-')[0].strip())
                else:
                    duration = int(duration_str)
            
            # Extract skills
            skills_match = re.search(r'\*\*Skills to Learn:\*\*\s*(.*?)(?=\n\n|\*\*|$)', content, re.DOTALL | re.IGNORECASE)
            skills = []
            if skills_match:
                skill_text = skills_match.group(1)
                # Split by commas, bullets, or line breaks
                skills = [s.strip() for s in re.split(r'[,•\n]', skill_text) if s.strip() and len(s.strip()) > 2]
                skills = skills[:10]  # Limit to 10 skills
            
            # Create the step
            step = RoadmapStep.objects.create(
                roadmap=roadmap,
                step_number=step_num,
                title=f"Step {step_num}: {title.strip()}",
                description=content.strip(),
                step_type='learning',
                estimated_duration_hours=duration,
                skills_to_develop=skills
            )
            
            # Extract resources
            resources_section = re.search(r'\*\*Recommended Resources:\*\*\s*(.*?)(?=\n\n|\*\*|$)', content, re.DOTALL | re.IGNORECASE)
            if resources_section:
                resource_text = resources_section.group(1)
                
                # Parse bullet points with links
                # Pattern for markdown links: [Title](url)
                link_pattern = r'\[\s*([^\]]+?)\s*\]\(\s*([^)]+?)\s*\)'
                links = re.findall(link_pattern, resource_text)
                
                for res_title, res_url in links:
                    # Try to extract platform and price from surrounding text
                    platform = 'Various'
                    is_free = True
                    
                    # Look for platform name near the link
                    platform_match = re.search(rf'{re.escape(res_title)}[^-–]*[-–]\s*([^-–\n]+)', resource_text)
                    if platform_match:
                        platform = platform_match.group(1).strip()
                    
                    # Check if it's paid
                    if 'paid' in resource_text.lower() or 'premium' in resource_text.lower():
                        is_free = False
                    
                    if res_title and res_url:
                        try:
                            LearningResource.objects.create(
                                step=step,
                                resource_type='course',
                                title=res_title.strip(),
                                url=res_url.strip(),
                                description=f"Resource for {step.title}",
                                platform=platform.strip(),
                                is_free=is_free,
                                completion_status='not_started'
                            )
                        except Exception as e:
                            logger.error(f"Error creating learning resource: {e}")
            
            created_steps.append(step)
            logger.info(f"Created step {step_num}: {step.title}")
        
        return created_steps

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate AI-powered roadmap with step parsing"""
        serializer = RoadmapGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Get user skills if available
            user_skills = list(request.user.skills.values_list('skill_name', flat=True))
            
            # Prepare data for AI
            ai_data = {
                'target_role': serializer.validated_data['target_role'],
                'target_industry': serializer.validated_data.get('target_industry', ''),
                'timeframe_months': serializer.validated_data['timeframe_months'],
                'current_skills': serializer.validated_data.get('current_skills', user_skills),
                'experience_level': serializer.validated_data.get('experience_level', ''),
            }

            # Generate roadmap with AI (returns text)
            gemini_client = GeminiClient()
            roadmap_data = gemini_client.generate_roadmap(ai_data)
            
            # Get the full text response
            full_text = roadmap_data.get('description', '')
            
            if not full_text:
                raise Exception("Empty response from AI")

            # Create roadmap instance with the full text description
            roadmap = Roadmap.objects.create(
                user=request.user,
                title=f"AI Path to {serializer.validated_data['target_role']}",
                description=full_text,  # Store the full text
                target_role=serializer.validated_data['target_role'],
                target_industry=serializer.validated_data.get('target_industry', ''),
                generated_by_ai=True,
                total_duration_months=serializer.validated_data['timeframe_months'],
                skill_gap_analysis={},
                market_insights={},
                salary_projection={}
            )

            # Parse the text to extract individual steps
            created_steps = self._parse_roadmap_steps(roadmap, full_text)

            # If no steps were parsed, create a fallback single step
            if not created_steps:
                logger.warning("No steps could be parsed, creating fallback step")
                step = RoadmapStep.objects.create(
                    roadmap=roadmap,
                    step_number=1,
                    title=f"Complete Roadmap to {serializer.validated_data['target_role']}",
                    description=full_text[:500] + "...",
                    step_type='learning',
                    estimated_duration_hours=serializer.validated_data['timeframe_months'] * 40,
                    skills_to_develop=user_skills
                )
                created_steps.append(step)

            # Create progress update
            ProgressUpdate.objects.create(
                roadmap=roadmap,
                update_type='roadmap_created',
                description=f"Generated AI roadmap for {serializer.validated_data['target_role']} with {len(created_steps)} steps"
            )

            # Refresh the roadmap to include all related data
            roadmap.refresh_from_db()
            
            # Return the serialized roadmap
            serializer = RoadmapSerializer(roadmap, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Failed to generate roadmap: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Failed to generate roadmap: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update step progress"""
        roadmap = self.get_object()
        step_id = request.data.get('step_id')
        is_completed = request.data.get('is_completed', False)
        notes = request.data.get('notes', '')
        actual_hours = request.data.get('actual_hours')

        try:
            step = roadmap.steps.get(id=step_id)
            step.is_completed = is_completed
            if is_completed:
                step.completion_date = timezone.now()
            if notes:
                step.user_notes = notes
            if actual_hours:
                step.actual_duration_hours = actual_hours
            step.save()

            # Update roadmap progress
            roadmap.update_progress()

            # Create progress update
            ProgressUpdate.objects.create(
                roadmap=roadmap,
                step=step,
                update_type='step_completed' if is_completed else 'step_modified',
                description=f"Step '{step.title}' {'completed' if is_completed else 'updated'}"
            )

            return Response({'message': 'Progress updated successfully'})

        except RoadmapStep.DoesNotExist:
            return Response({'error': 'Step not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get roadmap analytics"""
        roadmap = self.get_object()
        
        # Calculate analytics
        total_steps = roadmap.steps.count()
        completed_steps = roadmap.steps.filter(is_completed=True).count()
        
        # Time spent
        completed_steps_with_duration = roadmap.steps.filter(
            is_completed=True, actual_duration_hours__isnull=False
        )
        total_time_spent = sum(step.actual_duration_hours or 0 for step in completed_steps_with_duration)
        
        # Estimated remaining time
        remaining_steps = roadmap.steps.filter(is_completed=False)
        estimated_remaining = sum(step.estimated_duration_hours or 0 for step in remaining_steps)
        
        # Step type breakdown
        step_types = roadmap.steps.values('step_type').annotate(
            count=Count('id'),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        analytics_data = {
            'roadmap_id': roadmap.id,
            'roadmap_title': roadmap.title,
            'completion_percentage': roadmap.completion_percentage,
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'total_time_spent_hours': total_time_spent,
            'estimated_remaining_hours': estimated_remaining,
            'step_type_breakdown': list(step_types),
            'created_at': roadmap.created_at,
            'last_updated': roadmap.updated_at
        }
        
        return Response(analytics_data)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        user = request.user
        roadmaps = Roadmap.objects.filter(user=user)
        
        # Calculate stats
        total_roadmaps = roadmaps.count()
        completed_roadmaps = roadmaps.filter(is_completed=True).count()
        in_progress_roadmaps = roadmaps.filter(is_completed=False).count()
        
        # Average completion
        avg_completion = roadmaps.aggregate(Avg('completion_percentage'))['completion_percentage__avg'] or 0
        
        # Total time invested
        total_time = 0
        for roadmap in roadmaps:
            completed = roadmap.steps.filter(
                is_completed=True, actual_duration_hours__isnull=False
            )
            total_time += sum(step.actual_duration_hours or 0 for step in completed)
        
        # Recent updates
        recent_updates = ProgressUpdate.objects.filter(
            roadmap__user=user
        ).order_by('-created_at')[:5]
        
        stats = {
            'total_roadmaps': total_roadmaps,
            'completed_roadmaps': completed_roadmaps,
            'in_progress_roadmaps': in_progress_roadmaps,
            'average_completion': round(avg_completion, 1),
            'total_time_invested': total_time,
            'recent_updates': ProgressUpdateSerializer(recent_updates, many=True).data
        }
        
        return Response(stats)


class RoadmapStepViewSet(viewsets.ModelViewSet):
    """ViewSet for RoadmapStep model"""
    serializer_class = RoadmapStepSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = RoadmapStep.objects.filter(roadmap__user=user)
        
        # Filter by roadmap
        roadmap_id = self.request.query_params.get('roadmap')
        if roadmap_id:
            queryset = queryset.filter(roadmap_id=roadmap_id)
        
        return queryset

    def perform_create(self, serializer):
        roadmap_id = self.request.data.get('roadmap')
        try:
            roadmap = Roadmap.objects.get(id=roadmap_id, user=self.request.user)
            step_number = roadmap.steps.count() + 1
            serializer.save(roadmap=roadmap, step_number=step_number)
            
            # Create progress update
            ProgressUpdate.objects.create(
                roadmap=roadmap,
                step=serializer.instance,
                update_type='step_started',
                description=f"Added step: {serializer.instance.title}"
            )
        except Roadmap.DoesNotExist:
            from rest_framework import serializers
            raise serializers.ValidationError({"roadmap": "Invalid roadmap ID"})

    def perform_update(self, serializer):
        instance = serializer.save()
        # Update roadmap progress
        instance.roadmap.update_progress()


class LearningResourceViewSet(viewsets.ModelViewSet):
    """ViewSet for LearningResource model"""
    serializer_class = LearningResourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all resources from all steps of all roadmaps belonging to the user
        queryset = LearningResource.objects.filter(step__roadmap__user=user)
        
        # Apply filters from query params
        resource_type = self.request.query_params.get('type')
        if resource_type and resource_type != 'all':
            queryset = queryset.filter(resource_type=resource_type)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty and difficulty != 'all':
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        # Order by newest first
        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark resource as completed"""
        resource = self.get_object()
        resource.completion_status = 'completed'
        resource.completed_date = timezone.now()
        resource.user_rating = request.data.get('rating')
        resource.notes = request.data.get('notes', '')
        resource.save()
        
        return Response({'message': 'Resource marked as completed'})

    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Toggle bookmark status (using a custom field or tracking in frontend)"""
        return Response({'message': 'Bookmark toggled'})


class ProgressUpdateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ProgressUpdate model (read-only)"""
    serializer_class = ProgressUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ProgressUpdate.objects.filter(roadmap__user=user).order_by('-created_at')


class SkillDevelopmentViewSet(viewsets.ModelViewSet):
    """ViewSet for SkillDevelopment model"""
    serializer_class = SkillDevelopmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SkillDevelopment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Update skill development progress"""
        skill_dev = self.get_object()
        resources_completed = request.data.get('resources_completed', 0)
        
        skill_dev.resources_completed += resources_completed
        if skill_dev.total_resources > 0:
            skill_dev.progress_percentage = (skill_dev.resources_completed / skill_dev.total_resources) * 100
        skill_dev.last_practiced = timezone.now()
        skill_dev.save()
        
        return Response({'message': 'Progress updated successfully'})