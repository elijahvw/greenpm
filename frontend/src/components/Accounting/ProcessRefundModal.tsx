import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../Common/Modal';
import { ProcessRefundRequest } from '../../types/securityDeposit';
import { 
  CurrencyDollarIcon, 
  CalendarIcon,
  BanknotesIcon,
  DocumentTextIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface ProcessRefundFormData {
  refundDate: string;
  refundMethod: 'check' | 'bank_transfer' | 'cash';
  refundNotes: string;
}

interface ProcessRefundModalProps {
  isOpen: boolean;
  onClose: () => void;
  depositId: string;
  depositAmount: number;
  totalDeductions: number;
  tenantName: string;
  propertyAddress: string;
  onSubmit: (depositId: string, data: ProcessRefundRequest) => Promise<void>;
}

const ProcessRefundModal: React.FC<ProcessRefundModalProps> = ({
  isOpen,
  onClose,
  depositId,
  depositAmount,
  totalDeductions,
  tenantName,
  propertyAddress,
  onSubmit
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { 
    register, 
    handleSubmit, 
    reset,
    formState: { errors } 
  } = useForm<ProcessRefundFormData>({
    defaultValues: {
      refundDate: new Date().toISOString().split('T')[0], // Today's date
      refundMethod: 'check'
    }
  });

  const refundAmount = Math.max(0, depositAmount - totalDeductions);

  const onFormSubmit = async (data: ProcessRefundFormData) => {
    try {
      setIsSubmitting(true);

      const refundData: ProcessRefundRequest = {
        refundDate: data.refundDate,
        refundMethod: data.refundMethod,
        refundNotes: data.refundNotes || undefined
      };

      await onSubmit(depositId, refundData);
      
      toast.success('Refund processed successfully');
      reset();
      onClose();
    } catch (error) {
      console.error('Error processing refund:', error);
      toast.error('Failed to process refund');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    reset();
    onClose();
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
      month: 'long', 
      day: 'numeric' 
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Process Security Deposit Refund"
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Tenant and Property Info */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Refund Details</h4>
          <div className="space-y-2 text-sm">
            <p><span className="text-gray-500">Tenant:</span> <span className="font-medium">{tenantName}</span></p>
            <p><span className="text-gray-500">Property:</span> <span className="font-medium">{propertyAddress}</span></p>
          </div>
        </div>

        {/* Financial Summary */}
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Original Deposit</p>
              <p className="text-lg font-semibold text-gray-900">{formatCurrency(depositAmount)}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Deductions</p>
              <p className="text-lg font-semibold text-red-600">-{formatCurrency(totalDeductions)}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Refund Amount</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(refundAmount)}</p>
            </div>
          </div>
        </div>

        {/* Refund Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CalendarIcon className="inline h-4 w-4 mr-1" />
              Refund Date *
            </label>
            <input
              type="date"
              {...register('refundDate', { 
                required: 'Refund date is required',
                validate: {
                  notFuture: (value) => {
                    const selectedDate = new Date(value);
                    const today = new Date();
                    today.setHours(23, 59, 59, 999); // End of today
                    return selectedDate <= today || 'Refund date cannot be in the future';
                  }
                }
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            />
            {errors.refundDate && (
              <p className="mt-1 text-sm text-red-600">{errors.refundDate.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <BanknotesIcon className="inline h-4 w-4 mr-1" />
              Refund Method *
            </label>
            <select
              {...register('refundMethod', { required: 'Refund method is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="check">Check</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="cash">Cash</option>
            </select>
            {errors.refundMethod && (
              <p className="mt-1 text-sm text-red-600">{errors.refundMethod.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <DocumentTextIcon className="inline h-4 w-4 mr-1" />
              Refund Notes (Optional)
            </label>
            <textarea
              {...register('refundNotes')}
              rows={3}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              placeholder="Check number, transfer details, or other notes..."
            />
          </div>
        </div>

        {/* Confirmation Notice */}
        {refundAmount === 0 ? (
          <div className="rounded-md bg-yellow-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  No Refund Due
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    The total deductions equal or exceed the original deposit amount. 
                    Processing this will mark the deposit as fully processed with no refund.
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="rounded-md bg-green-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">
                  Ready to Process
                </h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>
                    A refund of <strong>{formatCurrency(refundAmount)}</strong> will be processed for {tenantName}.
                    This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={handleClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {isSubmitting ? 'Processing...' : `Process ${refundAmount > 0 ? 'Refund' : 'Completion'}`}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default ProcessRefundModal;