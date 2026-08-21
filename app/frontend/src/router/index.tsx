// src/router/index.tsx

import { createBrowserRouter, Navigate } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';
import AdminRoute from './AdminRoute';
import LoginPage from '../components/auth/LoginPage';
import MainLayout from '../components/layout/MainLayout';
import ChatWindow from '../components/chat/ChatWindow';
import HomePage from '../components/chat/HomePage';
import SettingsPage from '../components/settings/SettingsPage';
import AdminDashboard from '../components/admin/AdminDashboard';

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <MainLayout />
      </ProtectedRoute>
    ),
    children: [
      { index: true, element: <HomePage /> },
      { path: 'chat/:chatId', element: <ChatWindow /> },
      { path: 'settings', element: <SettingsPage /> },
    ],
  },
  {
    path: '/admin',
    element: (
      <AdminRoute>
        <AdminDashboard />
      </AdminRoute>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/login" replace />,
  },
]);