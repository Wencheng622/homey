'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/useToast';
import Toast from '@/components/Toast';
import AuthShell from '@/components/auth/AuthShell';
import PasswordField from '@/components/auth/PasswordField';
import { formatApiError, parseJsonResponse } from '@/lib/api';

interface LoginFormProps {
  config: {
    enableGoogleLogin: boolean;
    enableForgotPassword: boolean;
  };
}

export default function LoginForm({ config }: LoginFormProps) {
  const router = useRouter();
  const { toast, showMessage } = useToast();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const validateCredentials = (emailValue: string, passwordValue: string): boolean => {
    if (!emailValue.trim()) {
      showMessage('Email address is required', true);
      return false;
    }
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(emailValue)) {
      showMessage('Please enter a valid email address', true);
      return false;
    }
    if (!passwordValue.trim()) {
      showMessage('Password cannot be empty', true);
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateCredentials(email, password)) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await parseJsonResponse(response);
      if (!data) {
        showMessage('Server returned invalid response', true);
        return;
      }

      if (response.ok) {
        const user = data as { status?: string; email?: string };
        if (user.status === 'email_unverified') {
          showMessage('Please verify your email address before logging in.', true);
          return;
        }
        showMessage('Welcome back!', false);
        return;
      }

      showMessage(formatApiError(data, 'Login failed'), true);
    } catch {
      showMessage('Network error. Please try again.', true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    window.location.href = '/api/auth/google/login';
  };

  return (
    <AuthShell>
      <div className="p-8 pb-10 sm:p-9 sm:pb-10">
        <div className="text-center mb-8">
          <div className="bg-gradient-to-br from-orange-100 to-rose-100 w-[84px] h-[84px] rounded-[30px] flex items-center justify-center mx-auto mb-4 shadow-md shadow-orange-200/60">
            <i className="fas fa-building text-4xl text-orange-500" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-stone-800">Home In</h1>
          <p className="text-sm font-medium text-orange-700 mt-1">Find your perfect nest</p>
          <p className="text-sm text-stone-500 mt-4 leading-relaxed max-w-[280px] mx-auto">
            Welcome back. Sign in to pick up where you left off.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="relative mb-5">
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

          <PasswordField
            value={password}
            onChange={setPassword}
            placeholder="Password"
            disabled={isLoading}
          />

          {config.enableForgotPassword && (
            <div className="flex justify-end -mt-1 mb-6">
              <button
                type="button"
                onClick={() => router.push('/forgot-password')}
                className="text-sm font-semibold text-orange-600 border-b border-dashed border-orange-300 hover:text-orange-700"
              >
                Forgot password?
              </button>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-full bg-orange-400 hover:bg-orange-500 disabled:bg-orange-300 disabled:cursor-not-allowed font-bold text-orange-950 flex items-center justify-center gap-3 shadow-lg shadow-orange-300/40 transition-all hover:scale-[0.98] mb-7"
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin" />
                Signing in...
              </>
            ) : (
              <>
                <i className="fas fa-key" />
                Sign In
                <i className="fas fa-arrow-right" />
              </>
            )}
          </button>
        </form>

        {config.enableGoogleLogin && (
          <>
            <div className="flex items-center gap-3 mb-6 text-orange-600">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-orange-200 to-transparent" />
              <span className="text-xs font-semibold">OR</span>
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-orange-200 to-transparent" />
            </div>
            <button
              type="button"
              onClick={handleGoogleSignIn}
              className="w-full py-3.5 rounded-full bg-white border-2 border-orange-100 hover:bg-orange-50 hover:border-orange-300 font-semibold text-orange-900 flex items-center justify-center gap-3 transition-all"
            >
              <i className="fab fa-google text-xl text-orange-500" />
              Continue with Google
            </button>
          </>
        )}

        <div className="text-center mt-8 text-sm font-medium text-orange-800">
          Don&apos;t have an account?
          <button
            type="button"
            onClick={() => router.push('/register')}
            className="font-bold text-orange-600 ml-1.5 border-b border-orange-300 hover:text-orange-700"
          >
            Create account
          </button>
        </div>
      </div>

      <Toast show={toast.show} message={toast.message} isError={toast.isError} />
    </AuthShell>
  );
}
