"use client";

import { useState, useEffect } from "react";
import ChatInterface from "@/components/ChatInterface";
import AgentGraph from "@/components/AgentGraph";
import SettingsModal from "@/components/SettingsModal";
import { Settings, Activity, Shield, Users, Command, Terminal } from "lucide-react";

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
    <main className="h-screen w-screen bg-[#050510] text-white overflow-hidden flex flex-col relative">
       {/* Background Grid */}
       <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] pointer-events-none" />

       {/* Header */}
       <header className="h-16 border-b border-white/10 bg-black/40 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10 relative shadow-[0_5px_20px_rgba(0,0,0,0.5)]">
         <div className="flex items-center gap-4">
           <div className="w-10 h-10 border border-cyan-500/50 bg-cyan-500/10 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)]">
             <Terminal className="text-cyan-400" />
           </div>
           <div>
             <h1 className="font-orbitron text-2xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500 neon-text drop-shadow-[0_0_10px_rgba(0,243,255,0.5)]">
               OPENCORE
             </h1>
             <div className="flex items-center gap-2 text-[10px] text-gray-400 font-mono tracking-widest">
               <span>V2.0.0</span>
               <span className="text-green-500 drop-shadow-[0_0_5px_rgba(34,197,94,0.8)]">● SYSTEM ACTIVE</span>
             </div>
           </div>
         </div>

         <div className="flex items-center gap-6">
           {/* Status Indicators */}
           <div className="hidden md:flex gap-4">
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-white/5 bg-white/5 backdrop-blur-sm">
               <Activity size={14} className="text-green-400" />
               <span className="text-xs font-mono text-gray-300">UPTIME: {heartbeat?.uptime || "00:00:00"}</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-white/5 bg-white/5 backdrop-blur-sm">
               <Shield size={14} className="text-purple-400" />
               <span className="text-xs font-mono text-gray-300">SECURITY: MAX</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-white/5 bg-white/5 backdrop-blur-sm">
               <Users size={14} className="text-cyan-400" />
               <span className="text-xs font-mono text-gray-300">AGENTS: {agents.length}</span>
             </div>
           </div>

           <button
             onClick={() => setSettingsOpen(true)}
             className="p-2 hover:bg-white/10 rounded-lg transition-all border border-transparent hover:border-white/20 text-cyan-400 hover:text-white hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] active:scale-95"
           >
             <Settings size={24} />
           </button>
         </div>
       </header>

       {/* Main Content */}
       <div className="flex-1 flex overflow-hidden p-6 gap-6 relative z-0">
          {/* Left Panel: Chat */}
          <section className="w-1/3 min-w-[400px] flex flex-col gap-4 z-10 transition-all duration-500 ease-in-out">
            <div className="flex items-center justify-between px-1">
              <h2 className="text-sm font-orbitron text-cyan-500 tracking-widest flex items-center gap-2 drop-shadow-[0_0_5px_rgba(6,182,212,0.8)]">
                <Command size={16} /> COMMAND LINE
              </h2>
            </div>
            <div className="flex-1 h-full min-h-0">
               <ChatInterface onAgentsUpdate={setAgents} />
            </div>
          </section>

          {/* Right Panel: Visualization */}
          <section className="flex-1 flex flex-col gap-4 z-0 transition-all duration-500 ease-in-out">
             <div className="flex items-center justify-between px-1">
              <h2 className="text-sm font-orbitron text-purple-500 tracking-widest flex items-center gap-2 drop-shadow-[0_0_5px_rgba(168,85,247,0.8)]">
                <Activity size={16} /> NEURAL TOPOLOGY
              </h2>
            </div>
            <div className="flex-1 border border-white/10 rounded-xl bg-black/20 backdrop-blur-sm relative overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)]">
               <AgentGraph agents={agents} />
            </div>
          </section>
       </div>

       <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </main>
  );
}
