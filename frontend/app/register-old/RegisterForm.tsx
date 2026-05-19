'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/useToast';
import Toast from '@/components/Toast';

type Role = 'tenant' | 'landlord';

export default function RegisterForm() {
  const router = useRouter();
  const [role, setRole] = useState<Role>('tenant');
  const [email, setEmail] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [countdown, setCountdown] = useState(3);
  const { toast, showMessage } = useToast();
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const redirectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      if (redirectTimeoutRef.current) clearTimeout(redirectTimeoutRef.current);
    };
  }, []);

  useEffect(() => {
    if (showSuccess && countdown > 0) {
      countdownIntervalRef.current = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    } else if (showSuccess && countdown === 0) {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      redirectTimeoutRef.current = setTimeout(() => {
        router.push('/login');
      }, 100);
    }

    return () => {
      if (countdownIntervalRef.current) clearInterval(countdownIntervalRef.current);
      if (redirectTimeoutRef.current) clearTimeout(redirectTimeoutRef.current);
    };
  }, [showSuccess, countdown, router]);

  const handleRoleChange = (newRole: Role) => {
    setRole(newRole);
    showMessage(`Switched to ${newRole === 'tenant' ? 'Tenant' : 'Landlord'} view`, false);
  };

  const validateEmail = (email: string): boolean => {
    if (!email || email.trim() === '') {
      showMessage('Email address is required', true);
      return false;
    }
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showMessage('Please enter a valid email address', true);
      return false;
    }
    return true;
  };

  const handleSendVerificationEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateEmail(email)) return;
    
    setIsSending(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockSuccess = true;
      
      if (mockSuccess) {
        setShowSuccess(true);
        setCountdown(3);
        
        localStorage.setItem('pendingVerificationEmail', email);
        localStorage.setItem('pendingVerificationRole', role);
        
        console.log(`Verification email sent to ${email} as ${role}`);
      } else {
        showMessage('Failed to send verification email. Please try again.', true);
      }
    } catch (error) {
      console.error('Error sending verification email:', error);
      showMessage('Network error. Please try again.', true);
    } finally {
      setIsSending(false);
    }
  };

  if (showSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-amber-100 to-amber-300 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_40%,rgba(255,220,120,0.3)_1.2%,transparent_1.8%),radial-gradient(circle_at_70%_85%,rgba(247,190,70,0.25)_1%,transparent_1.5%)] bg-[length:48px_48px,64px_64px] pointer-events-none" />
        
        <div className="relative z-10 w-full max-w-md bg-white rounded-[36px] shadow-2xl overflow-hidden text-center p-8 animate-in fade-in zoom-in duration-300">
          <div className="h-2 bg-gradient-to-r from-green-500 via-green-400 to-green-500" />
          
          <div className="py-8">
            <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <i className="fas fa-envelope-open-text text-5xl text-green-600" />
            </div>
            
            <h2 className="text-2xl font-bold text-stone-800 mb-3">
              Check Your Email
            </h2>
            
            <p className="text-stone-600 mb-2">
              We've sent a verification link to
            </p>
            <p className="text-amber-700 font-semibold mb-6">
              {email}
            </p>
            
            <p className="text-sm text-stone-500 mb-4">
              Please click the link in the email to verify your account.
            </p>
            
            <div className="bg-amber-50 rounded-2xl p-4 mb-6">
              <p className="text-sm text-amber-800">
                <i className="fas fa-clock mr-2" />
                Redirecting to login page in <span className="font-bold text-lg mx-1">{countdown}</span> seconds...
              </p>
            </div>
            
            <button
              onClick={() => router.push('/login')}
              className="text-amber-600 hover:text-amber-700 text-sm font-semibold underline"
            >
              Click here if not redirected automatically
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-amber-100 to-amber-300 relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_40%,rgba(255,220,120,0.3)_1.2%,transparent_1.8%),radial-gradient(circle_at_70%_85%,rgba(247,190,70,0.25)_1%,transparent_1.5%)] bg-[length:48px_48px,64px_64px] pointer-events-none" />
      
      <div className="relative z-10 w-full max-w-md bg-white rounded-[36px] shadow-2xl overflow-hidden transition-all duration-200">
        <div className="h-2 bg-gradient-to-r from-amber-500 via-amber-300 to-amber-500" />
        
        <div className="p-8 pb-10 sm:p-7 sm:pb-9">
          <div className="text-center mb-7">
            <div className="bg-amber-50 w-[70px] h-[70px] rounded-[28px] flex items-center justify-center mx-auto mb-3 shadow-md">
              <i className="fas fa-user-plus text-4xl text-amber-600" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-stone-800">Create Account</h1>
            <div className="text-sm font-medium text-amber-700">Join Home In today</div>
          </div>

          <div className="flex gap-4 bg-amber-50 p-1.5 rounded-full border border-amber-100 mb-8">
            <button
              onClick={() => handleRoleChange('tenant')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
                role === 'tenant'
                  ? 'bg-amber-400 text-amber-900 shadow-sm'
                  : 'text-amber-700 hover:bg-amber-100'
              }`}
            >
              <i className="fas fa-user-friends" />
              <span>I'm a Tenant</span>
            </button>
            <button
              onClick={() => handleRoleChange('landlord')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
                role === 'landlord'
                  ? 'bg-amber-400 text-amber-900 shadow-sm'
                  : 'text-amber-700 hover:bg-amber-100'
              }`}
            >
              <i className="fas fa-home" />
              <span>I'm a Landlord</span>
            </button>
          </div>

          <form onSubmit={handleSendVerificationEmail}>
            <div className="relative mb-6">
              <i className="fas fa-envelope absolute left-5 top-1/2 -translate-y-1/2 text-amber-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full py-4 pl-12 pr-4 text-sm font-medium border-2 border-amber-100 rounded-full bg-amber-50/50 focus:outline-none focus:border-amber-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(242,184,46,0.15)] transition-all"
                placeholder="Enter your email address"
                required
                disabled={isSending}
              />
            </div>

            <div className="bg-blue-50 rounded-2xl p-4 mb-6">
              <p className="text-xs text-blue-800 flex items-start gap-2">
                <i className="fas fa-info-circle mt-0.5" />
                <span>We'll send you a verification link to activate your account. Please check your inbox.</span>
              </p>
            </div>

            <button
              type="submit"
              disabled={isSending}
              className="w-full py-4 rounded-full bg-amber-400 hover:bg-amber-500 disabled:bg-amber-300 disabled:cursor-not-allowed font-bold text-amber-900 flex items-center justify-center gap-3 shadow-lg shadow-amber-500/30 transition-all hover:scale-[0.98] mb-6"
            >
              {isSending ? (
                <>
                  <i className="fas fa-spinner fa-spin" />
                  Sending verification link...
                </>
              ) : (
                <>
                  <i className="fas fa-paper-plane" />
                  Send Verification Link
                </>
              )}
            </button>
          </form>

          <div className="flex items-center gap-3 mb-6 text-amber-600">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-amber-300 to-transparent" />
            <span className="text-xs font-semibold">OR</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-amber-300 to-transparent" />
          </div>

          <div className="text-center text-sm font-medium text-amber-700">
            Already have an account?
            <button
              onClick={() => router.push('/login')}
              className="font-bold text-amber-600 ml-1.5 border-b border-amber-300 hover:text-amber-700"
            >
              Sign in here
            </button>
          </div>
        </div>
      </div>

      <Toast show={toast.show} message={toast.message} isError={toast.isError} />
    </div>
  );
}