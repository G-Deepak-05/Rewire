"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Brain, ArrowRight, Loader2, Eye, EyeOff } from "lucide-react";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";
import { useStore } from "@/lib/store";
import { toast } from "sonner";

const loginSchema = z.object({
  username: z.string().email("Please enter a valid email"),
  password: z.string().min(1, "Password is required"),
});

const ECGBackground = () => (
  <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
    {/* Teal Signal - Top Left */}
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.4 }}
      transition={{ duration: 4, repeat: Infinity, repeatType: "reverse", ease: "easeInOut" }}
      className="absolute top-[10%] -left-[5%] text-[#4CB8C4] rotate-[-5deg]"
    >
      <svg width="600" height="200" viewBox="0 0 600 200" fill="none" stroke="currentColor" strokeWidth="2.5">
        <path d="M0 100 L250 100 L270 50 L300 170 L340 20 L370 130 L390 100 L600 100" />
      </svg>
    </motion.div>

    {/* Coral Signal - Bottom Right */}
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.3 }}
      transition={{ duration: 5, repeat: Infinity, repeatType: "reverse", ease: "easeInOut", delay: 1.5 }}
      className="absolute bottom-[15%] -right-[5%] text-[#F56C86] rotate-[5deg]"
    >
      <svg width="500" height="150" viewBox="0 0 500 150" fill="none" stroke="currentColor" strokeWidth="3">
        <path d="M0 75 L180 75 L195 40 L215 120 L245 20 L270 95 L285 75 L500 75" />
      </svg>
    </motion.div>

    {/* Subtle Dark Signal - Center */}
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 0.08 }}
      transition={{ duration: 6, repeat: Infinity, repeatType: "reverse", ease: "easeInOut", delay: 3 }}
      className="absolute top-[50%] left-[20%] text-[#151515]"
    >
      <svg width="800" height="250" viewBox="0 0 800 250" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M0 125 L350 125 L375 60 L410 200 L460 40 L495 160 L520 125 L800 125" />
      </svg>
    </motion.div>
  </div>
);

export default function LoginPage() {
  const router = useRouter();
  const setTokens = useStore((state) => state.setTokens);
  const setUser = useStore((state) => state.setUser);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof loginSchema>) {
    setIsLoading(true);
    try {
      const response = await api.post("/auth/login", {
        email: values.username,
        password: values.password,
      });

      const { access_token, refresh_token } = response.data;
      setTokens(access_token, refresh_token);
      
      // Fetch user profile
      const profileRes = await api.get("/users/me", {
        headers: { Authorization: `Bearer ${access_token}` }
      });
      setUser(profileRes.data);
      
      toast.success("Welcome back!");
      router.push("/dashboard");
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'string' ? detail : "Login failed. Please check your credentials.";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-[#F6F2EA] relative overflow-hidden text-[#151515] font-sans selection:bg-[#4CB8C4]/20">
      {/* Subtle Grid Background */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#15151506_1px,transparent_1px),linear-gradient(to_bottom,#15151506_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none z-0" />
      
      {/* ECG Background */}
      <ECGBackground />

      {/* Visual Side */}
      <div className="hidden lg:flex flex-col justify-center items-center relative overflow-hidden bg-[#4CB8C4]/[0.03] border-r border-[#D8D2C7]/30 z-10">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full bg-[#4CB8C4]/10 blur-[120px] mix-blend-multiply" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] rounded-full bg-[#F56C86]/5 blur-[120px] mix-blend-multiply" />
        
        <div className="relative z-10 max-w-[440px] text-center p-12 bg-white/50 backdrop-blur-xl rounded-[32px] border border-white shadow-[0_8px_40px_rgba(0,0,0,0.02)]">
          <Brain className="w-12 h-12 text-[#4CB8C4] mx-auto mb-8 animate-float" strokeWidth={1.5} />
          <h2 className="text-[32px] font-bold mb-4 tracking-tight text-[#151515] leading-tight">Reclaim Your Mind</h2>
          <p className="text-[16px] text-[#151515]/70 leading-relaxed font-normal">
            Sign in to access your protocol and continue your journey towards freedom.
          </p>
        </div>
      </div>

      {/* Form Side */}
      <div className="flex items-center justify-center p-8 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="w-full max-w-[420px] bg-white p-10 md:p-12 rounded-[32px] shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-[#D8D2C7]/40"
        >
          <div className="mb-10 text-center sm:text-left">
            <h1 className="text-[32px] font-bold tracking-tight text-[#151515] mb-2">Welcome back</h1>
            <p className="text-[#151515]/60 text-[15px] leading-relaxed">
              Enter your credentials to access your account.
            </p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-7">
              <FormField
                control={form.control}
                name="username"
                render={({ field }) => (
                  <FormItem className="space-y-2">
                    <FormLabel className="text-[12px] font-semibold text-[#151515]/80 tracking-[0.02em]">Email</FormLabel>
                    <FormControl>
                      <Input 
                        placeholder="name@example.com" 
                        {...field} 
                        className="bg-[#FBF9F5] border border-[#D8D2C7] rounded-[16px] h-[54px] px-5 text-[15px] text-[#151515] focus-visible:ring-[4px] focus-visible:ring-[#4CB8C4]/15 focus-visible:border-[#4CB8C4] transition-all duration-200 shadow-none placeholder:text-[#151515]/30 hover:border-[#D8D2C7]/80" 
                      />
                    </FormControl>
                    <FormMessage className="text-[#F56C86] text-xs" />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem className="space-y-2">
                    <FormLabel className="text-[12px] font-semibold text-[#151515]/80 tracking-[0.02em]">Password</FormLabel>
                    <FormControl>
                      <div className="relative group">
                        <Input 
                          type={showPassword ? "text" : "password"} 
                          placeholder="••••••••" 
                          {...field} 
                          className="bg-[#FBF9F5] border border-[#D8D2C7] rounded-[16px] h-[54px] pl-5 pr-12 text-[15px] text-[#151515] focus-visible:ring-[4px] focus-visible:ring-[#4CB8C4]/15 focus-visible:border-[#4CB8C4] transition-all duration-200 shadow-none placeholder:text-[#151515]/30 hover:border-[#D8D2C7]/80" 
                        />
                        <button 
                          type="button" 
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-[#151515]/30 hover:text-[#151515]/70 transition-colors p-1"
                        >
                          {showPassword ? <EyeOff className="w-[18px] h-[18px]" /> : <Eye className="w-[18px] h-[18px]" />}
                        </button>
                      </div>
                    </FormControl>
                    <FormMessage className="text-[#F56C86] text-xs" />
                  </FormItem>
                )}
              />
              
              <div className="pt-2">
                <Button type="submit" className="w-full h-[56px] text-[15px] font-semibold tracking-[0.02em] rounded-[16px] bg-[#151515] text-white shadow-[0_2px_10px_rgba(21,21,21,0.06)] hover:shadow-[0_6px_20px_rgba(21,21,21,0.1)] hover:-translate-y-[1px] transition-all duration-200" disabled={isLoading}>
                  {isLoading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : "Sign in"}
                </Button>
              </div>
            </form>
          </Form>

          <p className="text-center text-[14px] text-[#151515]/60 mt-8">
            Don't have an account?{" "}
            <Link href="/register" className="font-semibold text-[#4CB8C4] hover:text-[#4CB8C4]/80 transition-colors hover:underline underline-offset-4">
              Start your protocol
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
