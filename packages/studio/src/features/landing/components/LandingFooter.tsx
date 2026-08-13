import React from 'react';
import { useNavigate } from 'react-router-dom';

export const LandingFooter: React.FC = () => {
  const navigate = useNavigate();
  return (
    <footer className="w-full bg-background/80 backdrop-blur-md border-t border-border pt-16 pb-8 relative z-10">
      <div className="max-w-[1400px] mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-6 h-6 rounded bg-primary flex items-center justify-center font-bold text-white text-xs shadow-surface">FC</div>
              <span className="font-bold tracking-tight text-foreground">FlowCore</span>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Enterprise data infrastructure for modern engineering teams. Build, validate, and observe pipelines in real-time.
            </p>
          </div>
          
          <div>
            <h5 className="font-semibold text-foreground mb-4">Product</h5>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a onClick={() => navigate('/pipelines')} className="hover:text-primary transition-colors cursor-pointer">Pipeline Builder</a></li>
              <li><a onClick={() => navigate('/runs')} className="hover:text-primary transition-colors cursor-pointer">Execution Engine</a></li>
              <li><a onClick={() => navigate('/datasets')} className="hover:text-primary transition-colors cursor-pointer">Data Catalog</a></li>
              <li><span className="opacity-50 cursor-not-allowed">Lineage Graph <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-semibold text-foreground mb-4">Resources</h5>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><span className="opacity-50 cursor-not-allowed">Documentation <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">API Reference <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">Architecture Guide <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">GitHub <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-semibold text-foreground mb-4">Company</h5>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><span className="opacity-50 cursor-not-allowed">About <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">Blog <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">Security <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
              <li><span className="opacity-50 cursor-not-allowed">Terms of Service <span className="text-[10px] ml-1 opacity-70">(Soon)</span></span></li>
            </ul>
          </div>
          
        </div>
        
        <div className="pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between text-xs text-muted-foreground">
          <p>© {new Date().getFullYear()} FlowCore. All rights reserved.</p>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <span className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              All systems operational
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
