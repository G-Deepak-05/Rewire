"use client";

import { useState, useRef, useEffect } from "react";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, ShieldAlert } from "lucide-react";

export default function CoachPage() {
  const [messages, setMessages] = useState([
    { role: "assistant", content: "I am your Rewire AI coach. I analyze your stress metrics and triggers to keep you on the protocol. What's on your mind right now?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const res = await api.post("/coach/chat", {
        message: userMessage,
        context: "Chat interface"
      });
      
      setMessages(prev => [...prev, { role: "assistant", content: res.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: "assistant", content: "I'm having trouble connecting to the core system right now. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-in fade-in duration-500 relative">
       {/* Background ambient glow */}
       <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[60%] h-[60%] bg-primary/5 blur-[120px] rounded-full pointer-events-none" />
       
      <div className="mb-6 flex justify-between items-center relative z-10">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Recovery Coach</h1>
          <p className="text-muted-foreground mt-1">Real-time cognitive interventions and support.</p>
        </div>
      </div>

      <Card className="flex-1 flex flex-col glass-card border-primary/20 overflow-hidden relative z-10">
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-4 pb-4">
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                    <Bot className="w-5 h-5 text-primary" />
                  </div>
                )}
                
                <div className={`px-4 py-3 rounded-2xl max-w-[80%] text-sm ${
                  msg.role === "user" 
                    ? "bg-primary text-primary-foreground rounded-tr-sm" 
                    : "bg-muted/50 border border-border/50 text-foreground rounded-tl-sm"
                }`}>
                  {msg.content}
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center shrink-0">
                    <User className="w-5 h-5 text-accent" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-3 justify-start">
                <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5 text-primary" />
                </div>
                <div className="px-4 py-3 rounded-2xl bg-muted/50 border border-border/50 flex items-center gap-2">
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="p-4 bg-background/50 backdrop-blur-sm border-t border-border/50">
          <form onSubmit={handleSend} className="flex gap-2">
            <Input 
              placeholder="I'm feeling a strong urge right now..." 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="bg-background border-primary/20 focus-visible:ring-primary/50"
              disabled={isLoading}
            />
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()} className="bg-primary hover:bg-primary/90 shrink-0">
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
}
