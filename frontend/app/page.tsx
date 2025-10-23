// frontend/app/page.tsx
'use client';

import { useState } from 'react';
import ChatBox from '@/components/ChatBox';
import ImageUpload from '@/components/ImageUpload';
import CsvPanel from '@/components/CsvPanel';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/hooks/useAuth';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'image' | 'csv'>('chat');
  const { user, signOut } = useAuth();

  return (
    <ProtectedRoute>
      <main className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <header className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Multi-Modal Chat Assistant
              </h1>
              <p className="text-gray-600">
                Text conversations, image analysis, and CSV data insights
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Welcome back,</p>
                <p className="font-medium text-gray-900">{user?.full_name || user?.email}</p>
              </div>
              <button
                onClick={signOut}
                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg transition-colors text-sm font-medium"
              >
                Sign Out
              </button>
            </div>
          </header>

          {/* Tab Navigation */}
          <div className="bg-white rounded-lg shadow-sm mb-6">
            <div className="flex border-b">
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'chat'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                💬 Text Chat
              </button>
              <button
                onClick={() => setActiveTab('image')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'image'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🖼️ Image Q&A
              </button>
              <button
                onClick={() => setActiveTab('csv')}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'csv'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📊 CSV Analysis
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            {activeTab === 'chat' && <ChatBox />}
            {activeTab === 'image' && <ImageUpload />}
            {activeTab === 'csv' && <CsvPanel />}
          </div>
        </div>
      </main>
    </ProtectedRoute>
  );
}