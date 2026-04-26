"""Prompt templates for Gemini API - Text-based versions"""

def get_skill_gap_prompt(target_role, current_skills, experience_level=""):
    """Alias for get_skill_gap_text_prompt - for backward compatibility"""
    return get_skill_gap_text_prompt(target_role, current_skills, experience_level)

def get_roadmap_text_prompt(data):
    """Generate prompt for roadmap creation - returns formatted text, not JSON"""
    return f"""
You are an expert career advisor. Create a detailed, well-formatted career roadmap for someone who wants to become a **{data['target_role']}**.

## USER PROFILE
- Target Industry: {data.get('target_industry', 'Technology')}
- Timeframe: {data['timeframe_months']} months
- Current Skills: {', '.join(data.get('current_skills', [])) if data.get('current_skills') else 'None specified'}
- Experience Level: {data.get('experience_level', 'Not specified')}

## INSTRUCTIONS
Create a comprehensive career roadmap with the following sections. Use clear headings, bullet points, and formatting to make it easy to read.

Format your response like this:

# CAREER ROADMAP: [Target Role]

## OVERVIEW
[2-3 sentences describing this career path and what it entails]

## SKILL GAP ANALYSIS
**Required Skills:**
• Skill 1 - brief description
• Skill 2 - brief description
• Skill 3 - brief description
(list 8-12 skills)

**Your Current Strengths:**
• [Skills the user already has]

**Skills to Develop:**
• [Priority skills to focus on first]

## MARKET INSIGHTS
- Demand Trend: [High/Medium/Low]
- Average Salary Range: [$X - $Y]
- Growth Outlook: [X% over next 5 years]
- Top Industries Hiring: [Industry1, Industry2, Industry3]

## SALARY PROJECTION
- Entry Level: $XX,XXX
- Mid Level: $XX,XXX
- Senior Level: $XX,XXX
- Leadership: $XX,XXX

## STEP-BY-STEP ROADMAP

### Step 1: [Title - Month X]
**Duration:** [X hours]
**Skills to Learn:** [Skill1, Skill2, Skill3]

[Detailed description of what to learn and why it's important]

**Recommended Resources:**
• [Resource Name] - [Platform] ([Free/Paid]) - [URL]
• [Resource Name] - [Platform] ([Free/Paid]) - [URL]

### Step 2: [Title - Month X]
**Duration:** [X hours]
**Skills to Learn:** [Skill1, Skill2, Skill3]

[Detailed description]

**Recommended Resources:**
• [Resource Name] - [Platform] ([Free/Paid]) - [URL]
• [Resource Name] - [Platform] ([Free/Paid]) - [URL]

(Continue with 5-8 total steps)

## TIPS FOR SUCCESS
- [Practical tip 1]
- [Practical tip 2]
- [Practical tip 3]

## NEXT STEPS
[What to do immediately after finishing this roadmap]

Make the response detailed, motivational, and practical. Use proper formatting with headings, bullet points, and line breaks.
"""

def get_skill_gap_text_prompt(target_role, current_skills, experience_level=""):
    """Generate prompt for skill gap analysis - returns formatted text, not JSON"""
    skills_list = '\n'.join([f"  - {skill}" for skill in current_skills]) if current_skills else "  - None specified"
    
    return f"""
You are an expert career advisor. Create a detailed, well-formatted skill gap analysis for someone who wants to become a **{target_role}**.

## USER PROFILE
- Target Role: {target_role}
- Current Skills:
{skills_list}
- Experience Level: {experience_level if experience_level else 'Not specified'}

## INSTRUCTIONS
Create a comprehensive skill gap analysis with the following sections. Use clear headings, bullet points, and formatting to make it easy to read.

Format your response like this:

# SKILL GAP ANALYSIS: {target_role}

## OVERALL MATCH SCORE: [XX]%

## YOUR CURRENT STRENGTHS
• [Skill 1] - Brief description of your proficiency
• [Skill 2] - Brief description of your proficiency
• [Skill 3] - Brief description of your proficiency
(List all your strong skills)

## SKILLS TO DEVELOP
### Priority 5 (Critical - Must Learn)
**Skill Name:** [Skill 1]
**Description:** Why this skill is essential for the role and how it impacts your career growth

**Learning Resources:**
• [Resource Title] - [Platform] ([Free/Paid]) - [URL]
• [Resource Title] - [Platform] ([Free/Paid]) - [URL]

### Priority 4 (High Importance)
**Skill Name:** [Skill 2]
**Description:** Detailed explanation of why this skill matters

**Learning Resources:**
• [Resource Title] - [Platform] ([Free/Paid]) - [URL]
• [Resource Title] - [Platform] ([Free/Paid]) - [URL]

(Continue for Priority 3, etc.)

## MARKET INSIGHTS
- Demand Trend: [High/Medium/Low]
- Average Salary Range: [$X - $Y]
- Top Industries Hiring: [Industry1, Industry2, Industry3]
- Key Market Trends: [Brief summary of what's happening in this field]

## RECOMMENDED LEARNING PATH
1. **First 3 months:** Focus on [Priority 5 skills]
2. **Next 3 months:** Build [Priority 4 skills]
3. **Following 3 months:** Practice through projects
4. **Final 3 months:** Prepare for interviews and applications

## QUICK WINS
• [Immediately actionable tip 1]
• [Immediately actionable tip 2]
• [Immediately actionable tip 3]

Make the response detailed, motivational, and practical. Use proper formatting with headings, bullet points, and line breaks. Be honest but encouraging.
"""

