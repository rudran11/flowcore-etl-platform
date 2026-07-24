import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, GitMerge, Activity, Settings, ChevronLeft, ChevronRight, Box, Puzzle, CalendarClock } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useSidebarStore } from '../../stores/sidebarStore';
import { Button } from '../../components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../../components/ui/tooltip';

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/pipelines', label: 'Pipelines', icon: GitMerge },
  { path: '/schedules', label: 'Schedules', icon: CalendarClock },
  { path: '/runs', label: 'Runs', icon: Activity },
  { path: '/plugins', label: 'Plugins', icon: Puzzle },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  const { isCollapsed, toggleSidebar } = useSidebarStore();

  return (
    <div
      className={cn(
        "relative flex flex-col border-r bg-card transition-all duration-300",
        isCollapsed ? "w-[80px]" : "w-[240px]"
      )}
    >
      <div className="flex h-14 items-center justify-between border-b px-4">
        {!isCollapsed && (
          <div className="flex items-center gap-2 font-semibold tracking-tight">
            <Box className="h-5 w-5 text-primary" />
            <span>FlowCore Studio</span>
          </div>
        )}
        {isCollapsed && (
          <Box className="mx-auto h-6 w-6 text-primary" />
        )}
      </div>

      <div className="flex-1 overflow-auto py-4">
        <TooltipProvider delayDuration={0}>
          <nav className="grid gap-1 px-2">
            {navItems.map((item) => (
              <Tooltip key={item.path}>
                <TooltipTrigger asChild>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      cn(
                        "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                        isActive
                          ? "bg-primary text-primary-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                        isCollapsed && "justify-center px-0"
                      )
                    }
                  >
                    <item.icon className={cn("h-4 w-4", isCollapsed ? "h-5 w-5" : "")} />
                    {!isCollapsed && <span>{item.label}</span>}
                  </NavLink>
                </TooltipTrigger>
                {isCollapsed && (
                  <TooltipContent side="right" className="flex items-center gap-4">
                    {item.label}
                  </TooltipContent>
                )}
              </Tooltip>
            ))}
          </nav>
        </TooltipProvider>
      </div>

      <div className="mt-auto border-t p-4">
        <div className={cn("flex items-center gap-3", isCollapsed && "justify-center")}>
          <Avatar className="h-9 w-9">
            <AvatarImage src="" alt="User" />
            <AvatarFallback>U</AvatarFallback>
          </Avatar>
          {!isCollapsed && (
            <div className="flex flex-col">
              <span className="text-sm font-medium">User Profile</span>
              <span className="text-xs text-muted-foreground">Admin Workspace</span>
            </div>
          )}
        </div>
      </div>

      <Button
        variant="outline"
        size="icon"
        className="absolute -right-4 top-6 z-10 h-8 w-8 rounded-full shadow-md"
        onClick={toggleSidebar}
      >
        {isCollapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </Button>
    </div>
  );
};
