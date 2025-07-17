import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Upload, X, Sparkles, HelpCircle } from 'lucide-react';
import api from '../services/api';

interface Department {
  department_id: string;
  name: string;
}

interface Machine {
  machine_id: string;
  machine_number: string;
  model: string;
  department_id: string;
}

interface FormData {
  machine_id_ref: string;
  category: string;
  priority: string;
  alarm_code: string;
  description: string;
  is_runnable: boolean;
  reported_by: string;
}

const AddIssue: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    machine_id_ref: '',
    category: '',
    priority: 'medium',
    alarm_code: '',
    description: '',
    is_runnable: true,
    reported_by: ''
  });
  
  const [departments, setDepartments] = useState<Department[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [filteredMachines, setFilteredMachines] = useState<Machine[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [isImprovingDescription, setIsImprovingDescription] = useState(false);
  const [showGuide, setShowGuide] = useState(false);
  const [clickedCards, setClickedCards] = useState<Set<number>>(new Set());

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

  const problemGuide = `Problem Description Guide:

1. WHAT HAPPENED? (Brief description)
   - Start with a clear, concise summary
   - Example: "CNC machine stopped during cutting operation"

2. WHEN DID IT OCCUR? (Date/time specifics)
   - Exact time and date if known
   - Was it during startup, operation, or shutdown?
   - Example: "At 2:30 PM during second shift on 12/15/2024"

3. MACHINE BEHAVIOR OBSERVED
   - What exactly did the machine do or not do?
   - Any unusual sounds, movements, or displays?
   - Example: "Spindle stopped rotating, coolant pump continued running"

4. ERROR CODES/ALARMS (if any)
   - Record the exact alarm code or message
   - Take a photo of the display if possible
   - Example: "Alarm AL-1234: Spindle Overload"

5. IMPACT ON PRODUCTION
   - Is the machine completely stopped?
   - Can production continue with workarounds?
   - How many parts were affected?
   - Example: "Production stopped, 50 parts need rework"

6. SAFETY CONCERNS (if any)
   - Any immediate safety hazards?
   - Equipment damage visible?
   - Example: "No safety concerns, machine powered down safely"

Remember: The more detailed and specific your description, the faster technicians can diagnose and fix the problem!`;

  useEffect(() => {
    fetchDepartments();
    fetchMachines();
  }, []);

  useEffect(() => {
    if (selectedDepartment) {
      const filtered = machines.filter(machine => machine.department_id === selectedDepartment);
      setFilteredMachines(filtered);
      setFormData(prev => ({ ...prev, machine_id_ref: '' }));
    } else {
      setFilteredMachines(machines);
    }
  }, [selectedDepartment, machines]);

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/departments/');
      setDepartments(response.data);
    } catch (error) {
      console.error('Failed to fetch departments:', error);
    }
  };

  const fetchMachines = async () => {
    try {
      const response = await api.get('/machines/');
      setMachines(response.data);
      setFilteredMachines(response.data);
    } catch (error) {
      console.error('Failed to fetch machines:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments(prev => [...prev, ...newFiles]);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
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

  const improveDescription = async () => {
    if (!formData.description.trim()) {
      setError('Please enter a description first');
      return;
    }

    setIsImprovingDescription(true);
    setError('');

    try {
      const response = await api.post('/improve_description/', {
        description: formData.description,
        alarm_code: formData.alarm_code
      });
      
      setFormData(prev => ({
        ...prev,
        description: response.data.improved_description
      }));
    } catch (error: any) {
      console.error('Failed to improve description:', error);
      setError('Failed to improve description. Please try again.');
    } finally {
      setIsImprovingDescription(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.machine_id_ref || !formData.category || !formData.description.trim() || !formData.reported_by.trim()) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const response = await api.post('/issues/', formData);
      const issueId = response.data.id;

      // Upload attachments if any
      if (attachments.length > 0) {
        for (const file of attachments) {
          const attachmentFormData = new FormData();
          attachmentFormData.append('file', file);
          attachmentFormData.append('file_type', file.type.startsWith('image/') ? 'image' : 'video');
          attachmentFormData.append('purpose', 'alarm_screen');

          await api.post(`/issues/${issueId}/add_attachment/`, attachmentFormData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
        }
      }

      navigate(`/issues/${issueId}`);
    } catch (error: any) {
      console.error('Failed to create issue:', error);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        setError(errorMessages.join(', '));
      } else {
        setError('Failed to create issue. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => navigate('/issues')}
                  className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back to Issues
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Report New Issue</h1>
              </div>
              <button
                onClick={() => setShowGuide(!showGuide)}
                className="px-4 py-2 text-sm bg-blue-50 text-blue-600 border border-blue-200 rounded-md hover:bg-blue-100 flex items-center"
              >
                <HelpCircle className="h-4 w-4 mr-1" />
                {showGuide ? 'Hide Guide' : 'Show Guide'}
              </button>
            </div>
          </div>

          {showGuide && (
            <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
              <h3 className="text-sm font-medium text-blue-900 mb-2">Problem Description Guide</h3>
              <pre className="text-sm text-blue-800 whitespace-pre-line">{problemGuide}</pre>
            </div>
          )}

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Machine Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-2">
                  Department
                </label>
                <select
                  id="department"
                  value={selectedDepartment}
                  onChange={(e) => setSelectedDepartment(e.target.value)}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Departments</option>
                  {departments.map((dept) => (
                    <option key={dept.department_id} value={dept.department_id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="machine_id_ref" className="block text-sm font-medium text-gray-700 mb-2">
                  Machine *
                </label>
                <select
                  id="machine_id_ref"
                  name="machine_id_ref"
                  value={formData.machine_id_ref}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select a machine</option>
                  {filteredMachines.map((machine) => (
                    <option key={machine.machine_id} value={machine.machine_id}>
                      {machine.machine_number} - {machine.model}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Issue Details */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                  Category *
                </label>
                <select
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  <option value="">Select category</option>
                  <option value="alarm">Alarm</option>
                  <option value="mechanical">Mechanical</option>
                  <option value="electrical">Electrical</option>
                  <option value="quality">Quality</option>
                  <option value="process">Process</option>
                  <option value="material_issue">Material Issue</option>
                  <option value="machine_setup">Machine Setup</option>
                  <option value="no_planning">No Planning</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                  Priority
                </label>
                <select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>

              <div>
                <label htmlFor="alarm_code" className="block text-sm font-medium text-gray-700 mb-2">
                  Alarm Code
                </label>
                <input
                  type="text"
                  id="alarm_code"
                  name="alarm_code"
                  value={formData.alarm_code}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., AL-1234"
                />
              </div>
            </div>

            {/* Problem Description */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Problem Description *
                </label>
                <button
                  type="button"
                  onClick={improveDescription}
                  disabled={isImprovingDescription || !formData.description.trim()}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  {isImprovingDescription ? 'Improving...' : 'Improve with AI'}
                </button>
              </div>
              <textarea
                id="description"
                name="description"
                rows={6}
                value={formData.description}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="You can write in any language - AI will translate to English. Follow the guide above for best results..."
                required
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
            </div>

            {/* Additional Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="reported_by" className="block text-sm font-medium text-gray-700 mb-2">
                  Reported By *
                </label>
                <input
                  type="text"
                  id="reported_by"
                  name="reported_by"
                  value={formData.reported_by}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Your name"
                  required
                />
              </div>

              <div className="flex items-center">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    name="is_runnable"
                    checked={formData.is_runnable}
                    onChange={handleCheckboxChange}
                    className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-900">Machine is still runnable</span>
                </label>
              </div>
            </div>

            {/* File Attachments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Attachments (Optional)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                <div className="text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <div className="mt-4">
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <span className="mt-2 block text-sm font-medium text-gray-900">
                        Upload machine photos or videos
                      </span>
                      <input
                        id="file-upload"
                        name="file-upload"
                        type="file"
                        multiple
                        accept="image/*,video/*,.heic,.HEIC"
                        onChange={handleFileChange}
                        className="sr-only"
                      />
                    </label>
                    <p className="mt-1 text-xs text-gray-500">
                      PNG, JPG, HEIC, MP4 up to 50MB each (max 10 files). HEIC files will be converted to JPEG.
                    </p>
                  </div>
                </div>
              </div>

              {attachments.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Selected Files:</h4>
                  <div className="space-y-2">
                    {attachments.map((file, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 p-2 rounded">
                        <span className="text-sm text-gray-700">{file.name}</span>
                        <button
                          type="button"
                          onClick={() => removeAttachment(index)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
              <button
                type="button"
                onClick={() => navigate('/issues')}
                className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {isSubmitting ? 'Creating Issue...' : 'Create Issue'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AddIssue;