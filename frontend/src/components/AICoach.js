import React, { useState, useEffect, useRef } from 'react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/apiService';

const AICoach = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (user?.user_id) {
      fetchSuggestions();
      // Add welcome message
      setMessages([{
        type: 'coach',
        content: `Hello ${user.name}! I'm your AI coach for ${user.exam_type} preparation. I'm here to help with your doubts, provide study strategies, and keep you motivated. What would you like to know?`,
        timestamp: new Date().toISOString()
      }]);
    }
  }, [user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSuggestions = async () => {
    try {
      const data = await apiService.getSuggestions(user.user_id);
      setSuggestions(data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const handleSendMessage = async (message = inputMessage) => {
    if (!message.trim() || loading) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      const response = await apiService.chatWithCoach(user.user_id, message);
      
      const coachMessage = {
        type: 'coach',
        content: response.response,
        timestamp: response.timestamp
      };

      setMessages(prev => [...prev, coachMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        type: 'coach',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    const cleanSuggestion = suggestion.replace(/^[🎯💪📚🚀📈🌱🔥]+\s*/, '');
    handleSendMessage(cleanSuggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-full">
      {/* Chat Area */}
      <div className="flex-1 flex flex-col bg-white">
        {/* Chat Header */}
        <div className="border-b p-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-xl">🤖</span>
            </div>
            <div>
              <h2 className="text-lg font-semibold">AI Coach</h2>
              <p className="text-sm text-gray-600">Your personalized {user?.exam_type} mentor</p>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2 max-w-xs">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex space-x-3">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask your AI coach anything..."
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows="2"
              disabled={loading}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={loading || !inputMessage.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-80 bg-gray-50 border-l p-4 space-y-6">
        {/* Quick Actions */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Quick Actions</h3>
          <div className="space-y-2">
            <button
              onClick={() => handleSendMessage('Help me with study strategy')}
              className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
            >
              📚 Study Strategy
            </button>
            <button
              onClick={() => handleSendMessage('I need motivation')}
              className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
            >
              💪 Motivation
            </button>
            <button
              onClick={() => handleSendMessage('Explain a difficult concept')}
              className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
            >
              🧠 Concept Help
            </button>
            <button
              onClick={() => handleSendMessage('Previous year question patterns')}
              className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors"
            >
              📊 Exam Patterns
            </button>
          </div>
        </div>

        {/* Personalized Suggestions */}
        <div>
          <h3 className="text-lg font-semibold mb-3">💡 Suggestions</h3>
          <div className="space-y-2">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left p-3 bg-white rounded-lg hover:bg-blue-50 transition-colors text-sm"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>

        {/* Study Tips */}
        <div>
          <h3 className="text-lg font-semibold mb-3">📝 Study Tips</h3>
          <div className="space-y-3 text-sm text-gray-600">
            <div className="bg-white p-3 rounded-lg">
              <p className="font-medium text-gray-900 mb-1">Active Recall</p>
              <p>Test yourself regularly instead of just re-reading notes.</p>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <p className="font-medium text-gray-900 mb-1">Spaced Repetition</p>
              <p>Review topics at increasing intervals for better retention.</p>
            </div>
            <div className="bg-white p-3 rounded-lg">
              <p className="font-medium text-gray-900 mb-1">Practice Problems</p>
              <p>Solve problems daily to build speed and accuracy.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AICoach;