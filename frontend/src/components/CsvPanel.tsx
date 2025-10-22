'use client';

import { useState } from 'react';
import { analyzeCsvFromUrl, analyzeCsvFromFile } from '@/lib/api';

type InputMode = 'url' | 'file';

export default function CsvPanel() {
  const [mode, setMode] = useState<InputMode>('url');
  const [csvUrl, setCsvUrl] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<{ summary: string; plot_base64?: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!prompt.trim() || isLoading) return;
    if (mode === 'url' && !csvUrl.trim()) return;
    if (mode === 'file' && !csvFile) return;

    setIsLoading(true);
    setError('');
    setResult(null);

    try {
      if (mode === 'url') {
        const response = await analyzeCsvFromUrl(csvUrl, prompt);
        setResult(response);
      } else {
        const response = await analyzeCsvFromFile(csvFile!, prompt);
        setResult(response);
      }
    } catch (err: any) {
      console.error('CSV analysis error:', err);
      setError(err.message || 'Failed to analyze CSV');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Mode Toggle */}
      <div className="flex gap-4">
        <button
          onClick={() => setMode('url')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            mode === 'url'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          CSV URL
        </button>
        <button
          onClick={() => setMode('file')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            mode === 'file'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
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
            placeholder="https://example.com/data.csv"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
        </div>
      ) : (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload CSV File
          </label>
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          {csvFile && (
            <p className="text-sm text-gray-600 mt-2">
              Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(2)} KB)
            </p>
          )}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Analysis Prompt
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Summarize the data, show distribution of column X..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          rows={4}
          disabled={isLoading}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={isLoading || !prompt.trim() || (mode === 'url' ? !csvUrl.trim() : !csvFile)}
        className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
      >
        {isLoading ? 'Analyzing...' : 'Analyze CSV'}
      </button>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <h3 className="font-semibold text-gray-900 mb-2">Analysis Summary:</h3>
            <p className="text-gray-700 whitespace-pre-wrap">{result.summary}</p>
          </div>

          {result.plot_base64 && (
            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">Visualization:</h3>
              <img
                src={`data:image/png;base64,${result.plot_base64}`}
                alt="Data visualization"
                className="max-w-full mx-auto rounded"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}