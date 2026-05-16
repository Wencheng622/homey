'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';

type Role = 'tenant' | 'landlord';

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>('tenant');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [toast, setToast] = useState({ show: false, message: '', isError: false });
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const showMessage = (message: string, isError: boolean = false) => {
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    setToast({ show: true, message, isError });
    toastTimeoutRef.current = setTimeout(() => {
      setToast({ show: false, message: '', isError: false });
    }, 2000);
  };

  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const validateCredentials = (email: string, password: string): boolean => {
    if (!email || email.trim() === '') {
      showMessage('Email address is required', true);
      return false;
    }
    const emailRegex = /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/;
    if (!emailRegex.test(email)) {
      showMessage('Please enter a valid email address', true);
      return false;
    }
    if (!password || password.trim() === '') {
      showMessage('Password cannot be empty', true);
      return false;
    }
    return true;
  };

  const performSignIn = (role: Role, email: string, password: string, viaGoogle: boolean = false) => {
    const userPrefix = email.split('@')[0];
    if (role === 'tenant') {
      showMessage(`Welcome back ${userPrefix}! You are logged in as Tenant.`, false);
    } else {
      showMessage(`Welcome ${userPrefix}! Landlord dashboard ready.`, false);
    }
    console.log(`[Login] Role: ${role}, Email: ${email}, GoogleAuth: ${viaGoogle}`);
    
    // router.push('/dashboard');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateCredentials(email, password)) return;
    performSignIn(role, email, password, false);
  };

  const handleGoogleSignIn = () => {
    showMessage('Google login function is waiting for addition', false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-amber-100 to-amber-300 relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_40%,rgba(255,220,120,0.3)_1.2%,transparent_1.8%),radial-gradient(circle_at_70%_85%,rgba(247,190,70,0.25)_1%,transparent_1.5%)] bg-[length:48px_48px,64px_64px] pointer-events-none" />
      
      <div className="relative z-10 w-full max-w-md bg-white rounded-[36px] shadow-2xl overflow-hidden transition-all duration-200 hover:-translate-y-1 min-w-[300px] sm:min-w-[360px] md:min-w-[420px]">
        <div className="h-2 bg-gradient-to-r from-amber-500 via-amber-300 to-amber-500" />
        <div className="p-8 pb-10 sm:p-7 sm:pb-9">
          <div className="text-center mb-7">
            <div className="bg-amber-50 w-[70px] h-[70px] rounded-[28px] flex items-center justify-center mx-auto mb-3 shadow-md">
              <i className="fas fa-building text-4xl text-amber-600" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-stone-800">Home In</h1>
            <div className="text-sm font-medium text-amber-700">Find your perfect nest</div>
          </div>

          <div className="flex gap-4 bg-amber-50 p-1.5 rounded-full border border-amber-100 mb-8">
            <button
              onClick={() => setRole('tenant')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
                role === 'tenant'
                  ? 'bg-amber-400 text-amber-900 shadow-sm'
                  : 'text-amber-700 hover:bg-amber-100'
              }`}
            >
              <i className="fas fa-user-friends" />
              <span>Tenant</span>
            </button>
            <button
              onClick={() => setRole('landlord')}
              className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
                role === 'landlord'
                  ? 'bg-amber-400 text-amber-900 shadow-sm'
                  : 'text-amber-700 hover:bg-amber-100'
              }`}
            >
              <i className="fas fa-home" />
              <span>Landlord</span>
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="relative mb-5">
              <i className="fas fa-envelope absolute left-5 top-1/2 -translate-y-1/2 text-amber-500" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full py-4 pl-12 pr-4 text-sm font-medium border-2 border-amber-100 rounded-full bg-amber-50/50 focus:outline-none focus:border-amber-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(242,184,46,0.15)] transition-all"
                placeholder="Email address"
                required
              />
            </div>
            <div className="relative mb-5">
              <i className="fas fa-lock absolute left-5 top-1/2 -translate-y-1/2 text-amber-500" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full py-4 pl-12 pr-4 text-sm font-medium border-2 border-amber-100 rounded-full bg-amber-50/50 focus:outline-none focus:border-amber-400 focus:bg-white focus:shadow-[0_0_0_4px_rgba(242,184,46,0.15)] transition-all"
                placeholder="Password"
                required
              />
            </div>

            <div className="flex justify-end mb-6">
              <a
                href="#"
                onClick={() => router.push('/forget-password')}
                className="text-sm font-semibold text-amber-600 border-b border-dashed border-amber-300 hover:text-amber-700"
              >
                Forgot password?
              </a>
            </div>

            <button
              type="submit"
              className="w-full py-4 rounded-full bg-amber-400 hover:bg-amber-500 font-bold text-amber-900 flex items-center justify-center gap-3 shadow-lg shadow-amber-500/30 transition-all hover:scale-[0.98] mb-7"
            >
              <i className="fas fa-key" />
              Sign In
              <i className="fas fa-arrow-right" />
            </button>
          </form>

          <div className="flex items-center gap-3 mb-6 text-amber-600">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-amber-300 to-transparent" />
            <span className="text-xs font-semibold">OR</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-amber-300 to-transparent" />
          </div>

          <button
            onClick={handleGoogleSignIn}
            className="w-full py-3.5 rounded-full bg-white border-2 border-amber-200 hover:bg-amber-50 hover:border-amber-400 font-semibold text-amber-800 flex items-center justify-center gap-3 transition-all"
          >
            <i className="fab fa-google text-xl text-amber-600" />
            Continue with Google
          </button>

          <div className="text-center mt-7 text-sm font-medium text-amber-700">
            Don't have an account?
            <a
              href="#"
              onClick={() => router.push('/register')}
              className="font-bold text-amber-600 ml-1.5 border-b border-amber-300 hover:text-amber-700"
            >
              Create account
            </a>
          </div>
        </div>
      </div>

      <div
        className={`fixed bottom-8 left-1/2 -translate-x-1/2 px-6 py-2.5 rounded-full font-semibold text-sm z-50 transition-all duration-200 pointer-events-none whitespace-nowrap max-w-[85%] text-center ${
          toast.show ? 'opacity-100 scale-100' : 'opacity-0 scale-90'
        } ${
          toast.isError
            ? 'bg-stone-800/90 border-l-4 border-orange-500 text-amber-200'
            : 'bg-stone-800/90 border-l-4 border-amber-400 text-amber-200'
        }`}
      >
        {toast.message}
      </div>
    </div>
  );
}