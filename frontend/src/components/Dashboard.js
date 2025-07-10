import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/apiService';

const Dashboard = () => {
  const { user, userProfile, progress, loading } = useUser();
  const [suggestions, setSuggestions] = useState([]);
  const [motivationalMessage, setMotivationalMessage] = useState('');
  const [roadmapData, setRoadmapData] = useState(null);
  const [recentTests, setRecentTests] = useState([]);
  const [loadingData, setLoadingData] = useState(true);

  useEffect(() => {
    if (user?.user_id) {
      fetchDashboardData();
    }
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      setLoadingData(true);
      
      // Fetch suggestions and motivation
      const suggestionsData = await apiService.getSuggestions(user.user_id);
      setSuggestions(suggestionsData.suggestions || []);
      setMotivationalMessage(suggestionsData.motivational_message || '');

      // Fetch current roadmap
      const roadmap = await apiService.getRoadmap(user.user_id);
      setRoadmapData(roadmap.roadmap);

      // Fetch recent mock tests
      const tests = await apiService.getMockTests(user.user_id);
      setRecentTests(tests.tests?.slice(0, 3) || []);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoadingData(false);
    }
  };

  const calculateOverallProgress = () => {
    if (!progress || progress.length === 0) return 0;
    const totalMastery = progress.reduce((sum, item) => sum + item.mastery_level, 0);
    return Math.round((totalMastery / progress.length) * 100);
  };

  const getSubjectProgress = () => {
    if (!progress || progress.length === 0) return {};
    
    const subjectData = {};
    progress.forEach(item => {
      if (!subjectData[item.subject_name]) {
        subjectData[item.subject_name] = { total: 0, mastery: 0 };
      }
      subjectData[item.subject_name].total += 1;
      subjectData[item.subject_name].mastery += item.mastery_level;
    });

    Object.keys(subjectData).forEach(subject => {
      subjectData[subject].percentage = Math.round(
        (subjectData[subject].mastery / subjectData[subject].total) * 100
      );
    });

    return subjectData;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'struggling': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading || loadingData) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const overallProgress = calculateOverallProgress();
  const subjectProgress = getSubjectProgress();

  return (
    <div className="p-6 space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold mb-2">Hello {user?.name}! 👋</h1>
        <p className="text-blue-100 mb-4">{motivationalMessage}</p>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-2">
            <span>🎯 Target:</span>
            <span className="font-semibold">{user?.exam_type} {user?.target_year}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>📈 Progress:</span>
            <span className="font-semibold">{overallProgress}%</span>
          </div>
        </div>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Overall Progress</h3>
          <div className="relative pt-1">
            <div className="flex mb-2 items-center justify-between">
              <div>
                <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
                  {overallProgress}%
                </span>
              </div>
            </div>
            <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
              <div
                style={{ width: `${overallProgress}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500"
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Topics Covered</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Topics</span>
              <span className="font-semibold">{progress.length}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Completed</span>
              <span className="font-semibold text-green-600">
                {progress.filter(p => p.status === 'completed').length}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">In Progress</span>
              <span className="font-semibold text-blue-600">
                {progress.filter(p => p.status === 'in_progress').length}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Study Streak</h3>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-500 mb-2">🔥</div>
            <div className="text-2xl font-bold text-gray-900">7 Days</div>
            <div className="text-sm text-gray-600">Keep it up!</div>
          </div>
        </div>
      </div>

      {/* Subject Progress */}
      <div className="bg-white p-6 rounded-xl shadow-sm">
        <h3 className="text-lg font-semibold mb-4">Subject-wise Progress</h3>
        <div className="space-y-4">
          {Object.entries(subjectProgress).map(([subject, data]) => (
            <div key={subject} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <span className="font-medium">{subject}</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${data.percentage}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium w-12 text-right">{data.percentage}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions and Roadmap */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">💡 Personalized Suggestions</h3>
          <div className="space-y-3">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <p className="text-sm text-gray-700">{suggestion}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm">
          <h3 className="text-lg font-semibold mb-4">📅 This Week's Plan</h3>
          {roadmapData && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Week {roadmapData.week_number}</span>
                <span className="font-medium">{roadmapData.items?.length || 0} items</span>
              </div>
              <div className="space-y-1">
                {roadmapData.items?.slice(0, 3).map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-gray-700">{item.topic_name}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(item.status)}`}>
                      {item.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded-xl shadow-sm">
        <h3 className="text-lg font-semibold mb-4">📝 Recent Mock Tests</h3>
        {recentTests.length > 0 ? (
          <div className="space-y-3">
            {recentTests.map((test, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{test.test_name}</p>
                  <p className="text-sm text-gray-600">{test.exam_type}</p>
                </div>
                <div className="text-right">
                  {test.status === 'completed' ? (
                    <div>
                      <p className="font-medium text-green-600">{test.score}%</p>
                      <p className="text-sm text-gray-600">Percentile: {test.percentile}</p>
                    </div>
                  ) : (
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(test.status)}`}>
                      {test.status}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No mock tests taken yet. Start with your first test!</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;