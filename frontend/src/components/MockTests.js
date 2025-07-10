import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/apiService';

const MockTests = () => {
  const { user } = useUser();
  const [tests, setTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [trends, setTrends] = useState(null);
  const [activeTest, setActiveTest] = useState(null);

  useEffect(() => {
    if (user?.user_id) {
      fetchTests();
      fetchTrends();
    }
  }, [user]);

  const fetchTests = async () => {
    try {
      const response = await apiService.getMockTests(user.user_id);
      setTests(response.tests || []);
    } catch (error) {
      console.error('Error fetching tests:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTrends = async () => {
    try {
      const response = await apiService.getPerformanceTrends(user.user_id);
      setTrends(response.trends);
    } catch (error) {
      console.error('Error fetching trends:', error);
    }
  };

  const scheduleTest = async (testData) => {
    try {
      await apiService.scheduleMockTest(user.user_id, testData);
      setShowScheduleModal(false);
      fetchTests();
    } catch (error) {
      console.error('Error scheduling test:', error);
    }
  };

  const startTest = async (testId) => {
    try {
      const response = await apiService.startMockTest(testId);
      setActiveTest(response.session);
    } catch (error) {
      console.error('Error starting test:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'scheduled': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not scheduled';
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (activeTest) {
    return <TestInterface test={activeTest} onComplete={() => {
      setActiveTest(null);
      fetchTests();
      fetchTrends();
    }} />;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">📝 Mock Tests</h1>
          <p className="text-gray-600 mt-1">Practice with realistic exam simulations</p>
        </div>
        <button
          onClick={() => setShowScheduleModal(true)}
          className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
        >
          Schedule New Test
        </button>
      </div>

      {/* Performance Overview */}
      {trends && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Total Tests</h3>
            <div className="text-3xl font-bold text-blue-600">{trends.total_tests}</div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Average Score</h3>
            <div className="text-3xl font-bold text-green-600">
              {Math.round(trends.avg_score)}%
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Best Score</h3>
            <div className="text-3xl font-bold text-purple-600">
              {Math.round(trends.best_score)}%
            </div>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Trend</h3>
            <div className={`text-3xl font-bold ${
              trends.trend === 'improving' ? 'text-green-600' :
              trends.trend === 'declining' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {trends.trend === 'improving' ? '📈' :
               trends.trend === 'declining' ? '📉' : '➡️'}
            </div>
          </div>
        </div>
      )}

      {/* Tests List */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Your Mock Tests</h2>
        </div>
        
        {tests.length > 0 ? (
          <div className="divide-y">
            {tests.map((test) => (
              <div key={test.id} className="p-6 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-semibold">{test.test_name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(test.status)}`}>
                        {test.status}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <span>📋 {test.exam_type}</span>
                      <span>⏱️ {test.duration} minutes</span>
                      <span>❓ {test.total_questions} questions</span>
                      <span>📅 {formatDate(test.scheduled_date)}</span>
                    </div>
                    
                    {test.status === 'completed' && (
                      <div className="flex items-center space-x-4 mt-2">
                        <span className="text-sm font-medium text-green-600">
                          Score: {Math.round(test.score)}%
                        </span>
                        <span className="text-sm font-medium text-blue-600">
                          Percentile: {Math.round(test.percentile)}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex space-x-2">
                    {test.status === 'scheduled' && (
                      <button
                        onClick={() => startTest(test.id)}
                        className="bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600"
                      >
                        Start Test
                      </button>
                    )}
                    
                    {test.status === 'completed' && (
                      <button className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600">
                        View Results
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold mb-2">No Mock Tests Yet</h3>
            <p className="text-gray-600 mb-6">Start practicing with mock tests to improve your performance</p>
            <button
              onClick={() => setShowScheduleModal(true)}
              className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600"
            >
              Schedule Your First Test
            </button>
          </div>
        )}
      </div>

      {/* Schedule Modal */}
      {showScheduleModal && (
        <ScheduleTestModal
          examType={user.exam_type}
          onSchedule={scheduleTest}
          onClose={() => setShowScheduleModal(false)}
        />
      )}
    </div>
  );
};

const ScheduleTestModal = ({ examType, onSchedule, onClose }) => {
  const [formData, setFormData] = useState({
    exam_type: examType === 'JEE' ? 'JEE_MAIN' : 'NEET',
    test_name: '',
    scheduled_date: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const testData = {
      ...formData,
      scheduled_date: formData.scheduled_date ? new Date(formData.scheduled_date) : null
    };
    
    onSchedule(testData);
  };

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md">
        <h2 className="text-xl font-semibold mb-4">Schedule Mock Test</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Test Name
            </label>
            <input
              type="text"
              name="test_name"
              value={formData.test_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Weekly Mock Test 1"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Exam Type
            </label>
            <select
              name="exam_type"
              value={formData.exam_type}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {examType === 'JEE' && (
                <>
                  <option value="JEE_MAIN">JEE Main</option>
                  <option value="JEE_ADVANCED">JEE Advanced</option>
                </>
              )}
              {examType === 'NEET' && (
                <option value="NEET">NEET</option>
              )}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scheduled Date & Time (Optional)
            </label>
            <input
              type="datetime-local"
              name="scheduled_date"
              value={formData.scheduled_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
            >
              Schedule Test
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const TestInterface = ({ test, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(test.duration * 60); // Convert to seconds
  const [showConfirmSubmit, setShowConfirmSubmit] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          handleSubmitTest();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleAnswerSelect = (questionId, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleSubmitTest = async () => {
    try {
      // Submit all answers
      for (const [questionId, answer] of Object.entries(answers)) {
        await apiService.submitAnswer(test.mock_test_id, {
          question_id: questionId,
          user_answer: answer,
          time_taken: 120 // Default time
        });
      }
      
      // Complete the test
      await apiService.completeMockTest(test.mock_test_id);
      onComplete();
    } catch (error) {
      console.error('Error submitting test:', error);
    }
  };

  const questions = test.questions || [];
  const question = questions[currentQuestion];

  if (!question) {
    return (
      <div className="p-6 text-center">
        <p>No questions available</p>
        <button onClick={onComplete} className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-lg">
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm p-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Mock Test in Progress</h1>
          <p className="text-sm text-gray-600">Question {currentQuestion + 1} of {questions.length}</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="text-lg font-mono">
            ⏰ {formatTime(timeLeft)}
          </div>
          <button
            onClick={() => setShowConfirmSubmit(true)}
            className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
          >
            Submit Test
          </button>
        </div>
      </div>

      {/* Question Content */}
      <div className="flex-1 flex">
        <div className="flex-1 p-6">
          <div className="bg-white rounded-xl p-6 h-full">
            <div className="mb-4">
              <span className="text-sm text-gray-600">Question {currentQuestion + 1}</span>
              <h2 className="text-lg font-semibold mt-1">{question.question_text}</h2>
            </div>
            
            {question.options && JSON.parse(question.options).length > 0 && (
              <div className="space-y-3">
                {JSON.parse(question.options).map((option, index) => (
                  <label key={index} className="flex items-center space-x-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="radio"
                      name={`question-${question.id}`}
                      value={index.toString()}
                      checked={answers[question.id] === index.toString()}
                      onChange={(e) => handleAnswerSelect(question.id, e.target.value)}
                      className="text-blue-500"
                    />
                    <span>{String.fromCharCode(65 + index)}. {option}</span>
                  </label>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <div className="w-80 p-6">
          <div className="bg-white rounded-xl p-4">
            <h3 className="font-semibold mb-4">Question Navigation</h3>
            <div className="grid grid-cols-5 gap-2 mb-4">
              {questions.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentQuestion(index)}
                  className={`w-8 h-8 rounded text-sm ${
                    index === currentQuestion
                      ? 'bg-blue-500 text-white'
                      : answers[questions[index]?.id]
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {index + 1}
                </button>
              ))}
            </div>
            
            <div className="space-y-2">
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="w-full bg-gray-100 text-gray-700 py-2 rounded-lg disabled:opacity-50"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentQuestion(Math.min(questions.length - 1, currentQuestion + 1))}
                disabled={currentQuestion === questions.length - 1}
                className="w-full bg-blue-500 text-white py-2 rounded-lg disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Confirm Submit Modal */}
      {showConfirmSubmit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Submit Test?</h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to submit the test? You answered {Object.keys(answers).length} out of {questions.length} questions.
            </p>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowConfirmSubmit(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitTest}
                className="flex-1 bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600"
              >
                Submit Test
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MockTests;