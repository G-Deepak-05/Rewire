"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Activity, Loader2 } from "lucide-react";
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
import { toast } from "sonner";

const registerSchema = z.object({
  email: z.string().email("Please enter a valid email"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: z.infer<typeof registerSchema>) {
    setIsLoading(true);
    try {
      await api.post("/auth/register", values);
      toast.success("Account created successfully!");
      router.push("/login");
    } catch (error: any) {
      const detail = error.response?.data?.detail;
      const message = typeof detail === 'string' ? detail : "Registration failed. Please check your inputs.";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background">
      {/* Form Side */}
      <div className="flex items-center justify-center p-8 order-2 lg:order-1">
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-full max-w-md space-y-8"
        >
          <div className="text-center lg:text-left">
            <h1 className="text-3xl font-bold tracking-tight">Start Protocol</h1>
            <p className="text-muted-foreground mt-2">
              Create an account to initialize your recovery system
            </p>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="email"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Email</FormLabel>
                    <FormControl>
                      <Input placeholder="name@example.com" {...field} className="bg-background" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="password"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                      <Input type="password" placeholder="••••••••" {...field} className="bg-background" />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Create account"}
              </Button>
            </form>
          </Form>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link href="/login" className="font-semibold text-primary hover:underline">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>

      {/* Visual Side */}
      <div className="hidden lg:flex flex-col justify-center items-center relative overflow-hidden bg-muted/20 border-l border-border order-1 lg:order-2">
        <div className="absolute top-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-primary/10 blur-[100px]" />
        <div className="absolute bottom-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-accent/10 blur-[100px]" />
        
        <div className="relative z-10 max-w-lg text-center p-8">
          <Activity className="w-16 h-16 text-primary mx-auto mb-8 animate-float" />
          <h2 className="text-4xl font-bold mb-4">Rewire Your Baseline</h2>
          <p className="text-lg text-muted-foreground">
            Stop relying on willpower. Use systematic environmental control to overcome addiction.
          </p>
        </div>
      </div>
    </div>
  );
}
