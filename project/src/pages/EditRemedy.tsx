import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Upload,
  X,
  Camera,
  Loader,
  Sparkles,
  DollarSign,
  Package,
  User,
  Phone,
  AlertCircle,
  Save,
  FileImage,
  Video,
  Trash2
} from 'lucide-react';
import api, { publicAPI } from '../services/api';
import MediaDisplay from '../components/MediaDisplay';

interface Issue {
  id: string;
  machine_name: string;
  department_name: string;
  category: string;
  auto_title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  is_runnable: boolean;
}

interface Remedy {
  id: string;
  description: string;
  technician_name: string;
  is_external: boolean;
  phone_number: string;
  parts_purchased: string;
  labor_cost: number | null;
  parts_cost: number | null;
  is_machine_runnable: boolean;
  created_at: string;
  attachments: any[];
}

interface RemedyFormData {
  description: string;
  technician_name: string;
  is_external: boolean;
  phone_number: string;
  parts_purchased: string;
  labor_cost: string;
  parts_cost: string;
  is_machine_runnable: boolean;
}

const EditRemedy: React.FC = () => {
  const { id, remedyId } = useParams<{ id: string; remedyId: string }>();
  const navigate = useNavigate();
  const [issue, setIssue] = useState<Issue | null>(null);
  const [remedy, setRemedy] = useState<Remedy | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [formData, setFormData] = useState<RemedyFormData>({
    description: '',
    technician_name: '',
    is_external: false,
    phone_number: '',
    parts_purchased: '',
    labor_cost: '',
    parts_cost: '',
    is_machine_runnable: false,
  });
  const [existingAttachments, setExistingAttachments] = useState<any[]>([]);
  const [deletingAttachment, setDeletingAttachment] = useState<string | null>(null);
  const [showGuide, setShowGuide] = useState(false);
  const [error, setError] = useState('');
  const [isImprovingDescription, setIsImprovingDescription] = useState(false);

  const remedyGuide = `Remedy Description Guide:
1. Root cause identified
2. Actions taken
3. Parts replaced/purchased (list with quantities)
4. Tools/equipment used
5. Time taken to complete
6. Testing performed
7. Preventive measures recommended

Parts/Items Guide:
- List each part with part number and quantity
- Include supplier information if relevant
- Note any special tools or equipment used
- Record labor hours for accurate costing`;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [issueResponse, remediesResponse] = await Promise.all([
          publicAPI.getIssue(id!),
          publicAPI.getRemedies(id!)
        ]);
        
        // Find the specific remedy from the list
        const remedies = remediesResponse.data.results || remediesResponse.data;
        const specificRemedy = remedies.find((r: any) => r.id === remedyId);
        
        setIssue(issueResponse.data);
        
        if (specificRemedy) {
          setRemedy(specificRemedy);
          
          // Set existing attachments
          setExistingAttachments(specificRemedy.attachments || []);
          
          // Populate form with existing remedy data
          // Use current issue machine status as default for machine runnable
          setFormData({
            description: specificRemedy.description || '',
            technician_name: specificRemedy.technician_name || '',
            is_external: specificRemedy.is_external ?? false,
            phone_number: specificRemedy.phone_number || '',
            parts_purchased: specificRemedy.parts_purchased || '',
            labor_cost: specificRemedy.labor_cost ? specificRemedy.labor_cost.toString() : '',
            parts_cost: specificRemedy.parts_cost ? specificRemedy.parts_cost.toString() : '',
            is_machine_runnable: issueResponse.data.is_runnable ?? false,
          });
        } else {
          setError('Remedy not found');
        }
      } catch (error) {
        console.error('Failed to fetch data:', error);
        setError('Failed to load remedy data');
      } finally {
        setLoading(false);
      }
    };

    if (id && remedyId) {
      fetchData();
    }
  }, [id, remedyId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
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

  const improveDescription = async () => {
    if (!formData.description.trim()) {
      setError('Please enter a description first');
      return;
    }

    setIsImprovingDescription(true);
    setError('');

    try {
      const response = await api.post('/improve_remedy_description/', {
        description: formData.description
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

  const calculateTotalCost = () => {
    const labor = parseFloat(formData.labor_cost) || 0;
    const parts = parseFloat(formData.parts_cost) || 0;
    return labor + parts;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || []);
    
    // Validate file types and sizes
    const validFiles = selectedFiles.filter(file => {
      const isValidType = file.type.startsWith('image/') || file.type.startsWith('video/');
      const isValidSize = file.size <= 50 * 1024 * 1024; // 50MB limit
      return isValidType && isValidSize;
    });

    if (validFiles.length !== selectedFiles.length) {
      setError('Some files were rejected. Only images and videos under 50MB are allowed.');
    }

    setFiles(prev => [...prev, ...validFiles]);
    
    // Create previews
    validFiles.forEach(file => {
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

  const deleteAttachment = async (attachmentId: string) => {
    if (!confirm('Are you sure you want to delete this attachment?')) {
      return;
    }

    setDeletingAttachment(attachmentId);
    setError('');

    try {
      await api.delete(`/issues/${id}/remedies/${remedyId}/attachments/${attachmentId}/`);
      
      // Remove from local state
      setExistingAttachments(prev => prev.filter(att => att.id !== attachmentId));
    } catch (error: any) {
      console.error('Failed to delete attachment:', error);
      setError('Failed to delete attachment. Please try again.');
    } finally {
      setDeletingAttachment(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.description.trim() || !formData.technician_name.trim()) {
      setError('Description and technician name are required.');
      return;
    }

    if (formData.is_external && !formData.phone_number.trim()) {
      setError('Phone number is required for external technicians.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const submitData = {
        description: formData.description.trim(),
        technician_name: formData.technician_name.trim(),
        is_external: formData.is_external,
        phone_number: formData.phone_number.trim(),
        parts_purchased: formData.parts_purchased.trim(),
        labor_cost: formData.labor_cost ? parseFloat(formData.labor_cost) : null,
        parts_cost: formData.parts_cost ? parseFloat(formData.parts_cost) : null,
        is_machine_runnable: formData.is_machine_runnable
      };

      // Update remedy using public API - backend will handle issue status automatically
      const updateResponse = await publicAPI.updateRemedy(id!, remedyId!, submitData);
      console.log('Remedy updated successfully:', updateResponse.data);

      // Upload new files if any
      if (files.length > 0) {
        const uploadPromises = files.map(async (file) => {
        const uploadData = new FormData();
          uploadData.append('file', file);
        uploadData.append('purpose', 'other');

          try {
            const response = await publicAPI.uploadRemedyAttachment(id!, remedyId!, uploadData);
            console.log(`Uploaded ${file.name}:`, response.data);
          } catch (error: any) {
            console.error(`Failed to upload ${file.name}:`, error);
            throw new Error(`Failed to upload ${file.name}: ${error.response?.data?.error || error.message}`);
          }
        });

        try {
          await Promise.all(uploadPromises);
          console.log('All files uploaded successfully');
          // Clear uploaded files
          setFiles([]);
          setPreviews([]);
        } catch (uploadError: any) {
          throw uploadError;
        }
      }

      navigate(`/issues/${id}`);
    } catch (error: any) {
      console.error('Failed to update remedy:', error);
      let errorMessage = 'Failed to update remedy. Please try again.';
      
      if (error.response?.data) {
        if (typeof error.response.data === 'string') {
          errorMessage = error.response.data;
        } else if (error.response.data.detail) {
          errorMessage = error.response.data.detail;
        } else if (error.response.data.error) {
          errorMessage = error.response.data.error;
        } else {
          // Handle field-specific errors
          const fieldErrors = Object.entries(error.response.data).map(([field, errors]) => {
            if (Array.isArray(errors)) {
              return `${field}: ${errors.join(', ')}`;
            }
            return `${field}: ${errors}`;
          });
          if (fieldErrors.length > 0) {
            errorMessage = fieldErrors.join('; ');
          }
        }
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this remedy? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    setError('');

    try {
      await api.delete(`/issues/${id}/remedies/${remedyId}/`);
      navigate(`/issues/${id}`);
    } catch (error: any) {
      console.error('Failed to delete remedy:', error);
      setError(error.response?.data?.detail || 'Failed to delete remedy. Please try again.');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!issue || !remedy) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Remedy Not Found</h2>
          <p className="text-gray-600 mb-4">The remedy you're looking for doesn't exist.</p>
          <button
            onClick={() => navigate(`/issues/${id}`)}
            className="text-blue-600 hover:text-blue-800"
          >
            Back to Issue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/issues/${id}`)}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-5 w-5 mr-2" />
            Back to Issue
          </button>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Edit Remedy</h1>
            <div className="text-sm text-gray-600">
              <p><span className="font-medium">Issue:</span> {issue.auto_title}</p>
              <p><span className="font-medium">Machine:</span> {issue.machine_name}</p>
              <p><span className="font-medium">Department:</span> {issue.department_name}</p>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Remedy Description */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">Remedy Description</h2>
              <div className="flex space-x-2">
                <button
                  type="button"
                  onClick={() => setShowGuide(!showGuide)}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  {showGuide ? 'Hide Guide' : 'Show Guide'}
                </button>
                <button
                  type="button"
                  onClick={improveDescription}
                  disabled={isImprovingDescription || !formData.description.trim()}
                  className="inline-flex items-center px-3 py-1 text-sm bg-purple-100 hover:bg-purple-200 text-purple-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isImprovingDescription ? (
                    <Loader className="h-3 w-3 mr-1 animate-spin" />
                  ) : (
                    <Sparkles className="h-3 w-3 mr-1" />
                  )}
                  AI Improve
                </button>
              </div>
            </div>
            
            {showGuide && (
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
                <pre className="text-sm text-blue-800 whitespace-pre-wrap">{remedyGuide}</pre>
              </div>
            )}
            
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              placeholder="Describe the remedy applied, including root cause, actions taken, parts replaced, and testing performed..."
              rows={6}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Technician Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Technician Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Technician Name *
                </label>
                <input
                  type="text"
                  name="technician_name"
                  value={formData.technician_name}
                  onChange={handleInputChange}
                  placeholder="Enter technician name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Technician Type
                </label>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="is_external"
                      checked={!formData.is_external}
                      onChange={() => {
                        console.log('Setting internal technician');
                        setFormData(prev => ({ 
                          ...prev, 
                          is_external: false, 
                          phone_number: '' 
                        }));
                      }}
                      className="mr-2"
                    />
                    Internal
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="is_external"
                      checked={formData.is_external}
                      onChange={() => {
                        console.log('Setting external technician');
                        setFormData(prev => ({ 
                          ...prev, 
                          is_external: true 
                        }));
                      }}
                      className="mr-2"
                    />
                    External
                  </label>
                </div>
              </div>
            </div>
            
            {formData.is_external && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Phone className="h-4 w-4 inline mr-1" />
                  Phone Number *
                </label>
                <input
                  type="tel"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleInputChange}
                  placeholder="Enter phone number"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
            )}
          </div>

          {/* Parts and Cost Information */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Package className="h-5 w-5 mr-2" />
              Parts & Cost Information
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Parts/Items Purchased
                </label>
                <textarea
                  name="parts_purchased"
                  value={formData.parts_purchased}
                  onChange={handleInputChange}
                  placeholder="List parts purchased with quantities, part numbers, and suppliers..."
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DollarSign className="h-4 w-4 inline mr-1" />
                    Labor Cost
                  </label>
                  <input
                    type="number"
                    name="labor_cost"
                    value={formData.labor_cost}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <DollarSign className="h-4 w-4 inline mr-1" />
                    Parts Cost
                  </label>
                  <input
                    type="number"
                    name="parts_cost"
                    value={formData.parts_cost}
                    onChange={handleInputChange}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Total Cost
                  </label>
                  <div className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md text-gray-900 font-medium">
                    RM {calculateTotalCost().toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Machine Status */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Machine Status After Remedy</h2>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                name="is_machine_runnable"
                checked={formData.is_machine_runnable}
                onChange={handleCheckboxChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Machine is now runnable and operational
              </label>
            </div>
          </div>

          {/* Existing Attachments */}
          {existingAttachments.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Current Attachments</h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {existingAttachments.map((attachment) => (
                  <div key={attachment.id} className="relative group">
                    <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                      {attachment.file_type === 'image' ? (
                        <img
                          src={attachment.file_url}
                          alt="Attachment"
                          className="w-full h-full object-cover"
                        />
                      ) : attachment.file_type === 'video' ? (
                        <video
                          src={attachment.file_url}
                          className="w-full h-full object-cover"
                          controls
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <FileImage className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => deleteAttachment(attachment.id)}
                      disabled={deletingAttachment === attachment.id}
                      className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 opacity-0 group-hover:opacity-100 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {deletingAttachment === attachment.id ? (
                        <Loader className="h-3 w-3 animate-spin" />
                      ) : (
                        <X className="h-3 w-3" />
                      )}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* File Upload */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Camera className="h-5 w-5 mr-2" />
              Add New Attachments
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Images/Videos
                </label>
                <div className="flex items-center justify-center w-full">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-8 h-8 mb-4 text-gray-500" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-xs text-gray-500">Images and videos (MAX. 50MB each)</p>
                    </div>
                    <input
                      type="file"
                      multiple
                      accept="image/*,video/*"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
              </div>
              
              {/* File Previews */}
              {files.length > 0 && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {files.map((file, index) => (
                    <div key={index} className="relative">
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
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                      <p className="text-xs text-gray-600 mt-1 truncate">{file.name}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-between">
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="inline-flex items-center px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deleting ? (
                <Loader className="h-5 w-5 mr-2 animate-spin" />
              ) : (
                <Trash2 className="h-5 w-5 mr-2" />
              )}
              Delete Remedy
            </button>
            
            <button
              type="submit"
              disabled={submitting}
              className="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <Loader className="h-5 w-5 mr-2 animate-spin" />
              ) : (
                <Save className="h-5 w-5 mr-2" />
              )}
              Update Remedy
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditRemedy;