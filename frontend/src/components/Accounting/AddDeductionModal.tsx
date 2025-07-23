import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import Modal from '../Common/Modal';
import { AddDeductionRequest } from '../../types/securityDeposit';
import { 
  CurrencyDollarIcon, 
  DocumentTextIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface AddDeductionFormData {
  amount: number;
  description: string;
  category: 'damage' | 'cleaning' | 'unpaid_rent' | 'late_fees' | 'other';
  receipt: string;
  notes: string;
}

interface AddDeductionModalProps {
  isOpen: boolean;
  onClose: () => void;
  depositId: string;
  depositAmount: number;
  currentDeductions: number;
  onSubmit: (depositId: string, data: AddDeductionRequest) => Promise<void>;
}

const AddDeductionModal: React.FC<AddDeductionModalProps> = ({
  isOpen,
  onClose,
  depositId,
  depositAmount,
  currentDeductions,
  onSubmit
}) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { 
    register, 
    handleSubmit, 
    watch,
    reset,
    formState: { errors } 
  } = useForm<AddDeductionFormData>();

  const watchedAmount = watch('amount', 0);
  const remainingAmount = depositAmount - currentDeductions;
  const newRemaining = remainingAmount - (watchedAmount || 0);

  const onFormSubmit = async (data: AddDeductionFormData) => {
    try {
      setIsSubmitting(true);
      
      if (data.amount > remainingAmount) {
        toast.error('Deduction amount cannot exceed remaining deposit amount');
        return;
      }

      const deductionData: AddDeductionRequest = {
        date: new Date().toISOString().split('T')[0], // Today's date
        amount: data.amount,
        description: data.description,
        category: data.category,
        receipt: data.receipt || undefined,
        notes: data.notes || undefined
      };

      await onSubmit(depositId, deductionData);
      
      toast.success('Deduction added successfully');
      reset();
      onClose();
    } catch (error) {
      console.error('Error adding deduction:', error);
      toast.error('Failed to add deduction');
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

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Add Deduction"
      maxWidth="lg"
    >
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Deposit Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Original Deposit</p>
              <p className="font-medium">{formatCurrency(depositAmount)}</p>
            </div>
            <div>
              <p className="text-gray-500">Current Deductions</p>
              <p className="font-medium text-red-600">-{formatCurrency(currentDeductions)}</p>
            </div>
            <div>
              <p className="text-gray-500">Available Amount</p>
              <p className="font-medium text-green-600">{formatCurrency(remainingAmount)}</p>
            </div>
          </div>
        </div>

        {/* Deduction Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <CurrencyDollarIcon className="inline h-4 w-4 mr-1" />
              Deduction Amount *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max={remainingAmount}
              {...register('amount', {
                required: 'Amount is required',
                min: { value: 0.01, message: 'Amount must be greater than $0' },
                max: { value: remainingAmount, message: `Amount cannot exceed ${formatCurrency(remainingAmount)}` },
                valueAsNumber: true
              })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              placeholder="0.00"
            />
            {errors.amount && (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            )}
            {watchedAmount > 0 && (
              <p className="mt-1 text-xs text-gray-500">
                Remaining after deduction: {formatCurrency(newRemaining)}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              {...register('category', { required: 'Category is required' })}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            >
              <option value="">Select category...</option>
              <option value="damage">Property Damage</option>
              <option value="cleaning">Cleaning Costs</option>
              <option value="unpaid_rent">Unpaid Rent</option>
              <option value="late_fees">Late Fees</option>
              <option value="other">Other</option>
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <DocumentTextIcon className="inline h-4 w-4 mr-1" />
            Description *
          </label>
          <textarea
            {...register('description', { required: 'Description is required' })}
            rows={3}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            placeholder="Describe what this deduction is for..."
          />
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Receipt/Reference (Optional)
          </label>
          <input
            type="text"
            {...register('receipt')}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            placeholder="Receipt number, invoice ID, etc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            rows={2}
            className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
            placeholder="Any additional details about this deduction..."
          />
        </div>

        {/* Warning for large deductions */}
        {watchedAmount > remainingAmount * 0.8 && watchedAmount <= remainingAmount && (
          <div className="rounded-md bg-yellow-50 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  Large Deduction Warning
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    This deduction will use {Math.round((watchedAmount / depositAmount) * 100)}% of the original deposit.
                    Please ensure this amount is accurate.
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
            className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
          >
            {isSubmitting ? 'Adding...' : 'Add Deduction'}
          </button>
        </div>
      </form>
    </Modal>
  );
};

export default AddDeductionModal;