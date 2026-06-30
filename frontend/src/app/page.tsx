"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useEffect, useState, useRef } from "react";
import { Menu } from "lucide-react";

export default function Home() {
  const [isClient, setIsClient] = useState(false);
  const modelRef = useRef<any>(null);

  useEffect(() => {
    setIsClient(true);
    // Dynamically import the web component only on the client side
    import("@google/model-viewer").catch(console.error);
  }, []);

  useEffect(() => {
    const handleModelLoad = () => {
      // Wrap in requestAnimationFrame to prevent synchronous Lit update warnings
      requestAnimationFrame(() => {
        if (modelRef.current && modelRef.current.model) {
          const materials = modelRef.current.model.materials;
          if (materials && materials.length > 0) {
            // Material 0 (Main Body & Wires) -> Chrome Metallic
            materials[0].pbrMetallicRoughness.setBaseColorFactor([0.9, 0.9, 0.9, 1]);
            materials[0].pbrMetallicRoughness.setMetallicFactor(1.0);
            materials[0].pbrMetallicRoughness.setRoughnessFactor(0.1); 
            
            if (materials.length > 1) {
              // Material 1 (Face/AI Core) -> Chrome Metallic
              materials[1].pbrMetallicRoughness.setBaseColorFactor([0.9, 0.9, 0.9, 1]);
              materials[1].pbrMetallicRoughness.setMetallicFactor(1.0);
              materials[1].pbrMetallicRoughness.setRoughnessFactor(0.1);
              
              // Remove any emissive glow from previous design
              materials[1].setEmissiveFactor([0, 0, 0]);
            }
          }
        }
      });
    };

    const viewer = modelRef.current;
    if (viewer) {
      viewer.addEventListener("load", handleModelLoad);
    }
    return () => {
      if (viewer) {
        viewer.removeEventListener("load", handleModelLoad);
      }
    };
  }, [isClient]);

  return (
    <div className="min-h-screen w-full flex flex-col bg-background text-foreground overflow-x-hidden">
      
      {/* 100vh Hero Wrapper matching the split-pane design */}
      <div className="h-screen w-full flex flex-col">
        {/* Top Beige Section (60%) */}
        <section className="flex-[6] bg-background relative w-full flex flex-col">
          
          {/* Navigation */}
          <header className="w-full flex items-center justify-between px-8 md:px-16 py-8 relative z-20">
            <div className="font-bold text-xl tracking-tight">
              Rewire
            </div>
            
            <nav className="hidden md:flex items-center gap-12 text-sm font-medium tracking-wide">
              <Link href="/" className="hover:opacity-70 transition-opacity">Home</Link>
              <Link href="#how-it-works" className="hover:opacity-70 transition-opacity">How it Works</Link>
              <Link href="/login" className="hover:opacity-70 transition-opacity">Log In</Link>
              <Link href="/register" className="hover:opacity-70 transition-opacity">Sign Up</Link>
            </nav>
            
            <button className="md:hidden">
              <Menu className="w-6 h-6" />
            </button>
          </header>

          {/* Hero Content */}
          <div className="flex-1 w-full flex items-center relative px-8 md:px-24">
            
            {/* Vertical Decorator */}
            <div className="absolute left-8 md:left-12 top-1/2 -translate-y-1/2 flex flex-col gap-2">
              <div className="w-2 h-2 rounded-full border-2 border-foreground bg-transparent" />
              <div className="w-2 h-2 rounded-full bg-foreground" />
              <div className="w-2 h-2 rounded-full border-2 border-foreground bg-transparent" />
            </div>

            <h1 className="text-7xl md:text-[130px] font-bold tracking-tighter leading-none z-10 max-w-2xl">
              Dopamine<br/>OS.
            </h1>

            {/* 3D Model Viewer Container */}
            <div className="absolute inset-0 w-full h-full pointer-events-none flex justify-end items-center z-10 pr-10 md:pr-32 pt-16">
              {isClient && (
                <div className="w-[300px] h-[300px] md:w-[600px] md:h-[600px] pointer-events-auto drop-shadow-2xl hover:scale-125 transition-transform duration-500">
                  <model-viewer
                    ref={modelRef}
                    src="/model2.glb"
                    auto-rotate
                    rotation-per-second="10deg"
                    camera-controls
                    disable-zoom
                    shadow-intensity="1"
                    environment-image="neutral"
                    exposure="1"
                    style={{ width: "100%", height: "100%" }}
                    // @ts-ignore - model-viewer is a custom element
                  ></model-viewer>
                </div>
              )}
            </div>

            {/* Vertical Date Decorator */}
            <div className="absolute right-8 md:right-16 top-1/2 -translate-y-1/2 transform rotate-90 origin-right text-xs font-bold tracking-[0.3em]">
              R E W I R E
            </div>
          </div>
        </section>

        {/* Bottom Split Section (40%) */}
        <section className="flex-[4] flex flex-col md:flex-row w-full z-20 shadow-[0_-10px_40px_rgba(0,0,0,0.05)]">
          
          {/* Bottom Left - Blue */}
          <div className="flex-1 bg-primary flex items-center px-8 md:px-24 relative overflow-hidden">
            <div className="space-y-6 max-w-sm">
              <h2 className="text-2xl md:text-4xl font-bold leading-tight text-foreground">
                Environmental<br/>Control.
              </h2>
              <div className="w-12 h-1.5 bg-foreground rounded-full" />
              <p className="text-sm font-semibold uppercase tracking-wider leading-relaxed text-foreground/90">
                Stop relying on willpower. Our AI automatically adapts friction based on your behavioral patterns to protect you from relapse.
              </p>
            </div>
          </div>

          {/* Bottom Right - Pink */}
          <div className="flex-1 bg-secondary flex items-center px-8 md:px-24 justify-between gap-8">
            <p className="text-sm text-foreground max-w-sm leading-relaxed font-medium">
              Meet your AI Recovery Coach. A 24/7 intelligent system that predicts cravings before they happen, reframes cognitive distortions, and tracks your dopamine baseline in real-time.
            </p>
            
            <Link href="/register" className="shrink-0">
              <button className="border-2 border-foreground text-foreground font-bold tracking-widest text-sm px-10 py-4 uppercase hover:bg-foreground hover:text-secondary transition-all shadow-lg hover:shadow-xl hover:-translate-y-1 rounded-sm">
                Get Started
              </button>
            </Link>
          </div>

        </section>
      </div>

      {/* ADDITIONAL PRODUCT INFO SECTIONS */}
      
      {/* How it works */}
      <section id="how-it-works" className="py-32 px-8 md:px-24 bg-background">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center gap-20">
          <div className="flex-1 space-y-8">
            <h2 className="text-4xl md:text-6xl font-bold tracking-tighter">How Rewire<br/>Works.</h2>
            <p className="text-xl text-foreground/70 leading-relaxed font-medium">
              We replace the failing strategy of sheer willpower with environmental design. 
              Rewire learns your unique behavioral patterns and automatically introduces friction 
              when you're vulnerable.
            </p>
            <ul className="space-y-6 pt-4">
              <li className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0 mt-1">
                  <span className="font-bold text-foreground">1</span>
                </div>
                <div>
                  <h4 className="font-bold text-xl mb-1">Baseline Assessment</h4>
                  <p className="text-foreground/70">Upon signup, we map your unique dopamine baseline and triggers through a secure assessment.</p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-1">
                  <span className="font-bold text-foreground">2</span>
                </div>
                <div>
                  <h4 className="font-bold text-xl mb-1">Environmental Lockdown</h4>
                  <p className="text-foreground/70">When your distress level spikes, the app restricts access to digital triggers automatically.</p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-foreground flex items-center justify-center shrink-0 mt-1">
                  <span className="font-bold text-background">3</span>
                </div>
                <div>
                  <h4 className="font-bold text-xl mb-1">Cognitive Coaching</h4>
                  <p className="text-foreground/70">Interact with your AI coach in real-time to de-escalate cravings before a relapse occurs.</p>
                </div>
              </li>
            </ul>
          </div>
          <div className="flex-1 bg-primary/20 rounded-[40px] p-12 aspect-square flex items-center justify-center">
            {/* Minimalist Data Viz Representation */}
            <div className="w-full h-full border-4 border-foreground rounded-[20px] p-8 flex flex-col justify-end relative">
              <div className="absolute top-8 left-8 text-2xl font-bold">Stability Index</div>
              <div className="flex items-end gap-4 h-1/2 w-full">
                {[40, 60, 45, 80, 50, 90, 75].map((h, i) => (
                  <div key={i} className={`flex-1 ${i === 6 ? 'bg-secondary' : 'bg-foreground'} rounded-t-sm`} style={{ height: `${h}%` }}></div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-32 px-8 md:px-24 bg-primary text-foreground">
        <div className="max-w-6xl mx-auto space-y-16">
          <h2 className="text-4xl md:text-6xl font-bold tracking-tighter text-center">Core Features.</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { title: "Trigger Algorithms", desc: "Machine learning models that predict exactly when and why you're most likely to crave." },
              { title: "Device Restrictions", desc: "Automated trigger management that adapts to your distress level." },
              { title: "Real-time Metrics", desc: "Visualize your recovery score, track cravings, and watch your dopamine baseline stabilize." },
              { title: "Instant Protocols", desc: "One tap activates emergency protocols that lock down devices and alert accountability partners." },
              { title: "Gamified Progress", desc: "Earn experience points, level up your resilience, and unlock badges for maintaining your streaks." },
              { title: "Secure & Private", desc: "Your recovery data is encrypted and completely private. We never sell your data." },
            ].map((feature, i) => (
              <div key={i} className="bg-background p-10 rounded-[20px] hover:-translate-y-2 transition-transform duration-300 shadow-xl">
                <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                <p className="text-foreground/80 font-medium leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-32 px-8 md:px-24 bg-secondary text-foreground text-center">
        <div className="max-w-3xl mx-auto space-y-8">
          <h2 className="text-5xl md:text-7xl font-bold tracking-tighter">Ready to rewire?</h2>
          <p className="text-xl font-medium">Join thousands of others who have successfully rewired their brains and taken their lives back. The questionnaire begins when you sign up.</p>
          <div className="pt-8">
             <Link href="/register">
              <button className="bg-foreground text-background font-bold tracking-widest text-lg px-12 py-5 uppercase hover:bg-background hover:text-foreground transition-all shadow-2xl hover:-translate-y-1 rounded-sm">
                Start Your Trial
              </button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
