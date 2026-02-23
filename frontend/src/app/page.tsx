"use client";

import { useState, useEffect } from "react";
import ChatInterface from "@/components/ChatInterface";
import AgentGraph from "@/components/AgentGraph";
import SettingsModal from "@/components/SettingsModal";
import { Settings, Activity, Shield, Users, Command, Terminal } from "lucide-react";
import Image from "next/image";

export default function Home() {
  const [agents, setAgents] = useState<string[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [heartbeat, setHeartbeat] = useState<any>(null);

  useEffect(() => {
    fetchAgents();
    fetchHeartbeat();
    const interval = setInterval(fetchHeartbeat, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch("/agents");
      const data = await res.json();
      if (data.agents) setAgents(data.agents);
    } catch (e) {
      console.error("Failed to fetch agents", e);
    }
  };

  const fetchHeartbeat = async () => {
    try {
      const res = await fetch("/heartbeat");
      if (res.ok) {
        const data = await res.json();
        setHeartbeat(data);
      }
    } catch (e) {
      console.error("Failed to fetch heartbeat", e);
    }
  };

  return (
    <main className="h-screen w-screen bg-[#050505] text-white overflow-hidden flex flex-col relative">
       {/* Header */}
       <header className="h-20 border-b border-[#333] bg-[#0a0a0a] flex items-center justify-between px-6 shrink-0 z-10 relative shadow-[5px_0_20px_rgba(0,255,65,0.05)]">
         <div className="flex items-center gap-4">
           {/* Legacy Logo */}
           <div className="relative w-12 h-12 filter drop-shadow-[0_0_5px_var(--color-neon-purple)] animate-[flicker_4s_infinite]">
              <Image src="/logo.svg" alt="OpenCore Logo" fill className="object-contain" priority />
           </div>

           <div>
             <h1 className="font-orbitron text-2xl font-black tracking-[2px] text-[#e0e0e0] uppercase neon-text-logo">
               OPENCORE
             </h1>
             <div className="flex items-center gap-2 text-[10px] text-[#888888] font-mono tracking-widest">
               <span>V2.0.1</span>
               <span className="text-[#00ff41] drop-shadow-[0_0_5px_rgba(0,255,65,0.8)]">● SYSTEM ACTIVE</span>
             </div>
           </div>
         </div>

         <div className="flex items-center gap-6">
           {/* Status Indicators */}
           <div className="hidden md:flex gap-4">
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-[#333] bg-[#111] backdrop-blur-sm">
               <Activity size={14} className="text-[#00ff41]" />
               <span className="text-xs font-mono text-[#888]">UPTIME: {heartbeat?.uptime || "00:00:00"}</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-[#333] bg-[#111] backdrop-blur-sm">
               <Shield size={14} className="text-[#ff00ff]" />
               <span className="text-xs font-mono text-[#888]">SECURITY: MAX</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-[#333] bg-[#111] backdrop-blur-sm">
               <Users size={14} className="text-[#00ffff]" />
               <span className="text-xs font-mono text-[#888]">AGENTS: {agents.length}</span>
             </div>
           </div>

           <button
             onClick={() => setSettingsOpen(true)}
             className="p-2 hover:bg-[#111] rounded-lg transition-all border border-transparent hover:border-[#333] text-[#00ffff] hover:text-white hover:shadow-[0_0_15px_rgba(0,255,255,0.3)] active:scale-95"
           >
             <Settings size={24} />
           </button>
         </div>
       </header>

       {/* Main Content */}
       <div className="flex-1 flex overflow-hidden p-6 gap-6 relative z-0">
          {/* Left Panel: Chat */}
          <section className="w-1/3 min-w-[400px] flex flex-col gap-4 z-10 transition-all duration-500 ease-in-out">
            <div className="flex items-center justify-between px-1 border-b border-[#333] pb-2">
              <h2 className="text-sm font-orbitron text-[#00ffff] tracking-[2px] uppercase flex items-center gap-2">
                <Command size={16} /> COMMAND LINE
              </h2>
            </div>
            <div className="flex-1 h-full min-h-0">
               <ChatInterface onAgentsUpdate={setAgents} />
            </div>
          </section>

          {/* Right Panel: Visualization */}
          <section className="flex-1 flex flex-col gap-4 z-0 transition-all duration-500 ease-in-out">
             <div className="flex items-center justify-between px-1 border-b border-[#333] pb-2">
              <h2 className="text-sm font-orbitron text-[#00ffff] tracking-[2px] uppercase flex items-center gap-2">
                <Activity size={16} /> NEURAL TOPOLOGY
              </h2>
            </div>
            <div className="flex-1 border border-[#333] rounded bg-[#0a0a0a] relative overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)]">
               <AgentGraph agents={agents} />
            </div>
          </section>
       </div>

       <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </main>
  );
}
