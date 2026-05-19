'use client';

import { useState } from 'react';

interface PasswordFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  className?: string;
}

export default function PasswordField({
  value,
  onChange,
  placeholder = 'Password',
  disabled = false,
  className = 'mb-5',
}: PasswordFieldProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div className={`relative ${className}`}>
      <i className="fas fa-lock absolute left-5 top-1/2 -translate-y-1/2 text-orange-400 z-10" />
      <input
        type={visible ? 'text' : 'password'}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full py-4 pl-12 pr-14 text-sm font-medium border-2 border-orange-100 rounded-full bg-orange-50/40 focus:outline-none focus:border-orange-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(251,146,60,0.12)] transition-all"
        placeholder={placeholder}
        required
        disabled={disabled}
      />
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        className="absolute right-4 top-1/2 -translate-y-1/2 text-orange-500 hover:text-orange-700 p-1"
        tabIndex={-1}
        aria-label={visible ? 'Hide password' : 'Show password'}
        disabled={disabled}
      >
        <i className={`fas ${visible ? 'fa-eye-slash' : 'fa-eye'}`} />
      </button>
    </div>
  );
}
