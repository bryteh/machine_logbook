import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save, AlertCircle, CheckCircle } from 'lucide-react';

interface SettingsData {
  maxFileSize: number; // MB
  maxFiles: number;
  imageQuality: number; // percentage
  videoHeight: number; // pixels
  enableVideoProcessing: boolean;
  enableImageCompression: boolean;
}

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData>({
    maxFileSize: 50,
    maxFiles: 10,
    imageQuality: 50,
    videoHeight: 720,
    enableVideoProcessing: false,
    enableImageCompression: true,
  });
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : 
               type === 'number' ? Number(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      // For now, just save to localStorage
      // In a real implementation, this would call an API endpoint
      localStorage.setItem('app_settings', JSON.stringify(settings));
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Load settings from localStorage on component mount
    const savedSettings = localStorage.getItem('app_settings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    }
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="bg-white shadow-sm rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <SettingsIcon className="h-8 w-8 text-blue-600 mr-3" />
            System Settings
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Configure file upload limits, media processing, and other system settings.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {message && (
            <div className={`rounded-md p-4 ${message.type === 'success' ? 'bg-green-50' : 'bg-red-50'}`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  {message.type === 'success' ? (
                    <CheckCircle className="h-5 w-5 text-green-400" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-400" />
                  )}
                </div>
                <div className="ml-3">
                  <p className={`text-sm font-medium ${message.type === 'success' ? 'text-green-800' : 'text-red-800'}`}>
                    {message.text}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* File Upload Settings */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">File Upload Settings</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Maximum File Size (MB)
                </label>
                <input
                  type="number"
                  name="maxFileSize"
                  min="1"
                  max="100"
                  value={settings.maxFileSize}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">Current: {settings.maxFileSize}MB per file</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Maximum Number of Files
                </label>
                <input
                  type="number"
                  name="maxFiles"
                  min="1"
                  max="20"
                  value={settings.maxFiles}
                  onChange={handleChange}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                />
                <p className="mt-1 text-xs text-gray-500">Current: {settings.maxFiles} files per upload</p>
              </div>
            </div>
          </div>

          {/* Image Processing Settings */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Image Processing</h3>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="enableImageCompression"
                  checked={settings.enableImageCompression}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Enable image compression
                </label>
              </div>

              {settings.enableImageCompression && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Image Quality (%)
                  </label>
                  <input
                    type="range"
                    name="imageQuality"
                    min="10"
                    max="100"
                    value={settings.imageQuality}
                    onChange={handleChange}
                    className="mt-1 w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>Lower quality (smaller file)</span>
                    <span>{settings.imageQuality}%</span>
                    <span>Higher quality (larger file)</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Video Processing Settings */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Video Processing</h3>
            
            <div className="space-y-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="enableVideoProcessing"
                  checked={settings.enableVideoProcessing}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900">
                  Enable video processing (requires FFmpeg)
                </label>
              </div>

              {settings.enableVideoProcessing && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Video Resolution (Height)
                  </label>
                  <select
                    name="videoHeight"
                    value={settings.videoHeight}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value={480}>480p (SD)</option>
                    <option value={720}>720p (HD)</option>
                    <option value={1080}>1080p (Full HD)</option>
                  </select>
                </div>
              )}

              <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> Video processing is currently disabled due to FFmpeg compatibility issues. 
                  Videos are uploaded in their original format.
                </p>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="h-4 w-4 mr-2" />
              {loading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings; 