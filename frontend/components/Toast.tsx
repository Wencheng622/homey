'use client';

import { createPortal } from 'react-dom';
import { useEffect, useState } from 'react';

interface ToastProps {
  show: boolean;
  message: string;
  isError: boolean;
}

export default function Toast({ show, message, isError }: ToastProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!show || !mounted) return null;

  return createPortal(
    <div
      className={`fixed bottom-8 left-1/2 -translate-x-1/2 
        px-6 py-2.5 rounded-full font-semibold text-sm z-[9999] 
        transition-all duration-200 pointer-events-none 
        whitespace-nowrap max-w-[85%] text-center 
        bg-stone-800/90 border-l-4 text-amber-200
        ${show ? 'opacity-100 scale-100' : 'opacity-0 scale-90'}
        ${isError ? 'border-orange-500' : 'border-amber-400'}`}
    >
      {message}
    </div>,
    document.body  // 直接挂载到 body，避免受父容器影响
  );
}