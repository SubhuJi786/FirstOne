import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/apiService';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children, user: initialUser }) => {
  const [user, setUser] = useState(initialUser);
  const [userProfile, setUserProfile] = useState(null);
  const [progress, setProgress] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.user_id) {
      fetchUserProfile();
      fetchUserProgress();
    }
  }, [user]);

  const fetchUserProfile = async () => {
    try {
      const profile = await apiService.getUserProfile(user.user_id);
      setUserProfile(profile);
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  };

  const fetchUserProgress = async () => {
    try {
      const progressData = await apiService.getUserProgress(user.user_id);
      setProgress(progressData.progress || []);
    } catch (error) {
      console.error('Error fetching user progress:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateUserProfile = async (updates) => {
    try {
      await apiService.updateUserProfile(user.user_id, updates);
      setUserProfile(prev => ({ ...prev, ...updates }));
    } catch (error) {
      console.error('Error updating user profile:', error);
      throw error;
    }
  };

  const updateProgress = async (topicId, masteryLevel, timeSpent, attempts = 0, correctAnswers = 0) => {
    try {
      await apiService.updateProgress(user.user_id, {
        topic_id: topicId,
        mastery_level: masteryLevel,
        time_spent: timeSpent,
        attempts,
        correct_answers: correctAnswers
      });
      await fetchUserProgress(); // Refresh progress
    } catch (error) {
      console.error('Error updating progress:', error);
      throw error;
    }
  };

  const value = {
    user,
    setUser,
    userProfile,
    progress,
    loading,
    updateUserProfile,
    updateProgress,
    refreshProgress: fetchUserProgress,
    refreshProfile: fetchUserProfile
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};