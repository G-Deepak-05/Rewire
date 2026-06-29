"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, LayoutDashboard, BookOpen, MessageSquare, ShieldAlert, LogOut } from "lucide-react";
import { useStore } from "@/lib/store";
import { useRouter } from "next/navigation";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Journal", href: "/dashboard/journal", icon: BookOpen },
  { name: "AI Coach", href: "/dashboard/coach", icon: MessageSquare },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useStore(state => state.logout);

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  return (
    <div className="flex h-screen bg-background overflow-hidden relative">
      {/* Global Ambient Glow */}
      <div className="absolute top-0 left-[20%] w-[40%] h-[40%] bg-primary/5 blur-[150px] rounded-full pointer-events-none" />

      {/* Sidebar */}
      <aside className="w-64 border-r border-border/50 glass z-10 flex flex-col justify-between hidden md:flex">
        <div>
          <div className="h-16 flex items-center px-6 border-b border-border/50">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="bg-primary p-1.5 rounded-lg">
                <Brain className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="font-bold text-lg tracking-tight">Rewire</span>
            </Link>
          </div>
          <nav className="p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                    isActive 
                      ? "bg-primary/10 text-primary font-medium" 
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
        
        <div className="p-4 space-y-2">
          <Link
            href="/emergency"
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-destructive hover:bg-destructive/10 transition-colors font-medium border border-destructive/20"
          >
            <ShieldAlert className="w-5 h-5" />
            Emergency Mode
          </Link>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors text-left"
          >
            <LogOut className="w-5 h-5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto z-10 relative">
        <div className="md:hidden h-16 border-b border-border/50 glass flex items-center justify-between px-4 sticky top-0 z-20">
           <Link href="/dashboard" className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-primary" />
              <span className="font-bold">Rewire</span>
            </Link>
            <Link href="/emergency" className="text-destructive">
              <ShieldAlert className="w-5 h-5" />
            </Link>
        </div>
        <div className="p-6 md:p-8 max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
