import React, { useEffect, useState } from 'react';

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

interface DialogContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

interface DialogHeaderProps {
  children: React.ReactNode;
}

interface DialogTitleProps {
  children: React.ReactNode;
  className?: string;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  if (!open) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={() => onOpenChange(false)}
      />
      {/* Dialog */}
      <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
        <div className="pointer-events-auto">{children}</div>
      </div>
    </>
  );
}

export const DialogContent = React.forwardRef<HTMLDivElement, DialogContentProps>(
  ({ children, className, ...props }, ref) => {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
      const checkDarkMode = () => {
        setIsDark(document.documentElement.classList.contains('dark'));
      };
      checkDarkMode();
      const observer = new MutationObserver(checkDarkMode);
      observer.observe(document.documentElement, { attributes: true });
      return () => observer.disconnect();
    }, []);

    return (
      <div
        ref={ref}
        className={`rounded-lg shadow-2xl max-w-4xl max-h-[90vh] overflow-y-auto p-6 relative border-2 border-slate-300 dark:border-slate-700 ${
          className || ''
        }`}
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: isDark ? 'rgb(15 23 42)' : 'rgb(241 245 249)',
        }}
        {...props}
      >
        {children}
      </div>
    );
  }
);

export function DialogHeader({ children }: DialogHeaderProps) {
  return <div className="mb-4 pb-4 border-b border-slate-300 dark:border-slate-700">{children}</div>;
}

export function DialogTitle({ children, className }: DialogTitleProps) {
  return (
    <h2 className={`text-xl font-bold text-slate-900 dark:text-slate-100 ${className || ''}`}>
      {children}
    </h2>
  );
}
