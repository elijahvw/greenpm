import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { maintenanceService, MaintenanceRequest, MaintenanceStats } from '../services/maintenanceService';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  WrenchScrewdriverIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  CogIcon,
  ChatBubbleLeftIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const Maintenance: React.FC = () => {
  const { user } = useAuth();
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [stats, setStats] = useState<MaintenanceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    property_id: ''
  });
  const [selectedRequest, setSelectedRequest] = useState<MaintenanceRequest | null>(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [requestHistory, setRequestHistory] = useState<any[]>([]);

  useEffect(() => {
    fetchData();
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [requestsData, statsData] = await Promise.all([
        maintenanceService.getMaintenanceRequests(filters),
        maintenanceService.getMaintenanceStats()
      ]);
      setRequests(requestsData);
      setStats(statsData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch maintenance data');
      toast.error('Failed to load maintenance data');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (request: MaintenanceRequest, newStatus: string, notes?: string) => {
    try {
      await maintenanceService.updateMaintenanceStatus(request.id, newStatus as any, notes);
      toast.success('Status updated successfully');
      setShowStatusModal(false);
      fetchData(); // Refresh data
    } catch (error: any) {
      toast.error('Failed to update status');
      console.error('Status update error:', error);
    }
  };

  const handleViewHistory = async (request: MaintenanceRequest) => {
    try {
      const history = await maintenanceService.getMaintenanceHistory(request.id);
      setRequestHistory(history.history);
      setSelectedRequest(request);
      setShowHistoryModal(true);
    } catch (error: any) {
      toast.error('Failed to load request history');
      console.error('History load error:', error);
    }
  };

  const handleAddComment = async (requestId: string, comment: string) => {
    try {
      await maintenanceService.addMaintenanceComment(requestId, comment);
      toast.success('Comment added successfully');
      if (showHistoryModal && selectedRequest) {
        handleViewHistory(selectedRequest); // Refresh history
      }
    } catch (error: any) {
      toast.error('Failed to add comment');
      console.error('Comment add error:', error);
    }
  };

  const handleCloseRequest = async (id: string) => {
    const resolution = prompt('Please provide resolution notes:');
    if (!resolution) return;

    try {
      await maintenanceService.updateMaintenanceStatus(id, 'completed', resolution);
      toast.success('Request closed successfully');
      fetchData();
    } catch (err: any) {
      toast.error('Failed to close maintenance request');
      console.error('Close request error:', err);
    }
  };

  const filteredRequests = requests.filter(request =>
    request.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (request.description || '').toLowerCase().includes(searchTerm.toLowerCase())
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

      {/* Statistics Dashboard */}
      {stats && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Request Overview</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{stats.total_requests}</div>
                <div className="text-sm text-gray-500">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.open_requests}</div>
                <div className="text-sm text-gray-500">Open</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{stats.in_progress_requests}</div>
                <div className="text-sm text-gray-500">In Progress</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.completed_requests}</div>
                <div className="text-sm text-gray-500">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.high_priority}</div>
                <div className="text-sm text-gray-500">High Priority</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{stats.urgent_priority}</div>
                <div className="text-sm text-gray-500">Urgent</div>
              </div>
            </div>
          </div>
        </div>
      )}

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
                <label className="block text-sm font-medium text-gray-700">Property</label>
                <select
                  value={filters.property_id}
                  onChange={(e) => setFilters(prev => ({ ...prev, property_id: e.target.value }))}
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
                >
                  <option value="">All Properties</option>
                  {/* Property options would be populated dynamically */}
                </select>
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
              onStatusUpdate={handleStatusUpdate}
              onViewHistory={handleViewHistory}
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

      {/* History Modal */}
      {showHistoryModal && selectedRequest && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Request History: {selectedRequest.title}
                </h3>
                <button
                  onClick={() => setShowHistoryModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="max-h-96 overflow-y-auto">
                {requestHistory.length > 0 ? (
                  <div className="space-y-4">
                    {requestHistory.map((entry, index) => (
                      <div key={index} className="border-l-2 border-gray-200 pl-4 pb-4">
                        <div className="flex items-center justify-between">
                          <div className="text-sm font-medium text-gray-900">
                            {entry.action === 'status_change' ? 'Status Changed' : 
                             entry.action === 'comment' ? 'Comment Added' : entry.action}
                          </div>
                          <div className="text-xs text-gray-500">
                            {new Date(entry.created_at).toLocaleString()}
                          </div>
                        </div>
                        <div className="text-sm text-gray-600 mt-1">
                          By: {entry.user_name} ({entry.role})
                        </div>
                        {entry.old_value && entry.new_value && (
                          <div className="text-sm text-gray-600 mt-1">
                            Changed from: <span className="font-medium">{entry.old_value}</span> to <span className="font-medium">{entry.new_value}</span>
                          </div>
                        )}
                        {entry.notes && (
                          <div className="text-sm text-gray-700 mt-2 bg-gray-50 p-2 rounded">
                            {entry.notes}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500">No history available</div>
                )}
              </div>
              
              {/* Add Comment Section */}
              <div className="mt-4 border-t pt-4">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="Add a comment..."
                    className="flex-1 border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                        handleAddComment(selectedRequest.id, e.currentTarget.value.trim());
                        e.currentTarget.value = '';
                      }
                    }}
                  />
                  <button
                    onClick={(e) => {
                      const input = e.currentTarget.parentElement?.querySelector('input') as HTMLInputElement;
                      if (input?.value.trim()) {
                        handleAddComment(selectedRequest.id, input.value.trim());
                        input.value = '';
                      }
                    }}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                  >
                    <ChatBubbleLeftIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const MaintenanceRequestItem: React.FC<{
  request: MaintenanceRequest;
  userRole?: string;
  onClose: (id: string) => void;
  onStatusUpdate?: (request: MaintenanceRequest, status: string, notes?: string) => void;
  onViewHistory?: (request: MaintenanceRequest) => void;
}> = ({ request, userRole, onClose, onStatusUpdate, onViewHistory }) => {
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
              {request.priority === 'urgent' ? (
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
                {request.priority === 'urgent' && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Urgent
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
                  {request.property_name || 'Property'} • Created {new Date(request.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {onViewHistory && (
              <button
                onClick={() => onViewHistory(request)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <DocumentTextIcon className="h-4 w-4 mr-1" />
                History
              </button>
            )}
            
            {userRole === 'landlord' && onStatusUpdate && (
              <div className="relative inline-block text-left">
                <select
                  value={request.status}
                  onChange={(e) => {
                    const notes = e.target.value !== request.status ? 
                      prompt(`Update status to ${e.target.value}. Add notes (optional):`) || undefined : 
                      undefined;
                    if (e.target.value !== request.status) {
                      onStatusUpdate(request, e.target.value, notes);
                    }
                  }}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <option value="open">Open</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
              </div>
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
            {request.property_address && (
              <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
                Property: {request.property_address}
              </p>
            )}
          </div>
          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
            <p>
              Priority: <span className={`px-2 py-1 rounded-full text-xs font-medium ${maintenanceService.getPriorityColor(request.priority)}`}>
                {request.priority}
              </span>
            </p>
          </div>
        </div>
      </div>
    </li>
  );
};

export default Maintenance;