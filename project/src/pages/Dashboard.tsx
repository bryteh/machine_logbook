import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Filter,
  Plus,
  Activity,
  DollarSign
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface DashboardMetrics {
  total_issues: number;
  open_issues: number;
  resolved_issues: number;
  on_hold_issues: number;
  high_priority_issues: number;
  total_downtime_hours: number;
  avg_downtime_per_issue: number;
  daily_trend: Array<{
    date: string;
    issues: number;
    resolved: number;
  }>;
  department_breakdown: Array<{
    department_id: string;
    name: string;
    total_issues: number;
    open_issues: number;
    resolved_issues: number;
    downtime_hours: number;
    total_cost?: number;
  }>;
  total_cost?: number;
  avg_cost_per_issue?: number;
}

interface Department {
  department_id: string;
  name: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('');
  const [selectedDays, setSelectedDays] = useState<number>(30);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchMetrics = async () => {
    // Double-check authentication before making API call
    if (!isAuthenticated) {
      console.log('Dashboard: User not authenticated, skipping metrics fetch');
      setError('Please log in to view dashboard metrics');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      console.log('Dashboard: Fetching metrics for authenticated user:', user?.username);
      
      const params = new URLSearchParams({
        days: selectedDays.toString()
      });
      
      if (selectedDepartment) {
        params.append('department', selectedDepartment);
      }

      console.log('Dashboard: Making API call to /dashboard/metrics/');
      const response = await api.get(`/dashboard/metrics/?${params}`);
      
      console.log('Dashboard: Metrics response received:', response.status);
      setMetrics(response.data);
      
    } catch (error: any) {
      console.error('Dashboard: Failed to fetch metrics:', error);
      console.log('Dashboard: Current auth state - isAuthenticated:', isAuthenticated, 'user:', user);
      
      let errorMessage = 'Failed to load dashboard metrics';
      
      if (error.response?.status === 401) {
        errorMessage = 'Authentication expired. Please log in again.';
      } else if (error.response?.status === 403) {
        errorMessage = 'You do not have permission to view dashboard metrics';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = `Network error: ${error.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get('/departments/');
      // Handle paginated response - extract results array
      const departmentsData = response.data.results || response.data;
      setDepartments(Array.isArray(departmentsData) ? departmentsData : []);
    } catch (error) {
      console.error('Failed to fetch departments:', error);
      setDepartments([]);
    }
  };

  useEffect(() => {
    // Only fetch data when user is authenticated and auth is not loading
    if (isAuthenticated && !authLoading) {
      fetchDepartments();
    }
  }, [isAuthenticated, authLoading]);

  useEffect(() => {
    // Only fetch metrics when user is authenticated and auth is not loading
    if (isAuthenticated && !authLoading) {
      fetchMetrics();
    }
  }, [selectedDepartment, selectedDays, isAuthenticated, authLoading]);

  // Show loading while authentication is being checked
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Checking authentication...</p>
          </div>
        </div>
      </div>
    );
  }

  // Don't aggressively redirect - let AuthContext handle this
  if (!isAuthenticated && !authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
            <p className="mt-2 text-sm text-red-600">Please log in to view the dashboard</p>
            <button
              onClick={() => navigate('/login')}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show loading for dashboard data
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Loading dashboard...</p>
          </div>
        </div>
              </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto" />
            <p className="mt-2 text-sm text-red-600">{error || 'Failed to load dashboard'}</p>
          </div>
        </div>
      </div>
    );
  }

  const selectedDepartmentName = selectedDepartment 
    ? (Array.isArray(departments) ? departments.find(d => d.department_id === selectedDepartment)?.name : 'Unknown')
    : 'All Departments';

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Filters */}
      <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Machine Maintenance Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">
                {selectedDepartmentName} • Last {selectedDays} days
              </p>
            </div>
            
            <div className="mt-4 sm:mt-0 flex flex-col sm:flex-row gap-4">
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-500" />
                <select
                  value={selectedDepartment}
                  onChange={(e) => setSelectedDepartment(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Departments</option>
                  {Array.isArray(departments) && departments.map((dept) => (
                    <option key={dept.department_id} value={dept.department_id}>
                      {dept.name}
                    </option>
                  ))}
                </select>
      </div>

              <select
                value={selectedDays}
                onChange={(e) => setSelectedDays(parseInt(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>
        </div>

        {/* Key Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div 
            className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/issues')}
          >
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Issues</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.total_issues}</p>
              </div>
            </div>
          </div>

          <div 
            className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/issues?status=open,in_progress')}
          >
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Open Cases</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.open_issues}</p>
              </div>
            </div>
                </div>

          <div 
            className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/issues?status=resolved')}
          >
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Resolved</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.resolved_issues}</p>
              </div>
            </div>
      </div>

          <div 
            className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/issues?priority=high')}
          >
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-red-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.high_priority_issues}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Activity className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Downtime Hours</p>
                <p className="text-2xl font-bold text-gray-900">{metrics.total_downtime_hours.toFixed(4)}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Cost Metrics (if available) */}
        {metrics.total_cost !== undefined && (
          <div className="grid grid-cols-1 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-red-500" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Cost</p>
                  <p className="text-2xl font-bold text-gray-900">RM {metrics.total_cost.toFixed(2)}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Daily Trend Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Daily Issues Trend</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={metrics.daily_trend}>
              <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="issues" fill="#3B82F6" name="New Issues" />
                <Bar dataKey="resolved" fill="#10B981" name="Resolved" />
            </BarChart>
          </ResponsiveContainer>
        </div>

          {/* Department Cost Pie Chart */}
          {metrics.total_cost !== undefined && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Cost by Department</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={metrics.department_breakdown.filter(dept => dept.total_cost && dept.total_cost > 0)}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="total_cost"
                    nameKey="name"
                    label={({ name, value }) => `${name}: RM ${Number(value).toFixed(0)}`}
                  >
                    {metrics.department_breakdown.filter(dept => dept.total_cost && dept.total_cost > 0).map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={[
                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
                        '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'
                      ][index % 8]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`RM ${Number(value).toFixed(2)}`, 'Total Cost']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Department Breakdown */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Department Breakdown</h3>
            <div className="space-y-4">
              {metrics.department_breakdown.map((dept) => (
                <div key={dept.department_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">{dept.name}</h4>
                    <span className="text-sm text-gray-500">{dept.department_id}</span>
      </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Total Issues:</span>
                      <span className="ml-2 font-medium">{dept.total_issues}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Open:</span>
                      <span className="ml-2 font-medium text-orange-600">{dept.open_issues}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Resolved:</span>
                      <span className="ml-2 font-medium text-green-600">{dept.resolved_issues}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Downtime:</span>
                      <span className="ml-2 font-medium">{dept.downtime_hours.toFixed(4)}h</span>
                    </div>
                    {dept.total_cost !== undefined && (
                      <div className="col-span-2">
                        <span className="text-gray-600">Total Cost:</span>
                        <span className="ml-2 font-medium text-red-600">RM {dept.total_cost.toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;