import React from 'react';
import { useMembers, useUpdateMemberRole, useRemoveMember, useRoles } from '../hooks/useSettings';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, Trash2, User } from 'lucide-react';
import { toast } from 'sonner';
import { formatDistanceToNow } from 'date-fns';

export const MembersTab: React.FC = () => {
  const { data: members, isLoading } = useMembers();
  const { data: roles } = useRoles();
  const updateRoleMutation = useUpdateMemberRole();
  const removeMutation = useRemoveMember();

  const handleRoleChange = async (userId: string, roleId: string) => {
    try {
      await updateRoleMutation.mutateAsync({ userId, roleId });
      toast.success("Member role updated successfully.");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "An error occurred.");
    }
  };

  const handleRemove = async (userId: string) => {
    if (!window.confirm("Are you sure you want to remove this member?")) return;
    try {
      await removeMutation.mutateAsync(userId);
      toast.success("Member was removed from the workspace.");
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "An error occurred.");
    }
  };

  if (isLoading) {
    return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-white/40" /></div>;
  }

  return (
    <Card className="bg-black/40 border-white/10">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-xl font-medium text-white">Workspace Members</CardTitle>
          <CardDescription className="text-white/60">
            Manage who has access to this workspace and their permissions.
          </CardDescription>
        </div>
        <Button variant="outline" className="border-white/10 bg-white/5 hover:bg-white/10 text-white" disabled>
          Invite Member (Coming Soon)
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {members?.map(member => (
            <div key={member.user_id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 border border-white/10">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400">
                  <User className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{member.full_name}</p>
                  <p className="text-xs text-white/50">{member.email}</p>
                  <p className="text-xs text-white/30 mt-1">Joined {formatDistanceToNow(new Date(member.joined_at), { addSuffix: true })}</p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <Select 
                  value={member.role_id} 
                  onValueChange={(val) => handleRoleChange(member.user_id, val)}
                  disabled={updateRoleMutation.isPending}
                >
                  <SelectTrigger className="w-[160px] bg-black/50 border-white/10 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-white/10 text-white">
                    {roles?.map(r => (
                      <SelectItem key={r.id} value={r.id}>{r.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={() => handleRemove(member.user_id)}
                  disabled={removeMutation.isPending}
                  className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          {members?.length === 0 && (
            <div className="text-center py-8 text-white/50">
              No members found.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
