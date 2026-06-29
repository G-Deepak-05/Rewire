"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Flame, Target, BrainCircuit, Activity, ChevronUp } from "lucide-react";
import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";

// Dummy data for visual presentation since ML might take time to generate
const RECOVERY_SCORE = 82;
const CURRENT_STREAK = 14;

export default function DashboardOverview() {
  const { data: profile, isLoading } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const res = await api.get('/onboarding/profile');
      return res.data;
    }
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
          <p className="text-muted-foreground mt-1">Your dopamine baseline is stabilizing.</p>
        </div>
        <div className="flex items-center gap-2 bg-primary/10 border border-primary/20 px-4 py-2 rounded-full">
          <Activity className="w-4 h-4 text-primary animate-pulse" />
          <span className="text-sm font-medium text-primary">Protocol Active</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}>
          <Card className="glass-card p-6 border-l-4 border-l-primary relative overflow-hidden">
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Recovery Score</p>
                <h3 className="text-4xl font-bold text-foreground">{RECOVERY_SCORE}</h3>
              </div>
              <div className="bg-primary/10 p-2 rounded-lg">
                <BrainCircuit className="w-6 h-6 text-primary" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm text-emerald-500">
              <ChevronUp className="w-4 h-4 mr-1" />
              <span>4 points since last week</span>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
          <Card className="glass-card p-6 border-l-4 border-l-orange-500 relative overflow-hidden">
             <div className="absolute -right-4 -top-4 w-24 h-24 bg-orange-500/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Current Streak</p>
                <h3 className="text-4xl font-bold text-foreground">{CURRENT_STREAK} <span className="text-xl text-muted-foreground font-normal">days</span></h3>
              </div>
              <div className="bg-orange-500/10 p-2 rounded-lg">
                <Flame className="w-6 h-6 text-orange-500" />
              </div>
            </div>
            <div className="mt-4">
              <Progress value={65} className="h-2 bg-muted/50" />
              <p className="text-xs text-muted-foreground mt-2">7 days until next milestone</p>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
          <Card className="glass-card p-6 border-l-4 border-l-blue-500 relative overflow-hidden">
             <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Target Addiction</p>
                <h3 className="text-2xl font-bold text-foreground capitalize">
                  {profile ? profile.addiction_type : 'Loading...'}
                </h3>
              </div>
              <div className="bg-blue-500/10 p-2 rounded-lg">
                <Target className="w-6 h-6 text-blue-500" />
              </div>
            </div>
            <div className="mt-4 flex flex-col gap-2">
                <span className="text-xs font-medium px-2 py-1 bg-muted rounded-md w-fit">
                  Goal: {profile ? profile.goal : '...'}
                </span>
            </div>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <Card className="glass-card p-6 h-[400px] flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Dopamine Stability Chart</h3>
          <div className="flex-1 border border-border/50 rounded-lg border-dashed flex items-center justify-center text-muted-foreground bg-muted/5">
            [Chart Area: To be populated by Recharts]
          </div>
        </Card>
        
        <Card className="glass-card p-6 h-[400px] flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Recent Insights from Coach</h3>
          <div className="space-y-4 overflow-y-auto pr-2">
            {[1, 2, 3].map((_, i) => (
              <div key={i} className="p-4 rounded-lg bg-muted/30 border border-border/50">
                <p className="text-sm font-medium text-primary mb-1">Trigger Detected</p>
                <p className="text-sm text-muted-foreground">Late night hours combined with high stress are your primary failure point. Consider the pre-sleep protocol.</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
