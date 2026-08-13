import React, { Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../../components/ui/button';
import { FeaturesSection } from '../components/FeaturesSection';
import { ConnectorEcosystem } from '../components/ConnectorEcosystem';
import { LandingFooter } from '../components/LandingFooter';

const FlowCoreScene = React.lazy(() => import('../components/3d/FlowCoreScene'));

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-transparent text-foreground overflow-x-hidden selection:bg-primary/30 relative">
      
      {/* 3D WebGL Background Layer */}
      <Suspense fallback={<div className="fixed inset-0 z-0 bg-[#050505]" />}>
        <FlowCoreScene />
      </Suspense>

      {/* Z-10 HTML Overlay */}
      <div className="relative z-10">
        <header className="fixed top-0 left-0 right-0 z-50 px-6 py-4 border-b border-white/5 bg-background/50 backdrop-blur-md flex items-center justify-between">
        <div 
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        >
          {/* We will reuse FlowCore's logo icon if available, otherwise text */}
          <div className="w-8 h-8 rounded-md bg-primary flex items-center justify-center font-bold text-white shadow-surface">FC</div>
          <span className="font-bold text-lg tracking-tight text-white">FlowCore</span>
        </div>
        
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-300">
          <a href="#platform" className="hover:text-white transition-colors">Platform</a>
          <a href="#observability" className="hover:text-white transition-colors">Observability</a>
          <a href="#ecosystem" className="hover:text-white transition-colors">Ecosystem</a>
        </nav>

        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/dashboard')} className="text-sm font-medium text-slate-300 hover:text-white transition-colors">Sign In</button>
          <Button onClick={() => navigate('/dashboard')} className="shadow-surface font-semibold px-6">
            Open Studio
          </Button>
        </div>
      </header>

      <main className="pt-24 pb-16 px-6">
        <div className="max-w-[1400px] mx-auto min-h-[85vh] flex flex-col md:flex-row items-center relative">
          
          <div className="w-full md:w-1/2 z-10 flex flex-col items-start gap-6 pt-12 md:pt-0">
            <div className="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-3 py-1 text-xs font-semibold text-primary uppercase tracking-wider backdrop-blur-sm">
              Data Infrastructure, Reimagined
            </div>
            
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.1] text-white">
              Build. Move. <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-emerald-400">Observe.</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-slate-400 font-medium">
              Data in motion.
            </p>
            
            <p className="text-base text-slate-500 max-w-lg leading-relaxed mt-2">
              FlowCore is a visual data infrastructure platform for building, executing, and observing production data pipelines from a single workspace.
            </p>
            
            <div className="flex items-center gap-4 mt-4">
              <Button onClick={() => navigate('/dashboard')} size="lg" className="shadow-surface font-bold px-8 h-12">
                Open FlowCore Studio
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                className="bg-background font-semibold h-12"
                onClick={() => document.getElementById('platform')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Explore the Platform
              </Button>
            </div>
          </div>

          <div className="w-full md:w-1/2 h-[500px] md:h-full relative mt-12 md:mt-0 flex items-center justify-center pointer-events-none">
            {/* The 3D scene renders behind this. We leave this empty div to maintain flex layout for the text. */}
          </div>
          
        </div>
      </main>

      <FeaturesSection />
      
      <ConnectorEcosystem />
      
      <LandingFooter />
      </div>
    </div>
  );
};
