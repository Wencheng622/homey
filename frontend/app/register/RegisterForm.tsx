'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useToast } from '@/hooks/useToast';
import Toast from '@/components/Toast';
import AuthShell from '@/components/auth/AuthShell';
import PasswordField from '@/components/auth/PasswordField';
import RoleToggle, { AuthRole } from '@/components/auth/RoleToggle';
import RedirectSuccess from '@/components/auth/RedirectSuccess';
import { displayNameFromEmail, formatApiError, parseJsonResponse } from '@/lib/api';

export default function RegisterForm() {
  const router = useRouter();
  const { toast, showMessage } = useToast();
  const [role, setRole] = useState<AuthRole>('tenant');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const validateForm = (): boolean => {
    if (!email.trim()) {
      showMessage('Email address is required', true);
      return false;
    }
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showMessage('Please enter a valid email address', true);
      return false;
    }
    if (!password) {
      showMessage('Password is required', true);
      return false;
    }
    if (password !== confirmPassword) {
      showMessage('Passwords do not match', true);
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          role,
          name: displayNameFromEmail(email),
        }),
      });

      const data = await parseJsonResponse(response);
      if (!data) {
        showMessage('Server returned invalid response', true);
        return;
      }

      if (response.ok) {
        setShowSuccess(true);
        return;
      }

      showMessage(formatApiError(data, 'Registration failed'), true);
    } catch {
      showMessage('Network error. Please try again.', true);
    } finally {
      setIsLoading(false);
    }
  };

  if (showSuccess) {
    return (
      <RedirectSuccess
        title="Account Created"
        lines={['Your account has been registered successfully.']}
        highlight={email}
      />
    );
  }

  return (
    <AuthShell>
      <div className="p-8 pb-10 sm:p-9 sm:pb-10">
        <div className="text-center mb-7">
          <div className="bg-gradient-to-br from-orange-100 to-rose-100 w-[84px] h-[84px] rounded-[30px] flex items-center justify-center mx-auto mb-4 shadow-md shadow-orange-200/60">
            <i className="fas fa-user-plus text-4xl text-orange-500" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-stone-800">Create Account</h1>
          <p className="text-sm font-medium text-orange-700 mt-1">Join Home In today</p>
        </div>

        <RoleToggle
          role={role}
          onChange={setRole}
          tenantLabel="I'm a Tenant"
          landlordLabel="I'm a Landlord"
        />

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

          <PasswordField
            value={confirmPassword}
            onChange={setConfirmPassword}
            placeholder="Confirm password"
            disabled={isLoading}
            className="mb-6"
          />

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 rounded-full bg-orange-400 hover:bg-orange-500 disabled:bg-orange-300 disabled:cursor-not-allowed font-bold text-orange-950 flex items-center justify-center gap-3 shadow-lg shadow-orange-300/40 transition-all hover:scale-[0.98] mb-6"
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin" />
                Creating account...
              </>
            ) : (
              <>
                <i className="fas fa-user-check" />
                Create Account
              </>
            )}
          </button>
        </form>

        <div className="text-center text-sm font-medium text-orange-800">
          Already have an account?
          <button
            type="button"
            onClick={() => router.push('/login')}
            className="font-bold text-orange-600 ml-1.5 border-b border-orange-300 hover:text-orange-700"
          >
            Sign in here
          </button>
        </div>
      </div>

      <Toast show={toast.show} message={toast.message} isError={toast.isError} />
    </AuthShell>
  );
}
