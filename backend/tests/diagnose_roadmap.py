# diagnose_roadmap.py
import os
import django
import json
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'career_architect.settings')
django.setup()

from roadmap.models import Roadmap, RoadmapStep, LearningResource
from users.models import User

def diagnose_roadmap_issues():
    """Diagnose why roadmaps are not working correctly"""
    
    print("=" * 80)
    print("ROADMAP DIAGNOSTIC TOOL")
    print("=" * 80)
    
    # Get the user with roadmaps
    try:
        user = User.objects.get(email='johnmuchire46@gmail.com')
        print(f"\n✅ User found: {user.email}")
    except User.DoesNotExist:
        print("\n❌ User not found!")
        return

    # Get all roadmaps for this user
    roadmaps = Roadmap.objects.filter(user=user).order_by('-created_at')
    print(f"\n📊 Total roadmaps for user: {roadmaps.count()}")
    
    # Check each roadmap
    print("\n" + "=" * 80)
    print("ROADMAP DETAILS")
    print("=" * 80)
    
    for roadmap in roadmaps:
        print(f"\n{'─' * 40}")
        print(f"🆔 ID: {roadmap.id}")
        print(f"📌 Title: {roadmap.title}")
        print(f"🎯 Target Role: {roadmap.target_role}")
        print(f"📝 Description: {roadmap.description or 'No description'}")
        print(f"🤖 AI Generated: {roadmap.generated_by_ai}")
        print(f"📅 Created: {roadmap.created_at}")
        print(f"📊 Progress: {roadmap.completion_percentage}%")
        
        # Check steps
        steps = RoadmapStep.objects.filter(roadmap=roadmap).order_by('step_number')
        print(f"👣 Steps in database: {steps.count()}")
        
        if steps.count() == 0:
            print("  ⚠️  NO STEPS IN DATABASE!")
            
            # Check if steps exist in JSON fields
            has_json_data = False
            if roadmap.skill_gap_analysis and roadmap.skill_gap_analysis != {}:
                has_json_data = True
                print(f"  📦 Has skill_gap_analysis JSON")
            if roadmap.market_insights and roadmap.market_insights != {}:
                has_json_data = True
                print(f"  📦 Has market_insights JSON")
            if roadmap.salary_projection and roadmap.salary_projection != {}:
                has_json_data = True
                print(f"  📦 Has salary_projection JSON")
            
            if not has_json_data:
                print("  ❌ No data in roadmap JSON fields either!")
        else:
            # Show step details
            for step in steps:
                print(f"\n    Step {step.step_number}: {step.title}")
                print(f"      Type: {step.step_type}")
                print(f"      Hours: {step.estimated_duration_hours}")
                print(f"      Completed: {step.is_completed}")
                
                # Check resources in step
                if step.resources and len(step.resources) > 0:
                    print(f"      Resources in JSON: {len(step.resources)}")
                else:
                    print(f"      ⚠️  No resources in step.resources JSON")
                
                # Check learning resources
                learning_resources = LearningResource.objects.filter(step=step)
                if learning_resources.exists():
                    print(f"      📚 LearningResource objects: {learning_resources.count()}")
                    for lr in learning_resources:
                        print(f"        - {lr.title}")
                else:
                    print(f"      ❌ No LearningResource objects for this step")

