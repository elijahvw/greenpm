import React from 'react';
import { ExclamationTriangleIcon } from '@heroicons/react/24/outline';

interface OverdueTask {
  id: string;
  title: string;
  property: string;
  daysOverdue: number;
  priority: 'high' | 'medium' | 'low';
  assignedTo?: string;
}

const mockOverdueTasks: OverdueTask[] = [
  {
    id: '1',
    title: 'Broken AC unit repair',
    property: 'Sunset Apartments Unit 2A',
    daysOverdue: 7,
    priority: 'high',
    assignedTo: 'HVAC Pro Services',
  },
  {
    id: '2',
    title: 'Gutter cleaning',
    property: 'Oak Street House',
    daysOverdue: 3,
    priority: 'medium',
  },
  {
    id: '3',
    title: 'Light fixture replacement',
    property: 'Downtown Loft 5B',
    daysOverdue: 12,
    priority: 'low',
    assignedTo: 'Electric Solutions',
  },
  {
    id: '4',
    title: 'Tenant move-out inspection',
    property: 'Pine Valley Condo 3C',
    daysOverdue: 2,
    priority: 'high',
  },
];

const OverdueTasks: React.FC = () => {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'text-red-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-green-600';
      default:
        return 'text-gray-600';
    }
  };

  const getUrgencyLevel = (daysOverdue: number) => {
    if (daysOverdue >= 7) return 'Critical';
    if (daysOverdue >= 3) return 'Urgent';
    return 'Overdue';
  };

  const getUrgencyColor = (daysOverdue: number) => {
    if (daysOverdue >= 7) return 'bg-red-100 text-red-800';
    if (daysOverdue >= 3) return 'bg-orange-100 text-orange-800';
    return 'bg-yellow-100 text-yellow-800';
  };

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            <ExclamationTriangleIcon className="h-8 w-8 text-orange-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Overdue Tasks</h3>
            <p className="text-sm text-gray-500">
              {mockOverdueTasks.length} tasks need immediate attention
            </p>
          </div>
        </div>

        <div className="space-y-3">
          {mockOverdueTasks.map((task) => (
            <div key={task.id} className="border-l-4 border-orange-400 bg-orange-50 p-4 rounded-r-lg">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h4 className="text-sm font-medium text-gray-900">{task.title}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getUrgencyColor(task.daysOverdue)}`}>
                      {getUrgencyLevel(task.daysOverdue)}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{task.property}</p>
                  {task.assignedTo && (
                    <p className="text-xs text-gray-500">Assigned to: {task.assignedTo}</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-orange-600">
                    {task.daysOverdue} days overdue
                  </p>
                  <p className={`text-xs font-medium ${getPriorityColor(task.priority)}`}>
                    {task.priority.toUpperCase()} priority
                  </p>
                </div>
              </div>
              <div className="mt-3 flex space-x-2">
                <button className="text-xs bg-orange-600 text-white px-3 py-1 rounded-md hover:bg-orange-700 transition-colors">
                  Follow Up
                </button>
                <button className="text-xs bg-white text-orange-600 border border-orange-600 px-3 py-1 rounded-md hover:bg-orange-50 transition-colors">
                  Reassign
                </button>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4">
          <button className="w-full bg-orange-50 text-orange-700 hover:bg-orange-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            View All Overdue Tasks
          </button>
        </div>
      </div>
    </div>
  );
};

export default OverdueTasks;