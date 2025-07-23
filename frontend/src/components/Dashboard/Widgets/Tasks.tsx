import React, { useState } from 'react';
import { CheckCircleIcon, ClockIcon } from '@heroicons/react/24/outline';

interface Task {
  id: string;
  title: string;
  property: string;
  priority: 'high' | 'medium' | 'low';
  type: 'maintenance' | 'inspection' | 'tenant_issue';
  createdAt: string;
  assignedTo?: string;
}

const mockIncomingTasks: Task[] = [
  {
    id: '1',
    title: 'Leaky faucet in kitchen',
    property: 'Sunset Apartments Unit 2A',
    priority: 'high',
    type: 'maintenance',
    createdAt: '2024-01-15',
  },
  {
    id: '2',
    title: 'Annual inspection due',
    property: 'Oak Street House',
    priority: 'medium',
    type: 'inspection',
    createdAt: '2024-01-14',
  },
  {
    id: '3',
    title: 'Noise complaint from neighbor',
    property: 'Downtown Loft 5B',
    priority: 'medium',
    type: 'tenant_issue',
    createdAt: '2024-01-13',
  },
];

const mockAssignedTasks: Task[] = [
  {
    id: '4',
    title: 'HVAC maintenance check',
    property: 'Sunset Apartments Unit 2A',
    priority: 'low',
    type: 'maintenance',
    createdAt: '2024-01-12',
    assignedTo: 'John Maintenance',
  },
  {
    id: '5',
    title: 'Carpet cleaning after move-out',
    property: 'Oak Street House',
    priority: 'medium',
    type: 'maintenance',
    createdAt: '2024-01-11',
    assignedTo: 'Clean Pro Services',
  },
];

const Tasks: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'incoming' | 'assigned'>('incoming');

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'maintenance':
        return '🔧';
      case 'inspection':
        return '🔍';
      case 'tenant_issue':
        return '👥';
      default:
        return '📋';
    }
  };

  const currentTasks = activeTab === 'incoming' ? mockIncomingTasks : mockAssignedTasks;

  return (
    <div className="bg-white overflow-hidden shadow-sm rounded-lg">
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="flex-shrink-0">
            <CheckCircleIcon className="h-8 w-8 text-blue-500" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-gray-900">Tasks</h3>
            <p className="text-sm text-gray-500">
              {mockIncomingTasks.length} incoming, {mockAssignedTasks.length} assigned
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200 mb-4">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('incoming')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'incoming'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Incoming Requests ({mockIncomingTasks.length})
            </button>
            <button
              onClick={() => setActiveTab('assigned')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'assigned'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Assigned to Me ({mockAssignedTasks.length})
            </button>
          </nav>
        </div>

        {/* Task List */}
        <div className="space-y-3">
          {currentTasks.map((task) => (
            <div key={task.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-lg">{getTypeIcon(task.type)}</span>
                    <h4 className="text-sm font-medium text-gray-900">{task.title}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">{task.property}</p>
                  {task.assignedTo && (
                    <p className="text-xs text-gray-500">Assigned to: {task.assignedTo}</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">{task.createdAt}</p>
                  <button className="mt-2 text-xs text-blue-600 hover:text-blue-800">
                    View Details
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4">
          <button className="w-full bg-blue-50 text-blue-700 hover:bg-blue-100 px-4 py-2 rounded-md text-sm font-medium transition-colors">
            View All Tasks
          </button>
        </div>
      </div>
    </div>
  );
};

export default Tasks;