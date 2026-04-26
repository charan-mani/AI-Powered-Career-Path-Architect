# create_resources.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career_architect.settings')
django.setup()

from roadmap.models import Roadmap, RoadmapStep, LearningResource
from users.models import User

def create_resources_from_steps():
    """Create LearningResource objects from step.resources JSON field"""
    
    # Get your user
    try:
        user = User.objects.get(email='johnmuchire46@gmail.com')
        print(f"Processing resources for user: {user.email}")
    except User.DoesNotExist:
        print("User not found!")
        return

    # Get all roadmaps for this user
    roadmaps = Roadmap.objects.filter(user=user)
    print(f"Found {roadmaps.count()} roadmaps")

    resources_created = 0
    resources_skipped = 0

    for roadmap in roadmaps:
        print(f"\n📋 Roadmap: {roadmap.title}")
        steps = RoadmapStep.objects.filter(roadmap=roadmap)
        print(f"  Steps: {steps.count()}")
        
        for step in steps:
            print(f"  📝 Step {step.step_number}: {step.title}")
            
            # Check if step has resources in the JSON field
            if step.resources and isinstance(step.resources, list):
                for i, resource_data in enumerate(step.resources):
                    # Check if this resource already exists
                    title = resource_data.get('title', f'Resource {i+1}')
                    existing = LearningResource.objects.filter(
                        step=step,
                        title=title
                    ).first()
                    
                    if existing:
                        print(f"    ⏭️  Already exists: {title}")
                        resources_skipped += 1
                        continue
                    
                    # Create new learning resource
                    resource = LearningResource.objects.create(
                        step=step,
                        resource_type=resource_data.get('type', 'course'),
                        title=title,
                        url=resource_data.get('url', '#'),
                        description=resource_data.get('description', ''),
                        duration_estimate=resource_data.get('duration', ''),
                        difficulty_level=resource_data.get('difficulty', 'intermediate'),
                        is_free=resource_data.get('is_free', True),
                        platform=resource_data.get('platform', ''),
                        completion_status='not_started'
                    )
                    print(f"    ✅ Created: {resource.title}")
                    resources_created += 1
            else:
                print(f"    ℹ️  No resources in step.resources")

    print(f"\n📊 Summary:")
    print(f"  ✅ Resources created: {resources_created}")
    print(f"  ⏭️  Resources skipped (already exist): {resources_skipped}")
    print(f"  📚 Total resources now: {LearningResource.objects.filter(step__roadmap__user=user).count()}")

if __name__ == '__main__':
    create_resources_from_steps()