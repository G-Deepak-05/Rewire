"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Brain, Flame, Target, Loader2, CheckCircle2 } from "lucide-react";
import { api } from "@/lib/api";
import { useStore } from "@/lib/store";
import { toast } from "sonner";

const STEPS = [
  {
    id: "addiction",
    title: "Identify Your Target",
    subtitle: "What dopamine source are we rewiring?",
    options: ["Pornography", "Social Media", "Gaming", "Junk Food", "Substances", "Other"],
  },
  {
    id: "severity",
    title: "Current Baseline",
    subtitle: "How severe do you feel this addiction is right now?",
    options: ["Mild - Mostly manageable", "Moderate - Frequent urges", "Severe - Daily interference", "Critical - Controlling my life"],
  },
  {
    id: "goal",
    title: "Primary Objective",
    subtitle: "What is your end goal?",
    options: ["Complete Abstinence", "Controlled Moderation", "Reduce Frequency", "Build Better Habits"],
  }
];

export default function OnboardingWizard() {
  const router = useRouter();
  const setOnboardingStatus = useStore((state) => state.setOnboardingStatus);
  const [currentStep, setCurrentStep] = useState(0);
  const [selections, setSelections] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSelect = (option: string) => {
    setSelections({ ...selections, [STEPS[currentStep].id]: option });
  };

  const handleNext = async () => {
    if (currentStep < STEPS.length - 1) {
      setCurrentStep(prev => prev + 1);
    } else {
      await submitOnboarding();
    }
  };

  const submitOnboarding = async () => {
    setIsSubmitting(true);
    try {
      // Map to API schema format
      const payload = {
        addiction_type: selections.addiction || "Other",
        severity: selections.severity?.includes("Severe") ? 8 : selections.severity?.includes("Critical") ? 10 : selections.severity?.includes("Moderate") ? 5 : 2,
        goal: selections.goal || "Complete Abstinence",
        triggers: []
      };

      await api.post("/onboarding/profile", payload);
      setOnboardingStatus(true);
      toast.success("Protocol initialized successfully.");
      router.push("/dashboard");
    } catch (error) {
      toast.error("Failed to save protocol. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Background Gradients */}
      <div className="absolute top-0 left-1/4 w-[50%] h-[50%] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
      
      <div className="w-full max-w-2xl relative z-10">
        <div className="mb-8 flex justify-between items-center">
          <div className="flex gap-2 items-center text-primary font-bold">
            <Brain className="w-5 h-5" /> Rewire System
          </div>
          <div className="text-sm text-muted-foreground">
            Step {currentStep + 1} of {STEPS.length}
          </div>
        </div>

        <div className="relative h-[400px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
              className="absolute inset-0"
            >
              <h2 className="text-3xl font-bold mb-2">{STEPS[currentStep].title}</h2>
              <p className="text-muted-foreground mb-8 text-lg">{STEPS[currentStep].subtitle}</p>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {STEPS[currentStep].options.map((option) => {
                  const isSelected = selections[STEPS[currentStep].id] === option;
                  return (
                    <Card
                      key={option}
                      className={`p-4 cursor-pointer transition-all duration-300 ${
                        isSelected 
                          ? "border-primary bg-primary/10 shadow-[0_0_15px_rgba(var(--primary),0.3)]" 
                          : "glass-card hover:bg-white/5"
                      }`}
                      onClick={() => handleSelect(option)}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{option}</span>
                        {isSelected && <CheckCircle2 className="w-5 h-5 text-primary" />}
                      </div>
                    </Card>
                  );
                })}
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="mt-8 flex justify-between items-center border-t border-border/50 pt-6">
          <Button
            variant="ghost"
            onClick={() => setCurrentStep(prev => prev - 1)}
            disabled={currentStep === 0 || isSubmitting}
          >
            Back
          </Button>
          <Button
            onClick={handleNext}
            disabled={!selections[STEPS[currentStep].id] || isSubmitting}
            className="w-32 bg-primary hover:bg-primary/90"
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : currentStep === STEPS.length - 1 ? (
              "Initialize"
            ) : (
              "Continue"
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
