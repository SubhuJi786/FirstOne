import React, { useState } from 'react';
import { apiService } from '../services/apiService';

const UserSetup = ({ onUserSetup }) => {
  const [formData, setFormData] = useState({
    name: '',
    exam_type: '',
    target_year: new Date().getFullYear() + 1,
    study_hours_per_day: 4,
    preferred_study_time: 'morning'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Create user
      const userResponse = await apiService.createUser({
        name: formData.name,
        exam_type: formData.exam_type,
        target_year: formData.target_year
      });

      // Update profile with additional settings
      await apiService.updateUserProfile(userResponse.user_id, {
        study_hours_per_day: formData.study_hours_per_day,
        preferred_study_time: formData.preferred_study_time
      });

      // Pass user data to parent component
      onUserSetup({
        user_id: userResponse.user_id,
        name: formData.name,
        exam_type: formData.exam_type,
        target_year: formData.target_year
      });

    } catch (error) {
      setError('Failed to create user. Please try again.');
      console.error('User creation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">🧠 Enhanced AI Coach</h1>
          <p className="text-gray-600">Your personalized JEE & NEET preparation companion</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your full name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Exam
            </label>
            <select
              name="exam_type"
              value={formData.exam_type}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select your target exam</option>
              <option value="JEE">JEE (Joint Entrance Examination)</option>
              <option value="NEET">NEET (National Eligibility cum Entrance Test)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Year
            </label>
            <select
              name="target_year"
              value={formData.target_year}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={new Date().getFullYear() + 1}>{new Date().getFullYear() + 1}</option>
              <option value={new Date().getFullYear() + 2}>{new Date().getFullYear() + 2}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Study Hours Per Day
            </label>
            <select
              name="study_hours_per_day"
              value={formData.study_hours_per_day}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={2}>2 hours</option>
              <option value={4}>4 hours</option>
              <option value={6}>6 hours</option>
              <option value={8}>8 hours</option>
              <option value={10}>10 hours</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Study Time
            </label>
            <select
              name="preferred_study_time"
              value={formData.preferred_study_time}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="morning">Morning (6AM - 12PM)</option>
              <option value="afternoon">Afternoon (12PM - 6PM)</option>
              <option value="evening">Evening (6PM - 12AM)</option>
              <option value="night">Night (12AM - 6AM)</option>
            </select>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating Your Profile...' : 'Start Your Journey'}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="text-center">
            <p className="text-sm text-gray-600">Features you'll get:</p>
            <div className="mt-2 flex flex-wrap justify-center gap-2">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">AI Coach</span>
              <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">Weekly Roadmaps</span>
              <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">Mock Tests</span>
              <span className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-xs">Progress Tracking</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserSetup;