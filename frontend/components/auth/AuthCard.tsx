import type { ReactNode } from "react";

interface AuthCardProps {
  title: string;
  subtitle: string;
  children: ReactNode;
}

export function AuthCard({ title, subtitle, children }: AuthCardProps) {
  return (
    <div className="bg-card rounded-2xl border border-border shadow-warm-lg px-7 pt-9 pb-8 sm:px-8">
      <div className="flex flex-col items-center text-center mb-8">
        <img
          src="/logo-horizontal.svg"
          alt="Homey"
          className="h-9 w-auto mb-5"
        />
        <h1 className="text-[1.625rem] font-bold leading-tight tracking-tight text-foreground">
          {title}
        </h1>
        <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
      </div>
      {children}
    </div>
  );
}
