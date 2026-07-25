import { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      const isMissingWorkspace = this.state.error?.message?.includes('X-Workspace-ID');
      
      return (
        <div className="min-h-[400px] flex items-center justify-center p-8">
          <div className="max-w-md w-full bg-slate-900 border border-slate-800 rounded-xl p-8 text-center shadow-xl">
            <div className="w-16 h-16 bg-red-500/10 text-red-400 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertTriangle className="w-8 h-8" />
            </div>
            
            <h2 className="text-xl font-semibold text-white mb-3">
              {isMissingWorkspace ? 'Workspace Required' : 'Something went wrong'}
            </h2>
            
            <p className="text-slate-400 mb-8">
              {isMissingWorkspace 
                ? 'You must select a workspace before accessing this page. Please select a workspace from the dashboard.'
                : this.state.error?.message || 'An unexpected error occurred while loading this view.'}
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button
                onClick={() => window.location.reload()}
                className="flex items-center gap-2 px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors w-full sm:w-auto justify-center"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Retry</span>
              </button>
              
              <button
                onClick={() => window.location.href = '/'}
                className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-colors w-full sm:w-auto justify-center"
              >
                <Home className="w-4 h-4" />
                <span>Go Home</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
