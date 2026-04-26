from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.db.models import Q
from django.utils import timezone
from .models import (
    User, UserSkill, UserEducation, UserExperience,
    Resume, CareerGoal
)
from .serializers import (
    UserSerializer, UserProfileSerializer, RegisterSerializer,
    LoginSerializer, UserSkillSerializer, UserEducationSerializer,
    UserExperienceSerializer, ResumeSerializer, CareerGoalSerializer,
    ChangePasswordSerializer
)
from career_architect.apps.ai_services.gemini_client import GeminiClient
from career_architect.apps.ai_services.prompt_templates import get_resume_analysis_prompt
import os
import traceback
import logging
import time
import re

# For PDF text extraction
try:
    import PyPDF2
    HAS_PYPDF2 = True
except ImportError:
    HAS_PYPDF2 = False
    print("Warning: PyPDF2 not installed. PDF text extraction will fail.")

# For DOCX text extraction
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    print("Warning: python-docx not installed. DOCX text extraction will fail.")

logger = logging.getLogger(__name__)
gemini_client = GeminiClient()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'old_password': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password updated successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        user = request.user
        user.delete()
        return Response({'message': 'Account deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        logger.info("="*50)
        logger.info("REGISTER ENDPOINT CALLED")
        logger.info(f"Request data: {request.data}")
        
        try:
            email = request.data.get('email')
            if email and User.objects.filter(email=email).exists():
                return Response(
                    {'email': ['User with this email already exists.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                logger.info("Serializer is valid")
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                response_data = {
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                logger.info(f"User created successfully: {user.email}")
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"EXCEPTION in register: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserSkillViewSet(viewsets.ModelViewSet):
    serializer_class = UserSkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSkill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserEducationViewSet(viewsets.ModelViewSet):
    serializer_class = UserEducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserEducation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserExperienceViewSet(viewsets.ModelViewSet):
    serializer_class = UserExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserExperience.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
    return text


def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text:
                text += paragraph.text + "\n"
    except Exception as e:
        logger.error(f"DOCX extraction error: {str(e)}")
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")
    return text


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resume.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'file': ['No file uploaded.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            max_size = 10 * 1024 * 1024
            if file.size > max_size:
                return Response(
                    {'file': [f'File size too large. Max size is {max_size//(1024*1024)}MB.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            content_type = file.content_type
            allowed_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ]
            if content_type not in allowed_types:
                return Response(
                    {'file': ['File type not allowed. Please upload PDF or Word document.']},
                    status=status.HTTP_400_BAD_REQUEST
                )

            is_primary = request.data.get('is_primary', 'false').lower() == 'true'

            logger.info(f"Uploading resume: {file.name}, size: {file.size}, type: {content_type}, is_primary: {is_primary}")

            if is_primary:
                Resume.objects.filter(user=request.user, is_primary=True).update(is_primary=False)

            resume = Resume.objects.create(
                user=request.user,
                file=file,
                original_filename=file.name,
                file_type=content_type,
                file_size=file.size,
                is_primary=is_primary
            )

            serializer = self.get_serializer(resume, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error uploading resume: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': f'Failed to upload resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        try:
            resume = self.get_object()
            Resume.objects.filter(user=request.user, is_primary=True).exclude(id=resume.id).update(is_primary=False)
            resume.is_primary = True
            resume.save()
            return Response({'message': 'Resume set as primary successfully'})
        except Exception as e:
            logger.error(f"Error setting primary resume: {str(e)}")
            return Response(
                {'error': f'Failed to set primary resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Trigger AI analysis for a resume - IMPROVED SKILL EXTRACTION"""
        try:
            resume = self.get_object()
            
            if not resume.file:
                return Response(
                    {'error': 'No file to analyze'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            target_role = request.data.get('target_role', '')
            
            file_path = resume.file.path
            resume_text = ""
            file_ext = os.path.splitext(resume.original_filename)[1].lower()
            
            if file_ext == '.pdf':
                if not HAS_PYPDF2:
                    return Response(
                        {'error': 'PDF extraction library not installed. Please install PyPDF2.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                resume_text = extract_text_from_pdf(file_path)
                
            elif file_ext in ['.docx', '.doc']:
                if not HAS_DOCX:
                    return Response(
                        {'error': 'DOCX extraction library not installed. Please install python-docx.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                resume_text = extract_text_from_docx(file_path)
            else:
                return Response(
                    {'error': f'Unsupported file type: {file_ext}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not resume_text or len(resume_text.strip()) < 50:
                return Response(
                    {'error': 'Could not extract sufficient text from the resume.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Extracted {len(resume_text)} characters from resume")
            
            start_time = time.time()
            prompt = get_resume_analysis_prompt(resume_text, target_role)
            response = gemini_client.generate_content(prompt)
            
            if not response or not response.get('text'):
                raise Exception("Empty response from Gemini API")
            
            analysis_text = response['text']
            
            # Define common technical skills for extraction
            COMMON_SKILLS = [
                'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
                'React', 'Angular', 'Vue', 'Node.js', 'Express', 'Django', 'Flask', 'Spring',
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'Jenkins',
                'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy', 'Jupyter',
                'Git', 'GitHub', 'GitLab', 'CI/CD', 'DevOps', 'Agile', 'Scrum', 'Kanban',
                'REST API', 'GraphQL', 'gRPC', 'Microservices', 'Serverless',
                'HTML', 'CSS', 'Tailwind', 'Bootstrap', 'Material-UI',
                'Leadership', 'Project Management', 'Communication', 'Teamwork'
            ]
            
            # Parse analysis text
            analysis_result = {
                'text': analysis_text,
                'ats_score': 0,
                'strengths': [],
                'improvements': [],
                'keywords': {'matched': [], 'missing': []},
                'suggestions': []
            }
            
            # Extract overall score
            score_match = re.search(r'OVERALL SCORE:\s*(\d+)', analysis_text, re.IGNORECASE)
            if score_match:
                analysis_result['ats_score'] = int(score_match.group(1))
            else:
                score_match = re.search(r'(\d+)\s*/\s*100', analysis_text)
                if score_match:
                    analysis_result['ats_score'] = int(score_match.group(1))
            
            # Extract strengths
            strengths_section = re.search(r'STRENGTHS\s*\n-+\s*\n(.*?)(?=\n\n|\n[A-Z]|\Z)', analysis_text, re.DOTALL | re.IGNORECASE)
            if strengths_section:
                strength_lines = strengths_section.group(1).split('\n')
                for line in strength_lines:
                    cleaned = re.sub(r'^[•\-*\s]+', '', line.strip())
                    if cleaned and len(cleaned) > 10 and len(cleaned) < 200:
                        analysis_result['strengths'].append(cleaned)
            
            # Extract improvements
            improvements_section = re.search(r'AREAS FOR IMPROVEMENT\s*\n-+\s*\n(.*?)(?=\n\n|\n[A-Z]|\Z)', analysis_text, re.DOTALL | re.IGNORECASE)
            if improvements_section:
                improvement_lines = improvements_section.group(1).split('\n')
                for line in improvement_lines:
                    cleaned = re.sub(r'^[•\-*\s]+', '', line.strip())
                    if cleaned and len(cleaned) > 10 and len(cleaned) < 200:
                        analysis_result['improvements'].append(cleaned)
            
            # EXTRACT MATCHED SKILLS - Look for skills in the entire analysis text
            matched_skills = []
            analysis_lower = analysis_text.lower()
            
            for skill in COMMON_SKILLS:
                skill_lower = skill.lower()
                # Check if skill appears in analysis text
                if skill_lower in analysis_lower:
                    matched_skills.append(skill)
            
            # Also try to extract from "Strong Keywords Present" section
            matched_section = re.search(r'Strong Keywords Present[:\s]*\n?(.*?)(?=\n\n|\nMissing|\Z)', analysis_text, re.DOTALL | re.IGNORECASE)
            if matched_section:
                section_text = matched_section.group(1)
                for skill in COMMON_SKILLS:
                    if skill.lower() in section_text.lower() and skill not in matched_skills:
                        matched_skills.append(skill)
            
            # Remove duplicates and limit to 15
            analysis_result['keywords']['matched'] = list(set(matched_skills))[:15]
            
            # Extract suggestions from Quick Wins
            quick_wins_section = re.search(r'QUICK WINS.*?\n(.*?)(?=\n\n|\nLONG-TERM|\Z)', analysis_text, re.DOTALL | re.IGNORECASE)
            if quick_wins_section:
                suggestion_lines = quick_wins_section.group(1).split('\n')
                for line in suggestion_lines:
                    cleaned = re.sub(r'^[\d\.\s•\-*]+\s*', '', line.strip())
                    if cleaned and len(cleaned) > 15:
                        analysis_result['suggestions'].append(cleaned)
            
            # Update resume
            resume.analyzed = True
            resume.ats_score = analysis_result['ats_score']
            resume.match_score = 0
            resume.last_analyzed = timezone.now()
            resume.parsed_content = analysis_result
            resume.save()
            
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"Resume {resume.id} analyzed successfully in {processing_time}ms")
            logger.info(f"Extracted matched skills: {analysis_result['keywords']['matched']}")
            
            return Response(analysis_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error analyzing resume: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': f'Failed to analyze resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        try:
            resume = self.get_object()
            if not resume.analyzed or not resume.parsed_content:
                return Response(
                    {'message': 'Analysis not available'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(resume.parsed_content, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting resume analysis: {str(e)}")
            return Response(
                {'error': f'Failed to get analysis: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        try:
            resume = self.get_object()
            if not resume.file:
                return Response(
                    {'error': 'File not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            from django.http import FileResponse
            return FileResponse(
                resume.file.open('rb'),
                as_attachment=True,
                filename=resume.original_filename
            )
        except Exception as e:
            logger.error(f"Error downloading resume: {str(e)}")
            return Response(
                {'error': f'Failed to download resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            resume = self.get_object()
            if resume.file:
                if default_storage.exists(resume.file.name):
                    default_storage.delete(resume.file.name)
            resume.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting resume: {str(e)}")
            return Response(
                {'error': f'Failed to delete resume: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CareerGoalViewSet(viewsets.ModelViewSet):
    serializer_class = CareerGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CareerGoal.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        goal = self.get_object()
        goal.is_active = False
        goal.save()
        return Response({'message': 'Goal archived successfully'})

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        goal = self.get_object()
        goal.is_completed = True
        goal.completed_date = timezone.now()
        goal.save()
        return Response({'message': 'Goal marked as completed'})