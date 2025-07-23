import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { MaintenanceService } from '../services/api';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  WrenchScrewdriverIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const Maintenance: React.FC = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    category: '',
    emergency_only: false
  });

  useEffect(() => {
    fetchMaintenanceRequests();
  }, [filters]);

  const fetchMaintenanceRequests = async () => {
    try {
      setLoading(true);
      const params = {
        ...filters,
        skip: 0,
        limit: 50
      };
      const data = await MaintenanceService.getMaintenanceRequests(params);
      setRequests(data.requests);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch maintenance requests');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseRequest = async (id: string) => {
    const resolution = prompt('Please provide resolution notes:');
    if (!resolution) return;

    try {
      await MaintenanceService.closeMaintenanceRequest(id, resolution);
      fetchMaintenanceRequests();
    } catch (err: any) {
      setError(err.message || 'Failed to close maintenance request');
    }
  };

  const filteredRequests = requests.filter(request =>
    request.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    request.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <div className="flex">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Maintenance</h1>
          <p className="mt-1 text-sm text-gray-600">
            {user?.role === 'tenant' ? 'Your maintenance requests' : 'Manage maintenance requests'}
          </p>
        </div>
        {user?.role === 'tenant' && (
          <Link
            to="/maintenance/new"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Submit Request
          </Link>
        )}
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="sr-only">Search requests</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500"
                    placeholder="Search maintenance requests..."
                  />
                </div>
              </div>
            </div>

            {/* Filter Controls */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
                >
                  <option value="">All Statuses</option>
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="closed">Closed</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Priority</label>
                <select
                  value={filters.priority}
                  onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value }))}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
                >
                  <option value="">All Priorities</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Category</label>
                <select
                  value={filters.category}
                  onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
                >
                  <option value="">All Categories</option>
                  <option value="plumbing">Plumbing</option>
                  <option value="electrical">Electrical</option>
                  <option value="hvac">HVAC</option>
                  <option value="appliances">Appliances</option>
                  <option value="flooring">Flooring</option>
                  <option value="painting">Painting</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="emergency-only"
                  checked={filters.emergency_only}
                  onChange={(e) => setFilters(prev => ({ ...prev, emergency_only: e.target.checked }))}
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                />
                <label htmlFor="emergency-only" className="ml-2 block text-sm text-gray-900">
                  Emergency Only
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Maintenance Requests List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredRequests.map((request) => (
            <MaintenanceRequestItem
              key={request.id}
              request={request}
              userRole={user?.role}
              onClose={handleCloseRequest}
            />
          ))}
        </ul>
      </div>

      {filteredRequests.length === 0 && (
        <div className="text-center py-12">
          <WrenchScrewdriverIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No maintenance requests found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search criteria.' : 
             user?.role === 'tenant' ? 'Submit a request when you need maintenance.' : 
             'Maintenance requests will appear here when tenants submit them.'}
          </p>
          {user?.role === 'tenant' && (
            <div className="mt-6">
              <Link
                to="/maintenance/new"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Submit Request
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const MaintenanceRequestItem: React.FC<{
  request: any;
  userRole?: string;
  onClose: (id: string) => void;
}> = ({ request, userRole, onClose }) => {
  const statusIcons = {
    open: ClockIcon,
    in_progress: CogIcon,
    completed: CheckCircleIcon,
    closed: CheckCircleIcon
  };

  const statusColors = {
    open: 'text-yellow-600 bg-yellow-100',
    in_progress: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    closed: 'text-gray-600 bg-gray-100'
  };

  const priorityColors = {
    low: 'text-green-600 bg-green-100',
    medium: 'text-yellow-600 bg-yellow-100',
    high: 'text-orange-600 bg-orange-100',
    urgent: 'text-red-600 bg-red-100'
  };

  const StatusIcon = statusIcons[request.status as keyof typeof statusIcons];

  return (
    <li>
      <div className="px-4 py-4 sm:px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              {request.is_emergency ? (
                <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
              ) : (
                <StatusIcon className="h-6 w-6 text-gray-400" />
              )}
            </div>
            <div className="ml-4">
              <div className="flex items-center space-x-2">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {request.title}
                </p>
                {request.is_emergency && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Emergency
                  </span>
                )}
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[request.status as keyof typeof statusColors]}`}>
                  {request.status}
                </span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[request.priority as keyof typeof priorityColors]}`}>
                  {request.priority}
                </span>
              </div>
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <p className="truncate">
                  {request.category} • {request.property?.name || 'Property'}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Link
              to={`/maintenance/${request.id}`}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              View Details
            </Link>
            
            {userRole === 'landlord' && request.status === 'completed' && (
              <button
                onClick={() => onClose(request.id)}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <CheckCircleIcon className="h-4 w-4 mr-1" />
                Close
              </button>
            )}
          </div>
        </div>
        
        <div className="mt-2">
          <p className="text-sm text-gray-600 line-clamp-2">
            {request.description}
          </p>
        </div>
        
        <div className="mt-2 sm:flex sm:justify-between">
          <div className="sm:flex">
            <p className="flex items-center text-sm text-gray-500">
              Created: {new Date(request.created_at).toLocaleDateString()}
            </p>
            {request.location && (
              <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                Location: {request.location}
              </p>
            )}
          </div>
          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
            {request.estimated_cost && (
              <p>
                Estimated Cost: ${request.estimated_cost}
              </p>
            )}
          </div>
        </div>
      </div>
    </li>
  );
};

export default Maintenance;