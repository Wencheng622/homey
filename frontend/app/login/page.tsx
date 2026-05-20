// frontend/app/login/page.tsx
"use client";

import { useState } from "react";
import Link from "next/link";

// ── Inline SVG icons ─────────────────────────────────────────────────────────

function EyeOpenIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeClosedIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
      <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
      <line x1="2" x2="22" y1="2" y2="22" />
    </svg>
  );
}

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: POST /api/v1/auth/login/
  };

  const handleGoogleLogin = () => {
    // TODO: POST /api/v1/auth/google/login/
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-16 sm:py-20">
      {/* ── Ambient background blobs — purely decorative ─────────────────── */}
      <div
        className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute -top-40 right-0 w-[560px] h-[560px] rounded-full bg-honey-100/50 blur-3xl" />
        <div className="absolute -bottom-32 -left-24 w-[400px] h-[400px] rounded-full bg-accent/40 blur-3xl" />
      </div>

      <main className="w-full max-w-[400px] animate-fade-in">
        {/* ── Card ─────────────────────────────────────────────────────────── */}
        <div className="bg-card rounded-2xl border border-border shadow-warm-lg px-7 pt-9 pb-8 sm:px-8">
          {/* ── Logo + heading — lives inside the card ───────────────────── */}
          <div className="flex flex-col items-center text-center mb-8">
            <img
              src="/logo-horizontal.svg"
              alt="Homey"
              className="h-9 w-auto mb-5"
            />
            <h1 className="text-[1.625rem] font-bold leading-tight tracking-tight text-foreground">
              Welcome back
            </h1>
            <p className="mt-1.5 text-sm text-muted-foreground">
              Sign in to your Homey account
            </p>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {/* Email ──────────────────────────────────────────────────────── */}
            <div className="mb-4">
              <label
                htmlFor="email"
                className="block text-sm font-medium text-foreground mb-1.5"
              >
                Email address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="
                  w-full h-11 px-3.5 rounded-lg
                  bg-background border border-border
                  text-sm text-foreground placeholder:text-muted-foreground
                  transition-colors duration-150
                  focus:outline-none focus:border-primary focus:ring-2 focus:ring-ring/20
                "
              />
            </div>

            {/* Password ───────────────────────────────────────────────────── */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-1.5">
                <label
                  htmlFor="password"
                  className="text-sm font-medium text-foreground"
                >
                  Password
                </label>
                <Link
                  href="/forget-password"
                  className="text-xs font-medium text-primary hover:text-honey-600 underline-offset-2 hover:underline transition-colors"
                >
                  Forgot password?
                </Link>
              </div>

              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="
                    w-full h-11 px-3.5 pr-10 rounded-lg
                    bg-background border border-border
                    text-sm text-foreground placeholder:text-muted-foreground
                    transition-colors duration-150
                    focus:outline-none focus:border-primary focus:ring-2 focus:ring-ring/20
                  "
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  className="
                    absolute right-3 top-1/2 -translate-y-1/2
                    text-muted-foreground hover:text-foreground transition-colors
                  "
                >
                  {showPassword ? <EyeClosedIcon /> : <EyeOpenIcon />}
                </button>
              </div>
            </div>

            {/* Primary CTA ────────────────────────────────────────────────── */}
            <button
              type="submit"
              className="
                w-full h-11 rounded-lg
                bg-primary text-primary-foreground
                text-sm font-semibold
                shadow-warm-md
                hover:shadow-honey-glow hover:opacity-90
                active:scale-[0.98]
                transition-all duration-150
              "
            >
              Sign in
            </button>
          </form>

          {/* Divider ─────────────────────────────────────────────────────── */}
          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs font-medium text-muted-foreground">
              or continue with
            </span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Google OAuth ────────────────────────────────────────────────── */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="
              w-full h-11 flex items-center justify-center gap-2.5
              rounded-lg border border-border bg-card
              text-sm font-medium text-foreground
              hover:bg-secondary hover:border-honey-200
              shadow-warm-xs transition-colors duration-150
            "
          >
            <GoogleIcon className="w-[18px] h-[18px] shrink-0" />
            Continue with Google
          </button>
        </div>

        {/* Sign up link ────────────────────────────────────────────────────── */}
        <p className="text-center text-sm text-muted-foreground mt-6">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="font-semibold text-primary hover:text-honey-600 underline-offset-2 hover:underline transition-colors"
          >
            Create account
          </Link>
        </p>
      </main>
    </div>
  );
}
