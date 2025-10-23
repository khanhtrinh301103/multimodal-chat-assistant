'use client';

import { useState, useRef, useEffect } from 'react';
import { apiClient } from '@/lib/api'; // Sử dụng interceptor tự động gắn JWT

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ImageInfo {
  filename: string;
  width: number;
  height: number;
  format: string;
  size_kb: number;
}

export default function ImageUpload() {
  const [sessionId, setSessionId] = useState<string>('');
  const [imagePreview, setImagePreview] = useState<string>('');
  const [imageInfo, setImageInfo] = useState<ImageInfo | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // =====================
  // Handle Image Upload
  // =====================
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.match(/image\/(png|jpeg|jpg)/)) {
      setError('Please select a PNG or JPG image');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      // Preview image before upload
      const preview = URL.createObjectURL(file);
      setImagePreview(preview);

      // Upload via Axios (auto JWT)
      const formData = new FormData();
      formData.append('image', file);

      const { data } = await apiClient.post('/image/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setSessionId(data.session_id);
      setImageInfo(data.image_info);
      setMessages([
        {
          role: 'assistant',
          content: `I can see your image "${data.image_info.filename}". What would you like to know about it?`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.response?.data?.detail || 'Failed to upload image');
      setImagePreview('');
    } finally {
      setIsUploading(false);
    }
  };

  // =====================
  // Handle Send Message
  // =====================
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setError('');

    const newUserMessage: Message = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMessage]);

    try {
      const { data } = await apiClient.post('/image/chat', {
        session_id: sessionId,
        message: userMessage,
      });

      setMessages(data.conversation_history);
    } catch (err: any) {
      console.error('Chat error:', err);
      setError(err.response?.data?.detail || 'Failed to send message');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: '⚠️ Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewImage = () => {
    setSessionId('');
    setImagePreview('');
    setImageInfo(null);
    setMessages([]);
    setError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="flex flex-col h-[700px] max-w-4xl mx-auto border border-gray-200 rounded-lg shadow-lg bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-t-lg">
        <h2 className="text-2xl font-bold">Image Chat 🖼️</h2>
        <p className="text-sm text-blue-100 mt-1">
          Upload an image and ask questions about it
        </p>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        {!sessionId ? (
          // Upload Screen
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center space-y-6">
              <div className="w-32 h-32 mx-auto bg-blue-50 rounded-full flex items-center justify-center">
                <svg
                  className="w-16 h-16 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Upload an Image to Start
                </h3>
                <p className="text-gray-600">
                  PNG or JPG format, up to 5MB
                </p>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={handleImageUpload}
                className="hidden"
                id="image-upload"
              />

              <label
                htmlFor="image-upload"
                className="inline-block px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors font-medium"
              >
                {isUploading ? 'Uploading...' : 'Choose Image'}
              </label>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                  {error}
                </div>
              )}
            </div>
          </div>
        ) : (
          <>
            {/* Image Preview */}
            <div className="bg-gray-50 border-b border-gray-200 p-4 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {imagePreview && (
                  <img
                    src={imagePreview}
                    alt="Uploaded"
                    className="w-16 h-16 object-cover rounded-lg border border-gray-300"
                  />
                )}
                {imageInfo && (
                  <div className="text-sm">
                    <p className="font-medium text-gray-800">{imageInfo.filename}</p>
                    <p className="text-gray-600">
                      {imageInfo.width} × {imageInfo.height} • {imageInfo.format} •{' '}
                      {imageInfo.size_kb.toFixed(1)} KB
                    </p>
                  </div>
                )}
              </div>

              <button
                onClick={handleNewImage}
                className="px-4 py-2 text-sm bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                New Image
              </button>
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-3 ${
                      msg.role === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                    <p
                      className={`text-xs mt-1 ${
                        msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}
                    >
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 rounded-lg px-4 py-3">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 p-4">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Ask something about this image..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading}
                className="mt-2 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
