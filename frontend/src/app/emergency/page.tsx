"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { ShieldAlert, ArrowLeft, Phone, Brain, Activity, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { toast } from "sonner";

export default function EmergencyMode() {
  const router = useRouter();
  const [activating, setActivating] = useState(false);
  const [step, setStep] = useState(1);

  const activateLockdown = async () => {
    setActivating(true);
    try {
      await api.post("/emergency/activate", {
        reason: "Manual trigger from UI",
        severity_level: 10
      });
      toast.error("PROTOCOL LOCKDOWN INITIATED", { 
        description: "Environment overrides engaged. Follow breathing protocols immediately."
      });
      setStep(2);
    } catch (error) {
      toast.error("Failed to activate lockdown. Please try again.");
    } finally {
      setActivating(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 relative overflow-hidden text-red-50">
      {/* Intense red glow */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-red-900/40 via-black to-black pointer-events-none" />
      
      {/* Grid overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80000012_1px,transparent_1px),linear-gradient(to_bottom,#80000012_1px,transparent_1px)] bg-[size:24px_24px] pointer-events-none" />

      <div className="w-full max-w-lg relative z-10">
        <Button 
          variant="ghost" 
          onClick={() => router.back()}
          className="absolute -top-16 left-0 text-red-400 hover:text-red-300 hover:bg-red-950/50"
        >
          <ArrowLeft className="w-4 h-4 mr-2" /> Abort
        </Button>

        {step === 1 ? (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center space-y-8"
          >
            <div className="inline-flex items-center justify-center p-6 bg-red-500/10 rounded-full border border-red-500/30 mb-4 animate-pulse">
              <ShieldAlert className="w-20 h-20 text-red-500" />
            </div>
            
            <div className="space-y-2">
              <h1 className="text-5xl font-bold text-red-500 uppercase tracking-tighter">Emergency Mode</h1>
              <p className="text-xl text-red-300/80">You are about to break the protocol.</p>
            </div>

            <p className="text-red-400/60">
              Activating emergency mode will immediately notify your accountability partners, log a critical event, and invoke cognitive override interventions.
            </p>

            <button
              onClick={activateLockdown}
              disabled={activating}
              className="w-full relative group overflow-hidden rounded-xl bg-red-600 px-8 py-6 text-2xl font-bold text-white transition-all hover:bg-red-500 disabled:opacity-50"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
              {activating ? "INITIATING..." : "INITIATE LOCKDOWN"}
            </button>
          </motion.div>
        ) : (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
             <div className="text-center mb-10">
                <h1 className="text-4xl font-bold text-red-500 uppercase tracking-tighter mb-2">Protocol Active</h1>
                <p className="text-red-300/80">Do exactly as instructed.</p>
             </div>
             
             <div className="space-y-4">
               <div className="p-6 bg-red-950/40 border border-red-500/30 rounded-xl flex items-center gap-4">
                  <Activity className="w-8 h-8 text-red-400 shrink-0" />
                  <div>
                    <h3 className="font-bold text-red-100">Breathe (Box Breathing)</h3>
                    <p className="text-sm text-red-300/80">Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Repeat 5 times.</p>
                  </div>
               </div>

               <div className="p-6 bg-red-950/40 border border-red-500/30 rounded-xl flex items-center gap-4">
                  <Brain className="w-8 h-8 text-red-400 shrink-0" />
                  <div>
                    <h3 className="font-bold text-red-100">Urge Surfing</h3>
                    <p className="text-sm text-red-300/80">Notice the craving. Do not fight it. Watch it peak and fall like a wave.</p>
                  </div>
               </div>

               <div className="p-6 bg-red-950/40 border border-red-500/30 rounded-xl flex items-center gap-4">
                  <Phone className="w-8 h-8 text-red-400 shrink-0" />
                  <div>
                    <h3 className="font-bold text-red-100">Accountability</h3>
                    <p className="text-sm text-red-300/80">Your partner has been notified. Expect a call shortly.</p>
                  </div>
               </div>
             </div>

             <Button 
                variant="outline" 
                onClick={() => router.push('/dashboard/coach')}
                className="w-full h-14 text-lg border-red-500/50 text-red-400 hover:bg-red-950/50"
              >
                Talk to AI Coach Now
              </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
