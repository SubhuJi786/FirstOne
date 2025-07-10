import React from 'react';
import { NavLink } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';

const Sidebar = () => {
  const { user } = useUser();

  const navItems = [
    { path: '/dashboard', icon: '📊', label: 'Dashboard' },
    { path: '/ai-coach', icon: '🤖', label: 'AI Coach' },
    { path: '/roadmap', icon: '🗺️', label: 'Roadmap' },
    { path: '/mock-tests', icon: '📝', label: 'Mock Tests' },
    { path: '/analytics', icon: '📈', label: 'Analytics' },
    { path: '/settings', icon: '⚙️', label: 'Settings' }
  ];

  return (
    <div className="w-64 bg-white shadow-lg flex flex-col">
      <div className="p-6 border-b">
        <h1 className="text-xl font-bold text-gray-900">🧠 AI Coach</h1>
        <p className="text-sm text-gray-600 mt-1">{user?.exam_type} Preparation</p>
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border-l-4 border-blue-700'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`
                }
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-4 border-t">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold text-sm">
              {user?.name?.charAt(0) || 'U'}
            </span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-900">{user?.name}</p>
            <p className="text-xs text-gray-500">{user?.exam_type} {user?.target_year}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;