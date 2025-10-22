'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type InputMode = 'url' | 'file';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  plot_base64?: string;
  timestamp: string;
}

interface CsvInfo {
  rows: number;
  columns: number;
  column_names: string[];
  source_type: string;
  source_value: string;
}

export default function CsvPanel() {
  // Upload state
  const [mode, setMode] = useState<InputMode>('url');
  const [csvUrl, setCsvUrl] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  // Chat state
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [csvInfo, setCsvInfo] = useState<CsvInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showUpload, setShowUpload] = useState(true);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle CSV upload from URL
  const handleUploadUrl = async () => {
    if (!csvUrl.trim() || isUploading) return;

    setIsUploading(true);
    setUploadError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/csv/chat/upload-url`, {
        csvUrl: csvUrl,
        prompt: 'I want to analyze this dataset. Please give me an overview.',
      });

      const data = response.data;
      setSessionId(data.session_id);
      setCsvInfo(data.csv_info);
      setShowUpload(false);

      // Get initial conversation from backend
      const sessionResponse = await axios.get(
        `${API_BASE_URL}/csv/chat/session/${data.session_id}`
      );
      setMessages(sessionResponse.data.conversation_history);
    } catch (err: any) {
      console.error('Upload error:', err);
      setUploadError(
        err.response?.data?.detail || 'Failed to upload CSV from URL'
      );
    } finally {
      setIsUploading(false);
    }
  };

  // Handle CSV file upload
  const handleUploadFile = async () => {
    if (!csvFile || isUploading) return;

    setIsUploading(true);
    setUploadError('');

    try {
      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await axios.post(
        `${API_BASE_URL}/csv/chat/upload-file`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
        }
      );

      const data = response.data;
      setSessionId(data.session_id);
      setCsvInfo(data.csv_info);
      setShowUpload(false);

      // Get initial conversation from backend
      const sessionResponse = await axios.get(
        `${API_BASE_URL}/csv/chat/session/${data.session_id}`
      );
      setMessages(sessionResponse.data.conversation_history);
    } catch (err: any) {
      console.error('Upload error:', err);
      setUploadError(err.response?.data?.detail || 'Failed to upload CSV file');
    } finally {
      setIsUploading(false);
    }
  };

  // Send chat message
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isSending) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsSending(true);

    // Add user message to UI immediately
    const tempUserMsg: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const response = await axios.post(`${API_BASE_URL}/csv/chat/message`, {
        session_id: sessionId,
        message: userMessage,
      });

      const data = response.data;
      // Update with full conversation history from backend
      setMessages(data.conversation_history);
    } catch (err: any) {
      console.error('Send message error:', err);
      // Add error message
      const errorMsg: Message = {
        role: 'assistant',
        content: `⚠️ Error: ${err.response?.data?.detail || 'Failed to send message'}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsSending(false);
    }
  };

  // Start new conversation
  const handleNewConversation = () => {
    setSessionId(null);
    setCsvInfo(null);
    setMessages([]);
    setCsvUrl('');
    setCsvFile(null);
    setInputMessage('');
    setShowUpload(true);
    setUploadError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (sessionId) {
        handleSendMessage();
      } else if (mode === 'url') {
        handleUploadUrl();
      } else {
        handleUploadFile();
      }
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header with CSV Info */}
      {csvInfo && (
        <div className="bg-blue-50 border-b border-blue-200 px-4 py-3 flex justify-between items-center">
          <div className="flex-1">
            <h3 className="text-sm font-semibold text-blue-900">
              📊 {csvInfo.source_value}
            </h3>
            <p className="text-xs text-blue-700">
              {csvInfo.rows.toLocaleString()} rows × {csvInfo.columns} columns
              <span className="mx-2">•</span>
              {csvInfo.column_names.slice(0, 3).join(', ')}
              {csvInfo.column_names.length > 3 && '...'}
            </p>
          </div>
          <button
            onClick={handleNewConversation}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            New Conversation
          </button>
        </div>
      )}

      {/* Upload Section (Collapsible) */}
      {showUpload && (
        <div className="border-b border-gray-200 bg-gray-50">
          <div className="p-4 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                Upload CSV File
              </h3>
              {sessionId && (
                <button
                  onClick={() => setShowUpload(false)}
                  className="text-sm text-gray-600 hover:text-gray-800"
                >
                  Hide ▲
                </button>
              )}
            </div>

            {/* Mode Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setMode('url')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                  mode === 'url'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                disabled={isUploading}
              >
                CSV URL
              </button>
              <button
                onClick={() => setMode('file')}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors ${
                  mode === 'file'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                disabled={isUploading}
              >
                Upload File
              </button>
            </div>

            {/* Input */}
            {mode === 'url' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CSV File URL
                </label>
                <input
                  type="url"
                  value={csvUrl}
                  onChange={(e) => setCsvUrl(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="https://example.com/data.csv"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isUploading}
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload CSV File
                </label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  disabled={isUploading}
                />
                {csvFile && (
                  <p className="text-sm text-gray-600 mt-2">
                    Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(2)}{' '}
                    KB)
                  </p>
                )}
              </div>
            )}

            {/* Upload Button */}
            <button
              onClick={mode === 'url' ? handleUploadUrl : handleUploadFile}
              disabled={
                isUploading ||
                (mode === 'url' ? !csvUrl.trim() : !csvFile)
              }
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {isUploading ? 'Uploading...' : 'Start Analysis'}
            </button>

            {uploadError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                {uploadError}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Show Upload Button (when collapsed) */}
      {!showUpload && sessionId && (
        <div className="border-b border-gray-200 bg-gray-50 px-4 py-2">
          <button
            onClick={() => setShowUpload(true)}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            Show Upload Section ▼
          </button>
        </div>
      )}

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
        {messages.length === 0 && !sessionId && (
          <div className="text-center py-12 text-gray-500">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">CSV Data Chat</h3>
            <p className="text-sm">
              Upload a CSV file or provide a URL to start analyzing your data
              with AI
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-4 ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {/* Message Content */}
              <div className="whitespace-pre-wrap break-words">
                {msg.content}
              </div>

              {/* Plot Image */}
              {msg.plot_base64 && (
                <div className="mt-3">
                  <img
                    src={`data:image/png;base64,${msg.plot_base64}`}
                    alt="Visualization"
                    className="max-w-full rounded border border-gray-300"
                  />
                </div>
              )}

              {/* Timestamp */}
              <div
                className={`text-xs mt-2 ${
                  msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                }`}
              >
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {/* Loading Indicator */}
        {isSending && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {sessionId && (
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="flex gap-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your data..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isSending}
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || isSending}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Try: "Show statistics", "Plot histogram of [column]", "What are the
            top 10 values?", "Find missing values"
          </p>
        </div>
      )}
    </div>
  );
}