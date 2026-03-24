import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FiPlus,
  FiTrendingUp,
  FiTarget,
  FiCalendar,
  FiAward,
  FiBookOpen,
  FiBriefcase,
  FiMessageSquare,
  FiStar,
  FiChevronRight,
  FiClock,
  FiCheckCircle,
  FiBarChart2,
  FiUsers,
  FiActivity,
  FiArrowUpRight,
  FiArrowDownRight,
  FiZap,
  FiLayers,
  FiPieChart,
  FiGrid,
} from 'react-icons/fi';
import { HiOutlineSparkles } from 'react-icons/hi';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth.jsx';
import { useRoadmap } from '../hooks/useRoadmap.jsx';
import { useAI } from '../hooks/useAI.jsx';
import { userService } from '../services/userService.js';
import { roadmapService } from '../services/roadmapService.js';
import LoadingSpinner, { LoadingSkeleton } from '../components/common/LoadingSpinner';
import toast from 'react-hot-toast';

const DashboardPage = () => {
  const { user } = useAuth();
  const {
    roadmaps,
    dashboardStats,
    isLoading: roadmapsLoading,
  } = useRoadmap();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [greeting, setGreeting] = useState('');
  const [activeRoadmaps, setActiveRoadmaps] = useState([]);
  const [recentRoadmaps, setRecentRoadmaps] = useState([]);
  const [learningResources, setLearningResources] = useState([]);
  const [skills, setSkills] = useState([]);
  const [careerGoal, setCareerGoal] = useState(null);
  const [skillCategories, setSkillCategories] = useState([]);
  const [recentSkillActivity, setRecentSkillActivity] = useState([]);
  const [stats, setStats] = useState({
    totalRoadmaps: 0,
    activeRoadmaps: 0,
    completedRoadmaps: 0,
    averageProgress: 0,
    totalSkills: 0,
    masteredSkills: 0,
    learningSkills: 0,
    totalLearningHours: 0,
  });

  // Helper function to get user display name
  const getUserDisplayName = () => {
    if (!user) return 'Guest';
    if (user.first_name && user.last_name) {
      return `${user.first_name} ${user.last_name}`;
    }
    if (user.first_name) return user.first_name;
    if (user.username) return user.username;
    if (user.email) return user.email.split('@')[0];
    return 'User';
  };

  useEffect(() => {
    // Set greeting based on time of day
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');

    loadDashboardData();
  }, []);

  useEffect(() => {
    // Process roadmaps data when they change
    if (roadmaps && !roadmapsLoading) {
      const roadmapList = Array.isArray(roadmaps) ? roadmaps : (roadmaps.results || roadmaps.data || []);
      
      // Get active roadmaps (not completed)
      const active = roadmapList.filter(r => !r.is_completed);
      setActiveRoadmaps(active);
      
      // Get recent roadmaps (last 5 updated)
      const recent = [...roadmapList]
        .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
        .slice(0, 5);
      setRecentRoadmaps(recent);

      // Calculate learning hours from ALL steps
      let totalHours = 0;
      roadmapList.forEach(roadmap => {
        if (roadmap.steps && Array.isArray(roadmap.steps)) {
          roadmap.steps.forEach(step => {
            // Add estimated hours for all steps
            totalHours += step.estimated_duration_hours || 0;
          });
        }
      });

      // Calculate average progress from all roadmaps
      const totalProgress = roadmapList.reduce((sum, r) => sum + (r.completion_percentage || 0), 0);
      const avgProgress = roadmapList.length > 0 ? totalProgress / roadmapList.length : 0;

      setStats(prev => ({
        ...prev,
        totalRoadmaps: roadmapList.length,
        activeRoadmaps: active.length,
        completedRoadmaps: roadmapList.filter(r => r.is_completed).length,
        averageProgress: avgProgress,
        totalLearningHours: totalHours,
      }));
    }
  }, [roadmaps, roadmapsLoading]);

  // Update stats when skills change
  useEffect(() => {
    if (skills.length > 0) {
      const mastered = skills.filter(s => !s.is_learning).length;
      const learning = skills.filter(s => s.is_learning).length;
      
      setStats(prev => ({
        ...prev,
        totalSkills: skills.length,
        masteredSkills: mastered,
        learningSkills: learning,
      }));

      // Generate skill categories (NEW information not duplicated)
      generateSkillCategories(skills);
      
      // Generate recent skill activity (NEW information not duplicated)
      generateRecentSkillActivity(skills);
    } else {
      setStats(prev => ({
        ...prev,
        totalSkills: 0,
        masteredSkills: 0,
        learningSkills: 0,
      }));
      setSkillCategories([]);
      setRecentSkillActivity([]);
    }
  }, [skills]);

  const generateSkillCategories = (skillsArray) => {
    // Group skills by category based on skill name keywords
    const categories = {
      'Programming Languages': ['python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust', 'typescript'],
      'Frontend Development': ['react', 'angular', 'vue', 'html', 'css', 'frontend', 'ui', 'ux', 'web design'],
      'Backend Development': ['node', 'django', 'flask', 'spring', 'backend', 'api', 'rest', 'graphql'],
      'Database': ['sql', 'mysql', 'postgresql', 'mongodb', 'database', 'nosql', 'oracle', 'redis'],
      'DevOps & Cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'devops', 'jenkins', 'terraform', 'cloud'],
      'Data Science': ['data science', 'machine learning', 'ai', 'tensorflow', 'pytorch', 'pandas', 'numpy', 'analytics'],
      'Soft Skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking', 'time management'],
      'Project Management': ['project management', 'agile', 'scrum', 'jira', 'product management'],
    };

    const categoryCounts = {};
    const uncategorized = [];

    // Initialize categories
    Object.keys(categories).forEach(cat => {
      categoryCounts[cat] = 0;
    });

    // Categorize skills
    skillsArray.forEach(skill => {
      const skillName = skill.skill_name?.toLowerCase() || '';
      let categorized = false;

      for (const [category, keywords] of Object.entries(categories)) {
        if (keywords.some(keyword => skillName.includes(keyword))) {
          categoryCounts[category] = (categoryCounts[category] || 0) + 1;
          categorized = true;
          break;
        }
      }

      if (!categorized) {
        uncategorized.push(skill);
      }
    });

    // Convert to array format for display
    const categoryArray = Object.entries(categoryCounts)
      .filter(([_, count]) => count > 0)
      .map(([name, count]) => ({ name, count }));

    // Add "Other" category if there are uncategorized skills
    if (uncategorized.length > 0) {
      categoryArray.push({ name: 'Other', count: uncategorized.length });
    }

    setSkillCategories(categoryArray);
  };

  const generateRecentSkillActivity = (skillsArray) => {
    // Sort skills by last_used or created_at to get recently active skills
    const recent = [...skillsArray]
      .sort((a, b) => {
        const dateA = a.last_used ? new Date(a.last_used, 0) : new Date(a.created_at || 0);
        const dateB = b.last_used ? new Date(b.last_used, 0) : new Date(b.created_at || 0);
        return dateB - dateA;
      })
      .slice(0, 5)
      .map(skill => ({
        id: skill.id,
        name: skill.skill_name,
        level: skill.proficiency_level,
        lastUsed: skill.last_used || 'N/A',
      }));

    setRecentSkillActivity(recent);
  };

  const loadDashboardData = async () => {
    try {
      // Load skills
      console.log('Loading skills data for dashboard...');
      const skillsData = await userService.getSkills();
      console.log('Raw skills data from API:', skillsData);

      // Handle different response formats
      let skillsArray = [];

      if (Array.isArray(skillsData)) {
        skillsArray = skillsData;
        console.log('Skills data is an array with length:', skillsData.length);
      } 
      else if (skillsData && typeof skillsData === 'object') {
        console.log('Skills data is an object, checking for array properties...');
        
        const possibleArrays = [
          'results',      // Django REST Framework pagination
          'data',         // Common wrapper
          'skills',       // If wrapped in a skills property
          'items',        // Some APIs use items
          'records',      // Some APIs use records
          'user_skills',  // Specific to your app
        ];
        
        for (const key of possibleArrays) {
          if (skillsData[key] && Array.isArray(skillsData[key])) {
            skillsArray = skillsData[key];
            console.log(`Found skills array in .${key} with length:`, skillsArray.length);
            break;
          }
        }
        
        if (skillsArray.length === 0 && skillsData.id) {
          if (skillsData.skill_name || skillsData.proficiency_level) {
            skillsArray = [skillsData];
            console.log('Found single skill object, converted to array');
          }
        }
      }

      console.log('Final skills array processed:', skillsArray);
      console.log('Number of skills:', skillsArray.length);

      setSkills(skillsArray);
      
      // Load career goals
      console.log('Loading career goals...');
      const goalsData = await userService.getCareerGoals();
      console.log('Career goals data:', goalsData);
      
      let goalsArray = [];
      if (Array.isArray(goalsData)) {
        goalsArray = goalsData;
      } else if (goalsData?.results && Array.isArray(goalsData.results)) {
        goalsArray = goalsData.results;
      }
      
      if (goalsArray.length > 0) {
        setCareerGoal(goalsArray[0]);
        console.log('Career goal set:', goalsArray[0]);
      }

      // Load learning resources
      console.log('Loading learning resources...');
      const resourcesData = await roadmapService.getLearningResources();
      console.log('Learning resources data:', resourcesData);
      
      let resourcesArray = [];
      if (Array.isArray(resourcesData)) {
        resourcesArray = resourcesData;
      } else if (resourcesData?.results && Array.isArray(resourcesData.results)) {
        resourcesArray = resourcesData.results;
      }
      setLearningResources(resourcesArray);

    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Failed to load some dashboard data');
    }
  };
  
  // Debug effect to log skills state changes
  useEffect(() => {
    console.log('Skills state updated:', skills);
    console.log('Skills count:', skills.length);
    if (skills.length > 0) {
      console.log('First skill:', skills[0]);
    }
  }, [skills]);

  const handleGenerateRoadmap = () => {
    toast.loading('Preparing roadmap generator...');
    setTimeout(() => {
      window.location.href = '/roadmap?generate=true';
    }, 500);
  };

  const handleQuickAction = (action) => {
    switch (action) {
      case 'resume':
        toast.loading('Opening resume analyzer...');
        setTimeout(() => {
          window.location.href = '/resume';
        }, 500);
        break;
      case 'skills':
        toast.loading('Opening skill assessment...');
        setTimeout(() => {
          window.location.href = '/skills';
        }, 500);
        break;
      case 'goals':
        toast.loading('Opening career goals...');
        setTimeout(() => {
          window.location.href = '/goals';
        }, 500);
        break;
      default:
        break;
    }
  };

  if (roadmapsLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 animate-pulse">
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
                ))}
              </div>
            </div>
            <LoadingSkeleton count={3} className="h-40" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600 rounded-3xl shadow-2xl overflow-hidden relative"
          >
            <div className="absolute inset-0 bg-grid-pattern opacity-10"></div>
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl transform translate-x-32 -translate-y-32"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-black/10 rounded-full blur-2xl transform -translate-x-24 translate-y-24"></div>
            
            <div className="relative p-8 md:p-10">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div className="space-y-4">
                  <div className="inline-flex items-center px-4 py-2 bg-white/20 backdrop-blur-sm rounded-full text-white text-sm font-medium">
                    <FiZap className="w-4 h-4 mr-2" />
                    Welcome back to your dashboard
                  </div>
                  
                  <h1 className="text-3xl md:text-4xl font-bold text-white">
                    {greeting}, {getUserDisplayName()}! 
                    <span className="ml-2 text-4xl">👋</span>
                  </h1>
                  
                  <p className="text-white/90 text-lg max-w-2xl">
                    {user?.current_position 
                      ? `Ready to advance your career as a ${user.current_position}? You're making great progress!`
                      : 'Welcome to your career development journey! Let\'s start building your future.'}
                  </p>

                  {/* Quick Stats Pills */}
                  <div className="flex flex-wrap items-center gap-4 mt-4">
                    <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                      <FiTarget className="w-4 h-4 text-white" />
                      <span className="text-white text-sm font-medium">
                        {stats.activeRoadmaps} Active Roadmap{stats.activeRoadmaps !== 1 ? 's' : ''}
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                      <FiBarChart2 className="w-4 h-4 text-white" />
                      <span className="text-white text-sm font-medium">
                        {stats.averageProgress.toFixed(1)}% Avg. Progress
                      </span>
                    </div>
                    <div className="flex items-center space-x-2 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                      <FiClock className="w-4 h-4 text-white" />
                      <span className="text-white text-sm font-medium">
                        {stats.totalLearningHours} Learning Hours
                      </span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleGenerateRoadmap}
                  className="group relative inline-flex items-center px-8 py-4 bg-white text-gray-900 rounded-xl font-semibold text-lg hover:shadow-2xl transform hover:-translate-y-1 transition-all duration-200"
                >
                  <HiOutlineSparkles className="w-6 h-6 mr-2 text-indigo-600 group-hover:rotate-12 transition-transform" />
                  <span>Generate New Roadmap</span>
                  <FiArrowUpRight className="w-5 h-5 ml-2 text-gray-400 group-hover:text-indigo-600 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total Roadmaps */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Roadmaps</p>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.totalRoadmaps}
                  </h3>
                </div>
                <div className="w-12 h-12 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
                  <FiLayers className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                </div>
              </div>
              <div className="mt-4 flex items-center text-xs">
                <span className="text-green-600 dark:text-green-400 font-medium flex items-center">
                  <FiArrowUpRight className="w-3 h-3 mr-1" />
                  +{stats.activeRoadmaps} active
                </span>
                <span className="mx-2 text-gray-300 dark:text-gray-600">•</span>
                <span className="text-gray-500 dark:text-gray-400">
                  {stats.completedRoadmaps} completed
                </span>
              </div>
            </motion.div>

            {/* Active Progress */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Active Progress</p>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.averageProgress.toFixed(1)}%
                  </h3>
                </div>
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                  <FiTrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
              </div>
              <div className="mt-4">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 dark:bg-green-500 h-2 rounded-full"
                    style={{ width: `${stats.averageProgress}%` }}
                  ></div>
                </div>
              </div>
            </motion.div>

            {/* Total Skills */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Total Skills</p>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.totalSkills}
                  </h3>
                </div>
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                  <FiAward className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
              <div className="mt-4 flex items-center justify-between text-xs">
                <span className="text-gray-500 dark:text-gray-400">
                  {stats.learningSkills} learning
                </span>
                <Link
                  to="/skills"
                  className="text-indigo-600 dark:text-indigo-400 font-medium hover:underline flex items-center"
                >
                  View all
                  <FiChevronRight className="w-3 h-3 ml-1" />
                </Link>
              </div>
            </motion.div>

            {/* Learning Hours */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Learning Hours</p>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stats.totalLearningHours}
                  </h3>
                </div>
                <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/30 rounded-xl flex items-center justify-center">
                  <FiClock className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-500 dark:text-gray-400">
                Across {stats.totalRoadmaps} roadmap{stats.totalRoadmaps !== 1 ? 's' : ''}
              </div>
            </motion.div>
          </div>

          {/* Tabs Navigation */}
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8">
              {[
                { id: 'overview', label: 'Overview', icon: FiPieChart },
                { id: 'roadmaps', label: 'Roadmaps', icon: FiLayers },
                { id: 'skills', label: 'Skills', icon: FiAward },
                { id: 'learning', label: 'Learning', icon: FiBookOpen },
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-all ${
                      isActive
                        ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                        : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Main Content - Left Column */}
              <div className="lg:col-span-2 space-y-8">
                {/* Active Roadmaps Section */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
                  <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
                          <FiTarget className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                            Active Roadmaps
                          </h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Continue your journey
                          </p>
                        </div>
                      </div>
                      <Link
                        to="/roadmap"
                        className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                      >
                        View all
                        <FiChevronRight className="w-4 h-4 ml-1" />
                      </Link>
                    </div>
                  </div>
                  <div className="p-6">
                    {activeRoadmaps.length > 0 ? (
                      <div className="space-y-4">
                        {activeRoadmaps.slice(0, 3).map((roadmap) => (
                          <Link
                            key={roadmap.id}
                            to={`/roadmap/${roadmap.id}`}
                            className="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <h4 className="font-medium text-sm text-gray-900 dark:text-white">
                                  {roadmap.title}
                                </h4>
                                <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">
                                  Target: {roadmap.target_role}
                                </p>
                              </div>
                              <div className="text-right">
                                <div className="text-base font-semibold text-indigo-600 dark:text-indigo-400">
                                  {roadmap.completion_percentage?.toFixed(0) || 0}%
                                </div>
                                <p className="text-[10px] text-gray-500 dark:text-gray-400">
                                  {roadmap.total_duration_months} months
                                </p>
                              </div>
                            </div>
                            <div className="mt-3 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-indigo-600 rounded-full"
                                style={{ width: `${roadmap.completion_percentage || 0}%` }}
                              />
                            </div>
                          </Link>
                        ))}
                        {activeRoadmaps.length > 3 && (
                          <Link
                            to="/roadmap"
                            className="block text-center text-sm text-indigo-600 dark:text-indigo-400 hover:underline mt-2"
                          >
                            View all {activeRoadmaps.length} roadmaps →
                          </Link>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 mx-auto bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
                          <FiTarget className="w-8 h-8 text-gray-400 dark:text-gray-500" />
                        </div>
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                          No active roadmaps
                        </h4>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
                          Start your career journey by creating your first roadmap
                        </p>
                        <button
                          onClick={handleGenerateRoadmap}
                          className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
                        >
                          <HiOutlineSparkles className="w-5 h-5 mr-2" />
                          Generate Your First Roadmap
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Actions Section */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6">
                  <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center">
                      <FiZap className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        Quick Actions
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Boost your career in one click
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    <button
                      onClick={() => handleQuickAction('resume')}
                      className="group relative bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                    >
                      <div className="w-14 h-14 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-md">
                        <FiBriefcase className="w-7 h-7 text-indigo-600 dark:text-indigo-400" />
                      </div>
                      <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                        Analyze Resume
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Get AI-powered feedback
                      </p>
                    </button>

                    <button
                      onClick={() => handleQuickAction('skills')}
                      className="group relative bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                    >
                      <div className="w-14 h-14 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-md">
                        <FiAward className="w-7 h-7 text-green-600 dark:text-green-400" />
                      </div>
                      <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                        Skill Assessment
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Identify skill gaps
                      </p>
                    </button>

                    <button
                      onClick={() => handleQuickAction('goals')}
                      className="group relative bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                    >
                      <div className="w-14 h-14 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-md">
                        <FiTarget className="w-7 h-7 text-orange-600 dark:text-orange-400" />
                      </div>
                      <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                        Set Career Goals
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Define your targets
                      </p>
                    </button>

                    <Link
                      to="/learning"
                      className="group relative bg-gradient-to-br from-pink-50 to-rose-50 dark:from-pink-900/20 dark:to-rose-900/20 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-200 hover:-translate-y-1"
                    >
                      <div className="w-14 h-14 bg-white dark:bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-md">
                        <FiBookOpen className="w-7 h-7 text-pink-600 dark:text-pink-400" />
                      </div>
                      <h4 className="font-semibold text-sm text-gray-900 dark:text-white mb-1">
                        Learning
                      </h4>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Browse resources
                      </p>
                    </Link>
                  </div>
                </div>
              </div>

              {/* Sidebar - Right Column */}
              <div className="space-y-8">
                {/* Recent Activity Card */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden">
                  <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                        <FiActivity className="w-5 h-5 text-green-600 dark:text-green-400" />
                      </div>
                      <div>
                        <h4 className="text-base font-semibold text-gray-900 dark:text-white">
                          Recent Activity
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Your latest updates
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="divide-y divide-gray-200 dark:divide-gray-700">
                    {recentRoadmaps.length > 0 ? (
                      recentRoadmaps.map((roadmap, index) => (
                        <Link
                          key={roadmap.id || index}
                          to={`/roadmap/${roadmap.id}`}
                          className="block p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                              <FiTrendingUp className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                {roadmap.title || 'Untitled Roadmap'}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                Updated {new Date(roadmap.updated_at || roadmap.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="text-right">
                              <p className="text-sm font-bold text-indigo-600 dark:text-indigo-400">
                                {roadmap.completion_percentage?.toFixed(0) || 0}%
                              </p>
                            </div>
                          </div>
                        </Link>
                      ))
                    ) : (
                      <div className="p-8 text-center">
                        <FiActivity className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          No recent activity
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'roadmaps' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-indigo-100 dark:bg-indigo-900/30 rounded-xl flex items-center justify-center">
                    <FiLayers className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      All Roadmaps
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Manage and track your career paths
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleGenerateRoadmap}
                  className="inline-flex items-center px-6 py-3 bg-indigo-600 text-white rounded-xl font-medium hover:bg-indigo-700 transition-colors"
                >
                  <FiPlus className="w-5 h-5 mr-2" />
                  New Roadmap
                </button>
              </div>
              <div className="space-y-4">
                {roadmaps && roadmaps.length > 0 ? (
                  roadmaps.map((roadmap) => (
                    <Link
                      key={roadmap.id}
                      to={`/roadmap/${roadmap.id}`}
                      className="block p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h4 className="font-medium text-sm text-gray-900 dark:text-white">
                            {roadmap.title}
                          </h4>
                          <p className="text-[11px] text-gray-500 dark:text-gray-400 mt-1">
                            Target: {roadmap.target_role}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-base font-semibold text-indigo-600 dark:text-indigo-400">
                            {roadmap.completion_percentage?.toFixed(0) || 0}%
                          </div>
                          <p className="text-[10px] text-gray-500 dark:text-gray-400">
                            {roadmap.total_duration_months} months • {roadmap.steps?.length || 0} steps
                          </p>
                        </div>
                      </div>
                      <div className="mt-3 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-600 rounded-full"
                          style={{ width: `${roadmap.completion_percentage || 0}%` }}
                        />
                      </div>
                    </Link>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 dark:text-gray-400">No roadmaps found</p>
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'skills' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Your Skills
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Track and manage your professional skills
                  </p>
                </div>
                <Link
                  to="/skills"
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                >
                  Manage Skills
                  <FiChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </div>

              {skills && skills.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-4">
                      <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {skills.length}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Total Skills</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {skills.filter(s => s.proficiency_level === 'expert').length}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Expert Level</p>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4">
                      <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        {skills.filter(s => s.proficiency_level === 'advanced').length}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Advanced</p>
                    </div>
                  </div>

                  {/* Top Skills Preview */}
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Your Top Skills</h4>
                    <div className="space-y-2">
                      {skills.slice(0, 3).map((skill) => (
                        <div key={skill.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                          <span className="text-sm font-medium text-gray-900 dark:text-white">{skill.skill_name}</span>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            skill.proficiency_level === 'expert' ? 'bg-purple-100 text-purple-700' :
                            skill.proficiency_level === 'advanced' ? 'bg-green-100 text-green-700' :
                            skill.proficiency_level === 'intermediate' ? 'bg-blue-100 text-blue-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {skill.proficiency_level}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {careerGoal && (
                    <div className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl p-4 mt-4">
                      <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Current Career Goal
                      </p>
                      <p className="text-base font-semibold text-indigo-600 dark:text-indigo-400">
                        {careerGoal.target_role}
                      </p>
                      <Link
                        to="/skills?analyze=true"
                        className="mt-3 inline-block text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        Run Gap Analysis →
                      </Link>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                    <FiAward className="w-8 h-8 text-gray-400" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
                    No skills added yet
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                    Add your skills to get personalized career recommendations
                  </p>
                  <Link
                    to="/skills"
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
                  >
                    Add Your First Skill
                  </Link>
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'learning' && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Learning Resources
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Resources from your roadmaps
                  </p>
                </div>
                <Link
                  to="/learning"
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-lg transition-colors"
                >
                  View All
                  <FiChevronRight className="w-4 h-4 ml-1" />
                </Link>
              </div>

              {learningResources.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="bg-indigo-50 dark:bg-indigo-900/20 rounded-xl p-4">
                      <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {learningResources.length}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Total Resources</p>
                    </div>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-xl p-4">
                      <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                        {learningResources.filter(r => r.completion_status === 'completed').length}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Completed</p>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {learningResources.slice(0, 3).map((resource) => (
                      <div
                        key={resource.id}
                        className="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                      >
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                          {resource.title}
                        </h4>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {resource.platform} • {resource.difficulty_level || 'All levels'}
                        </p>
                      </div>
                    ))}
                  </div>

                  {learningResources.length > 3 && (
                    <Link
                      to="/learning"
                      className="block text-center text-sm text-indigo-600 dark:text-indigo-400 hover:underline mt-2"
                    >
                      View all {learningResources.length} resources →
                    </Link>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <div className="w-16 h-16 mx-auto bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mb-4">
                    <FiBookOpen className="w-8 h-8 text-gray-400" />
                  </div>
                  <h4 className="text-base font-semibold text-gray-900 dark:text-white mb-2">
                    No learning resources yet
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                    Create roadmaps with AI to generate personalized learning resources
                  </p>
                  <button
                    onClick={handleGenerateRoadmap}
                    className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
                  >
                    <HiOutlineSparkles className="w-4 h-4 mr-2" />
                    Generate Roadmap
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Skill Categories Card - At the bottom with better emerald gradient */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-gradient-to-br from-emerald-600 to-teal-600 rounded-2xl shadow-2xl overflow-hidden relative"
          >
            <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
            
            <div className="relative p-8">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                    <FiGrid className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="text-lg font-semibold text-white">Skill Categories</h4>
                </div>
                <Link
                  to="/skills"
                  className="bg-white/20 text-white text-xs px-3 py-1 rounded-full hover:bg-white/30 transition-colors"
                >
                  View all
                </Link>
              </div>

              {skillCategories.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {skillCategories.slice(0, 6).map((category, index) => (
                    <div
                      key={index}
                      className="bg-white/10 backdrop-blur-sm rounded-xl p-4"
                    >
                      <div className="flex items-center justify-between">
                        <h5 className="text-white font-medium text-base">
                          {category.name}
                        </h5>
                        <span className="bg-emerald-500 text-white text-xs px-2 py-1 rounded-full">
                          {category.count} {category.count === 1 ? 'skill' : 'skills'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-white/80 text-sm">
                    No skills added yet. Add skills to see categories.
                  </p>
                  <Link
                    to="/skills"
                    className="inline-block mt-4 text-white bg-white/20 px-4 py-2 rounded-lg text-sm hover:bg-white/30 transition-colors"
                  >
                    Add Skills
                  </Link>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;