const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

class ApiService {
  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // User Management
  async createUser(userData) {
    return this.request('/api/users', {
      method: 'POST',
      body: userData,
    });
  }

  async getUserProfile(userId) {
    return this.request(`/api/users/${userId}`);
  }

  async updateUserProfile(userId, updates) {
    return this.request(`/api/users/${userId}`, {
      method: 'PUT',
      body: updates,
    });
  }

  async getUserProgress(userId) {
    return this.request(`/api/users/${userId}/progress`);
  }

  async updateProgress(userId, progressData) {
    return this.request(`/api/users/${userId}/progress`, {
      method: 'POST',
      body: progressData,
    });
  }

  // AI Coach
  async chatWithCoach(userId, message, topicId = null) {
    return this.request(`/api/chat/${userId}`, {
      method: 'POST',
      body: { message, topic_id: topicId },
    });
  }

  async getSuggestions(userId) {
    return this.request(`/api/chat/${userId}/suggestions`);
  }

  async getPerformanceAnalytics(userId) {
    return this.request(`/api/chat/${userId}/analytics`);
  }

  async getStudyStrategy(topicId, userId) {
    return this.request(`/api/topics/${topicId}/strategy?user_id=${userId}`);
  }

  // Subjects and Topics
  async getSubjects(examType) {
    return this.request(`/api/subjects?exam_type=${examType}`);
  }

  async getTopics(subjectId) {
    return this.request(`/api/subjects/${subjectId}/topics`);
  }

  // Roadmap
  async generateRoadmap(userId, weekOffset = 0) {
    return this.request(`/api/roadmap/${userId}`, {
      method: 'POST',
      body: { week_offset: weekOffset },
    });
  }

  async getRoadmap(userId, weekOffset = 0) {
    return this.request(`/api/roadmap/${userId}?week_offset=${weekOffset}`);
  }

  async updateRoadmapItem(itemId, status) {
    return this.request(`/api/roadmap/items/${itemId}`, {
      method: 'PUT',
      body: status,
    });
  }

  async getRoadmapAnalytics(userId) {
    return this.request(`/api/roadmap/${userId}/analytics`);
  }

  // Mock Tests
  async scheduleMockTest(userId, testData) {
    return this.request(`/api/mock-tests/${userId}`, {
      method: 'POST',
      body: testData,
    });
  }

  async getMockTests(userId) {
    return this.request(`/api/mock-tests/${userId}`);
  }

  async startMockTest(testId) {
    return this.request(`/api/mock-tests/${testId}/start`, {
      method: 'POST',
    });
  }

  async submitAnswer(testId, answerData) {
    return this.request(`/api/mock-tests/${testId}/submit`, {
      method: 'POST',
      body: answerData,
    });
  }

  async completeMockTest(testId) {
    return this.request(`/api/mock-tests/${testId}/complete`, {
      method: 'POST',
    });
  }

  async getPerformanceTrends(userId) {
    return this.request(`/api/mock-tests/${userId}/trends`);
  }

  async scheduleRegularTests(userId, examType, frequency = 'weekly') {
    return this.request(`/api/mock-tests/${userId}/schedule-regular?exam_type=${examType}&frequency=${frequency}`, {
      method: 'POST',
    });
  }

  // Learning Sessions
  async createLearningSession(userId, topicId, sessionType) {
    return this.request(`/api/sessions/${userId}?topic_id=${topicId}&session_type=${sessionType}`, {
      method: 'POST',
    });
  }

  async endLearningSession(sessionId, performanceScore, understandingLevel, mood = 'neutral', notes = '') {
    return this.request(`/api/sessions/${sessionId}/end?performance_score=${performanceScore}&understanding_level=${understandingLevel}&mood=${mood}&notes=${encodeURIComponent(notes)}`, {
      method: 'PUT',
    });
  }

  // Health Check
  async healthCheck() {
    return this.request('/api/health');
  }
}

export const apiService = new ApiService();