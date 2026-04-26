from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg
from django.utils import timezone
from .models import AIAnalysis, AIRecommendation, AIInteraction
from .serializers import (
    AIAnalysisSerializer, AIRecommendationSerializer,
    AIInteractionSerializer, AIChatSerializer,
    SkillGapAnalysisSerializer, ResumeAnalysisSerializer
)
from .gemini_client import GeminiClient
from .prompt_templates import (
    get_skill_gap_text_prompt,
    get_resume_analysis_prompt,
    get_career_suggestions_prompt,
    get_market_insights_text_prompt,
    get_roadmap_text_prompt
)
import time
import logging
import google.generativeai as genai  # ADD THIS IMPORT

logger = logging.getLogger(__name__)
gemini_client = GeminiClient()


class AIAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for AI Analysis - NO FALLBACKS, NO MOCK DATA"""
    serializer_class = AIAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AIAnalysis.objects.filter(user=self.request.user)
        
        # Filter by type
        analysis_type = self.request.query_params.get('type')
        if analysis_type:
            queryset = queryset.filter(analysis_type=analysis_type)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def skill_gap(self, request):
        """Perform skill gap analysis - returns text, no fallbacks"""
        serializer = SkillGapAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create analysis record
        analysis = AIAnalysis.objects.create(
            user=request.user,
            analysis_type='skill_gap',
            input_data=serializer.validated_data,
            status='processing'
        )

        try:
            start_time = time.time()
            
            # Generate prompt and call Gemini
            prompt = get_skill_gap_text_prompt(
                target_role=serializer.validated_data['target_role'],
                current_skills=serializer.validated_data['current_skills'],
                experience_level=serializer.validated_data.get('experience_level', '')
            )
            
            response = gemini_client.generate_content(prompt)
            
            # Update analysis record - store the text response
            analysis.output_data = {
                'text': response['text'],
                'structured': None
            }
            analysis.status = 'completed'
            analysis.processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = timezone.now()
            analysis.save()

            # Return the text response directly
            return Response({
                'text': response['text']
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()
            # Return the actual error - no fallbacks
            return Response(
                {'error': f'Skill gap analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def resume(self, request):
        """Analyze resume - no fallbacks"""
        serializer = ResumeAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        analysis = AIAnalysis.objects.create(
            user=request.user,
            analysis_type='resume',
            input_data=serializer.validated_data,
            status='processing'
        )

        try:
            start_time = time.time()
            
            prompt = get_resume_analysis_prompt(
                resume_text=serializer.validated_data['resume_text'],
                target_role=serializer.validated_data.get('target_role', '')
            )
            
            response = gemini_client.generate_content(prompt)
            
            analysis.output_data = {
                'text': response['text'],
                'structured': None
            }
            analysis.status = 'completed'
            analysis.processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = timezone.now()
            analysis.save()

            return Response({
                'text': response['text']
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()
            return Response(
                {'error': f'Resume analysis failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def career_suggestions(self, request):
        """Get career suggestions based on profile - no fallbacks"""
        serializer = SkillGapAnalysisSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        analysis = AIAnalysis.objects.create(
            user=request.user,
            analysis_type='career_suggestion',
            input_data=serializer.validated_data,
            status='processing'
        )

        try:
            start_time = time.time()
            
            prompt = get_career_suggestions_prompt(serializer.validated_data)
            response = gemini_client.generate_content(prompt)
            
            analysis.output_data = {
                'text': response['text'],
                'structured': None
            }
            analysis.status = 'completed'
            analysis.processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = timezone.now()
            analysis.save()

            return Response({
                'text': response['text']
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()
            return Response(
                {'error': f'Failed to get suggestions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def market_insights(self, request):
        """Get market insights for a role - NO FALLBACKS, pure API errors"""
        # The data should be in the request body, not query params
        role = request.data.get('role')
        location = request.data.get('location', 'United States')
        
        if not role:
            return Response(
                {'error': 'role is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create analysis record
        analysis = AIAnalysis.objects.create(
            user=request.user,
            analysis_type='market_insights',
            input_data={'role': role, 'location': location},
            status='processing'
        )

        try:
            start_time = time.time()
            
            # Call Gemini API for market insights
            prompt = get_market_insights_text_prompt(role, location)
            response = gemini_client.generate_content(prompt)
            
            analysis.output_data = {
                'text': response['text'],
                'structured': None
            }
            analysis.status = 'completed'
            analysis.processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = timezone.now()
            analysis.save()

            return Response({
                'text': response['text']
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()
            logger.error(f"Market insights error: {str(e)}")
            # Return the actual error - no fallback data
            return Response(
                {'error': f'Failed to get market insights: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def learning_resources(self, request):
        """Generate 2 simple learning resource recommendations - NO RETRIES, NO TIMEOUT ISSUES"""
        skills = request.data.get('skills', [])
        goals = request.data.get('goals', [])
        
        if not skills and not goals:
            return Response(
                {'error': 'Either skills or goals must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create analysis record
        analysis = AIAnalysis.objects.create(
            user=request.user,
            analysis_type='learning_resources',
            input_data={'skills': skills, 'goals': goals},
            status='processing'
        )

        try:
            start_time = time.time()
            
            # EXTREMELY SIMPLE PROMPT - just 2 resources, no formatting instructions
            skills_text = ', '.join(skills[:2]) if skills else 'No skills'
            
            goals_text = ''
            if goals and len(goals) > 0:
                if isinstance(goals[0], dict) and goals[0].get('target_role'):
                    goals_text = goals[0].get('target_role', '')
            
            prompt = f"""Recommend 2 learning resources for someone with skills: {skills_text}.
