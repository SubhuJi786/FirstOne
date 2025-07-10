import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';
import { ThemeProvider } from './contexts/ThemeContext';
import Dashboard from './components/Dashboard';
import AICoach from './components/AICoach';
import Roadmap from './components/Roadmap';
import MockTests from './components/MockTests';
import Analytics from './components/Analytics';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';
import UserSetup from './components/UserSetup';
import Header from './components/Header';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user exists in localStorage
    const savedUser = localStorage.getItem('enhancedAICoachUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const handleUserSetup = (userData) => {
    setUser(userData);
    localStorage.setItem('enhancedAICoachUser', JSON.stringify(userData));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!user) {
    return (
      <ThemeProvider>
        <UserSetup onUserSetup={handleUserSetup} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider>
      <UserProvider user={user}>
        <Router>
          <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
              <Header />
              <main className="flex-1 overflow-auto">
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/ai-coach" element={<AICoach />} />
                  <Route path="/roadmap" element={<Roadmap />} />
                  <Route path="/mock-tests" element={<MockTests />} />
                  <Route path="/analytics" element={<Analytics />} />
                  <Route path="/settings" element={<Settings />} />
                </Routes>
              </main>
            </div>
          </div>
        </Router>
      </UserProvider>
    </ThemeProvider>
  );
}

export default App;