import React from 'react';
import { formatCurrency, getCurrencySymbol, CURRENCIES } from '@/lib/currency';

interface CurrencyDisplayProps {
  amount: number;
  currency?: string;
  showSymbol?: boolean;
  showCode?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'muted' | 'highlight';
}

export function CurrencyDisplay({
  amount,
  currency = 'USD',
  showSymbol = true,
  showCode = false,
  className = '',
  size = 'md',
  variant = 'default'
}: CurrencyDisplayProps) {
  const currencyInfo = CURRENCIES[currency];
  const symbol = currencyInfo?.symbol || '$';
  
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg font-semibold'
  };

  const variantClasses = {
    default: 'text-gray-900 dark:text-gray-100',
    muted: 'text-gray-500 dark:text-gray-400',
    highlight: 'text-green-600 dark:text-green-400 font-medium'
  };

  const formattedAmount = formatCurrency(amount, currency);

  return (
    <span className={`${sizeClasses[size]} ${variantClasses[variant]} ${className}`}>
      {formattedAmount}
      {showCode && currency !== 'USD' && (
        <span className="text-xs text-gray-400 ml-1">({currency})</span>
      )}
    </span>
  );
}

interface SalaryRangeDisplayProps {
  min: number;
  max: number;
  currency?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'muted' | 'highlight';
}

export function SalaryRangeDisplay({
  min,
  max,
  currency = 'USD',
  className = '',
  size = 'md',
  variant = 'default'
}: SalaryRangeDisplayProps) {
  return (
    <span className={className}>
      <CurrencyDisplay 
        amount={min} 
        currency={currency} 
        size={size} 
        variant={variant} 
      />
      <span className="mx-1 text-gray-400">-</span>
      <CurrencyDisplay 
        amount={max} 
        currency={currency} 
        size={size} 
        variant={variant} 
      />
    </span>
  );
}

interface CurrencyBadgeProps {
  currency: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function CurrencyBadge({
  currency,
  className = '',
  size = 'sm'
}: CurrencyBadgeProps) {
  const currencyInfo = CURRENCIES[currency];
  if (!currencyInfo) return null;

  const sizeClasses = {
    sm: 'text-xs px-2 py-1',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-2'
  };

  return (
    <span className={`
      inline-flex items-center gap-1
      bg-gray-100 dark:bg-gray-800
      text-gray-700 dark:text-gray-300
      rounded-full font-medium
      ${sizeClasses[size]}
      ${className}
    `}>
      <span>{currencyInfo.symbol}</span>
      <span>{currency}</span>
    </span>
  );
} 