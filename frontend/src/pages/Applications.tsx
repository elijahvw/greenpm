import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ApplicationService } from '../services/api';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  BuildingOfficeIcon
} from '@heroicons/react/24/outline';

const Applications: React.FC = () => {
  const { user } = useAuth();
  const [applications, setApplications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchApplications();
  }, [statusFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchApplications = async () => {
    try {
      setLoading(true);
      const params = {
        status: statusFilter,
        skip: 0,
        limit: 50
      };
      const data = await ApplicationService.getApplications(params);
      setApplications(data.applications);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch applications');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await ApplicationService.approveApplication(id);
      fetchApplications();
    } catch (err: any) {
      setError(err.message || 'Failed to approve application');
    }
  };

  const handleReject = async (id: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    try {
      await ApplicationService.rejectApplication(id, reason);
      fetchApplications();
    } catch (err: any) {
      setError(err.message || 'Failed to reject application');
    }
  };

  const filteredApplications = applications.filter(app =>
    app.property?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    app.applicant?.email?.toLowerCase().includes(searchTerm.toLowerCase())
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
          <h1 className="text-2xl font-bold text-gray-900">Applications</h1>
          <p className="mt-1 text-sm text-gray-600">
            {user?.role === 'tenant' ? 'Your rental applications' : 'Manage rental applications'}
          </p>
        </div>
        {user?.role === 'tenant' && (
          <Link
            to="/properties"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Browse Properties
          </Link>
        )}
      </div>

      {/* Search and Filters */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="sr-only">Search applications</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-green-500 focus:border-green-500"
                  placeholder="Search applications..."
                />
              </div>
            </div>

            <div className="w-full sm:w-auto">
              <label className="sr-only">Filter by status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="leased">Leased</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Applications List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {filteredApplications.map((application) => (
            <ApplicationItem
              key={application.id}
              application={application}
              userRole={user?.role}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </ul>
      </div>

      {filteredApplications.length === 0 && (
        <div className="text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No applications found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search criteria.' : 
             user?.role === 'tenant' ? 'Start by browsing available properties.' : 
             'Applications will appear here when tenants apply.'}
          </p>
          {user?.role === 'tenant' && (
            <div className="mt-6">
              <Link
                to="/properties"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
              >
                <BuildingOfficeIcon className="h-4 w-4 mr-2" />
                Browse Properties
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const ApplicationItem: React.FC<{
  application: any;
  userRole?: string;
  onApprove: (id: string) => void;
  onReject: (id: string) => void;
}> = ({ application, userRole, onApprove, onReject }) => {
  const statusIcons = {
    pending: ClockIcon,
    approved: CheckCircleIcon,
    rejected: XCircleIcon,
    leased: CheckCircleIcon
  };

  const statusColors = {
    pending: 'text-yellow-600 bg-yellow-100',
    approved: 'text-green-600 bg-green-100',
    rejected: 'text-red-600 bg-red-100',
    leased: 'text-blue-600 bg-blue-100'
  };

  const StatusIcon = statusIcons[application.status as keyof typeof statusIcons];

  return (
    <li>
      <div className="px-4 py-4 sm:px-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <StatusIcon className="h-6 w-6 text-gray-400" />
            </div>
            <div className="ml-4">
              <div className="flex items-center">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {application.property?.name || 'Property'}
                </p>
                <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColors[application.status as keyof typeof statusColors]}`}>
                  {application.status}
                </span>
              </div>
              <div className="mt-2 flex items-center text-sm text-gray-500">
                <p className="truncate">
                  {userRole === 'tenant' ? 
                    `Applied on ${new Date(application.created_at).toLocaleDateString()}` :
                    `From ${application.applicant?.email || 'Unknown'}`
                  }
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Link
              to={`/applications/${application.id}`}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              View Details
            </Link>
            
            {userRole === 'landlord' && application.status === 'pending' && (
              <>
                <button
                  onClick={() => onApprove(application.id)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
                >
                  <CheckCircleIcon className="h-4 w-4 mr-1" />
                  Approve
                </button>
                <button
                  onClick={() => onReject(application.id)}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                >
                  <XCircleIcon className="h-4 w-4 mr-1" />
                  Reject
                </button>
              </>
            )}
          </div>
        </div>
        
        <div className="mt-2 sm:flex sm:justify-between">
          <div className="sm:flex">
            <p className="flex items-center text-sm text-gray-500">
              Annual Income: ${application.annual_income?.toLocaleString() || 'N/A'}
            </p>
            <p className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0 sm:ml-6">
              Move-in Date: {new Date(application.move_in_date).toLocaleDateString()}
            </p>
          </div>
          <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
            <p>
              Employment: {application.employment_status}
            </p>
          </div>
        </div>
      </div>
    </li>
  );
};

export default Applications;