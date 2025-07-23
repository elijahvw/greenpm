import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  HomeIcon,
  BuildingOfficeIcon,
  DocumentTextIcon,
  UserGroupIcon,
  UsersIcon,
  CurrencyDollarIcon,
  WrenchScrewdriverIcon,
  CheckCircleIcon,
  ChatBubbleLeftRightIcon,
  FolderIcon,
  ChartBarIcon,
  PuzzlePieceIcon,
  Cog6ToothIcon,
  ClockIcon,
  UserIcon,
} from '@heroicons/react/24/outline';

const landlordNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'Rentals', href: '/dashboard/rentals', icon: BuildingOfficeIcon },
  { name: 'Tenants', href: '/dashboard/tenants', icon: UsersIcon },
  { name: 'Leasing', href: '/dashboard/leasing', icon: DocumentTextIcon },
  { name: 'Associations', href: '/dashboard/associations', icon: UserGroupIcon },
  { name: 'Accounting', href: '/dashboard/accounting', icon: CurrencyDollarIcon },
  { name: 'Maintenance', href: '/dashboard/maintenance', icon: WrenchScrewdriverIcon },
  { name: 'Tasks', href: '/dashboard/tasks', icon: CheckCircleIcon },
  { name: 'Communication', href: '/dashboard/communication', icon: ChatBubbleLeftRightIcon },
  { name: 'Files', href: '/dashboard/files', icon: FolderIcon },
  { name: 'Reports', href: '/dashboard/reports', icon: ChartBarIcon },
  { name: 'Analytics Hub', href: '/dashboard/analytics', icon: ChartBarIcon },
  { name: 'Add-on Services', href: '/dashboard/addons', icon: PuzzlePieceIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
];

const tenantNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'My Lease', href: '/dashboard/lease', icon: DocumentTextIcon },
  { name: 'Rent Payments', href: '/dashboard/payments', icon: CurrencyDollarIcon },
  { name: 'Payment History', href: '/dashboard/payment-history', icon: ClockIcon },
  { name: 'Maintenance Requests', href: '/dashboard/maintenance', icon: WrenchScrewdriverIcon },
  { name: 'Messages', href: '/dashboard/communication', icon: ChatBubbleLeftRightIcon },
  { name: 'Documents', href: '/dashboard/files', icon: FolderIcon },
  { name: 'Profile', href: '/dashboard/profile', icon: UserIcon },
  { name: 'Settings', href: '/dashboard/settings', icon: Cog6ToothIcon },
];

const Sidebar: React.FC = () => {
  const { user } = useAuth();
  
  // Determine navigation based on user role
  const navigation = user?.role === 'tenant' ? tenantNavigation : landlordNavigation;
  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:z-50 lg:flex lg:w-64 lg:flex-col">
      <div className="flex grow flex-col gap-y-5 overflow-y-auto bg-white px-6 pb-4 shadow-lg">
        <div className="flex h-16 shrink-0 items-center">
          <div className="flex items-center">
            <div className="h-8 w-8 bg-green-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">GP</span>
            </div>
            <span className="ml-2 text-xl font-bold text-gray-900">Green PM</span>
          </div>
        </div>
        <nav className="flex flex-1 flex-col">
          <ul role="list" className="flex flex-1 flex-col gap-y-7">
            <li>
              <ul role="list" className="-mx-2 space-y-1">
                {navigation.map((item) => (
                  <li key={item.name}>
                    <NavLink
                      to={item.href}
                      className={({ isActive }) =>
                        `group flex gap-x-3 rounded-md p-2 text-sm leading-6 font-semibold transition-colors ${
                          isActive
                            ? 'bg-green-50 text-green-700'
                            : 'text-gray-700 hover:text-green-700 hover:bg-green-50'
                        }`
                      }
                    >
                      <item.icon
                        className="h-6 w-6 shrink-0"
                        aria-hidden="true"
                      />
                      {item.name}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
};

export default Sidebar;