Goal: {goals_text if goals_text else 'Career advancement'}

For each resource, give:
- Title
- Type
- Platform
- Price (Free/Paid)
- Brief description (1 sentence)

Keep it simple."""
            
            # SINGLE ATTEMPT - no retry loop
            logger.info(f"Sending simple learning resources prompt to Gemini (length: {len(prompt)} chars)")
            
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,
            )
            
            response = gemini_client.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini API")
            
            analysis.output_data = {
                'text': response.text,
                'structured': None
            }
            analysis.status = 'completed'
            analysis.processing_time_ms = int((time.time() - start_time) * 1000)
            analysis.completed_at = timezone.now()
            analysis.save()

            logger.info(f"Learning resources generated successfully ({len(response.text)} chars)")
            
            return Response({
                'text': response.text
            })

        except Exception as e:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            analysis.completed_at = timezone.now()
            analysis.save()
            logger.error(f"Learning resources error: {str(e)}")
            return Response(
                {'error': f'Failed to generate learning resources: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for AI Recommendations"""
    serializer_class = AIRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = AIRecommendation.objects.filter(user=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by type
        rec_type = self.request.query_params.get('type')
        if rec_type:
            queryset = queryset.filter(recommendation_type=rec_type)
        
        return queryset

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a recommendation"""
        recommendation = self.get_object()
        recommendation.status = 'accepted'
        recommendation.save()
        return Response({'message': 'Recommendation accepted'})

    @action(detail=True, methods=['post'])
    def implement(self, request, pk=None):
        """Mark recommendation as implemented"""
        recommendation = self.get_object()
        recommendation.status = 'implemented'
        recommendation.save()
        return Response({'message': 'Recommendation implemented'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a recommendation with feedback"""
        recommendation = self.get_object()
        recommendation.status = 'rejected'
        recommendation.feedback = request.data.get('feedback', '')
        recommendation.feedback_score = request.data.get('score')
        recommendation.save()
        return Response({'message': 'Recommendation rejected'})


class AIInteractionViewSet(viewsets.ModelViewSet):
    """ViewSet for AI Interactions"""
    serializer_class = AIInteractionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return AIInteraction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def chat(self, request):
        """Chat with AI assistant"""
        serializer = AIChatSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = gemini_client.chat(
                message=serializer.validated_data['message'],
                context=serializer.validated_data.get('context', {})
            )

            # Save interaction
            AIInteraction.objects.create(
                user=request.user,
                interaction_type='chat',
                prompt=serializer.validated_data['message'],
                response=response.get('text', ''),
                metadata={'context': serializer.validated_data.get('context', {})},
                tokens_consumed=response.get('usage', {}).get('total_tokens', 0)
            )

            return Response({'text': response.get('text', '')})

        except Exception as e:
            return Response(
                {'error': f'Chat failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AIDashboardViewSet(viewsets.ViewSet):
    """ViewSet for AI dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Get AI dashboard stats - this handles GET to /api/ai/dashboard/"""
        return self.get_stats(request)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get AI dashboard stats - this handles GET to /api/ai/dashboard/stats/"""
        return self.get_stats(request)

    def get_stats(self, request):
        """Common method to get AI dashboard stats"""
        user = request.user
        
        # Get recent analyses
        recent_analyses = AIAnalysis.objects.filter(
            user=user
        ).order_by('-created_at')[:5]
        
        # Get pending recommendations
        pending_recommendations = AIRecommendation.objects.filter(
            user=user,
            status='pending'
        ).count()
        
        # Calculate statistics
        total_analyses = AIAnalysis.objects.filter(user=user).count()
        completed_analyses = AIAnalysis.objects.filter(
            user=user, status='completed'
        ).count()
        
        # Token usage stats
        token_stats = AIAnalysis.objects.filter(
            user=user, status='completed'
        ).aggregate(
            total_tokens=Avg('tokens_used')
        )
        
        stats = {
            'total_analyses': total_analyses,
            'completed_analyses': completed_analyses,
            'pending_recommendations': pending_recommendations,
            'average_tokens_per_analysis': token_stats['total_tokens'] or 0,
            'recent_analyses': AIAnalysisSerializer(recent_analyses, many=True).data
        }
        
        return Response(stats)