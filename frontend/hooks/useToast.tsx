import { useState, useRef, useEffect, useCallback } from 'react';

interface ToastState {
  show: boolean;
  message: string;
  isError: boolean;
}

export const useToast = (duration: number = 2600) => {
  const [toast, setToast] = useState<ToastState>({
    show: false,
    message: '',
    isError: false,
  });
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const showMessage = useCallback((message: string, isError: boolean = false) => {
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    setToast({ show: true, message, isError });
    toastTimeoutRef.current = setTimeout(() => {
      setToast({ show: false, message: '', isError: false });
    }, duration);
  }, [duration]);

  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  return { toast, showMessage };
};