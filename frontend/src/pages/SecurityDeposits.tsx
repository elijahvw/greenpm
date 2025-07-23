import React, { useState, useEffect } from 'react';
import { SecurityDeposit } from '../types/securityDeposit';
import { securityDepositService } from '../services/securityDepositService';
import { 
  CurrencyDollarIcon, 
  MagnifyingGlassIcon, 
  PlusIcon,
  BanknotesIcon,
  DocumentTextIcon,
  CalendarIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SecurityDeposits: React.FC = () => {
  const [deposits, setDeposits] = useState<SecurityDeposit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    fetchSecurityDeposits();
  }, []);

  const fetchSecurityDeposits = async () => {
    try {
      setLoading(true);
      console.log('💰 SecurityDeposits - Fetching deposits...');
      const data = await securityDepositService.getSecurityDeposits();
      console.log('💰 SecurityDeposits - Fetched data:', data);
      setDeposits(data);
    } catch (error) {
      console.error('❌ SecurityDeposits - Error fetching deposits:', error);
      toast.error('Failed to load security deposits');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'unpaid': return 'bg-red-100 text-red-800';
      case 'held': return 'bg-blue-100 text-blue-800';
      case 'partial_refunded': return 'bg-yellow-100 text-yellow-800';
      case 'refunded': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'unpaid': return 'Unpaid';
      case 'held': return 'Held';
      case 'partial_refunded': return 'Partial Refunded';
      case 'refunded': return 'Refunded';
      default: return 'Unknown';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Filter deposits based on search and status
  const filteredDeposits = deposits.filter(deposit => {
    const tenantName = deposit.tenant_name || '';
    const propertyAddress = deposit.property_address || '';
    const referenceNumber = deposit.referenceNumber || '';
    
    const matchesSearch = 
      tenantName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      propertyAddress.toLowerCase().includes(searchTerm.toLowerCase()) ||
      referenceNumber.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || deposit.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  // Calculate summary statistics
  const summary = {
    totalDeposits: deposits.length,
    totalAmount: deposits.reduce((sum, d) => sum + d.amount, 0),
    totalInterest: deposits.reduce((sum, d) => sum + (d.interestAccrued || 0), 0),
    totalDeductions: deposits.reduce((sum, d) => sum + (d.deductions?.reduce((deductionSum, deduction) => deductionSum + (deduction.amount || 0), 0) || 0), 0),
    byStatus: {
      unpaid: deposits.filter(d => d.status === 'unpaid').length,
      held: deposits.filter(d => d.status === 'held').length,
      partial_refunded: deposits.filter(d => d.status === 'partial_refunded').length,
      refunded: deposits.filter(d => d.status === 'refunded').length,
    }
  };

  const handleAddDeduction = (depositId: string) => {
    // TODO: Implement add deduction modal
    toast('Add deduction functionality coming soon', { icon: '💡' });
  };

  const handleProcessRefund = (depositId: string) => {
    // TODO: Implement process refund modal
    toast('Process refund functionality coming soon', { icon: '💡' });
  };

  const handleViewDetails = (deposit: SecurityDeposit) => {
    // For now, show deposit details in a modal/alert
    const details = `
Security Deposit Details:
━━━━━━━━━━━━━━━━━━━━━━━━
👤 Tenant: ${deposit.tenant_name || 'Unknown'}
🏠 Property: ${deposit.property_address || 'No address'}
💰 Amount: $${deposit.amount.toLocaleString()}
📅 Date Received: ${formatDate(deposit.dateReceived)}
📋 Status: ${getStatusLabel(deposit.status)}
🔢 Reference: ${deposit.referenceNumber || 'N/A'}

${deposit.interestAccrued && deposit.interestAccrued > 0 ? `💰 Interest Accrued: $${deposit.interestAccrued.toFixed(2)}` : ''}

${deposit.deductions && deposit.deductions.length > 0 ? 
  `\n📉 Deductions:\n${deposit.deductions.map(d => `  • ${d.description}: -$${d.amount}`).join('\n')}` : 
  'No deductions recorded'}
    `;
    
    alert(details);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Security Deposits</h1>
            <p className="text-gray-600">
              Track and manage security deposits for all your properties
            </p>
          </div>
          <button
            onClick={() => toast('Create deposit functionality coming soon', { icon: '💡' })}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Record Deposit
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BanknotesIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Deposits</dt>
                  <dd className="text-lg font-medium text-gray-900">{summary.totalDeposits}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-green-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Amount</dt>
                  <dd className="text-lg font-medium text-gray-900">{formatCurrency(summary.totalAmount)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-blue-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Interest Accrued</dt>
                  <dd className="text-lg font-medium text-gray-900">{formatCurrency(summary.totalInterest)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CurrencyDollarIcon className="h-6 w-6 text-red-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Deductions</dt>
                  <dd className="text-lg font-medium text-gray-900">{formatCurrency(summary.totalDeductions)}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white shadow rounded-lg p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search Deposits
            </label>
            <div className="mt-1 relative">
              <MagnifyingGlassIcon className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                id="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by tenant, property, or reference..."
                className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700">
              Status
            </label>
            <select
              id="status"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="all">All Statuses</option>
              <option value="unpaid">Unpaid</option>
              <option value="held">Held</option>
              <option value="partial_refunded">Partial Refunded</option>
              <option value="refunded">Refunded</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={fetchSecurityDeposits}
              className="w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Deposits Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Security Deposits ({filteredDeposits.length})
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Manage security deposits and track refunds
          </p>
        </div>

        {filteredDeposits.length === 0 ? (
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No security deposits found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {deposits.length === 0
                ? "Get started by recording your first security deposit."
                : "Try adjusting your search or filter criteria."
              }
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {filteredDeposits.map((deposit) => (
              <li key={deposit.id}>
                <div className="px-4 py-4 sm:px-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <BanknotesIcon className="h-6 w-6 text-gray-400" />
                      </div>
                      <div className="ml-4 min-w-0 flex-1">
                        <div className="flex items-center">
                          <p className="text-sm font-medium text-indigo-600 truncate">
                            {deposit.tenant_name || 'Unknown Tenant'}
                          </p>
                          <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(deposit.status)}`}>
                            {getStatusLabel(deposit.status)}
                          </span>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500">
                          <p className="truncate">
                            {deposit.property_address || 'Property address not available'}
                          </p>
                        </div>
                        <div className="mt-2 flex items-center text-sm text-gray-500 space-x-4">
                          <div className="flex items-center">
                            <CurrencyDollarIcon className="flex-shrink-0 mr-1.5 h-4 w-4 text-green-400" />
                            <span>Amount: {formatCurrency(deposit.amount)}</span>
                          </div>
                          <div className="flex items-center">
                            <CalendarIcon className="flex-shrink-0 mr-1.5 h-4 w-4 text-gray-400" />
                            <span>Received: {formatDate(deposit.dateReceived)}</span>
                          </div>
                          {deposit.interestAccrued && deposit.interestAccrued > 0 && (
                            <div className="flex items-center">
                              <span>Interest: {formatCurrency(deposit.interestAccrued)}</span>
                            </div>
                          )}
                        </div>
                        {deposit.referenceNumber && (
                          <div className="mt-1 text-xs text-gray-400">
                            Ref: {deposit.referenceNumber}
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex space-x-2">
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
                            className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          >
                            Process Refund
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleViewDetails(deposit)}
                        className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        View Details
                      </button>
                    </div>
                  </div>

                  {/* Deductions Summary */}
                  {deposit.deductions && deposit.deductions.length > 0 && (
                    <div className="mt-4 ml-10">
                      <div className="text-xs text-gray-500 mb-2">Deductions:</div>
                      <div className="space-y-1">
                        {deposit.deductions.slice(0, 3).map((deduction, index) => (
                          <div key={index} className="flex justify-between text-xs text-gray-600">
                            <span>{deduction.description}</span>
                            <span className="text-red-600">-{formatCurrency(deduction.amount)}</span>
                          </div>
                        ))}
                        {deposit.deductions.length > 3 && (
                          <div className="text-xs text-gray-400">
                            ... and {deposit.deductions.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default SecurityDeposits;