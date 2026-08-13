import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useWorkspace, useUpdateWorkspace } from '../hooks/useSettings';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

interface GeneralFormValues {
  name: string;
  description: string;
}

export const GeneralTab: React.FC = () => {
  const { data: workspace, isLoading } = useWorkspace();
  const updateMutation = useUpdateWorkspace();

  const { register, handleSubmit, reset, formState: { isDirty, isSubmitting } } = useForm<GeneralFormValues>({
    defaultValues: {
      name: '',
      description: ''
    }
  });

  useEffect(() => {
    if (workspace) {
      reset({
        name: workspace.name,
        description: workspace.description || ''
      });
    }
  }, [workspace, reset]);

  const onSubmit = async (data: GeneralFormValues) => {
    try {
      await updateMutation.mutateAsync(data);
      toast.success("Workspace settings have been updated successfully.");
      reset(data); // reset isDirty
    } catch (err) {
      toast.error("There was a problem updating the workspace settings.");
    }
  };

  if (isLoading) {
    return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-white/40" /></div>;
  }

  return (
    <Card className="bg-black/40 border-white/10">
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardHeader>
          <CardTitle className="text-xl font-medium text-white">Workspace Details</CardTitle>
          <CardDescription className="text-white/60">
            Manage your workspace name and description.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium text-white/80">Workspace Name</label>
            <Input 
              {...register('name', { required: true })} 
              placeholder="e.g. Production Data"
              className="bg-black/50 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-indigo-500"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-white/80">Description</label>
            <Textarea 
              {...register('description')} 
              placeholder="Describe the purpose of this workspace..."
              className="bg-black/50 border-white/10 text-white placeholder:text-white/30 min-h-[100px] focus-visible:ring-indigo-500"
            />
          </div>
        </CardContent>
        <CardFooter className="border-t border-white/10 pt-6">
          <Button 
            type="submit" 
            disabled={!isDirty || isSubmitting}
            className="bg-indigo-600 hover:bg-indigo-700 text-white transition-all disabled:opacity-50"
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Save Changes
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};
