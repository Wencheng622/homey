import Link from "next/link";
import { AuthCard } from "@/components/auth/AuthCard";
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-16 sm:py-20">
      <div
        className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
        aria-hidden="true"
      >
        <div className="absolute -top-40 right-0 w-[560px] h-[560px] rounded-full bg-honey-100/50 blur-3xl" />
        <div className="absolute -bottom-32 -left-24 w-[400px] h-[400px] rounded-full bg-accent/40 blur-3xl" />
      </div>

      <main className="w-full max-w-[400px] animate-fade-in">
        <AuthCard
          title="Welcome back"
          subtitle="Sign in to your Homey account"
        >
          <LoginForm />
        </AuthCard>

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
