import React from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { SecurityDeposit } from '../../types/securityDeposit';

interface SecurityDepositDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  deposit: SecurityDeposit | null;
}

const SecurityDepositDetailsModal: React.FC<SecurityDepositDetailsModalProps> = ({
  isOpen,
  onClose,
  deposit
}) => {
  if (!deposit) return null;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      'held': { color: 'bg-green-100 text-green-800', label: 'Held' },
      'partial_refunded': { color: 'bg-yellow-100 text-yellow-800', label: 'Partially Refunded' },
      'refunded': { color: 'bg-blue-100 text-blue-800', label: 'Refunded' },
      'disputed': { color: 'bg-red-100 text-red-800', label: 'Disputed' },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || 
                   { color: 'bg-gray-100 text-gray-800', label: status };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  return (
    <Transition appear show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-10" onClose={onClose}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex justify-between items-start mb-6">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    Security Deposit Details
                  </Dialog.Title>
                  <button
                    onClick={onClose}
                    className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none"
                  >
                    <XMarkIcon className="h-6 w-6" />
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* Left Column - Basic Info */}
                  <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Basic Information</h4>
                      <dl className="space-y-2">
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Deposit ID:</dt>
                          <dd className="text-sm font-medium text-gray-900">#{deposit.id}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Status:</dt>
                          <dd>{getStatusBadge(deposit.status)}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Amount:</dt>
                          <dd className="text-sm font-medium text-gray-900">{formatCurrency(deposit.amount)}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Date Received:</dt>
                          <dd className="text-sm text-gray-900">{formatDate(deposit.dateReceived)}</dd>
                        </div>
                      </dl>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Property & Tenant</h4>
                      <dl className="space-y-2">
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Tenant:</dt>
                          <dd className="text-sm font-medium text-gray-900">{deposit.tenant_name || 'Unknown'}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Property:</dt>
                          <dd className="text-sm text-gray-900">{deposit.property_address || 'Unknown'}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Lease Start:</dt>
                          <dd className="text-sm text-gray-900">
                            {deposit.lease_start_date ? formatDate(deposit.lease_start_date) : 'Unknown'}
                          </dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Lease End:</dt>
                          <dd className="text-sm text-gray-900">
                            {deposit.lease_end_date ? formatDate(deposit.lease_end_date) : 'Unknown'}
                          </dd>
                        </div>
                      </dl>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Payment Details</h4>
                      <dl className="space-y-2">
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Payment Method:</dt>
                          <dd className="text-sm text-gray-900 capitalize">
                            {deposit.paymentMethod?.replace('_', ' ') || 'Unknown'}
                          </dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Bank Account:</dt>
                          <dd className="text-sm text-gray-900">{deposit.bankAccount || 'Unknown'}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Reference #:</dt>
                          <dd className="text-sm text-gray-900">{deposit.referenceNumber || 'None'}</dd>
                        </div>
                        {deposit.interestRate && (
                          <div className="flex justify-between">
                            <dt className="text-sm text-gray-500">Interest Rate:</dt>
                            <dd className="text-sm text-gray-900">{deposit.interestRate}%</dd>
                          </div>
                        )}
                        {deposit.interestAccrued && (
                          <div className="flex justify-between">
                            <dt className="text-sm text-gray-500">Interest Accrued:</dt>
                            <dd className="text-sm text-gray-900">{formatCurrency(deposit.interestAccrued)}</dd>
                          </div>
                        )}
                      </dl>
                    </div>
                  </div>

                  {/* Right Column - Deductions & Summary */}
                  <div className="space-y-6">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Financial Summary</h4>
                      <dl className="space-y-2">
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Original Amount:</dt>
                          <dd className="text-sm font-medium text-gray-900">{formatCurrency(deposit.amount)}</dd>
                        </div>
                        <div className="flex justify-between">
                          <dt className="text-sm text-gray-500">Total Deductions:</dt>
                          <dd className="text-sm text-red-600">
                            -{formatCurrency(deposit.totalDeductions || 0)}
                          </dd>
                        </div>
                        {deposit.interestAccrued && (
                          <div className="flex justify-between">
                            <dt className="text-sm text-gray-500">Interest Added:</dt>
                            <dd className="text-sm text-green-600">+{formatCurrency(deposit.interestAccrued)}</dd>
                          </div>
                        )}
                        <div className="border-t pt-2 mt-2">
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-900">Refund Amount:</dt>
                            <dd className="text-sm font-bold text-gray-900">
                              {formatCurrency(deposit.refundAmount || deposit.amount)}
                            </dd>
                          </div>
                        </div>
                      </dl>
                    </div>

                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-900 mb-3">
                        Deductions ({(deposit.deductions || []).length})
                      </h4>
                      {deposit.deductions && deposit.deductions.length > 0 ? (
                        <div className="space-y-3 max-h-60 overflow-y-auto">
                          {deposit.deductions.map((deduction, index) => (
                            <div key={index} className="bg-white p-3 rounded border">
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900">
                                    {deduction.description}
                                  </p>
                                  <p className="text-xs text-gray-500 capitalize">
                                    {deduction.category} • {formatDate(deduction.date)}
                                  </p>
                                </div>
                                <span className="text-sm font-medium text-red-600">
                                  -{formatCurrency(deduction.amount)}
                                </span>
                              </div>
                              {deduction.notes && (
                                <p className="text-xs text-gray-600 mt-1">{deduction.notes}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500">No deductions recorded</p>
                      )}
                    </div>

                    {deposit.notes && (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Notes</h4>
                        <p className="text-sm text-gray-600">{deposit.notes}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="button"
                    onClick={onClose}
                    className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default SecurityDepositDetailsModal;