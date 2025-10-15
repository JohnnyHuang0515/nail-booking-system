import React from 'react';

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  children?: React.ReactNode;
  className?: string;
}

export function Label({ children, className = '', ...props }: LabelProps) {
  const baseClasses = 'block text-sm font-medium text-gray-700';
  
  return (
    <label className={`${baseClasses} ${className}`} {...props}>
      {children}
    </label>
  );
}