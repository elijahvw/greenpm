import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  BuildingOfficeIcon, 
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  WrenchScrewdriverIcon,
  CreditCardIcon,
  ChatBubbleLeftRightIcon,
  Cog6ToothIcon,
  UserGroupIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  userRole: string;
}

const Sidebar: React.FC<SidebarProps> = ({ sidebarOpen, setSidebarOpen, userRole }) => {
  const location = useLocation();

  const navigation = getNavigationItems(userRole);

  return (
    <>
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 flex z-40 lg:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <span className="sr-only">Close sidebar</span>
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <SidebarContent navigation={navigation} currentPath={location.pathname} />
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 pt-5 pb-4 overflow-y-auto">
          <SidebarContent navigation={navigation} currentPath={location.pathname} />
        </div>
      </div>
    </>
  );
};

const SidebarContent: React.FC<{ navigation: any[], currentPath: string }> = ({ navigation, currentPath }) => {
  return (
    <>
      {/* Logo */}
      <div className="flex items-center flex-shrink-0 px-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="h-8 w-8 bg-green-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">G</span>
            </div>
          </div>
          <div className="ml-3">
            <p className="text-xl font-semibold text-gray-900">Green PM</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-5 flex-1 px-2 space-y-1">
        {navigation.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className={`${
              currentPath === item.href
                ? 'bg-green-50 border-green-500 text-green-700'
                : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            } group flex items-center px-2 py-2 text-sm font-medium border-l-4 transition-colors duration-150 ease-in-out`}
          >
            <item.icon
              className={`${
                currentPath === item.href ? 'text-green-500' : 'text-gray-400 group-hover:text-gray-500'
              } mr-3 h-6 w-6`}
            />
            {item.name}
          </Link>
        ))}
      </nav>
    </>
  );
};

function getNavigationItems(userRole: string) {
  const baseItems = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  ];

  const tenantItems = [
    { name: 'My Applications', href: '/applications', icon: DocumentTextIcon },
    { name: 'My Lease', href: '/leases', icon: ClipboardDocumentListIcon },
    { name: 'Maintenance', href: '/maintenance', icon: WrenchScrewdriverIcon },
    { name: 'Payments', href: '/payments', icon: CreditCardIcon },
    { name: 'Messages', href: '/messages', icon: ChatBubbleLeftRightIcon },
  ];

  const landlordItems = [
    { name: 'Properties', href: '/properties', icon: BuildingOfficeIcon },
    { name: 'Applications', href: '/applications', icon: DocumentTextIcon },
    { name: 'Leases', href: '/leases', icon: ClipboardDocumentListIcon },
    { name: 'Maintenance', href: '/maintenance', icon: WrenchScrewdriverIcon },
    { name: 'Payments', href: '/payments', icon: CreditCardIcon },
    { name: 'Messages', href: '/messages', icon: ChatBubbleLeftRightIcon },
  ];

  const adminItems = [
    { name: 'Properties', href: '/properties', icon: BuildingOfficeIcon },
    { name: 'Users', href: '/users', icon: UserGroupIcon },
    { name: 'Applications', href: '/applications', icon: DocumentTextIcon },
    { name: 'Leases', href: '/leases', icon: ClipboardDocumentListIcon },
    { name: 'Maintenance', href: '/maintenance', icon: WrenchScrewdriverIcon },
    { name: 'Payments', href: '/payments', icon: CreditCardIcon },
    { name: 'Messages', href: '/messages', icon: ChatBubbleLeftRightIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  ];

  const commonItems = [
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  switch (userRole) {
    case 'tenant':
      return [...baseItems, ...tenantItems, ...commonItems];
    case 'landlord':
      return [...baseItems, ...landlordItems, ...commonItems];
    case 'admin':
      return [...baseItems, ...adminItems, ...commonItems];
    default:
      return [...baseItems, ...commonItems];
  }
}

export default Sidebar;