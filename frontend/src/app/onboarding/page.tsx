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
    id: "trigger",
    title: "Primary Trigger",
    subtitle: "What usually precedes a relapse?",
    options: ["Stress & Anxiety", "Boredom", "Late Night / Insomnia", "Social Settings", "Emotional Distress"],
  },
  {
    id: "sleep",
    title: "Sleep Habits",
    subtitle: "How many hours of sleep do you get on average?",
    options: ["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours"],
  },
  {
    id: "stress",
    title: "Stress Levels",
    subtitle: "How would you rate your daily stress?",
    options: ["Low - Relaxed", "Moderate - Manageable", "High - Often Overwhelmed", "Extreme - Constant Pressure"],
  },
  {
    id: "good_habit",
    title: "Keystone Habit",
    subtitle: "Which positive habit do you want to build to replace the addiction?",
    options: ["Daily Exercise", "Meditation / Mindfulness", "Reading / Learning", "Creative Hobbies", "Social Connection"],
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

  const [isGenerating, setIsGenerating] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("Analyzing your responses...");

  const submitOnboarding = async () => {
    setIsSubmitting(true);
    try {
      const severityStr = selections.severity || "";
      const severity = severityStr.includes("Severe") ? 8 : severityStr.includes("Critical") ? 10 : severityStr.includes("Moderate") ? 5 : 2;

      const payload = {
        bad_habits: [{ name: selections.addiction || "Other", severity: severity }],
        goals: [selections.goal || "Complete Abstinence"],
        triggers: [selections.trigger || "Stress"],
        sleep_hours: selections.sleep === "Less than 5 hours" ? 4 : selections.sleep === "5-6 hours" ? 5.5 : selections.sleep === "7-8 hours" ? 7.5 : 9,
        stress_level: selections.stress?.includes("Low") ? 2 : selections.stress?.includes("High") ? 8 : selections.stress?.includes("Extreme") ? 10 : 5,
        good_habits: [selections.good_habit || "Exercise"]
      };

      await api.post("/onboarding/profile", payload);
      setOnboardingStatus(true);
      
      // Transition to loading screen
      setIsGenerating(true);
      
      // Cycle through messages
      const messages = [
        "Analyzing your responses...",
        "Our AI is curating your personalized experience...",
        "Building your personalized dashboard...",
        "Preparing your recommendations..."
      ];
      let msgIndex = 0;
      const msgInterval = setInterval(() => {
        msgIndex = (msgIndex + 1) % messages.length;
        setLoadingMessage(messages[msgIndex]);
      }, 3000);

      // Redirect to dashboard after a short 3s transition
      // We don't wait for the AI plan to finish generating here anymore to unblock the user.
      // The dashboard itself will show a loading state for the AI plan section while it generates.
      setTimeout(() => {
        clearInterval(msgInterval);
        toast.success("Protocol initialized successfully.");
        // Force a hard reload to clear any stale react-query caches
        window.location.href = "/dashboard";
      }, 3000);

    } catch (error) {
      toast.error("Failed to save protocol. Please try again.");
      setIsSubmitting(false);
    }
  };

  if (isGenerating) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6 relative overflow-hidden">
        <div className="absolute top-0 left-1/4 w-[50%] h-[50%] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md relative z-10 text-center space-y-6"
        >
          <div className="inline-flex items-center justify-center p-6 bg-primary/10 rounded-full border border-primary/20 mb-4">
            <Brain className="w-16 h-16 text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold text-foreground">Initializing Protocol</h2>
          
          <div className="space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-primary mx-auto" />
            <AnimatePresence mode="wait">
              <motion.p
                key={loadingMessage}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-muted-foreground"
              >
                {loadingMessage}
              </motion.p>
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    );
  }

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
