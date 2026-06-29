"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Brain, Activity, Shield, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden bg-background">
      {/* Background Orbs for Premium Glass Effect */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-accent/20 blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass border-b border-border/40">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-primary p-1.5 rounded-lg">
              <Brain className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg tracking-tight">Rewire</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground transition-colors">
                Log in
              </Button>
            </Link>
            <Link href="/register">
              <Button className="bg-primary hover:bg-primary/90 text-primary-foreground">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="container mx-auto px-6 pt-40 pb-20 relative z-10">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <span className="px-4 py-1.5 rounded-full glass border-primary/20 text-primary text-sm font-medium mb-6 inline-flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Introducing Dopamine OS v1.0
            </span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold tracking-tight text-foreground leading-[1.1]"
          >
            Your Second Brain for <br />
            <span className="text-glow bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
              Defeating Addiction
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed"
          >
            Destroy dopamine addiction by changing your environment, not relying on willpower. 
            Rewire uses advanced AI and behavioral science to give you control back.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8"
          >
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto text-lg h-14 px-8 bg-primary hover:bg-primary/90">
                Start Your Protocol <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </motion.div>
        </div>

        {/* Feature Grid */}
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto mt-32">
          {[
            {
              title: "AI Recovery Coach",
              description: "A 24/7 intelligent coach that detects relapse triggers before they happen and provides cognitive interventions.",
              icon: Brain,
            },
            {
              title: "Real-time Metrics",
              description: "Visualize your recovery score, track cravings, and watch your dopamine baseline stabilize day by day.",
              icon: Activity,
            },
            {
              title: "Environmental Control",
              description: "Automated trigger management that adapts to your distress level, protecting you when willpower fails.",
              icon: Shield,
            }
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
            >
              <Card className="glass-card p-8 h-full hover:-translate-y-1 transition-transform duration-300">
                <div className="bg-primary/10 w-12 h-12 rounded-lg flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </Card>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
}
