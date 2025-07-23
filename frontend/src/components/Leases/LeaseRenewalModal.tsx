import React, { useState } from 'react';
import { Lease } from '../../types/lease';
import Modal from '../Common/Modal';
import { useForm } from 'react-hook-form';
import { CalendarIcon, CurrencyDollarIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface LeaseRenewalFormData {
  newStartDate: string;
  newEndDate: string;
  newMonthlyRent: number;
  newSecurityDeposit: number;
  renewalType: 'fixed' | 'month-to-month';
  rentIncrease: number;
  notes: string;
}

interface LeaseRenewalModalProps {
  isOpen: boolean;
  onClose: () => void;
  lease: Lease;
  onSubmit: (data: LeaseRenewalFormData) => void;
}

const LeaseRenewalModal: React.FC<LeaseRenewalModalProps> = ({
  isOpen,
  onClose,
  lease,
  onSubmit
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<LeaseRenewalFormData>();

  const currentRent = lease.monthlyRent || lease.rent_amount || 0;
  const currentDeposit = lease.securityDeposit || lease.security_deposit || 0;
  const watchedRentIncrease = watch('rentIncrease', 0);
  const watchedNewRent = watch('newMonthlyRent', currentRent);

  // Calculate suggested dates
  const currentEndDate = new Date(lease.endDate || lease.end_date || new Date());
  const suggestedStartDate = new Date(currentEndDate);
  suggestedStartDate.setDate(suggestedStartDate.getDate() + 1);
  const suggestedEndDate = new Date(suggestedStartDate);
  suggestedEndDate.setFullYear(suggestedEndDate.getFullYear() + 1);

  React.useEffect(() => {
    // Set default values
    setValue('newStartDate', suggestedStartDate.toISOString().split('T')[0]);
    setValue('newEndDate', suggestedEndDate.toISOString().split('T')[0]);
    setValue('newMonthlyRent', currentRent);
    setValue('newSecurityDeposit', currentDeposit);
    setValue('renewalType', 'fixed');
    setValue('rentIncrease', 0);
  }, [lease, setValue]);

  // Update rent when rent increase changes
  React.useEffect(() => {
    const rentIncreaseAmount = typeof watchedRentIncrease === 'number' ? watchedRentIncrease : parseFloat(watchedRentIncrease as string) || 0;
    const newRent = currentRent + rentIncreaseAmount;
    console.log('🏠 LeaseRenewal - Rent calculation:', {
      currentRent,
      rentIncreaseAmount,
      newRent,
      watchedRentIncrease,
      watchedRentIncreaseType: typeof watchedRentIncrease
    });
    setValue('newMonthlyRent', Math.round(newRent * 100) / 100); // Ensure proper currency precision
  }, [watchedRentIncrease, currentRent, setValue]);

  const onFormSubmit = async (data: LeaseRenewalFormData) => {
    try {
      setIsSubmitting(true);
      await onSubmit(data);
      toast.success('Lease renewal submitted successfully!');
      onClose();
    } catch (error) {
      toast.error('Failed to submit lease renewal');
    } finally {
      setIsSubmitting(false);
    }
  };

  const tenantName = lease.tenant_name || 'Unknown Tenant';
  const propertyName = lease.property_name || 'Unknown Property';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Renew Lease" maxWidth="2xl">
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Current Lease Info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Current Lease</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-500">Tenant:</span>
              <p className="text-gray-900">{tenantName}</p>
            </div>
            <div>
              <span className="font-medium text-gray-500">Property:</span>
              <p className="text-gray-900">{propertyName}</p>
            </div>
            <div>
              <span className="font-medium text-gray-500">Current Rent:</span>
              <p className="text-gray-900">${currentRent.toLocaleString()}/month</p>
            </div>
            <div>
              <span className="font-medium text-gray-500">Expires:</span>
              <p className="text-gray-900">
                {lease.endDate || lease.end_date ? 
                  new Date(lease.endDate || lease.end_date || '').toLocaleDateString() : 
                  'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Renewal Terms */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">New Lease Terms</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="newStartDate" className="block text-sm font-medium text-gray-700">
                New Start Date
              </label>
              <div className="mt-1 relative">
                <CalendarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="date"
                  id="newStartDate"
                  {...register('newStartDate', { required: 'Start date is required' })}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                />
              </div>
              {errors.newStartDate && (
                <p className="mt-1 text-sm text-red-600">{errors.newStartDate.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="newEndDate" className="block text-sm font-medium text-gray-700">
                New End Date
              </label>
              <div className="mt-1 relative">
                <CalendarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="date"
                  id="newEndDate"
                  {...register('newEndDate', { required: 'End date is required' })}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                />
              </div>
              {errors.newEndDate && (
                <p className="mt-1 text-sm text-red-600">{errors.newEndDate.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="renewalType" className="block text-sm font-medium text-gray-700">
              Renewal Type
            </label>
            <select
              id="renewalType"
              {...register('renewalType', { required: 'Renewal type is required' })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="fixed">Fixed Term</option>
              <option value="month-to-month">Month-to-Month</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="rentIncrease" className="block text-sm font-medium text-gray-700">
                Rent Increase ($)
              </label>
              <div className="mt-1 relative">
                <CurrencyDollarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="number"
                  id="rentIncrease"
                  step="1"
                  min="0"
                  placeholder="100"
                  {...register('rentIncrease', { 
                    min: { value: 0, message: 'Rent increase cannot be negative' },
                    valueAsNumber: true,
                    setValueAs: (value) => {
                      // Ensure we get a proper number, round to nearest cent
                      const num = parseFloat(value);
                      return isNaN(num) ? 0 : Math.round(num * 100) / 100;
                    }
                  })}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                />
              </div>
              {errors.rentIncrease && (
                <p className="mt-1 text-sm text-red-600">{errors.rentIncrease.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="newMonthlyRent" className="block text-sm font-medium text-gray-700">
                New Monthly Rent
              </label>
              <div className="mt-1 relative">
                <CurrencyDollarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                <input
                  type="number"
                  id="newMonthlyRent"
                  step="0.01"
                  {...register('newMonthlyRent', { 
                    required: 'Monthly rent is required',
                    min: { value: 1, message: 'Rent must be greater than 0' }
                  })}
                  className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 bg-gray-50"
                  readOnly
                />
              </div>
              {errors.newMonthlyRent && (
                <p className="mt-1 text-sm text-red-600">{errors.newMonthlyRent.message}</p>
              )}
            </div>
          </div>

          <div>
            <label htmlFor="newSecurityDeposit" className="block text-sm font-medium text-gray-700">
              Security Deposit
            </label>
            <div className="mt-1 relative">
              <CurrencyDollarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="number"
                id="newSecurityDeposit"
                step="0.01"
                {...register('newSecurityDeposit', { 
                  required: 'Security deposit is required',
                  min: { value: 0, message: 'Security deposit cannot be negative' }
                })}
                className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              />
            </div>
            {errors.newSecurityDeposit && (
              <p className="mt-1 text-sm text-red-600">{errors.newSecurityDeposit.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
              Renewal Notes
            </label>
            <textarea
              id="notes"
              rows={3}
              {...register('notes')}
              placeholder="Any additional terms or conditions for the renewal..."
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
          </div>
        </div>

        {/* Summary */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="text-md font-medium text-blue-900 mb-2">Renewal Summary</h4>
          <div className="text-sm text-blue-800 space-y-1">
            <p>Current rent: ${currentRent.toLocaleString()}/month</p>
            <p>New rent: ${watchedNewRent.toLocaleString()}/month</p>
            <p>Increase: ${watchedRentIncrease || 0}/month ({((((watchedRentIncrease || 0) / currentRent) * 100) || 0).toFixed(1)}%)</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isSubmitting ? 'Processing...' : 'Create Renewal'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default LeaseRenewalModal;