/**
 * Currency formatting utilities
 */

export const formatCurrency = (amount: number | string | undefined | null): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : (amount || 0);
  
  // Ensure we preserve cents by using toFixed first, then formatting
  return numAmount.toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

export const formatCurrencyWithoutSymbol = (amount: number | string | undefined | null): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : (amount || 0);
  
  return numAmount.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
};

export const parseCurrency = (value: string): number => {
  // Remove currency symbols and parse
  const cleaned = value.replace(/[$,]/g, '');
  return parseFloat(cleaned) || 0;
};

export const roundToCents = (amount: number): number => {
  return Math.round(amount * 100) / 100;
};