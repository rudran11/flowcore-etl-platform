import React from 'react';
import { Search, Bell, Slash, Plus, Sun, Moon, LogOut } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { useLocation } from 'react-router-dom';
import { WorkspaceSwitcher } from '../../features/auth/components/WorkspaceSwitcher';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger } from '../../components/ui/dropdown-menu';
import { useTheme } from 'next-themes';
import { useAuthStore } from '../../stores/authStore';
import { Avatar, AvatarImage, AvatarFallback } from '../../components/ui/avatar';

export const Header: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);
  const { setTheme } = useTheme();
  const { user, logout } = useAuthStore();
  
  return (
    <header className="sticky top-0 z-40 flex h-[52px] w-full shrink-0 items-center justify-between gap-4 border-b border-border/50 bg-background px-4">
      <div className="flex items-center gap-3">
        <WorkspaceSwitcher />
        <div className="h-4 w-px bg-border/50 hidden sm:block"></div>
        <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
          <span className="font-medium text-foreground capitalize">
            {pathnames.length === 0 ? 'Dashboard' : pathnames[0]}
          </span>
          {pathnames.length > 1 && (
            <>
              <Slash className="h-3 w-3 opacity-50 shrink-0" />
              <span className="capitalize truncate max-w-[200px]">{pathnames[1]}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="relative hidden w-56 items-center sm:flex group">
          <Search className="absolute left-2.5 h-3.5 w-3.5 text-muted-foreground transition-colors group-focus-within:text-primary" />
          <Input
            type="search"
            placeholder="Search..."
            className="h-8 w-full bg-accent/30 pl-8 pr-10 text-xs shadow-none border-border/50 focus-visible:bg-background focus-visible:border-primary/50 transition-all rounded-md"
          />
          <kbd className="pointer-events-none absolute right-1.5 flex h-5 select-none items-center gap-1 rounded border border-border/50 bg-muted/50 px-1.5 font-mono text-[9px] font-medium opacity-100 text-muted-foreground">
            <span>⌘K</span>
          </kbd>
        </div>
        
        <Button variant="default" size="sm" className="h-8 text-xs bg-primary hover:bg-primary/90 hidden sm:flex">
          <Plus className="mr-1.5 h-3.5 w-3.5" /> New Pipeline
        </Button>
        
        <div className="flex items-center gap-1 border-l border-border/50 pl-3 ml-1">
          <Button variant="ghost" size="icon" className="h-8 w-8 rounded-md text-muted-foreground hover:text-foreground">
            <Bell className="h-4 w-4" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 rounded-full ml-1">
                <Avatar className="h-7 w-7 rounded-full border border-border/50">
                  <AvatarFallback className="bg-accent text-xs">
                    {user?.full_name?.charAt(0) || "U"}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]">
              <div className="flex flex-col space-y-1 p-2 leading-none">
                <span className="font-medium text-sm">{user?.full_name || "User"}</span>
                <span className="truncate text-xs text-muted-foreground">{user?.email || "user@example.com"}</span>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setTheme("light")} className="text-xs cursor-pointer">
                <Sun className="mr-2 h-3.5 w-3.5" /> Light Mode
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setTheme("dark")} className="text-xs cursor-pointer">
                <Moon className="mr-2 h-3.5 w-3.5" /> Dark Mode
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} className="text-xs text-destructive focus:bg-destructive/10 focus:text-destructive cursor-pointer">
                <LogOut className="mr-2 h-3.5 w-3.5" /> Log out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
};
