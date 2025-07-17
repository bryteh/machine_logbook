import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  Filter,
  Search,
  Eye,
  Edit
} from 'lucide-react';
import api from '../services/api';

interface Issue {
  id: string;
  machine_name: string;
  department_name: string;
  category: string;
  auto_title: string;
  status: string;
  created_at: string;
  resolved_at?: string;
  downtime_minutes?: number;
  is_runnable: boolean;
  remedies_count: number;
}

interface Department {
  department_id: string;
  name: string;
}

const IssueList: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [issues, setIssues] = useState<Issue[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const categoryOptions = [
    { value: 'alarm', label: 'Alarm' },
    { value: 'mechanical', label: 'Mechanical' },
    { value: 'electrical', label: 'Electrical' },
    { value: 'quality', label: 'Quality' },
    { value: 'process', label: 'Process' },
    { value: 'material_issue', label: 'Material Issue' },
    { value: 'machine_setup', label: 'Machine Setup' },
    { value: 'no_planning', label: 'No Planning' },
    { value: 'other', label: 'Other' },
  ];

  // Initialize filters from URL parameters
  useEffect(() => {
    const statusParam = searchParams.get('status');
    const priorityParam = searchParams.get('priority');
    const departmentParam = searchParams.get('department');

    console.log('URL params:', { statusParam, priorityParam, departmentParam });

    if (statusParam) {
      setStatusFilter(statusParam);
    }
    if (priorityParam) {
      setPriorityFilter(priorityParam);
    }
    if (departmentParam) {
      setDepartmentFilter(departmentParam);
    }
  }, [searchParams]);

  const loadDepartments = async () => {
    try {
      const response = await api.get('/departments');
      setDepartments(Array.isArray(response.data.results) ? response.data.results : []);
    } catch (error) {
      console.error('Error loading departments:', error);
      setDepartments([]);
    }
  };

  const loadIssues = async () => {
    try {
      setLoading(true);
      const params: any = {};
      
      // Handle multiple statuses from dashboard (e.g., "open,in_progress")
      if (statusFilter !== 'all') {
        if (statusFilter.includes(',')) {
          // For multiple statuses, we'll filter on frontend since backend might not support multiple
          // Just load all and filter below
        } else {
          params.status = statusFilter;
        }
      }
      
      if (priorityFilter !== 'all') params.priority = priorityFilter;
      if (departmentFilter !== 'all') params.department = departmentFilter;
      
      console.log('Loading issues with params:', params);
      const response = await api.get('/issues', { params });
      let issuesData = Array.isArray(response.data.results) ? response.data.results : [];
      
      // Handle multiple statuses filtering on frontend
      if (statusFilter !== 'all' && statusFilter.includes(',')) {
        const allowedStatuses = statusFilter.split(',');
        issuesData = issuesData.filter(issue => allowedStatuses.includes(issue.status));
      }
      
      setIssues(issuesData);
      console.log('Loaded issues:', issuesData.length);
    } catch (error) {
      console.error('Error loading issues:', error);
      setIssues([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  // Load issues when filters change, but add a small delay to ensure URL params are processed first
  useEffect(() => {
    const timer = setTimeout(() => {
      loadIssues();
    }, 100);
    
    return () => clearTimeout(timer);
  }, [statusFilter, priorityFilter, departmentFilter]);

  const handleCategoryToggle = (category: string) => {
    setCategoryFilter(prev => 
      prev.includes(category) 
        ? prev.filter(c => c !== category)
        : [...prev, category]
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <AlertTriangle className="h-5 w-5 text-orange-600" />;
      case 'on_hold':
        return <Clock className="h-5 w-5 text-yellow-600" />;
      case 'resolved':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      default:
        return <AlertTriangle className="h-5 w-5 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    switch (status) {
      case 'open':
        return `${baseClasses} bg-orange-100 text-orange-800`;
      case 'on_hold':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'resolved':
        return `${baseClasses} bg-green-100 text-green-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const getCategoryBadge = (category: string) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium";
    switch ((category || '').toLowerCase()) {
      case 'alarm':
        return `${baseClasses} bg-red-100 text-red-800`;
      case 'mechanical':
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case 'electrical':
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case 'quality':
        return `${baseClasses} bg-purple-100 text-purple-800`;
      case 'process':
        return `${baseClasses} bg-indigo-100 text-indigo-800`;
      case 'material_issue':
        return `${baseClasses} bg-orange-100 text-orange-800`;
      case 'machine_setup':
        return `${baseClasses} bg-teal-100 text-teal-800`;
      case 'no_planning':
        return `${baseClasses} bg-pink-100 text-pink-800`;
      case 'other':
        return `${baseClasses} bg-gray-100 text-gray-800`;
      default:
        return `${baseClasses} bg-gray-100 text-gray-800`;
    }
  };

  const filteredIssues = issues.filter(issue => {
    // Search term filter
    const matchesSearch = (issue.machine_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (issue.auto_title || '').toLowerCase().includes(searchTerm.toLowerCase());
    
    // Category filter (multi-select)
    const matchesCategory = categoryFilter.length === 0 || categoryFilter.includes(issue.category);
    
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">All Issues</h1>
        <p className="text-gray-600">Track and manage machine issues across your facility</p>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex flex-col space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Status</option>
                  <option value="open">Open</option>
                  <option value="on_hold">On Hold</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Priority</option>
                  <option value="low">🟢 Low</option>
                  <option value="medium">🟡 Medium</option>
                  <option value="high">🔴 High</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-2">
                <select
                  value={departmentFilter}
                  onChange={(e) => setDepartmentFilter(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">All Departments</option>
                  {departments.map(department => (
                    <option key={department.department_id} value={department.department_id}>
                      {department.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
           
             <div className="relative">
               <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
               <input
                 type="text"
                 placeholder="Search issues..."
                 value={searchTerm}
                 onChange={(e) => setSearchTerm(e.target.value)}
                 className="pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
               />
             </div>
           </div>
           
           {/* Category Filter */}
           <div>
             <label className="block text-sm font-medium text-gray-700 mb-2">Categories (Multi-select)</label>
             <div className="flex flex-wrap gap-2">
               {categoryOptions.map(category => (
                 <button
                   key={category.value}
                   onClick={() => handleCategoryToggle(category.value)}
                   className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                     categoryFilter.includes(category.value)
                       ? 'bg-blue-500 text-white'
                       : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                   }`}
                 >
                   {category.label}
                 </button>
               ))}
               {categoryFilter.length > 0 && (
                 <button
                   onClick={() => setCategoryFilter([])}
                   className="px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700 hover:bg-red-200"
                 >
                   Clear All
                 </button>
               )}
             </div>
           </div>
         </div>
       </div>

      {/* Issues List */}
      <div className="space-y-4">
        {filteredIssues.map((issue) => (
          <div key={issue.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    {getStatusIcon(issue.status)}
                    <h3 className="text-lg font-semibold text-gray-900 truncate">
                      {issue.auto_title || 'Untitled Issue'}
                    </h3>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-2 mb-3">
                    <span className={getStatusBadge(issue.status)}>
                      {(issue.status || 'unknown').replace('_', ' ').toUpperCase()}
                    </span>
                    <span className={getCategoryBadge(issue.category)}>
                      {issue.category || 'Unknown'}
                    </span>
                    {!issue.is_runnable && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        NOT RUNNABLE
                      </span>
                    )}
                  </div>

                  <div className="text-sm text-gray-600 space-y-1">
                    <p><span className="font-medium">Machine:</span> {issue.machine_name || 'Unknown'}</p>
                    <p><span className="font-medium">Department:</span> {issue.department_name || 'Unknown'}</p>
                    <p><span className="font-medium">Created:</span> {new Date(issue.created_at).toLocaleString()}</p>
                    {issue.resolved_at && (
                      <p><span className="font-medium">Resolved:</span> {new Date(issue.resolved_at).toLocaleString()}</p>
                    )}
                    {issue.downtime_minutes && (
                      <p><span className="font-medium">Downtime:</span> {issue.downtime_minutes} minutes</p>
                    )}
                  </div>
                </div>

                <div className="ml-6 flex-shrink-0">
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/issues/${issue.id}`}
                      className="inline-flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Eye className="h-4 w-4" />
                      <span>View</span>
                    </Link>
                    
                    {/* TODO: Add proper role-based access control */}
                    {/* For now, show edit button for all users - replace with role check */}
                    <Link
                      to={`/issues/${issue.id}/edit`}
                      className="inline-flex items-center space-x-2 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
                    >
                      <Edit className="h-4 w-4" />
                      <span>Edit</span>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredIssues.length === 0 && (
          <div className="text-center py-12">
            <AlertTriangle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No issues found</h3>
            <p className="text-gray-600">
              {searchTerm || statusFilter !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'No issues have been logged yet'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default IssueList;