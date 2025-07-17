import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  CheckCircle,
  Pause,
  Plus,
  FileImage,
  FileVideo,
  Calendar,
  Wrench,
  AlertTriangle,
  DollarSign,
  Package,
  Shield,
  Eye,
  EyeOff,
  User,
  Phone,
  Play,
  RotateCcw,
  Download,
  ExternalLink
} from 'lucide-react';
import api from '../services/api';
import MediaDisplay from '../components/MediaDisplay';

interface Attachment {
  id: string;
  file_url: string;
  file_name: string;
  file_type: string;
  purpose: string;
  uploaded_at: string;
}

interface Machine {
  machine_id: string;
  machine_number: string;
  model: string;
  status: string;
}

interface Department {
  department_id: string;
  name: string;
}

interface Remedy {
  id: string;
  description: string;
  technician_name: string;
  technician_display_name?: string;
  is_external: boolean;
  phone_number?: string;
  phone_display?: string;
  parts_purchased?: string;
  labor_cost?: number;
  parts_cost?: number;
  total_cost?: number;
  cost_display?: {
    labor_cost?: number;
    parts_cost?: number;
    total_cost?: number;
  };
  created_at: string;
  attachments?: Attachment[];
}

interface Issue {
  id: string;
  category: string;
  priority: string;
  alarm_code?: string;
  description: string;
  is_runnable: boolean;
  auto_title: string;
  ai_summary?: string;
  status: string;
  machine_id_ref: string;
  reported_by: string;
  downtime_start?: string;
  downtime_end?: string;
  downtime_hours?: number;
  created_at: string;
  updated_at: string;
  machine: Machine;
  department: Department;
  remedies: Remedy[];
  attachments?: Attachment[];
}

const IssueDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [updating, setUpdating] = useState(false);

  const fetchIssue = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/issues/${id}/`);
      setIssue(response.data);
    } catch (error) {
      console.error('Failed to fetch issue:', error);
      setError('Failed to load issue details');
    } finally {
      setLoading(false);
    }
  };

  // Fetch only downtime data for real-time updates
  const fetchDowntime = async () => {
    try {
      const response = await api.get(`/issues/${id}/`);
      if (issue && response.data.downtime_hours !== issue.downtime_hours) {
        setIssue(prev => prev ? {
          ...prev,
          downtime_hours: response.data.downtime_hours
        } : null);
      }
    } catch (error) {
      console.error('Failed to fetch downtime:', error);
    }
  };

  useEffect(() => {
    if (id) {
      fetchIssue();
    }
  }, [id]);

  // Auto-refresh for real-time downtime updates - only update downtime, not entire page
  useEffect(() => {
    if (!issue || issue.is_runnable || issue.status !== 'in_progress') {
      return;
    }

    const interval = setInterval(() => {
      fetchDowntime(); // Only fetch downtime data, not entire issue
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, [issue?.is_runnable, issue?.status, id]);

  const handleStatusUpdate = async (newStatus: string) => {
    if (!issue) return;
    
    setUpdating(true);
    try {
      const response = await api.patch(`/issues/${id}/update_status/`, {
        status: newStatus
      });
      setIssue(response.data);
    } catch (error) {
      console.error('Failed to update status:', error);
      setError('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open': return 'bg-red-100 text-red-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'on_hold': return 'bg-yellow-100 text-yellow-800';
      case 'resolved': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open': return <AlertTriangle className="h-4 w-4" />;
      case 'in_progress': return <Clock className="h-4 w-4" />;
      case 'on_hold': return <Pause className="h-4 w-4" />;
      case 'resolved': return <CheckCircle className="h-4 w-4" />;
      default: return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const calculateTotalCost = () => {
    if (!issue?.remedies) return 0;
    return issue.remedies.reduce((total, remedy) => {
      return total + (remedy.cost_display?.total_cost || 0);
    }, 0);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading issue details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
            <p className="mt-2 text-sm text-red-600">{error || 'Issue not found'}</p>
            <Link
              to="/issues"
              className="mt-4 inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to Issues
        </Link>
          </div>
        </div>
      </div>
    );
  }

  const totalCost = calculateTotalCost();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg rounded-lg">
      {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
                <Link
                  to="/issues"
                  className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  <ArrowLeft className="h-4 w-4 mr-1" />
                  Back to Issues
                </Link>
          <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    {issue.auto_title || 'Issue Details'}
                  </h1>
                  <p className="text-sm text-gray-600">
                    {issue.machine.model} • {issue.department.name}
                  </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(issue.priority)}`}>
                  {issue.priority}
                </span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(issue.status)}`}>
                  {getStatusIcon(issue.status)}
                  <span className="ml-1">{issue.status.replace('_', ' ')}</span>
                </span>
              </div>
              </div>
            </div>

          {/* Issue Information */}
          <div className="px-6 py-6 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Issue Information</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Category</dt>
                    <dd className="mt-1 text-sm text-gray-900">{issue.category}</dd>
                  </div>
                  {issue.alarm_code && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Alarm Code</dt>
                      <dd className="mt-1 text-sm text-gray-900">{issue.alarm_code}</dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Machine Runnable</dt>
                    <dd className="mt-1">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        issue.is_runnable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {issue.is_runnable ? 'Yes' : 'No'}
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-4">Tracking Information</h3>
                <dl className="space-y-3">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Reported By</dt>
                    <dd className="mt-1 text-sm text-gray-900">{issue.reported_by}</dd>
                  </div>
                <div>
                    <dt className="text-sm font-medium text-gray-500">Created</dt>
                    <dd className="mt-1 text-sm text-gray-900">{formatDateTime(issue.created_at)}</dd>
                  </div>
                  {issue.downtime_hours !== undefined && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Downtime</dt>
                      <dd className="mt-1 text-sm text-gray-900">{issue.downtime_hours.toFixed(4)} hours</dd>
                </div>
              )}
                  {totalCost > 0 && (
                <div>
                      <dt className="text-sm font-medium text-gray-500">Total Cost</dt>
                      <dd className="mt-1 text-sm text-gray-900 font-medium text-red-600">
                        <DollarSign className="h-4 w-4 inline mr-1" />
                        ${totalCost.toFixed(2)}
                      </dd>
                </div>
              )}
                </dl>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
              <p className="text-sm text-gray-900 bg-gray-50 p-4 rounded-md">{issue.description}</p>
          </div>

            {issue.ai_summary && (
              <div className="mt-6">
                <h3 className="text-sm font-medium text-gray-500 mb-2">AI Summary</h3>
                <p className="text-sm text-gray-900 bg-blue-50 p-4 rounded-md">{issue.ai_summary}</p>
                        </div>
                      )}
                    </div>

          {/* Issue Media Attachments */}
          {issue.attachments && issue.attachments.length > 0 && (
            <div className="px-6 py-6 border-b border-gray-200">
              <MediaDisplay 
                attachments={issue.attachments} 
                title="Issue Media Attachments" 
              />
            </div>
          )}

          {/* Status Actions */}
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Status Actions</h3>
            <div className="flex flex-wrap gap-3">
              {issue.status === 'open' && (
                <button
                  onClick={() => handleStatusUpdate('in_progress')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Start Progress
                </button>
              )}
              
              {issue.status === 'in_progress' && (
                <>
                  <button
                    onClick={() => handleStatusUpdate('on_hold')}
                    className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 flex items-center gap-2"
                  >
                    <Pause className="w-4 h-4" />
                    Put On Hold
                  </button>
                  <button
                    onClick={() => handleStatusUpdate('resolved')}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center gap-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    Mark Resolved
                  </button>
                </>
              )}
              
              {issue.status === 'on_hold' && (
                <button
                  onClick={() => handleStatusUpdate('in_progress')}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Resume Progress
                </button>
              )}
              
              {issue.status === 'resolved' && (
                <button
                  onClick={() => handleStatusUpdate('in_progress')}
                  className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700 flex items-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Reopen Issue
                </button>
              )}
            </div>
                      </div>

          {/* Remedies Section */}
          <div className="px-6 py-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">
                Remedies ({issue.remedies.length})
              </h3>
              <Link
                to={`/issues/${id}/add-remedy`}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Remedy
              </Link>
                      </div>

            {issue.remedies.length === 0 ? (
              <div className="text-center py-12 bg-gray-50 rounded-lg">
                <Wrench className="h-8 w-8 text-gray-400 mx-auto mb-4" />
                <p className="text-sm text-gray-600">No remedies have been added yet.</p>
                <Link
                  to={`/issues/${id}/add-remedy`}
                  className="mt-2 inline-flex items-center text-blue-600 hover:text-blue-800"
                >
                  Add the first remedy
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                {issue.remedies.map((remedy) => (
                  <div key={remedy.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            remedy.is_external ? 'bg-orange-100' : 'bg-blue-100'
                          }`}>
                            {remedy.is_external ? 
                              <Shield className="h-5 w-5 text-orange-600" /> : 
                              <User className="h-5 w-5 text-blue-600" />
                            }
                          </div>
              </div>
                        <div>
                          <h4 className="text-lg font-medium text-gray-900">
                            {remedy.technician_display_name || remedy.technician_name}
                          </h4>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              remedy.is_external ? 'bg-orange-100 text-orange-800' : 'bg-blue-100 text-blue-800'
                            }`}>
                              {remedy.is_external ? 'External' : 'Internal'}
                            </span>
                            {remedy.phone_display && (
                              <span className="text-sm text-gray-600 flex items-center">
                                <Phone className="h-3 w-3 mr-1" />
                                {remedy.phone_display}
                              </span>
            )}
          </div>
        </div>
              </div>
                      <span className="text-sm text-gray-500">
                        {formatDateTime(remedy.created_at)}
                      </span>
          </div>

                    <div className="mb-4">
                      <h5 className="text-sm font-medium text-gray-900 mb-2">Remedy Description</h5>
                      <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md">
                        {remedy.description}
                      </p>
              </div>

                    {remedy.parts_purchased && (
                      <div className="mb-4">
                        <h5 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <Package className="h-4 w-4 mr-1" />
                          Parts/Items Purchased
                        </h5>
                        <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-md">
                          {remedy.parts_purchased}
                        </p>
                  </div>
                    )}

                    {/* Remedy Media Attachments */}
                    {remedy.attachments && remedy.attachments.length > 0 && (
                      <div className="mb-4">
                        <MediaDisplay 
                          attachments={remedy.attachments} 
                          title="Remedy Media" 
                        />
                </div>
              )}

                    {remedy.cost_display && (
                      <div className="bg-green-50 p-4 rounded-md">
                        <h5 className="text-sm font-medium text-gray-900 mb-2 flex items-center">
                          <DollarSign className="h-4 w-4 mr-1" />
                          Cost Breakdown
                        </h5>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Labor:</span>
                            <span className="ml-2 font-medium">
                              ${remedy.cost_display.labor_cost?.toFixed(2) || '0.00'}
                            </span>
                          </div>
                          <div>
                            <span className="text-gray-600">Parts:</span>
                            <span className="ml-2 font-medium">
                              ${remedy.cost_display.parts_cost?.toFixed(2) || '0.00'}
                            </span>
                  </div>
                  <div>
                            <span className="text-gray-600">Total:</span>
                            <span className="ml-2 font-medium text-green-600">
                              ${remedy.cost_display.total_cost?.toFixed(2) || '0.00'}
                            </span>
                          </div>
                  </div>
                </div>
              )}
            </div>
                  )
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IssueDetail;