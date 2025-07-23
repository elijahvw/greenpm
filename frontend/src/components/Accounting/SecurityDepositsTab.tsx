import React, { useState, useEffect } from 'react';
import { SecurityDeposit, AddDeductionRequest, ProcessRefundRequest } from '../../types/securityDeposit';
import { securityDepositService } from '../../services/securityDepositService';
import AddDeductionModal from './AddDeductionModal';
import ProcessRefundModal from './ProcessRefundModal';
import SecurityDepositDetailsModal from './SecurityDepositDetailsModal';
import { 
  CurrencyDollarIcon, 
  PlusIcon, 
  BanknotesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SecurityDepositsTab: React.FC = () => {
  const [deposits, setDeposits] = useState<SecurityDeposit[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  
  // Modal states
  const [isAddDeductionModalOpen, setIsAddDeductionModalOpen] = useState(false);
  const [isProcessRefundModalOpen, setIsProcessRefundModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedDeposit, setSelectedDeposit] = useState<SecurityDeposit | null>(null);

  useEffect(() => {
    fetchDeposits();
  }, [selectedStatus]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchDeposits = async () => {
    try {
      setLoading(true);
      const data = await securityDepositService.getSecurityDeposits();
      let filteredDeposits = data;
      
      if (selectedStatus !== 'all') {
        filteredDeposits = data.filter(deposit => deposit.status === selectedStatus);
      }
      
      setDeposits(filteredDeposits);
    } catch (error) {
      console.error('Failed to fetch security deposits:', error);
      toast.error('Failed to load security deposits');
    } finally {
      setLoading(false);
    }
  };

  const handleAddDeduction = (depositId: string) => {
    const deposit = deposits.find(d => d.id === depositId);
    if (deposit) {
      setSelectedDeposit(deposit);
      setIsAddDeductionModalOpen(true);
    }
  };

  const handleProcessRefund = (depositId: string) => {
    const deposit = deposits.find(d => d.id === depositId);
    if (deposit) {
      setSelectedDeposit(deposit);
      setIsProcessRefundModalOpen(true);
    }
  };

  const handleDeductionSubmit = async (depositId: string, data: AddDeductionRequest) => {
    try {
      await securityDepositService.addDeduction(depositId, data);
      await fetchDeposits(); // Refresh data
      setIsAddDeductionModalOpen(false);
      setSelectedDeposit(null);
    } catch (error) {
      throw error; // Let modal handle the error
    }
  };

  const handleRefundSubmit = async (depositId: string, data: ProcessRefundRequest) => {
    try {
      await securityDepositService.processRefund(depositId, data);
      await fetchDeposits(); // Refresh data
      setIsProcessRefundModalOpen(false);
      setSelectedDeposit(null);
    } catch (error) {
      throw error; // Let modal handle the error
    }
  };

  const getStatusBadge = (status: SecurityDeposit['status']) => {
    const statusConfig = {
      unpaid: { color: 'bg-red-100 text-red-800', icon: ExclamationTriangleIcon, label: 'Unpaid' },
      held: { color: 'bg-blue-100 text-blue-800', icon: ClockIcon, label: 'Held' },
      partial_refunded: { color: 'bg-yellow-100 text-yellow-800', icon: ExclamationTriangleIcon, label: 'Partial Refunded' },
      refunded: { color: 'bg-green-100 text-green-800', icon: CheckCircleIcon, label: 'Refunded' }
    };

    const config = statusConfig[status] || statusConfig.held;
    const IconComponent = config.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <IconComponent className="w-3 h-3 mr-1" />
        {config.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Calculate summary stats
  const totalDeposits = deposits.reduce((sum, deposit) => sum + deposit.amount, 0);
  const heldDeposits = deposits.filter(d => d.status === 'held');
  const refundedDeposits = deposits.filter(d => d.status === 'refunded' || d.status === 'partial_refunded');
  const totalHeld = heldDeposits.reduce((sum, deposit) => sum + deposit.amount, 0);
  const totalRefunded = refundedDeposits.reduce((sum, deposit) => {
    return sum + (deposit.refundAmount || 0);
  }, 0);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <BanknotesIcon className="h-5 w-5 text-blue-600" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Deposits
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(totalDeposits)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                  <ClockIcon className="h-5 w-5 text-yellow-600" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Currently Held
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(totalHeld)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Refunded
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {formatCurrency(totalRefunded)}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center">
                  <CurrencyDollarIcon className="h-5 w-5 text-indigo-600" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Deposits
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {heldDeposits.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="flex items-center space-x-4">
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-sm"
          >
            <option value="all">All Statuses</option>
            <option value="unpaid">Unpaid</option>
            <option value="held">Held</option>
            <option value="partial_refunded">Partial Refunded</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>
        
        <button
          onClick={() => toast('Create deposit functionality coming soon', { icon: '💡' })}
          className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Record Deposit
        </button>
      </div>

      {/* Deposits Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {deposits.length === 0 ? (
          <div className="text-center py-12">
            <BanknotesIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No security deposits</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by recording your first security deposit.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {deposits.map((deposit) => (
              <li key={deposit.id} className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                        <BanknotesIcon className="h-6 w-6 text-gray-600" />
                      </div>
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <p className="text-sm font-medium text-gray-900">
                          {deposit.property_address || 'Unknown Property'}
                        </p>
                        {getStatusBadge(deposit.status)}
                      </div>
                      <p className="text-sm text-gray-500">
                        Tenant: {deposit.tenant_name || 'Unknown'}
                      </p>
                      <p className="text-xs text-gray-400">
                        Received: {formatDate(deposit.dateReceived)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">
                        {formatCurrency(deposit.amount)}
                      </p>
                      {deposit.refundAmount && (
                        <p className="text-sm text-green-600">
                          Refunded: {formatCurrency(deposit.refundAmount)}
                        </p>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {deposit.status === 'held' && (
                        <>
                          <button
                            onClick={() => handleAddDeduction(deposit.id)}
                            className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                          >
                            Add Deduction
                          </button>
                          <button
                            onClick={() => handleProcessRefund(deposit.id)}
                            className="inline-flex items-center px-2.5 py-1.5 border border-transparent shadow-sm text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            Process Refund
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => {
                          setSelectedDeposit(deposit);
                          setIsDetailsModalOpen(true);
                        }}
                        className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Modals */}
      {selectedDeposit && (
        <>
          <AddDeductionModal
            isOpen={isAddDeductionModalOpen}
            onClose={() => {
              setIsAddDeductionModalOpen(false);
              setSelectedDeposit(null);
            }}
            depositId={selectedDeposit.id}
            depositAmount={selectedDeposit.amount}
            currentDeductions={selectedDeposit.totalDeductions || 0}
            onSubmit={handleDeductionSubmit}
          />

          <ProcessRefundModal
            isOpen={isProcessRefundModalOpen}
            onClose={() => {
              setIsProcessRefundModalOpen(false);
              setSelectedDeposit(null);
            }}
            depositId={selectedDeposit.id}
            depositAmount={selectedDeposit.amount}
            totalDeductions={selectedDeposit.totalDeductions || 0}
            tenantName={selectedDeposit.tenant_name || 'Unknown Tenant'}
            propertyAddress={selectedDeposit.property_address || 'Unknown Property'}
            onSubmit={handleRefundSubmit}
          />
        </>
      )}

      {/* Security Deposit Details Modal */}
      <SecurityDepositDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedDeposit(null);
        }}
        deposit={selectedDeposit}
      />
    </div>
  );
};

export default SecurityDepositsTab;