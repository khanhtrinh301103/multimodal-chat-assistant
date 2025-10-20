'use client';

import { useState } from 'react';
import { sendImageQuestion } from '@/lib/api';

export default function ImageUpload() {
  const [imageUrl, setImageUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<{ caption: string; answer: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!imageUrl.trim() || !question.trim() || isLoading) return;

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await sendImageQuestion(imageUrl, question);
      setResult(response);
    } catch (err: any) {
      console.error('Image analysis error:', err);
      setError(err.message || 'Failed to analyze image');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Image URL
        </label>
        <input
          type="url"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
          placeholder="https://example.com/image.jpg"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
      </div>

      {imageUrl && (
        <div className="border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-2">Preview:</p>
          <img
            src={imageUrl}
            alt="Preview"
            className="max-w-full max-h-64 object-contain mx-auto rounded"
            onError={() => setError('Failed to load image')}
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Question
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What's in this image?"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={3}
          disabled={isLoading}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!imageUrl.trim() || !question.trim() || isLoading}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isLoading ? 'Analyzing...' : 'Analyze Image'}
      </button>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-2">Caption:</h3>
          <p className="text-gray-700 mb-4">{result.caption}</p>
          <h3 className="font-semibold text-gray-900 mb-2">Answer:</h3>
          <p className="text-gray-700">{result.answer}</p>
        </div>
      )}
    </div>
  );
}