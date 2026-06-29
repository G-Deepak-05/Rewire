"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Flame, Target, BrainCircuit, Activity, ChevronUp, CheckCircle2, Loader2 } from "lucide-react";
import { motion } from "framer-motion";
import { Progress } from "@/components/ui/progress";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Dummy data for visual presentation since ML might take time to generate
const RECOVERY_SCORE = 82;
const CURRENT_STREAK = 14;

const mockDopamineData = [
  { day: 'Mon', stability: 45 },
  { day: 'Tue', stability: 52 },
  { day: 'Wed', stability: 48 },
  { day: 'Thu', stability: 61 },
  { day: 'Fri', stability: 59 },
  { day: 'Sat', stability: 75 },
  { day: 'Sun', stability: 82 },
];

import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function DashboardOverview() {
  const router = useRouter();
  const { data: profile, isLoading: isProfileLoading, isError: isProfileError } = useQuery({
    queryKey: ['profile'],
    queryFn: async () => {
      const res = await api.get('/onboarding/profile');
      return res.data;
    },
    retry: false
  });

  const { data: dashboard, isLoading: isDashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await api.get('/dashboard');
      return res.data;
    }
  });

  const { data: plan, refetch: refetchPlan } = useQuery({
    queryKey: ['plan'],
    queryFn: async () => {
      const res = await api.get('/plan');
      return res.data;
    },
    refetchInterval: (data) => (data ? false : 3000), // Poll every 3s if not generated yet
  });

  useEffect(() => {
    if (isProfileError) {
      router.push('/onboarding');
    }
  }, [isProfileError, router]);

  if (isProfileLoading || isDashboardLoading) {
    return (
      <div className="flex h-full min-h-[60vh] items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  const recoveryScore = dashboard?.recovery_score || 0;
  const currentStreak = dashboard?.streak_days || 0;

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
          <Card className="glass-card p-6 border-l-4 border-l-primary relative overflow-hidden h-full">
            <div className="absolute -right-4 -top-4 w-24 h-24 bg-primary/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Recovery Score</p>
                <h3 className="text-4xl font-bold text-foreground">{recoveryScore}</h3>
              </div>
              <div className="bg-primary/10 p-2 rounded-lg">
                <BrainCircuit className="w-6 h-6 text-primary" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.2 }}>
          <Card className="glass-card p-6 border-l-4 border-l-orange-500 relative overflow-hidden h-full">
             <div className="absolute -right-4 -top-4 w-24 h-24 bg-orange-500/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Current Streak</p>
                <h3 className="text-4xl font-bold text-foreground">{currentStreak} <span className="text-xl text-muted-foreground font-normal">days</span></h3>
              </div>
              <div className="bg-orange-500/10 p-2 rounded-lg">
                <Flame className="w-6 h-6 text-orange-500" />
              </div>
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.3 }}>
          <Card className="glass-card p-6 border-l-4 border-l-blue-500 relative overflow-hidden h-full">
             <div className="absolute -right-4 -top-4 w-24 h-24 bg-blue-500/10 rounded-full blur-2xl" />
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm text-muted-foreground font-medium mb-1">Target Addiction</p>
                <h3 className="text-2xl font-bold text-foreground capitalize">
                  {profile?.bad_habits?.[0]?.name || 'Loading...'}
                </h3>
              </div>
              <div className="bg-blue-500/10 p-2 rounded-lg">
                <Target className="w-6 h-6 text-blue-500" />
              </div>
            </div>
            <div className="mt-4 flex flex-col gap-2">
                <span className="text-xs font-medium px-2 py-1 bg-muted rounded-md w-fit">
                  Goal: {profile?.goals?.[0] || '...'}
                </span>
            </div>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        <Card className="glass-card p-6 h-[400px] flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Dopamine Stability Chart</h3>
          <div className="flex-1 w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockDopamineData} margin={{ top: 5, right: 20, bottom: 5, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="day" stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="stability" 
                  stroke="var(--primary)" 
                  strokeWidth={3}
                  dot={{ r: 4, fill: 'var(--primary)', strokeWidth: 2, stroke: '#000' }}
                  activeDot={{ r: 6, fill: 'var(--primary)', stroke: '#fff' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        
        <Card className="glass-card p-6 h-[400px] flex flex-col">
          <h3 className="text-lg font-semibold mb-4">Your AI Recovery Program</h3>
          <div className="space-y-4 overflow-y-auto pr-2">
            {plan ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-primary">
                    Phase {plan.current_phase_index + 1}: {plan.phases[plan.current_phase_index]?.title || "Recovery"}
                  </span>
                  <span className="text-xs text-muted-foreground">Day {plan.current_day} of {plan.phases[plan.current_phase_index]?.duration_days || 7}</span>
                </div>
                <div className="space-y-2">
                  {plan.phases[plan.current_phase_index]?.daily_tasks?.map((task: string, i: number) => {
                    const isCompleted = plan.completed_tasks?.[`day_${plan.current_day}`]?.includes(task);
                    return (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-muted/30 border border-border/50">
                        <div 
                           className={`w-5 h-5 rounded-md border flex items-center justify-center cursor-pointer transition-colors ${isCompleted ? 'bg-primary border-primary' : 'border-muted-foreground/50 hover:border-primary'}`}
                           onClick={async () => {
                             await api.post(`/plan/task?day=${plan.current_day}&task=${encodeURIComponent(task)}`);
                             refetchPlan();
                           }}
                        >
                           {isCompleted && <CheckCircle2 className="w-3 h-3 text-primary-foreground" />}
                        </div>
                        <span className={`text-sm ${isCompleted ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                          {task}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="p-4 rounded-lg bg-muted/30 border border-border/50 text-center text-muted-foreground flex flex-col items-center justify-center h-full">
                <Loader2 className="w-6 h-6 animate-spin text-primary mb-2" />
                <p>The AI is generating your personalized recovery program...</p>
                <p className="text-xs mt-1">This takes about 10-20 seconds.</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
