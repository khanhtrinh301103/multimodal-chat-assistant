// frontend/src/components/ImageUpload.tsx
'use client';

import { useState } from 'react';

export default function ImageUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState<{ caption: string; answer: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    
    if (file) {
      // Validate file type (PNG/JPG as per requirement)
      if (!file.type.match(/image\/(png|jpeg|jpg)/)) {
        setError('Please select a PNG or JPG image');
        return;
      }
      
      setSelectedFile(file);
      setError('');
      
      // Create preview URL
      const preview = URL.createObjectURL(file);
      setPreviewUrl(preview);
    }
  };

  const handleSubmit = async () => {
    if (!selectedFile || !question.trim() || isLoading) return;

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      // Create FormData with file and question
      const formData = new FormData();
      formData.append('image', selectedFile);
      formData.append('question', question);

      const response = await fetch('http://localhost:8000/image/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      console.error('Image analysis error:', err);
      setError(err.message || 'Failed to analyze image');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* File Upload Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Image (PNG/JPG)
        </label>
        <input
          type="file"
          accept="image/png,image/jpeg,image/jpg"
          onChange={handleFileChange}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        {selectedFile && (
          <p className="text-sm text-green-600 mt-2">
            ✓ Selected: {selectedFile.name}
          </p>
        )}
      </div>

      {/* Image Preview */}
      {previewUrl && (
        <div className="border border-gray-200 rounded-lg p-4">
          <p className="text-sm text-gray-600 mb-2">Preview:</p>
          <img
            src={previewUrl}
            alt="Preview"
            className="max-w-full max-h-64 object-contain mx-auto rounded"
          />
        </div>
      )}

      {/* Question Input */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Your Question
        </label>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="What's in this photo?"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={3}
          disabled={isLoading}
        />
      </div>

      {/* Analyze Button */}
      <button
        onClick={handleSubmit}
        disabled={!selectedFile || !question.trim() || isLoading}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isLoading ? 'Analyzing...' : 'Analyze Image'}
      </button>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Results Display */}
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