def check_api_endpoints():
    """Check if API endpoints are accessible"""
    
    print("\n" + "=" * 80)
    print("API ENDPOINT CHECK")
    print("=" * 80)
    
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    session = requests.Session()
    retry = Retry(connect=1, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # Test endpoints
    endpoints = [
        ('/api/health/', 'Health Check'),
        ('/api/roadmap/roadmaps/', 'Roadmaps List'),
        ('/api/roadmap/steps/', 'Steps List'),
        ('/api/roadmap/resources/', 'Resources List'),
    ]
    
    base_url = 'http://localhost:8000'
    
    for endpoint, name in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = session.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: OK (200)")
            elif response.status_code == 401:
                print(f"⚠️  {name}: Unauthorized (401) - Need authentication")
            else:
                print(f"❌ {name}: Error {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Connection refused - Is Django running?")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")

def check_frontend_console_logs():
    """Instructions for checking frontend console"""
    
    print("\n" + "=" * 80)
    print("FRONTEND CONSOLE CHECK")
    print("=" * 80)
    print("""
1. Open your browser at http://localhost:5173/roadmap
2. Press F12 to open Developer Tools
3. Go to the Console tab
4. Click on a roadmap that shows as "Untitled Roadmap"
5. Look for these errors:
   - 404 errors (API endpoint not found)
   - 401 errors (authentication issues)
   - 500 errors (server errors)
   - Network tab shows failed requests
   - Console shows "Error fetching roadmap"
    """)

def check_network_requests():
    """Instructions for checking network requests"""
    
    print("\n" + "=" * 80)
    print("NETWORK REQUEST CHECK")
    print("=" * 80)
    print("""
1. Open browser DevTools (F12)
2. Go to Network tab
3. Clear existing logs (🚫 button)
4. Refresh the page
5. Look for requests to:
   - `/api/roadmap/roadmaps/` - Should return 200 with roadmap list
   - `/api/roadmap/roadmaps/{id}/` - When you click a roadmap
   - `/api/roadmap/steps/?roadmap={id}` - Should load steps
   
Check for:
✅ 200 - OK
⚠️ 401 - Unauthorized (login required)
❌ 404 - Endpoint not found
❌ 500 - Server error
    """)

def check_database_consistency():
    """Check for data consistency issues"""
    
    print("\n" + "=" * 80)
    print("DATABASE CONSISTENCY CHECK")
    print("=" * 80)
    
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check for orphaned steps
        cursor.execute("""
            SELECT COUNT(*) FROM roadmap_steps 
            WHERE roadmap_id NOT IN (SELECT id FROM roadmaps)
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned > 0:
            print(f"❌ Found {orphaned} orphaned steps (steps without a roadmap)")
        else:
            print(f"✅ No orphaned steps")
        
        # Check for steps with missing roadmap reference
        cursor.execute("""
            SELECT COUNT(*) FROM roadmap_steps WHERE roadmap_id IS NULL
        """)
        null_roadmap = cursor.fetchone()[0]
        if null_roadmap > 0:
            print(f"❌ Found {null_roadmap} steps with NULL roadmap_id")
        else:
            print(f"✅ All steps have valid roadmap_id")
        
        # Check for duplicate step numbers in same roadmap
        cursor.execute("""
            SELECT roadmap_id, step_number, COUNT(*) 
            FROM roadmap_steps 
            GROUP BY roadmap_id, step_number 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"❌ Found duplicate step numbers:")
            for dup in duplicates:
                print(f"   Roadmap {dup[0]}, Step {dup[1]}: {dup[2]} copies")
        else:
            print(f"✅ No duplicate step numbers")

def check_roadmap_data_integrity():
    """Check if roadmap data is properly structured"""
    
    print("\n" + "=" * 80)
    print("ROADMAP DATA INTEGRITY CHECK")
    print("=" * 80)
    
    from django.core import serializers
    
    roadmaps = Roadmap.objects.all()
    issues_found = 0
    
    for roadmap in roadmaps:
        issues = []
        
        # Check required fields
        if not roadmap.title:
            issues.append("Missing title")
        if not roadmap.target_role:
            issues.append("Missing target role")
        
        # Check JSON fields
        if roadmap.skill_gap_analysis and not isinstance(roadmap.skill_gap_analysis, dict):
            issues.append(f"skill_gap_analysis is {type(roadmap.skill_gap_analysis)}, not dict")
        if roadmap.market_insights and not isinstance(roadmap.market_insights, dict):
            issues.append(f"market_insights is {type(roadmap.market_insights)}, not dict")
        
        if issues:
            issues_found += 1
            print(f"\n❌ Roadmap {roadmap.id} - {roadmap.title}")
            for issue in issues:
                print(f"   - {issue}")
    
    if issues_found == 0:
        print("✅ All roadmaps have valid data structure")

def main():
    """Run all diagnostic checks"""
    
    print("\n" + "🔥" * 40)
    print("🔥 ROADMAP DIAGNOSTIC TOOL - RUNNING ALL CHECKS")
    print("🔥" * 40)
    
    # Run checks
    diagnose_roadmap_issues()
    check_database_consistency()
    check_roadmap_data_integrity()
    check_api_endpoints()
    check_frontend_console_logs()
    check_network_requests()
    
    print("\n" + "=" * 80)
    print("📋 SUMMARY")
    print("=" * 80)
    print("""
Based on your data, the main issues are:

1️⃣ 9 out of 10 roadmaps have ZERO steps in the database
   - They were created by AI but steps were not saved properly
   - This is why they show "0 steps" in the list

2️⃣ The Data Scientist roadmap (ID 2) has steps but they have NO resources
   - The steps exist but the `resources` JSON field is empty
   - This is why Learning Resources page shows nothing

3️⃣ "Untitled Roadmap" appears when:
   - The roadmap data fails to load from the API
   - The roadmap exists in database but steps are missing
   - Check Network tab to see if API calls are failing

✅ Fixes needed:
   - Run a script to create steps from the JSON data
   - Add resources to existing steps
   - Ensure API endpoints are returning data correctly
    """)
    
    print("\n" + "🛠️  NEXT STEPS")
    print("-" * 40)
    print("""
1. Run the create_steps_from_json.py script to create steps
2. Run the add_resources_to_steps.py script to add resources
3. Check browser console for API errors
4. Verify Django server is running (python manage.py runserver)
5. Check that you're logged in with the correct user
    """)

if __name__ == '__main__':
    main()