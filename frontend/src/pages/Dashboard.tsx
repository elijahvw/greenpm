import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { DashboardService } from '../services/api';
import { 
  BuildingOfficeIcon, 
  DocumentTextIcon, 
  ClipboardDocumentListIcon,
  WrenchScrewdriverIcon,
  CreditCardIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const data = await DashboardService.getDashboardStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

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
          <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
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
      {/* Welcome Section */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's what's happening with your {user?.role === 'tenant' ? 'rental' : 'properties'} today.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {user?.role === 'landlord' && (
          <>
            <StatCard
              title="Total Properties"
              value={stats?.total_properties || 0}
              icon={BuildingOfficeIcon}
              color="bg-blue-500"
            />
            <StatCard
              title="Active Leases"
              value={stats?.active_leases || 0}
              icon={ClipboardDocumentListIcon}
              color="bg-green-500"
            />
            <StatCard
              title="Pending Applications"
              value={stats?.pending_applications || 0}
              icon={DocumentTextIcon}
              color="bg-yellow-500"
            />
            <StatCard
              title="Open Maintenance"
              value={stats?.open_maintenance || 0}
              icon={WrenchScrewdriverIcon}
              color="bg-red-500"
            />
          </>
        )}
        
        {user?.role === 'tenant' && (
          <>
            <StatCard
              title="Active Applications"
              value={stats?.active_applications || 0}
              icon={DocumentTextIcon}
              color="bg-blue-500"
            />
            <StatCard
              title="Current Lease"
              value={stats?.current_lease ? 1 : 0}
              icon={ClipboardDocumentListIcon}
              color="bg-green-500"
            />
            <StatCard
              title="Maintenance Requests"
              value={stats?.maintenance_requests || 0}
              icon={WrenchScrewdriverIcon}
              color="bg-yellow-500"
            />
            <StatCard
              title="Pending Payments"
              value={stats?.pending_payments || 0}
              icon={CreditCardIcon}
              color="bg-red-500"
            />
          </>
        )}
        
        {user?.role === 'admin' && (
          <>
            <StatCard
              title="Total Users"
              value={stats?.total_users || 0}
              icon={BuildingOfficeIcon}
              color="bg-blue-500"
            />
            <StatCard
              title="Total Properties"
              value={stats?.total_properties || 0}
              icon={BuildingOfficeIcon}
              color="bg-green-500"
            />
            <StatCard
              title="Active Leases"
              value={stats?.active_leases || 0}
              icon={ClipboardDocumentListIcon}
              color="bg-yellow-500"
            />
            <StatCard
              title="Open Maintenance"
              value={stats?.open_maintenance || 0}
              icon={WrenchScrewdriverIcon}
              color="bg-red-500"
            />
          </>
        )}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentActivity activities={stats?.recent_activities || []} />
        <QuickActions userRole={user?.role} />
      </div>
    </div>
  );
};

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}> = ({ title, value, icon: Icon, color }) => {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`${color} rounded-md p-3`}>
              <Icon className="h-6 w-6 text-white" />
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-medium text-gray-900">{value}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

const RecentActivity: React.FC<{ activities: any[] }> = ({ activities }) => {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Recent Activity</h3>
        <div className="mt-5">
          {activities.length === 0 ? (
            <p className="text-sm text-gray-500">No recent activity</p>
          ) : (
            <div className="flow-root">
              <ul className="-mb-8">
                {activities.map((activity, index) => (
                  <li key={index}>
                    <div className="relative pb-8">
                      {index !== activities.length - 1 && (
                        <span className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200" />
                      )}
                      <div className="relative flex space-x-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-500">
                          <span className="text-xs font-medium text-white">
                            {activity.type?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-500">{activity.description}</p>
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            {new Date(activity.created_at).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const QuickActions: React.FC<{ userRole?: string }> = ({ userRole }) => {
  const actions = getQuickActions(userRole);

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Quick Actions</h3>
        <div className="mt-5 grid grid-cols-1 gap-3">
          {actions.map((action, index) => (
            <button
              key={index}
              onClick={action.onClick}
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <action.icon className="h-4 w-4 mr-2" />
              {action.title}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

function getQuickActions(userRole?: string) {
  const baseActions = [
    {
      title: 'View Messages',
      icon: DocumentTextIcon,
      onClick: () => window.location.href = '/messages'
    }
  ];

  switch (userRole) {
    case 'tenant':
      return [
        {
          title: 'Submit Maintenance Request',
          icon: WrenchScrewdriverIcon,
          onClick: () => window.location.href = '/maintenance/new'
        },
        {
          title: 'View Lease',
          icon: ClipboardDocumentListIcon,
          onClick: () => window.location.href = '/leases'
        },
        ...baseActions
      ];
    
    case 'landlord':
      return [
        {
          title: 'Add Property',
          icon: BuildingOfficeIcon,
          onClick: () => window.location.href = '/properties/new'
        },
        {
          title: 'View Applications',
          icon: DocumentTextIcon,
          onClick: () => window.location.href = '/applications'
        },
        ...baseActions
      ];
    
    default:
      return baseActions;
  }
}

export default Dashboard;