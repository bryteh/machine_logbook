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
  Video
} from 'lucide-react';
import api from '../services/api';

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

const AddRemedy: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
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
        ...formData,
        labor_cost: formData.labor_cost ? parseFloat(formData.labor_cost) : null,
        parts_cost: formData.parts_cost ? parseFloat(formData.parts_cost) : null
      };

      console.log('Submitting remedy data:', submitData);
      const response = await api.post(`/issues/${id}/add_remedy/`, submitData);
      console.log('Remedy created successfully:', response.data);

      // Handle file uploads if there are any files
      if (files.length > 0) {
        const uploadPromises = files.map(file => {
          const formData = new FormData();
          formData.append('file', file);
          formData.append('file_type', file.type.startsWith('image/') ? 'image' : 'video');
          formData.append('purpose', 'remedy_documentation');
          return api.post(`/issues/${id}/add_attachment/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        });

        try {
          await Promise.all(uploadPromises);
          console.log('All remedy files uploaded successfully');
        } catch (uploadError) {
          console.error('Error uploading remedy files:', uploadError);
          // Still navigate even if file upload fails
        }
      }

      navigate(`/issues/${id}`);
    } catch (error: any) {
      console.error('Failed to add remedy:', error);
      console.error('Error response:', error.response?.data);
      if (error.response?.data) {
        const errorMessages = Object.values(error.response.data).flat();
        setError(errorMessages.join(', '));
      } else {
        setError('Failed to add remedy. Please try again.');
      }
    } finally {
      setSubmitting(false);
    }
  };

  const totalCost = calculateTotalCost();

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

  useEffect(() => {
    const fetchIssue = async () => {
      try {
        const response = await api.get(`/issues/${id}`);
        setIssue(response.data);
        setFormData(prev => ({
          ...prev,
          description: response.data.description,
          technician_name: response.data.technician_name,
          is_external: response.data.is_external,
          phone_number: response.data.phone_number,
          parts_purchased: response.data.parts_purchased,
          labor_cost: response.data.labor_cost?.toString() || '',
          parts_cost: response.data.parts_cost?.toString() || '',
          is_machine_runnable: response.data.is_machine_runnable
        }));
    } catch (error) {
        console.error('Failed to fetch issue:', error);
    }
  };

    fetchIssue();
  }, [id]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate(`/issues/${id}`)}
                  className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back to Issue
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Add Remedy</h1>
              </div>
              <button
                onClick={() => setShowGuide(!showGuide)}
                className="px-4 py-2 text-sm bg-blue-50 text-blue-600 border border-blue-200 rounded-md hover:bg-blue-100"
              >
                {showGuide ? 'Hide Guide' : 'Show Guide'}
        </button>
        </div>
      </div>

          {showGuide && (
            <div className="px-6 py-4 bg-blue-50 border-b border-blue-200">
              <div className="border border-blue-200 bg-blue-50 p-4 rounded-md mb-4">
                <h4 className="text-sm font-medium text-blue-900 mb-2">Remedy Documentation Guide</h4>
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">Remedy Description Guide:</p>
                  <ol className="list-decimal list-inside space-y-1 text-xs">
                    <li>Root cause identified</li>
                    <li>Actions taken</li>
                    <li>Parts replaced/purchased (list with quantities)</li>
                    <li>Tools/equipment used</li>
                    <li>Time taken to complete</li>
                    <li>Testing performed</li>
                    <li>Preventive measures recommended</li>
                  </ol>
                </div>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Error</h3>
                    <p className="text-sm text-red-700 mt-1">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Remedy Description */}
          <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Remedy Description *
            </label>
                <button
                  type="button"
                  onClick={improveDescription}
                  disabled={isImprovingDescription || !formData.description.trim()}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  <Sparkles className="h-3 w-3 mr-1" />
                  {isImprovingDescription ? 'Refining...' : 'Refine with AI'}
                </button>
              </div>
            <textarea
              id="description"
                name="description"
                rows={6}
                value={formData.description}
                onChange={handleInputChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Describe the remedy performed, following the guide above..."
                required
              />
            </div>

            {/* Technician Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="technician_name" className="block text-sm font-medium text-gray-700 mb-2">
                  <User className="h-4 w-4 inline mr-1" />
                  Technician Name *
                </label>
                <input
                  type="text"
                  id="technician_name"
                  name="technician_name"
                  value={formData.technician_name}
                  onChange={handleInputChange}
                  className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Technician Type
                  </label>
                </div>
                <div className="space-y-2">
                  <label className="inline-flex items-center">
                    <input
                      type="checkbox"
                      name="is_external"
                      checked={formData.is_external}
                      onChange={handleCheckboxChange}
                      className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                    />
                    <span className="ml-2 text-sm text-gray-900">External technician</span>
                  </label>
                  <div className="mt-2">
                    <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-1">
                      <Phone className="h-4 w-4 inline mr-1" />
                      Phone Number {formData.is_external && '*'}
                    </label>
                    <input
                      type="tel"
                      id="phone_number"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleInputChange}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder={formData.is_external ? "External technician contact (required)" : "Technician contact (optional)"}
                      required={formData.is_external}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Machine Status Section */}
            <div className="border-t border-gray-200 pt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Machine Status After Remedy
              </h3>
              <div className="space-y-2">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    name="is_machine_runnable"
                    checked={formData.is_machine_runnable}
                    onChange={handleCheckboxChange}
                    className="rounded border-gray-300 text-green-600 shadow-sm focus:border-green-300 focus:ring focus:ring-green-200 focus:ring-opacity-50"
                  />
                  <span className="ml-2 text-sm text-gray-900">Machine is runnable (no downtime)</span>
                </label>
                <p className="text-xs text-gray-500 ml-6">
                  Check this if the machine can operate normally even though the issue isn't fully resolved. 
                  This prevents counting it as downtime while the final fix is pending.
                </p>
              </div>
            </div>

            {/* Parts and Costing Section */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Parts & Costing Information</h3>
              
              {/* Parts/Items Guide */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-medium text-green-900 mb-2">📦 Parts/Items Guide</h4>
                <ul className="text-sm text-green-800 space-y-1">
                  <li>1. List all parts/items purchased with part numbers and quantities</li>
                  <li>2. Include supplier information and purchase dates</li>
                  <li>3. Document labor hours and hourly rates</li>
                  <li>4. Calculate total costs accurately for budget tracking</li>
                </ul>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="parts_purchased" className="block text-sm font-medium text-gray-700 mb-2">
                    Parts/Items Purchased
                  </label>
                  <textarea
                    id="parts_purchased"
                    name="parts_purchased"
                    rows={3}
                    value={formData.parts_purchased}
                    onChange={handleInputChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="List parts with quantities, part numbers, and suppliers..."
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="labor_cost" className="block text-sm font-medium text-gray-700 mb-2">
                      <DollarSign className="h-4 w-4 inline mr-1" />
                      Labor Cost
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      id="labor_cost"
                      name="labor_cost"
                      value={formData.labor_cost}
                      onChange={handleInputChange}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label htmlFor="parts_cost" className="block text-sm font-medium text-gray-700 mb-2">
                      <Package className="h-4 w-4 inline mr-1" />
                      Parts Cost
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      id="parts_cost"
                      name="parts_cost"
                      value={formData.parts_cost}
                      onChange={handleInputChange}
                      className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Total Cost
                    </label>
                    <div className="block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-50 text-gray-900 font-medium">
                      ${totalCost.toFixed(2)}
                    </div>
                  </div>
                </div>
          </div>
        </div>

        {/* Media Upload Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Media Documentation</h2>
          <p className="text-sm text-gray-600 mb-4">Upload photos or videos showing the remedy work (optional)</p>
          
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
            <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate(`/issues/${id}`)}
                className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
                disabled={submitting}
                className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
                {submitting ? 'Adding Remedy...' : 'Add Remedy'}
          </button>
        </div>
      </form>
        </div>
      </div>
    </div>
  );
};

export default AddRemedy;