def get_resume_analysis_prompt(resume_text, target_role=""):
    """Generate prompt for resume analysis - returns text, not JSON"""
    return f"""
You are an expert resume reviewer. Analyze this resume and provide detailed, actionable feedback.

## TARGET ROLE
{target_role if target_role else 'Not specified (general resume review)'}

## RESUME CONTENT
{resume_text}

## INSTRUCTIONS
Provide a comprehensive resume analysis with the following sections. Use clear headings and bullet points.

Format your response like this:

# RESUME ANALYSIS

## OVERALL SCORE: [XX]/100

## STRENGTHS
• [Strength 1] - Explanation
• [Strength 2] - Explanation
• [Strength 3] - Explanation

## AREAS FOR IMPROVEMENT
• [Improvement 1] - Specific suggestion
• [Improvement 2] - Specific suggestion
• [Improvement 3] - Specific suggestion

## KEYWORD ANALYSIS
**Strong Keywords Present:** [keyword1, keyword2, keyword3]
**Missing Keywords to Add:** [keyword4, keyword5, keyword6]

## FORMATTING FEEDBACK
- [Formatting suggestion 1]
- [Formatting suggestion 2]
- [Formatting suggestion 3]

## SECTION-BY-SECTION FEEDBACK

### Summary/Objective
[Feedback on this section]

### Experience
[Feedback on this section]

### Education
[Feedback on this section]

### Skills
[Feedback on this section]

## QUICK WINS (Can fix immediately)
1. [Immediate fix 1]
2. [Immediate fix 2]
3. [Immediate fix 3]

## LONG-TERM IMPROVEMENTS
1. [Long-term suggestion 1]
2. [Long-term suggestion 2]
3. [Long-term suggestion 3]

Provide honest, constructive feedback that will help improve the resume. Be specific and actionable.
"""

def get_career_suggestions_prompt(user_data):
    """Generate prompt for career suggestions - returns text, not JSON"""
    return f"""
You are an expert career advisor. Based on the user's profile, suggest potential career paths with detailed analysis.

## USER PROFILE
{user_data}

## INSTRUCTIONS
Provide 3-5 detailed career path suggestions with the following format:

# CAREER SUGGESTIONS

## SUGGESTION 1: [Career Path Title]
**Match Score:** [XX]%
**Industry:** [Industry Name]
**Estimated Salary:** [$X - $Y]
**Time to Enter:** [X months/years]

**Why This Fits You:**
[Detailed explanation of why this career aligns with their skills and experience]

**Required Skills:**
• [Skill 1]
• [Skill 2]
• [Skill 3]
• [Skill 4]
• [Skill 5]

**Growth Potential:**
[Description of career progression and long-term outlook]

**Immediate Next Steps:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Resources to Get Started:**
• [Resource 1] - [URL]
• [Resource 2] - [URL]
• [Resource 3] - [URL]

(Repeat for each suggestion)

## SUMMARY
[Brief recommendation on which path to prioritize]

Provide detailed, personalized suggestions based on their profile. Be realistic but encouraging.
"""

def get_market_insights_text_prompt(role, location):
    """Generate prompt for market insights - returns text, not JSON"""
    return f"""
You are a labor market analyst. Provide detailed market insights for **{role}** roles in **{location}**.

## INSTRUCTIONS
Provide a comprehensive market analysis with the following sections. Use clear headings and bullet points.

# MARKET INSIGHTS: {role} in {location}

## MARKET OVERVIEW
[2-3 paragraph summary of the current job market for this role]

## DEMAND ANALYSIS
- **Overall Demand:** [High/Medium/Low]
- **Year-over-Year Growth:** [X]%

## SALARY INFORMATION
- **Entry Level:** $XX,XXX - $XX,XXX
- **Mid Level:** $XX,XXX - $XX,XXX
- **Senior Level:** $XX,XXX - $XX,XXX

## TOP SKILLS IN DEMAND
• [Skill 1]
• [Skill 2]
• [Skill 3]
• [Skill 4]
• [Skill 5]

## TOP COMPANIES HIRING
• [Company 1]
• [Company 2]
• [Company 3]

## MARKET TRENDS
- [Trend 1]
- [Trend 2]
- [Trend 3]

## RECOMMENDATIONS FOR JOB SEEKERS
1. [Recommendation 1]
2. [Recommendation 2]
3. [Recommendation 3]
"""