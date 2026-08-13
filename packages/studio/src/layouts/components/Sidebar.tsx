import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, GitMerge, Activity, Settings, ChevronLeft, ChevronRight, Box, Puzzle, CalendarClock, Server, Database } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useSidebarStore } from '../../stores/sidebarStore';
import { Button } from '../../components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../../components/ui/tooltip';
import { useAuthStore } from '../../stores/authStore';


const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/pipelines', label: 'Pipelines', icon: GitMerge },
  { path: '/environments', label: 'Environments', icon: Server },
  { path: '/datasets', label: 'Data Catalog', icon: Database },
  { path: '/schedules', label: 'Schedules', icon: CalendarClock },
  { path: '/runs', label: 'Runs', icon: Activity },
  { path: '/plugins', label: 'Plugins', icon: Puzzle },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { isCollapsed, toggleSidebar } = useSidebarStore();
  const { user } = useAuthStore();

  return (
    <div
      className={cn(
        "relative flex flex-col border-r bg-card transition-all duration-300 border-border shadow-sm z-20",
        isCollapsed ? "w-[72px]" : "w-[240px]"
      )}
    >
      <div className="flex h-[52px] items-center justify-between border-b border-border/50 px-4">
        {!isCollapsed && (
          <div className="flex items-center gap-2 font-semibold tracking-tight text-foreground">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary text-primary-foreground shadow-surface">
              <Box className="h-4 w-4" />
            </div>
            <span className="text-[14px] font-mono tracking-tight font-bold">FLOWCORE</span>
          </div>
        )}
        {isCollapsed && (
          <div className="flex h-full w-full items-center justify-center">
            <div className="flex h-6 w-6 items-center justify-center rounded bg-primary text-primary-foreground shadow-sm">
              <Box className="h-4 w-4" />
            </div>
          </div>
        )}
        
        {!isCollapsed && (
          <Button variant="ghost" size="icon" className="h-7 w-7 text-muted-foreground hover:text-foreground hover:bg-accent" onClick={toggleSidebar}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
        )}
      </div>

      <div className="flex-1 overflow-auto py-3">
        <TooltipProvider delayDuration={0}>
          <nav className="grid gap-0.5 px-3">
            {navItems.map((item) => (
              <Tooltip key={item.path}>
                <TooltipTrigger asChild>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center gap-3 rounded-md px-2.5 py-1.5 text-[13px] font-medium transition-all group relative overflow-hidden",
                        isActive
                          ? "bg-accent text-foreground font-semibold shadow-surface"
                          : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                        isCollapsed && "justify-center px-0 py-2.5"
                      )
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <div className="absolute left-0 top-0 bottom-0 w-[3px] bg-primary rounded-r-full" />
                        )}
                        <item.icon className={cn("h-4 w-4 z-10 transition-colors", isActive ? "text-primary" : "opacity-70 group-hover:opacity-100", isCollapsed && "h-5 w-5")} />
                        {!isCollapsed && <span className="z-10">{item.label}</span>}
                      </>
                    )}
                  </NavLink>
                </TooltipTrigger>
                {isCollapsed && (
                  <TooltipContent side="right" className="flex items-center gap-4 text-xs">
                    {item.label}
                  </TooltipContent>
                )}
              </Tooltip>
            ))}
          </nav>
        </TooltipProvider>
      </div>

      <div className="mt-auto border-t border-border/50 p-3">
        <div className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
          <Avatar className="h-7 w-7 rounded-md border border-border/50">
            <AvatarImage src="" alt="User" />
            <AvatarFallback className="rounded-md bg-accent text-xs">
              {user?.full_name?.charAt(0) || "U"}
            </AvatarFallback>
          </Avatar>
          {!isCollapsed && (
            <div className="flex flex-col items-start truncate">
              <span className="text-[13px] font-medium leading-none mb-1 text-foreground">{user?.full_name || "User"}</span>
              <span className="text-[11px] text-muted-foreground leading-none">Settings & Profile</span>
            </div>
          )}
        </div>
      </div>

      {/* Subtle Sidebar Toggle when collapsed */}
      {isCollapsed && (
        <div 
          onClick={toggleSidebar}
          className="absolute -right-3 top-6 z-10 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border bg-background text-muted-foreground shadow-sm hover:text-foreground transition-all"
        >
          <ChevronRight className="h-3 w-3" />
        </div>
      )}
    </div>
  );
};
