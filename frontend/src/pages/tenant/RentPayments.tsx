import React from 'react';
import { CurrencyDollarIcon, CreditCardIcon, BanknotesIcon } from '@heroicons/react/24/outline';

const RentPayments: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center">
            <CurrencyDollarIcon className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">Rent Payments</h1>
              <p className="text-sm text-gray-600">Pay your monthly rent securely</p>
            </div>
          </div>
        </div>
      </div>

      {/* Coming Soon Message */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <CreditCardIcon className="h-8 w-8 text-blue-600" />
          </div>
          <div className="ml-4">
            <h3 className="text-lg font-medium text-blue-900">Secure Online Payments</h3>
            <div className="mt-2 text-blue-800">
              <p>We're setting up secure online rent payment functionality. This will include:</p>
              <ul className="mt-3 list-disc list-inside space-y-1">
                <li>Multiple payment methods (credit card, bank transfer, ACH)</li>
                <li>Automatic recurring payments</li>
                <li>Payment confirmations and receipts</li>
                <li>Payment history tracking</li>
                <li>Late fee calculations</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Options Preview */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Available Payment Methods</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <CreditCardIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Credit/Debit Card</h3>
              <p className="text-sm text-gray-500 mt-1">Instant processing</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <BanknotesIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Bank Transfer</h3>
              <p className="text-sm text-gray-500 mt-1">Low fees, secure</p>
            </div>
            <div className="border border-gray-200 rounded-lg p-4 text-center">
              <CurrencyDollarIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">ACH Payment</h3>
              <p className="text-sm text-gray-500 mt-1">Automatic recurring</p>
            </div>
          </div>
        </div>
      </div>

      {/* Contact Info */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-2">Current Payment Methods</h3>
        <p className="text-gray-700">
          Until online payments are available, please contact your landlord for payment instructions.
        </p>
        <button className="mt-4 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2">
          Contact Landlord
        </button>
      </div>
    </div>
  );
};

export default RentPayments;