import React, { useState, useEffect } from 'react';
import { Dialog } from '@headlessui/react';
import { useForm } from 'react-hook-form';
import { XMarkIcon, PencilIcon } from '@heroicons/react/24/outline';
import { Lease, UpdateLeaseRequest } from '../../types/lease';
import { roundToCents } from '../../utils/currency';

interface LeaseEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  lease: Lease;
  onSubmit: (data: UpdateLeaseRequest) => Promise<void>;
}

interface LeaseEditForm {
  monthlyRent: number;
  securityDeposit: number;
  lateFeePenalty: number;
  gracePeriodDays: number;
  startDate: string;
  endDate: string;
  leaseType: 'fixed' | 'month-to-month' | 'yearly';
  status: 'active' | 'expired' | 'terminated' | 'pending' | 'draft';
  notes: string;
  specialTerms: string;
}

const LeaseEditModal: React.FC<LeaseEditModalProps> = ({
  isOpen,
  onClose,
  lease,
  onSubmit
}) => {
  const [loading, setLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm<LeaseEditForm>();

  useEffect(() => {
    if (isOpen && lease) {
      // Pre-populate form with current lease data
      reset({
        monthlyRent: lease.rent_amount || lease.monthlyRent || 0,
        securityDeposit: lease.security_deposit || lease.securityDeposit || 0,
        lateFeePenalty: lease.late_fee_penalty || lease.lateFeePenalty || 0,
        gracePeriodDays: lease.grace_period_days || lease.gracePeriodDays || 5,
        startDate: (lease.start_date || lease.startDate || '').split('T')[0],
        endDate: (lease.end_date || lease.endDate || '').split('T')[0],
        leaseType: (lease.lease_type || lease.leaseType || 'fixed') as 'fixed' | 'month-to-month' | 'yearly',
        status: (lease.status?.toLowerCase() || 'active') as 'active' | 'expired' | 'terminated' | 'pending' | 'draft',
        notes: lease.notes || '',
        specialTerms: lease.special_terms || lease.specialTerms || '',
      });
    }
  }, [isOpen, lease, reset]);

  const handleFormSubmit = async (data: LeaseEditForm) => {
    try {
      setLoading(true);
      
      console.log('📝 LeaseEditModal - Form data:', data);
      console.log('📝 LeaseEditModal - Original lease:', lease);
      
      const updateData: UpdateLeaseRequest = {
        id: lease.id,
        monthlyRent: roundToCents(data.monthlyRent || 0),
        securityDeposit: roundToCents(data.securityDeposit || 0),
        lateFeePenalty: roundToCents(data.lateFeePenalty || 0),
        gracePeriodDays: data.gracePeriodDays,
        startDate: data.startDate,
        endDate: data.endDate,
        leaseType: data.leaseType,
        status: data.status,
        notes: data.notes,
        specialTerms: data.specialTerms,
      };

      console.log('📝 LeaseEditModal - Update data being sent:', updateData);

      await onSubmit(updateData);
      onClose();
    } catch (error) {
      console.error('❌ Error updating lease:', error);
      // Don't close modal on error - let user try again
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div className="fixed inset-0 bg-black bg-opacity-25" />
      
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-center justify-center p-4 text-center">
          <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-lg bg-white p-6 text-left align-middle shadow-xl transition-all">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center">
                <PencilIcon className="h-6 w-6 text-blue-600 mr-3" />
                <div>
                  <Dialog.Title className="text-lg font-medium text-gray-900">
                    Edit Lease
                  </Dialog.Title>
                  <p className="text-sm text-gray-500">
                    Modify lease details for {lease.tenant_name || 'tenant'}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
              {/* Property and Tenant Info (Read-only) */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Lease Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-500">Property:</span>
                    <span className="ml-2 text-gray-900">{lease.property_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-500">Tenant:</span>
                    <span className="ml-2 text-gray-900">{lease.tenant_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-500">Email:</span>
                    <span className="ml-2 text-gray-900">{lease.tenant_email || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="font-medium text-gray-500">Phone:</span>
                    <span className="ml-2 text-gray-900">{lease.tenant_phone || 'N/A'}</span>
                  </div>
                </div>
              </div>

              {/* Financial Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monthly Rent *
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      {...register('monthlyRent', { 
                        required: 'Monthly rent is required',
                        min: { value: 0, message: 'Rent must be positive' },
                        valueAsNumber: true,
                        setValueAs: (value) => {
                          // Round to nearest cent to avoid floating point issues
                          const num = parseFloat(value);
                          return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                        }
                      })}
                      className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                  {errors.monthlyRent && (
                    <p className="mt-1 text-xs text-red-600">{errors.monthlyRent.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Security Deposit
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      {...register('securityDeposit', {
                        min: { value: 0, message: 'Deposit must be positive' },
                        valueAsNumber: true,
                        setValueAs: (value) => {
                          const num = parseFloat(value);
                          return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                        }
                      })}
                      className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                  {errors.securityDeposit && (
                    <p className="mt-1 text-xs text-red-600">{errors.securityDeposit.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Late Fee Penalty
                  </label>
                  <div className="relative">
                    <span className="absolute left-3 top-2 text-gray-500">$</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      {...register('lateFeePenalty', {
                        min: { value: 0, message: 'Late fee must be positive' },
                        valueAsNumber: true,
                        setValueAs: (value) => {
                          const num = parseFloat(value);
                          return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                        }
                      })}
                      className="pl-8 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    />
                  </div>
                  {errors.lateFeePenalty && (
                    <p className="mt-1 text-xs text-red-600">{errors.lateFeePenalty.message}</p>
                  )}
                </div>
              </div>

              {/* Dates and Terms */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date *
                  </label>
                  <input
                    type="date"
                    {...register('startDate', { required: 'Start date is required' })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  {errors.startDate && (
                    <p className="mt-1 text-xs text-red-600">{errors.startDate.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    End Date *
                  </label>
                  <input
                    type="date"
                    {...register('endDate', { required: 'End date is required' })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  {errors.endDate && (
                    <p className="mt-1 text-xs text-red-600">{errors.endDate.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Lease Type
                  </label>
                  <select
                    {...register('leaseType')}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="fixed">Fixed Term</option>
                    <option value="month-to-month">Month-to-Month</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    {...register('status')}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    <option value="draft">Draft</option>
                    <option value="pending">Pending</option>
                    <option value="active">Active</option>
                    <option value="expired">Expired</option>
                    <option value="terminated">Terminated</option>
                  </select>
                </div>
              </div>

              {/* Grace Period */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Grace Period (Days)
                  </label>
                  <input
                    type="number"
                    {...register('gracePeriodDays', {
                      min: { value: 0, message: 'Grace period must be positive' }
                    })}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  />
                  {errors.gracePeriodDays && (
                    <p className="mt-1 text-xs text-red-600">{errors.gracePeriodDays.message}</p>
                  )}
                </div>
              </div>

              {/* Notes and Special Terms */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Special Terms
                  </label>
                  <textarea
                    {...register('specialTerms')}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Any special terms or conditions..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Notes
                  </label>
                  <textarea
                    {...register('notes')}
                    rows={3}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    placeholder="Internal notes about this lease..."
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {loading && (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  )}
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </Dialog.Panel>
        </div>
      </div>
    </Dialog>
  );
};

export default LeaseEditModal;