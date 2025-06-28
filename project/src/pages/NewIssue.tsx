import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  X,
  Camera,
  AlertTriangle,
  Loader,
  Sparkles,
  FileImage
} from 'lucide-react';
import api from '../services/api';

interface Machine {
  machine_id: string;
  machine_number: string;
  model: string;
  status: string;
  department_id: string;
}

interface Department {
  department_id: string;
  name: string;
}

interface FormData {
  department_id: string;
  machine_id: string;
  category: string;
  priority: string;
  alarm_code: string;
  description: string;
  is_runnable: boolean;
  reported_by: string;
}

const NewIssue: React.FC = () => {
  const navigate = useNavigate();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [allMachines, setAllMachines] = useState<Machine[]>([]);
  const [filteredMachines, setFilteredMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(false);
  const [refiningDescription, setRefiningDescription] = useState(false);
  const [formData, setFormData] = useState<FormData>({
    department_id: '',
    machine_id: '',
    category: '',
    priority: 'medium',
    alarm_code: '',
    description: '',
    is_runnable: true,
    reported_by: '',
  });
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [alarmImage, setAlarmImage] = useState<File | null>(null);
  const [alarmImagePreview, setAlarmImagePreview] = useState<string>('');
  const [clickedCards, setClickedCards] = useState<Set<number>>(new Set());

  const categories = [
    'Alarm',
    'Mechanical',
    'Quality',
    'Process',
    'Other'
  ];

  // Suggestion cards for common machine issues
  const suggestionCards = [
    "Abnormal sound with spindle",
    "Abnormal sound with turret", 
    "Abnormal sound with belt",
    "Abnormal sound with chip conveyor",
    "Hydraulic motor high temperature",
    "Coolant motor high temperature",
    "Hydraulic fan motor not running",
    "Machine lamp off",
    "Ceiling LED lamp off",
    "Hydraulic oil serious leakage",
    "Bad coolant",
    "Machine servo alarm",
    "Jaw jammed",
    "No alarm, but machine cannot run",
    "Turret cannot rotate",
    "Alarm",
    "Machine(s) trip",
    "Monitor problem",
    "Air leaking"
  ];

  useEffect(() => {
    loadDepartments();
    loadMachines();
  }, []);

  // Filter machines when department changes
  useEffect(() => {
    if (formData.department_id) {
      // Use API to get filtered machines by department
      loadMachinesByDepartment(formData.department_id);
      // Reset machine selection when department changes
      setFormData(prev => ({ ...prev, machine_id: '' }));
    } else {
      setFilteredMachines([]);
    }
  }, [formData.department_id]);

  const loadDepartments = async () => {
    try {
      const response = await api.get('/departments');
      // Handle paginated response - extract results array
      const departmentData = response.data.results || response.data || [];
      setDepartments(Array.isArray(departmentData) ? departmentData : []);
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments([]);
    }
  };

  const loadMachines = async () => {
    try {
      const response = await api.get('/machines');
      // Handle paginated response - extract results array
      const machineData = response.data.results || response.data || [];
      setAllMachines(Array.isArray(machineData) ? machineData : []);
    } catch (error) {
      console.error('Error loading machines:', error);
      setAllMachines([]);
    }
  };

  const loadMachinesByDepartment = async (departmentId: string) => {
    try {
      const response = await api.get(`/machines/?department_id=${departmentId}`);
      // Handle paginated response - extract results array
      const machineData = response.data.results || response.data || [];
      const machines = (Array.isArray(machineData) ? machineData : [])
        .sort((a, b) => {
          // Extract numbers from machine_number (e.g., "S1" -> 1, "A10" -> 10)
          const getNumber = (machineNumber: string) => {
            const match = machineNumber.match(/\d+/);
            return match ? parseInt(match[0], 10) : 0;
          };
          return getNumber(a.machine_number) - getNumber(b.machine_number);
        }); // Numerical order (S1, S2, S3, A1, A2, A10, etc.)
      setFilteredMachines(machines);
    } catch (error) {
      console.error('Error loading machines for department:', error);
      setFilteredMachines([]);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleAlarmImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setAlarmImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setAlarmImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeAlarmImage = () => {
    setAlarmImage(null);
    setAlarmImagePreview('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    const totalFiles = files.length + selectedFiles.length;
    
    if (totalFiles > 5) {
      alert('Maximum 5 files allowed');
      return;
    }

    setFiles(prev => [...prev, ...selectedFiles]);
    
    selectedFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviews(prev => [...prev, e.target?.result as string]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleSuggestionClick = (suggestion: string, index: number) => {
    // Add the suggestion to the description
    const currentDescription = formData.description;
    const newDescription = currentDescription 
      ? `${currentDescription}${currentDescription.endsWith('.') || currentDescription.endsWith(',') || currentDescription.endsWith(';') ? ' ' : '. '}${suggestion}`
      : suggestion;
    
    setFormData(prev => ({
      ...prev,
      description: newDescription
    }));

    // Mark this card as clicked for visual feedback
    setClickedCards(prev => new Set([...prev, index]));

    // Remove the visual feedback after a short delay
    setTimeout(() => {
      setClickedCards(prev => {
        const newSet = new Set([...prev]);
        newSet.delete(index);
        return newSet;
      });
    }, 800);
  };

  const refineDescription = async () => {
    if (!formData.description.trim()) {
      alert('Please enter a description first');
      return;
    }

    setRefiningDescription(true);
    try {
      const response = await api.post('/ai/improve-description/', {
        description: formData.description,
        alarm_code: formData.alarm_code || null,
        category: formData.category || null
      });
      
      if (response.data.improved_description) {
        setFormData(prev => ({
          ...prev,
          description: response.data.improved_description
        }));
      }
    } catch (error) {
      console.error('Error refining description:', error);
      alert('Failed to refine description. Please try again.');
    } finally {
      setRefiningDescription(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation - including mandatory reporter name
    if (!formData.machine_id || !formData.category || !formData.description.trim() || !formData.reported_by.trim()) {
      alert('Please fill in all required fields including reporter name');
      return;
    }

    setLoading(true);
    
    try {
      // Prepare issue data
      const issueData = {
        machine_id_ref: formData.machine_id,
        category: formData.category,
        description: formData.description,
        is_runnable: formData.is_runnable,
        priority: formData.priority,
        reported_by: formData.reported_by.trim(),
        alarm_code: formData.alarm_code || null,
      };

      console.log('Submitting issue data:', issueData);

      // Create the issue first
      const response = await api.post('/issues/', issueData, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Issue created successfully:', response.data);
      const issueId = response.data.id;

      // Handle file uploads separately if there are any files
      if (alarmImage || files.length > 0) {
        const uploadPromises = [];

        // Upload alarm image
        if (alarmImage) {
          const formData = new FormData();
          formData.append('file', alarmImage);
          formData.append('file_type', 'image');
          formData.append('purpose', 'alarm_screen');
          uploadPromises.push(
            api.post(`/issues/${issueId}/add_attachment/`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })
          );
        }

        // Upload other media files
        files.forEach(file => {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('file_type', file.type.startsWith('image/') ? 'image' : 'video');
          formData.append('purpose', 'other');
          uploadPromises.push(
            api.post(`/issues/${issueId}/add_attachment/`, formData, {
              headers: { 'Content-Type': 'multipart/form-data' }
            })
          );
        });

        // Wait for all uploads to complete
        try {
          await Promise.all(uploadPromises);
          console.log('All files uploaded successfully');
        } catch (uploadError) {
          console.error('Error uploading files:', uploadError);
          // Still navigate to the issue even if file upload fails
        }
      }

      navigate(`/issues/${issueId}`);
    } catch (error: any) {
      console.error('Error creating issue:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to create issue: ${error.response?.data?.detail || error.message || 'Please try again.'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Log New Issue</h1>
        <p className="text-gray-600">Report a machine issue to track and resolve quickly</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Issue Details</h2>
          

          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="department_id" className="block text-sm font-medium text-gray-700 mb-2">
                Department *
              </label>
              <select
                id="department_id"
                name="department_id"
                value={formData.department_id}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a department</option>
                {Array.isArray(departments) && departments.map(department => (
                  <option key={department.department_id} value={department.department_id}>
                    {department.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="machine_id" className="block text-sm font-medium text-gray-700 mb-2">
                Machine *
              </label>
              <select
                id="machine_id"
                name="machine_id"
                value={formData.machine_id}
                onChange={handleInputChange}
                required
                disabled={!formData.department_id}
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
              >
                <option value="">
                  {formData.department_id ? 'Select a machine' : 'Select department first'}
                </option>
                {Array.isArray(filteredMachines) && filteredMachines.map(machine => (
                  <option key={machine.machine_id} value={machine.machine_id}>
                    {machine.machine_number} ({machine.model})
                  </option>
                ))}
              </select>
              {formData.department_id && filteredMachines.length === 0 && (
                <p className="text-sm text-gray-500 mt-1">No machines found for this department</p>
              )}
            </div>

            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Issue Category *
              </label>
              <select
                id="category"
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select a category</option>
                {categories.map(category => (
                  <option key={category} value={category.toLowerCase()}>
                    {category}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                Priority Level *
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="low">🟢 Low - Can wait</option>
                <option value="medium">🟡 Medium - Standard</option>
                <option value="high">🔴 High - Urgent</option>
              </select>
            </div>

            <div>
              <label htmlFor="reported_by" className="block text-sm font-medium text-gray-700 mb-2">
                Reporter Name *
              </label>
              <input
                type="text"
                id="reported_by"
                name="reported_by"
                value={formData.reported_by}
                onChange={handleInputChange}
                placeholder="Enter your name"
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-sm text-gray-500 mt-1">Required field for issue tracking</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Machine Status
              </label>
              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="is_runnable"
                    value="true"
                    checked={formData.is_runnable === true}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_runnable: true }))}
                    className="mr-2 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Still Runnable</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="is_runnable"
                    value="false"
                    checked={formData.is_runnable === false}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_runnable: false }))}
                    className="mr-2 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Not Runnable</span>
                </label>
              </div>
            </div>
          </div>

          {/* Alarm Code Section */}
          <div className="mt-6">
            <label htmlFor="alarm_code" className="block text-sm font-medium text-gray-700 mb-2">
              Alarm Code (Optional)
            </label>
            <div className="flex space-x-4">
              <input
                type="text"
                id="alarm_code"
                name="alarm_code"
                value={formData.alarm_code}
                onChange={handleInputChange}
                placeholder="e.g., 101, 204, A123, etc."
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            {/* Alarm Image Upload */}
            <div className="mt-3">
              <p className="text-sm text-gray-600 mb-2">Or upload alarm screen image for OCR reading:</p>
              {!alarmImagePreview ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <div className="text-center">
                    <FileImage className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <label htmlFor="alarm-image-upload" className="cursor-pointer">
                      <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded text-sm hover:bg-blue-200 transition-colors inline-flex items-center space-x-1">
                        <Camera className="h-3 w-3" />
                        <span>Upload Alarm Screen</span>
                      </span>
                      <input
                        id="alarm-image-upload"
                        type="file"
                        accept="image/*"
                        onChange={handleAlarmImageChange}
                        className="hidden"
                      />
                    </label>
                    <p className="mt-1 text-xs text-gray-500">PNG, JPG up to 5MB</p>
                  </div>
                </div>
              ) : (
                <div className="relative inline-block">
                  <img
                    src={alarmImagePreview}
                    alt="Alarm screen"
                    className="h-20 w-auto rounded border"
                  />
                  <button
                    type="button"
                    onClick={removeAlarmImage}
                    className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Description Section with AI Refine */}
          <div className="mt-6">
            <div className="flex items-center justify-between mb-2">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Problem Description *
              </label>
              <button
                type="button"
                onClick={refineDescription}
                disabled={refiningDescription || !formData.description.trim()}
                className="inline-flex items-center space-x-1 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-md hover:bg-purple-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Sparkles className="h-3 w-3" />
                <span>{refiningDescription ? 'Refining...' : 'Refine with AI'}</span>
              </button>
            </div>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              required
              rows={4}
              placeholder="Describe the issue in detail... (You can write in any language - AI will translate to English and improve your description)"
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            
            {/* Suggestion Cards */}
            <div className="mt-4">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-gray-700">Quick-fill suggestions</h4>
                <span className="text-xs text-gray-500">Click to add to description</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestionCards.map((suggestion, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleSuggestionClick(suggestion, index)}
                    className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-all duration-200 transform hover:scale-105 ${
                      clickedCards.has(index)
                        ? 'bg-green-100 border-green-300 text-green-800 shadow-sm'
                        : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-blue-50 hover:border-blue-300 hover:text-blue-800'
                    }`}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                💡 These cards help you describe common issues quickly. You can click multiple cards and edit the text afterward.
              </p>
            </div>
            
            <p className="text-xs text-gray-500 mt-1">
              💡 You can write in any language. Click "Refine with AI" to translate to English and improve clarity with technical details.
            </p>
          </div>
        </div>

        {/* Media Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Media Attachments</h2>
          <p className="text-sm text-gray-600 mb-4">Upload up to 5 photos or videos to help document the issue</p>
          
          <div className="space-y-4">
            {files.length < 5 && (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Camera className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors inline-flex items-center space-x-2">
                      <Upload className="h-4 w-4" />
                      <span>Choose Files</span>
                    </span>
                    <input
                      id="file-upload"
                      type="file"
                      multiple
                      accept="image/*,video/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                  <p className="mt-2 text-sm text-gray-600">PNG, JPG, GIF, MP4, MOV up to 10MB each</p>
                </div>
              </div>
            )}

            {previews.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {previews.map((preview, index) => (
                  <div key={index} className="relative group">
                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      {files[index].type.startsWith('image/') ? (
                        <img
                          src={preview}
                          alt={`Preview ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <video
                          src={preview}
                          className="w-full h-full object-cover"
                          controls={false}
                        />
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={() => navigate('/issues')}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading && <Loader className="h-4 w-4 animate-spin" />}
            <span>{loading ? 'Creating...' : 'Submit Issue'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default NewIssue;