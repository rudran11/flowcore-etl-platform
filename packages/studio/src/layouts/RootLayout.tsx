import React from 'react';
import { Outlet } from 'react-router-dom';
import { Toaster } from '../components/ui/sonner';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ThemeProvider } from '../providers/ThemeProvider';

export const RootLayout: React.FC = () => {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <div className="flex h-screen overflow-hidden bg-background font-sans antialiased text-foreground">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden relative">
          <Header />
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <Outlet />
          </main>
        </div>
        <Toaster position="top-right" />
      </div>
    </ThemeProvider>
  );
};
