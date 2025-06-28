import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { AlertTriangle, Save, X, Trash2, Upload, FileImage, Video } from 'lucide-react';
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

interface Attachment {
  id: string;
  file_name: string;
  file_type: string;
  file_url: string;
  purpose: string;
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

const EditIssue: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [filteredMachines, setFilteredMachines] = useState<Machine[]>([]);
  const [attachments, setAttachments] = useState<Attachment[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
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

  const categories = ['Alarm', 'Mechanical', 'Quality', 'Process', 'Electrical', 'Other'];

  useEffect(() => {
    loadDepartments();
    loadMachines();
  }, []);

  useEffect(() => {
    if (id && machines.length > 0) {
      loadIssue();
    }
  }, [id, machines]);

  useEffect(() => {
    if (formData.department_id) {
      const filtered = machines.filter(machine => machine.department_id === formData.department_id);
      setFilteredMachines(filtered);
    } else {
      setFilteredMachines([]);
    }
  }, [formData.department_id, machines]);

  const loadDepartments = async () => {
    try {
      const response = await api.get('/departments');
      setDepartments(Array.isArray(response.data.results) ? response.data.results : []);
    } catch (error) {
      console.error('Error loading departments:', error);
    }
  };

  const loadMachines = async () => {
    try {
      const response = await api.get('/machines');
      setMachines(Array.isArray(response.data.results) ? response.data.results : []);
    } catch (error) {
      console.error('Error loading machines:', error);
    }
  };

  const loadIssue = async () => {
    try {
      const response = await api.get(`/issues/${id}/`);
      const issue = response.data;
      
      // Find the department_id from the machine
      const machine = machines.find(m => m.machine_id === issue.machine_id_ref);
      const department_id = machine?.department_id || '';

      setFormData({
        department_id,
        machine_id: issue.machine_id_ref,
        category: issue.category,
        priority: issue.priority,
        alarm_code: issue.alarm_code || '',
        description: issue.description,
        is_runnable: issue.is_runnable,
        reported_by: issue.reported_by || '',
      });
    } catch (error) {
      console.error('Error loading issue:', error);
      alert('Failed to load issue data');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.machine_id || !formData.category || !formData.description.trim() || !formData.reported_by.trim()) {
      alert('Please fill in all required fields including reporter name');
      return;
    }

    setSaving(true);
    
    try {
      const updateData = {
        machine_id_ref: formData.machine_id,
        category: formData.category,
        priority: formData.priority,
        description: formData.description,
        is_runnable: formData.is_runnable,
        alarm_code: formData.alarm_code || null,
        reported_by: formData.reported_by,
      };

      console.log('Updating issue with data:', updateData);
      await api.patch(`/issues/${id}/`, updateData);

      // Handle new file uploads if there are any files
      if (files.length > 0) {
        const uploadPromises = files.map(file => {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('file_type', file.type.startsWith('image/') ? 'image' : 'video');
          formData.append('purpose', 'issue_update');
          return api.post(`/issues/${id}/add_attachment/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        });

        try {
          await Promise.all(uploadPromises);
          console.log('All new files uploaded successfully');
        } catch (uploadError) {
          console.error('Error uploading files:', uploadError);
          // Still navigate even if file upload fails
        }
      }

      navigate(`/issues/${id}`);
    } catch (error: any) {
      console.error('Error updating issue:', error);
      console.error('Error response:', error.response?.data);
      alert(`Failed to update issue: ${error.response?.data?.detail || error.message || 'Please try again.'}`);
    } finally {
      setSaving(false);
    }
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

  const removeAttachment = async (attachmentId: string) => {
    try {
      await api.delete(`/issues/${id}/attachments/${attachmentId}/`);
      setAttachments(prev => prev.filter(att => att.id !== attachmentId));
    } catch (error) {
      console.error('Error removing attachment:', error);
      alert('Failed to remove attachment. Please try again.');
    }
  };

  const loadAttachments = async () => {
    try {
      const response = await api.get(`/issues/${id}/attachments/`);
      setAttachments(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      console.error('Error loading attachments:', error);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await api.delete(`/issues/${id}/`);
      navigate('/issues');
    } catch (error) {
      console.error('Error deleting issue:', error);
      alert('Failed to delete issue. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-10 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Issue</h1>
        <p className="text-gray-600">Update issue details and information</p>
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
                {departments.map(department => (
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
                {filteredMachines.map(machine => (
                  <option key={machine.machine_id} value={machine.machine_id}>
                    {machine.machine_number} ({machine.model})
                  </option>
                ))}
              </select>
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
                    onChange={() => setFormData(prev => ({ ...prev, is_runnable: true }))}
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
                    onChange={() => setFormData(prev => ({ ...prev, is_runnable: false }))}
                    className="mr-2 text-blue-600"
                  />
                  <span className="text-sm text-gray-700">Not Runnable</span>
                </label>
              </div>
            </div>

            <div>
              <label htmlFor="alarm_code" className="block text-sm font-medium text-gray-700 mb-2">
                Alarm Code (Optional)
              </label>
              <input
                type="text"
                id="alarm_code"
                name="alarm_code"
                value={formData.alarm_code}
                onChange={handleInputChange}
                placeholder="e.g., 101, 204, A123, etc."
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
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
                placeholder="Enter reporter name"
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div className="mt-6">
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Issue Description *
            </label>
            <textarea
              id="description"
              name="description"
              rows={4}
              value={formData.description}
              onChange={handleInputChange}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe the issue in detail..."
            />
          </div>
        </div>

        {/* Media Management Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Media Attachments</h2>
          
          {/* Existing Attachments */}
          {attachments.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Current Attachments</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {attachments.map((attachment) => (
                  <div key={attachment.id} className="relative group">
                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      {attachment.file_type === 'image' ? (
                        <img 
                          src={attachment.file_url} 
                          alt={attachment.file_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Video className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeAttachment(attachment.id)}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                      <X className="h-4 w-4" />
                    </button>
                    <p className="text-xs text-gray-500 mt-1 truncate">{attachment.file_name}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* New File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Add New Media (Images/Videos)
            </label>
            <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div className="space-y-1 text-center">
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <div className="flex text-sm text-gray-600">
                  <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                    <span>Upload files</span>
                    <input
                      id="file-upload"
                      name="file-upload"
                      type="file"
                      className="sr-only"
                      multiple
                      accept="image/*,video/*"
                      onChange={handleFileChange}
                    />
                  </label>
                  <p className="pl-1">or drag and drop</p>
                </div>
                <p className="text-xs text-gray-500">
                  Images and videos up to 10MB each (max 5 files)
                </p>
              </div>
            </div>

            {/* New File Previews */}
            {files.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">New Files to Upload</h4>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {files.map((file, index) => (
                    <div key={index} className="relative group">
                      <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                        {file.type.startsWith('image/') ? (
                          <img 
                            src={previews[index]} 
                            alt={file.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Video className="h-8 w-8 text-gray-400" />
                          </div>
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={() => removeFile(index)}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <X className="h-4 w-4" />
                      </button>
                      <p className="text-xs text-gray-500 mt-1 truncate">{file.name}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Submit Buttons */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate(`/issues/${id}`)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <X className="h-4 w-4 mr-2" />
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="h-4 w-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </form>

      <div className="mt-6">
        <button
          type="button"
          onClick={() => setShowDeleteConfirm(true)}
          className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        >
          <Trash2 className="h-4 w-4 mr-2" />
          Delete Issue
        </button>
      </div>

      {showDeleteConfirm && (
        <div className="mt-6 p-6 bg-white rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Confirm Deletion</h2>
          <p className="text-gray-700 mb-4">Are you sure you want to delete this issue? This action cannot be undone.</p>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setShowDeleteConfirm(false)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default EditIssue; 