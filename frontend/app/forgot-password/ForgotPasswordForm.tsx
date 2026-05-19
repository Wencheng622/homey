'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/useToast';
import Toast from '@/components/Toast';
import AuthShell from '@/components/auth/AuthShell';
import PasswordField from '@/components/auth/PasswordField';
import RedirectSuccess from '@/components/auth/RedirectSuccess';
import { formatApiError, parseJsonResponse } from '@/lib/api';

type Step = 'email' | 'reset' | 'success';

export default function ForgotPasswordForm() {
  const router = useRouter();
  const { toast, showMessage } = useToast();
  const [step, setStep] = useState<Step>('email');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const validateEmail = (value: string): boolean => {
    if (!value.trim()) {
      showMessage('Email address is required', true);
      return false;
    }
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(value)) {
      showMessage('Please enter a valid email address', true);
      return false;
    }
    return true;
  };

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateEmail(email)) return;

    setIsLoading(true);
    try {
      await new Promise((resolve) => setTimeout(resolve, 800));
      setStep('reset');
      showMessage('Verification code sent', false);
    } catch {
      showMessage('Network error. Please try again.', true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!code.trim() || code.trim().length < 4) {
      showMessage('Please enter the verification code', true);
      return;
    }
    if (!password) {
      showMessage('Password is required', true);
      return;
    }
    if (password !== confirmPassword) {
      showMessage('Passwords do not match', true);
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/password/reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          password_confirm: confirmPassword,
        }),
      });

      const data = await parseJsonResponse(response);
      if (!data) {
        showMessage('Server returned invalid response', true);
        return;
      }

      if (response.ok) {
        setStep('success');
        return;
      }

      showMessage(formatApiError(data, 'Failed to reset password'), true);
    } catch {
      showMessage('Network error. Please try again.', true);
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 'success') {
    return (
      <RedirectSuccess
        title="Password Updated"
        lines={['Your password has been reset successfully.']}
        highlight={email}
      />
    );
  }

  return (
    <AuthShell>
      <div className="p-8 pb-10 sm:p-9 sm:pb-10">
        <div className="text-center mb-7">
          <div className="bg-gradient-to-br from-orange-100 to-rose-100 w-[84px] h-[84px] rounded-[30px] flex items-center justify-center mx-auto mb-4 shadow-md shadow-orange-200/60">
            <i className="fas fa-key text-4xl text-orange-500" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-stone-800">Forgot Password?</h1>
          <p className="text-sm font-medium text-orange-700 mt-1">We&apos;ll help you reset it</p>
        </div>

        {step === 'email' ? (
          <form onSubmit={handleSendCode}>
            <div className="bg-orange-50/80 rounded-2xl p-4 mb-6 border border-orange-100">
              <p className="text-sm text-stone-700 flex items-start gap-2">
                <i className="fas fa-info-circle text-orange-500 mt-0.5" />
                <span>Enter your email and we&apos;ll send you a verification code.</span>
              </p>
            </div>

            <div className="relative mb-8">
              <i className="fas fa-envelope absolute left-5 top-1/2 -translate-y-1/2 text-orange-400" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full py-4 pl-12 pr-4 text-sm font-medium border-2 border-orange-100 rounded-full bg-orange-50/40 focus:outline-none focus:border-orange-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(251,146,60,0.12)] transition-all"
                placeholder="Email address"
                required
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 rounded-full bg-orange-400 hover:bg-orange-500 disabled:bg-orange-300 disabled:cursor-not-allowed font-bold text-orange-950 flex items-center justify-center gap-3 shadow-lg shadow-orange-300/40 transition-all hover:scale-[0.98] mb-6"
            >
              {isLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin" />
                  Sending code...
                </>
              ) : (
                <>
                  <i className="fas fa-paper-plane" />
                  Send Verification Code
                </>
              )}
            </button>
          </form>
        ) : (
          <form onSubmit={handleResetPassword}>
            <p className="text-sm text-stone-600 mb-5 text-center">
              Code sent to <span className="font-semibold text-orange-700">{email}</span>
            </p>

            <div className="relative mb-5">
              <i className="fas fa-shield-alt absolute left-5 top-1/2 -translate-y-1/2 text-orange-400" />
              <input
                type="text"
                inputMode="numeric"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                className="w-full py-4 pl-12 pr-4 text-sm font-medium border-2 border-orange-100 rounded-full bg-orange-50/40 focus:outline-none focus:border-orange-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(251,146,60,0.12)] transition-all tracking-widest"
                placeholder="Verification code"
                required
                disabled={isLoading}
              />
            </div>

            <PasswordField
              value={password}
              onChange={setPassword}
              placeholder="New password"
              disabled={isLoading}
            />

            <PasswordField
              value={confirmPassword}
              onChange={setConfirmPassword}
              placeholder="Confirm new password"
              disabled={isLoading}
              className="mb-6"
            />

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-4 rounded-full bg-orange-400 hover:bg-orange-500 disabled:bg-orange-300 disabled:cursor-not-allowed font-bold text-orange-950 flex items-center justify-center gap-3 shadow-lg shadow-orange-300/40 transition-all hover:scale-[0.98] mb-4"
            >
              {isLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin" />
                  Updating password...
                </>
              ) : (
                <>
                  <i className="fas fa-check" />
                  Reset Password
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => setStep('email')}
              className="w-full text-sm font-semibold text-orange-600 hover:text-orange-700 mb-2"
              disabled={isLoading}
            >
              Use a different email
            </button>
          </form>
        )}

        <div className="text-center text-sm font-medium text-orange-800 mt-4">
          Remember your password?
          <button
            type="button"
            onClick={() => router.push('/login')}
            className="font-bold text-orange-600 ml-1.5 border-b border-orange-300 hover:text-orange-700"
          >
            Back to Sign In
          </button>
        </div>
      </div>

      <Toast show={toast.show} message={toast.message} isError={toast.isError} />
    </AuthShell>
  );
}
