'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import AuthShell from './AuthShell';

interface RedirectSuccessProps {
  title: string;
  lines: React.ReactNode[];
  highlight?: string;
  redirectLabel?: string;
  redirectPath?: string;
  seconds?: number;
}

export default function RedirectSuccess({
  title,
  lines,
  highlight,
  redirectLabel = 'Redirecting to login page',
  redirectPath = '/login',
  seconds = 3,
}: RedirectSuccessProps) {
  const router = useRouter();
  const [countdown, setCountdown] = useState(seconds);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const redirectRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    intervalRef.current = setInterval(() => {
      setCountdown((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  useEffect(() => {
    if (countdown > 0) return;

    if (intervalRef.current) clearInterval(intervalRef.current);
    redirectRef.current = setTimeout(() => router.push(redirectPath), 100);

    return () => {
      if (redirectRef.current) clearTimeout(redirectRef.current);
    };
  }, [countdown, router, redirectPath]);

  return (
    <AuthShell accent="success">
      <div className="text-center p-8 sm:p-10">
        <div className="w-24 h-24 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <i className="fas fa-check-circle text-5xl text-orange-500" />
        </div>
        <h2 className="text-2xl font-bold text-stone-800 mb-3">{title}</h2>
        {lines.map((line, i) => (
          <p key={i} className="text-stone-600 mb-2">
            {line}
          </p>
        ))}
        {highlight && <p className="text-orange-700 font-semibold mb-6">{highlight}</p>}
        <div className="bg-orange-50 rounded-2xl p-4 mb-6">
          <p className="text-sm text-orange-800">
            <i className="fas fa-clock mr-2" />
            {redirectLabel} in <span className="font-bold text-lg mx-1">{countdown}</span> seconds...
          </p>
        </div>
        <button
          type="button"
          onClick={() => router.push(redirectPath)}
          className="text-orange-600 hover:text-orange-700 text-sm font-semibold underline"
        >
          Click here if not redirected automatically
        </button>
      </div>
    </AuthShell>
  );
}
