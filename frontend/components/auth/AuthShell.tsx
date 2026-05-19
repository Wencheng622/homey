interface AuthShellProps {
  children: React.ReactNode;
  accent?: 'warm' | 'success';
}

export default function AuthShell({ children, accent = 'warm' }: AuthShellProps) {
  const barClass =
    accent === 'success'
      ? 'from-orange-400 via-amber-400 to-rose-400'
      : 'from-orange-400 via-amber-300 to-rose-300';

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-orange-50 via-amber-50 to-rose-100 relative">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(251,191,136,0.35)_1.2%,transparent_1.8%),radial-gradient(circle_at_80%_75%,rgba(253,186,140,0.3)_1%,transparent_1.5%)] bg-[length:52px_52px,68px_68px] pointer-events-none" />
      <div className="relative z-10 w-full max-w-md bg-white/95 backdrop-blur-sm rounded-[36px] shadow-2xl shadow-orange-200/50 overflow-hidden transition-all duration-200 min-w-[300px] sm:min-w-[360px] md:min-w-[420px]">
        <div className={`h-2 bg-gradient-to-r ${barClass}`} />
        {children}
      </div>
    </div>
  );
}
