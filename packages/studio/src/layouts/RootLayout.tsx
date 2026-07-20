import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Settings, Box, Activity } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const RootLayout: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Pipelines', href: '/pipelines', icon: Box },
    { name: 'Runs', href: '/runs', icon: Activity },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 items-center pl-8">
          <div className="mr-4 hidden md:flex">
            <Link to="/" className="mr-6 flex items-center space-x-2">
              <span className="hidden font-bold sm:inline-block">FlowCore Studio</span>
            </Link>
            <nav className="flex items-center space-x-6 text-sm font-medium">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  className={cn(
                    "transition-colors hover:text-foreground/80 flex items-center gap-2",
                    location.pathname === item.href ? "text-foreground" : "text-foreground/60"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
};
