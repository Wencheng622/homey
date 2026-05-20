import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "outline" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  fullWidth?: boolean;
  leftIcon?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "h-11 bg-primary text-primary-foreground font-semibold shadow-warm-md hover:shadow-honey-glow hover:opacity-90 active:scale-[0.98]",
  outline:
    "h-11 gap-2.5 border border-border bg-card text-foreground hover:bg-secondary hover:border-honey-200 shadow-warm-xs transition-colors duration-150",
  ghost:
    "text-muted-foreground hover:text-foreground transition-colors",
};

const sharedBase =
  "inline-flex items-center justify-center rounded-lg text-sm font-medium transition-all duration-150 disabled:opacity-50 disabled:pointer-events-none";

export function Button({
  variant = "primary",
  fullWidth = false,
  leftIcon,
  className,
  type = "button",
  children,
  ...props
}: ButtonProps) {
  const classes = [
    variant !== "ghost" && sharedBase,
    variantClasses[variant],
    fullWidth && "w-full",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <button type={type} className={classes} {...props}>
      {leftIcon}
      {children}
    </button>
  );
}
