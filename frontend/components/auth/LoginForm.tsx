"use client";

import { useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { EyeOpenIcon, EyeClosedIcon, GoogleIcon } from "@/components/icons";

export function LoginForm() {
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
    <>
      <form onSubmit={handleSubmit} noValidate>
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
            <Button
              type="button"
              variant="ghost"
              className="absolute right-3 top-1/2 -translate-y-1/2"
              onClick={() => setShowPassword((v) => !v)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeClosedIcon /> : <EyeOpenIcon />}
            </Button>
          </div>
        </div>

        <Button type="submit" variant="primary" fullWidth>
          Sign in
        </Button>
      </form>

      <div className="flex items-center gap-3 my-5">
        <div className="flex-1 h-px bg-border" />
        <span className="text-xs font-medium text-muted-foreground">
          or continue with
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>

      <Button
        type="button"
        variant="outline"
        fullWidth
        leftIcon={<GoogleIcon className="w-[18px] h-[18px] shrink-0" />}
        onClick={handleGoogleLogin}
      >
        Continue with Google
      </Button>
    </>
  );
}
