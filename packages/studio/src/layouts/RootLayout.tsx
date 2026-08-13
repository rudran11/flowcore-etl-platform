import React from 'react';
import { useLocation, useOutlet } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from '../components/ui/sonner';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { ThemeProvider } from '../providers/ThemeProvider';
import { CommandPalette } from '../components/CommandPalette';

export const RootLayout: React.FC = () => {
  const location = useLocation();
  const outlet = useOutlet();
  
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <div className="flex h-screen overflow-hidden bg-background font-sans antialiased text-foreground">
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden relative">
          {/* Global Background Effects */}
          <div className="absolute inset-0 bg-dot-topology opacity-[0.02] dark:opacity-[0.01]" />
          <div className="bg-radial-glow" />
          
          <Header />
          <main className="flex-1 overflow-y-auto relative z-10">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname.split('/')[1] || 'dashboard'}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="h-full flex flex-col w-full"
              >
                {outlet}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
        <Toaster position="top-right" />
        <CommandPalette />
      </div>
    </ThemeProvider>
  );
};
