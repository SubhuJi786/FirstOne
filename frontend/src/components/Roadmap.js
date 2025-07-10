import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/apiService';

const Roadmap = () => {
  const { user } = useUser();
  const [roadmapData, setRoadmapData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedWeek, setSelectedWeek] = useState(0);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    if (user?.user_id) {
      fetchRoadmap();
      fetchAnalytics();
    }
  }, [user, selectedWeek]);

  const fetchRoadmap = async () => {
    try {
      setLoading(true);
      const response = await apiService.getRoadmap(user.user_id, selectedWeek);
      setRoadmapData(response.roadmap);
    } catch (error) {
      console.error('Error fetching roadmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await apiService.getRoadmapAnalytics(user.user_id);
      setAnalytics(response);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const generateNewRoadmap = async () => {
    try {
      setLoading(true);
      const response = await apiService.generateRoadmap(user.user_id, selectedWeek);
      setRoadmapData(response.roadmap);
    } catch (error) {
      console.error('Error generating roadmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateItemStatus = async (itemId, status) => {
    try {
      await apiService.updateRoadmapItem(itemId, status);
      await fetchRoadmap(); // Refresh roadmap
    } catch (error) {
      console.error('Error updating item status:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200';
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'skipped': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDayName = (dayOfWeek) => {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayOfWeek] || 'Unknown';
  };

  const groupItemsByDay = (items) => {
    if (!items) return {};
    
    const grouped = {};
    items.forEach(item => {
      const day = item.day_of_week;
      if (!grouped[day]) {
        grouped[day] = [];
      }
      grouped[day].push(item);
    });
    
    return grouped;
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const groupedItems = groupItemsByDay(roadmapData?.items);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📅 Study Roadmap</h1>
          <p className="text-gray-600 mt-1">Your personalized weekly study plan</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={selectedWeek}
            onChange={(e) => setSelectedWeek(parseInt(e.target.value))}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value={-1}>Previous Week</option>
            <option value={0}>Current Week</option>
            <option value={1}>Next Week</option>
            <option value={2}>Week After Next</option>
          </select>
          <button
            onClick={generateNewRoadmap}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
          >
            Regenerate Plan
          </button>
        </div>
      </div>

      {/* Analytics Summary */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Completion Rate</h3>
            <div className="text-3xl font-bold text-blue-600">
              {Math.round(analytics.analytics?.avg_completion_rate || 0)}%
            </div>
            <p className="text-sm text-gray-600">Average across weeks</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Weeks Tracked</h3>
            <div className="text-3xl font-bold text-green-600">
              {analytics.analytics?.total_weeks_tracked || 0}
            </div>
            <p className="text-sm text-gray-600">Total weeks</p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Adaptations</h3>
            <div className="text-3xl font-bold text-purple-600">
              {analytics.adaptations?.adaptations?.length || 0}
            </div>
            <p className="text-sm text-gray-600">Recommended changes</p>
          </div>
        </div>
      )}

      {/* Roadmap Content */}
      {roadmapData ? (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-6 border-b bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold">
                  Week {roadmapData.week_number}, {roadmapData.year}
                </h2>
                <p className="text-gray-600">
                  {roadmapData.items?.length || 0} study items planned
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Study Hours/Day</p>
                <p className="text-lg font-semibold">{roadmapData.study_hours_per_day}</p>
              </div>
            </div>
          </div>

          {/* Daily Schedule */}
          <div className="p-6">
            <div className="space-y-6">
              {[1, 2, 3, 4, 5, 6, 7].map(day => (
                <div key={day} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="text-lg font-semibold">{getDayName(day)}</h3>
                    <span className="text-sm text-gray-600">
                      {groupedItems[day]?.length || 0} items
                    </span>
                  </div>
                  
                  {groupedItems[day] && groupedItems[day].length > 0 ? (
                    <div className="space-y-2">
                      {groupedItems[day].map(item => (
                        <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3">
                              <span className="font-medium">{item.topic_name}</span>
                              <span className="text-sm text-gray-600">({item.subject_name})</span>
                            </div>
                            <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
                              <span>⏱️ {item.study_hours}h</span>
                              <span>🎯 Priority {item.priority}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(item.status)}`}>
                              {item.status}
                            </span>
                            
                            <div className="flex space-x-1">
                              {item.status !== 'completed' && (
                                <button
                                  onClick={() => updateItemStatus(item.id, 'completed')}
                                  className="text-green-600 hover:bg-green-100 p-1 rounded"
                                  title="Mark as completed"
                                >
                                  ✓
                                </button>
                              )}
                              {item.status !== 'skipped' && (
                                <button
                                  onClick={() => updateItemStatus(item.id, 'skipped')}
                                  className="text-red-600 hover:bg-red-100 p-1 rounded"
                                  title="Mark as skipped"
                                >
                                  ⤴️
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <p>🎉 Rest day or no specific topics planned</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <div className="text-6xl mb-4">📅</div>
          <h2 className="text-xl font-semibold mb-2">No Roadmap Found</h2>
          <p className="text-gray-600 mb-6">Let's create your personalized study plan!</p>
          <button
            onClick={generateNewRoadmap}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
          >
            Generate My Roadmap
          </button>
        </div>
      )}

      {/* Adaptations Section */}
      {analytics?.adaptations?.recommended_changes && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 text-yellow-800">🎯 Recommended Adaptations</h3>
          <div className="space-y-3">
            {analytics.adaptations.adaptations.map((adaptation, index) => (
              <div key={index} className="bg-white p-4 rounded-lg">
                <div className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                  <div>
                    <p className="font-medium">{adaptation.type.replace('_', ' ')}</p>
                    <p className="text-sm text-gray-600 mt-1">{adaptation.reason}</p>
                    <p className="text-sm text-blue-600 mt-1">💡 {adaptation.action}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Roadmap;