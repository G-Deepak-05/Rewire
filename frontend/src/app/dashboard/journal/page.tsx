"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Plus, PenTool } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";

export default function JournalPage() {
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const [content, setContent] = useState("");
  const [stress, setStress] = useState("");
  const [cravings, setCravings] = useState("");

  const { data: entries, isLoading } = useQuery({
    queryKey: ['journal'],
    queryFn: async () => {
      const res = await api.get('/journal');
      return res.data.entries || [];
    }
  });

  const createEntry = useMutation({
    mutationFn: async (payload: any) => {
      const res = await api.post('/journal', payload);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal'] });
      setIsOpen(false);
      setContent("");
      setStress("");
      setCravings("");
      toast.success("Journal entry logged.");
    },
    onError: () => {
      toast.error("Failed to log entry.");
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createEntry.mutate({
      notes: content,
      entry_type: "reflection",
      emotion: "neutral",
      stress_level: parseInt(stress) || 5,
      emotion_intensity: 5
    });
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Journal</h1>
          <p className="text-muted-foreground mt-1">Log your thoughts and environmental state.</p>
        </div>
        
        <Dialog open={isOpen} onOpenChange={setIsOpen}>
          <DialogTrigger render={<Button className="bg-primary hover:bg-primary/90" />}>
            <Plus className="w-4 h-4 mr-2" /> New Entry
          </DialogTrigger>
          <DialogContent className="glass-card sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Log Entry</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4 mt-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">How are you feeling right now?</label>
                <Textarea 
                  placeholder="Dump your thoughts here..." 
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  className="min-h-[120px] bg-background"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Stress Level (1-10)</label>
                  <Input 
                    type="number" 
                    min="1" max="10" 
                    value={stress}
                    onChange={(e) => setStress(e.target.value)}
                    className="bg-background" 
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Cravings Today</label>
                  <Input 
                    type="number" 
                    min="0" 
                    value={cravings}
                    onChange={(e) => setCravings(e.target.value)}
                    className="bg-background" 
                  />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={createEntry.isPending}>
                {createEntry.isPending ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : "Save Entry"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 mt-8">
        {isLoading ? (
          <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
        ) : entries?.length === 0 ? (
          <Card className="p-12 text-center glass-card border-dashed">
            <PenTool className="w-12 h-12 text-muted-foreground mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-semibold">No entries yet</h3>
            <p className="text-muted-foreground">Start tracking your baseline by creating a journal entry.</p>
          </Card>
        ) : (
          entries?.map((entry: any) => (
            <Card key={entry.id} className="p-6 glass-card hover:bg-white/5 transition-colors">
              <div className="flex justify-between items-start mb-4">
                <span className="text-xs font-medium text-muted-foreground">
                  {format(new Date(entry.created_at), 'MMMM d, yyyy • h:mm a')}
                </span>
                <div className="flex gap-2 text-xs">
                  {entry.stress_level && <span className="bg-orange-500/10 text-orange-500 px-2 py-1 rounded-md">Stress: {entry.stress_level}</span>}
                  <span className="bg-primary/10 text-primary px-2 py-1 rounded-md capitalize">{entry.entry_type}</span>
                </div>
              </div>
              <p className="text-foreground leading-relaxed">{entry.notes || "No additional notes provided."}</p>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
