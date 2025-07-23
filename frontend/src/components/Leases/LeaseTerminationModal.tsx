import React, { useState } from 'react';
import { Lease } from '../../types/lease';
import Modal from '../Common/Modal';
import { useForm } from 'react-hook-form';
import { CalendarIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface LeaseTerminationFormData {
  terminationDate: string;
  terminationReason: string;
  noticeGiven: boolean;
  securityDepositReturn: number;
  finalRentAmount: number;
  notes: string;
  confirmTermination: boolean;
}

interface LeaseTerminationModalProps {
  isOpen: boolean;
  onClose: () => void;
  lease: Lease;
  onSubmit: (data: LeaseTerminationFormData) => void;
}

const LeaseTerminationModal: React.FC<LeaseTerminationModalProps> = ({
  isOpen,
  onClose,
  lease,
  onSubmit
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm<LeaseTerminationFormData>();

  const currentRent = lease.monthlyRent || lease.rent_amount || 0;
  const currentDeposit = lease.securityDeposit || lease.security_deposit || 0;
  const watchedConfirm = watch('confirmTermination', false);

  // Set default values
  React.useEffect(() => {
    const today = new Date();
    setValue('terminationDate', today.toISOString().split('T')[0]);
    setValue('securityDepositReturn', currentDeposit);
    setValue('finalRentAmount', 0);
    setValue('noticeGiven', false);
    setValue('confirmTermination', false);
  }, [lease, setValue, currentDeposit]);

  const onFormSubmit = async (data: LeaseTerminationFormData) => {
    try {
      setIsSubmitting(true);
      await onSubmit(data);
      toast.success('Lease termination processed successfully!');
      onClose();
    } catch (error) {
      toast.error('Failed to process lease termination');
    } finally {
      setIsSubmitting(false);
    }
  };

  const tenantName = lease.tenant_name || 'Unknown Tenant';
  const propertyName = lease.property_name || 'Unknown Property';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Terminate Lease" maxWidth="2xl">
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Warning Banner */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400 mr-3 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Warning: Lease Termination</h3>
              <p className="mt-1 text-sm text-red-700">
                This action will terminate the lease agreement. Please ensure you have followed all legal requirements 
                and given proper notice to the tenant.
              </p>
            </div>
          </div>
        </div>

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
              <span className="font-medium text-gray-500">Monthly Rent:</span>
              <p className="text-gray-900">${currentRent.toLocaleString()}</p>
            </div>
            <div>
              <span className="font-medium text-gray-500">Security Deposit:</span>
              <p className="text-gray-900">${currentDeposit.toLocaleString()}</p>
            </div>
            <div>
              <span className="font-medium text-gray-500">Original End Date:</span>
              <p className="text-gray-900">
                {lease.endDate || lease.end_date ? 
                  new Date(lease.endDate || lease.end_date || '').toLocaleDateString() : 
                  'N/A'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Termination Details */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Termination Details</h3>
          
          <div>
            <label htmlFor="terminationDate" className="block text-sm font-medium text-gray-700">
              Termination Date *
            </label>
            <div className="mt-1 relative">
              <CalendarIcon className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <input
                type="date"
                id="terminationDate"
                {...register('terminationDate', { required: 'Termination date is required' })}
                className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500"
              />
            </div>
            {errors.terminationDate && (
              <p className="mt-1 text-sm text-red-600">{errors.terminationDate.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="terminationReason" className="block text-sm font-medium text-gray-700">
              Reason for Termination *
            </label>
            <select
              id="terminationReason"
              {...register('terminationReason', { required: 'Reason is required' })}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500"
            >
              <option value="">Select a reason</option>
              <option value="lease_violation">Lease Violation</option>
              <option value="non_payment">Non-Payment of Rent</option>
              <option value="property_damage">Property Damage</option>
              <option value="illegal_activity">Illegal Activity</option>
              <option value="landlord_needs">Landlord Needs Property</option>
              <option value="mutual_agreement">Mutual Agreement</option>
              <option value="tenant_request">Tenant Request</option>
              <option value="other">Other</option>
            </select>
            {errors.terminationReason && (
              <p className="mt-1 text-sm text-red-600">{errors.terminationReason.message}</p>
            )}
          </div>

          <div className="flex items-center">
            <input
              id="noticeGiven"
              type="checkbox"
              {...register('noticeGiven', { required: 'You must confirm proper notice was given' })}
              className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
            />
            <label htmlFor="noticeGiven" className="ml-2 block text-sm text-gray-900">
              Proper legal notice has been given to the tenant *
            </label>
          </div>
          {errors.noticeGiven && (
            <p className="mt-1 text-sm text-red-600">{errors.noticeGiven.message}</p>
          )}
        </div>

        {/* Financial Settlement */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Financial Settlement</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="securityDepositReturn" className="block text-sm font-medium text-gray-700">
                Security Deposit Return ($)
              </label>
              <input
                type="number"
                id="securityDepositReturn"
                step="0.01"
                {...register('securityDepositReturn', { 
                  required: 'Security deposit return amount is required',
                  min: { value: 0, message: 'Amount cannot be negative' },
                  max: { value: currentDeposit, message: `Cannot exceed original deposit of $${currentDeposit}` }
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500"
              />
              {errors.securityDepositReturn && (
                <p className="mt-1 text-sm text-red-600">{errors.securityDepositReturn.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="finalRentAmount" className="block text-sm font-medium text-gray-700">
                Final Rent Amount Owed ($)
              </label>
              <input
                type="number"
                id="finalRentAmount"
                step="0.01"
                {...register('finalRentAmount', { 
                  min: { value: 0, message: 'Amount cannot be negative' }
                })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500"
              />
              {errors.finalRentAmount && (
                <p className="mt-1 text-sm text-red-600">{errors.finalRentAmount.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
            Additional Notes
          </label>
          <textarea
            id="notes"
            rows={3}
            {...register('notes')}
            placeholder="Any additional notes about the termination..."
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-red-500 focus:ring-red-500"
          />
        </div>

        {/* Final Confirmation */}
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <input
              id="confirmTermination"
              type="checkbox"
              {...register('confirmTermination', { required: 'You must confirm termination' })}
              className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
            />
            <label htmlFor="confirmTermination" className="ml-2 block text-sm font-medium text-red-900">
              I confirm that I want to terminate this lease agreement. This action cannot be undone.
            </label>
          </div>
          {errors.confirmTermination && (
            <p className="mt-1 text-sm text-red-600">{errors.confirmTermination.message}</p>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !watchedConfirm}
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {isSubmitting ? 'Processing...' : 'Terminate Lease'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default LeaseTerminationModal;