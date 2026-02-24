"use client";

import { useState, useEffect, useCallback } from "react";
import ChatInterface from "@/components/ChatInterface";
import AgentGraph from "@/components/AgentGraph";
import { HEARTBEAT_INTERVAL, API_AGENTS, API_HEARTBEAT } from "@/constants";
import SettingsModal from "@/components/SettingsModal";
import ThemeSelector from "@/components/ThemeSelector";
import { Settings, Activity, Shield, Users, Command } from "lucide-react";
import Image from "next/image";
import { AgentGraphData } from "@/types/agent";

export default function Home() {
  const [graphData, setGraphData] = useState<AgentGraphData>({ nodes: [], edges: [] });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [heartbeat, setHeartbeat] = useState<any>(null);
  const [uptimeString, setUptimeString] = useState("00:00:00");

  const fetchAgents = useCallback(async () => {
    try {
      const res = await fetch(API_AGENTS);
      const data = await res.json();
      if (data.graph) {
          setGraphData(data.graph);
      } else if (data.agents) {
          // Fallback for older API format
          setGraphData({
              nodes: data.agents.map((a: string) => ({ id: a, name: a, parent: null })),
              edges: []
          });
      }
    } catch (e) {
      console.error("Failed to fetch agents", e);
    }
  }, []);

  const fetchHeartbeat = useCallback(async () => {
    try {
      const res = await fetch(API_HEARTBEAT);
      if (res.ok) {
        const data = await res.json();
        setHeartbeat(data);
      }
    } catch (e) {
      console.error("Failed to fetch heartbeat", e);
    }
  }, []);

  useEffect(() => {
    fetchAgents();
    fetchHeartbeat();
    const interval = setInterval(fetchHeartbeat, HEARTBEAT_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchAgents, fetchHeartbeat]);

  useEffect(() => {
    if (!heartbeat?.start_time) return;

    const updateUptime = () => {
      const start = new Date(heartbeat.start_time);
      const now = new Date();
      const diff = Math.max(0, now.getTime() - start.getTime());

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setUptimeString(
          `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      );
    };

    updateUptime(); // Update immediately
    const interval = setInterval(updateUptime, 1000);
    return () => clearInterval(interval);
  }, [heartbeat?.start_time]);

  return (
    <main className="h-screen w-screen bg-bg-primary text-text-primary overflow-hidden flex flex-col relative transition-colors duration-300">
       {/* Header */}
       <header className="h-20 border-b border-border-primary bg-bg-secondary flex items-center justify-between px-6 shrink-0 z-10 relative shadow-md shadow-accent-3/5 transition-colors duration-300">
         <div className="flex items-center gap-4">
           {/* Legacy Logo */}
           <div className="relative w-12 h-12 filter drop-shadow-[0_0_5px_var(--accent-2)] animate-[flicker_4s_infinite]">
              <Image src="/logo.svg" alt="OpenCore Logo" fill className="object-contain" priority />
           </div>

           <div>
             <h1 className="font-orbitron text-2xl font-black tracking-[2px] text-text-primary uppercase neon-text-logo">
               OPENCORE
             </h1>
             <div className="flex items-center gap-2 text-[10px] text-text-secondary font-mono tracking-widest">
               <span>V{heartbeat?.version || "..."}</span>
               <span className="text-status-active drop-shadow-[0_0_5px_var(--status-active)]">● SYSTEM ACTIVE</span>
             </div>
           </div>
         </div>

         <div className="flex items-center gap-6">
           {/* Status Indicators */}
           <div className="hidden md:flex gap-4">
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-border-primary bg-bg-tertiary backdrop-blur-sm">
               <Activity size={14} className="text-status-active" />
               <span className="text-xs font-mono text-text-secondary">UPTIME: {uptimeString}</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-border-primary bg-bg-tertiary backdrop-blur-sm">
               <Shield size={14} className="text-accent-2" />
               <span className="text-xs font-mono text-text-secondary">SECURITY: MAX</span>
             </div>
             <div className="flex items-center gap-2 px-3 py-1 rounded border border-border-primary bg-bg-tertiary backdrop-blur-sm">
               <Users size={14} className="text-accent-1" />
               <span className="text-xs font-mono text-text-secondary">AGENTS: {graphData.nodes.length}</span>
             </div>
           </div>

           <div className="flex items-center gap-3">
             <ThemeSelector />

             <button
               onClick={() => setSettingsOpen(true)}
               aria-label="Settings"
               className="p-2 hover:bg-bg-tertiary rounded-lg transition-all border border-transparent hover:border-border-primary text-accent-1 hover:text-text-primary hover:shadow-[0_0_15px_var(--accent-1)] active:scale-95"
             >
               <Settings size={24} />
             </button>
           </div>
         </div>
       </header>

       {/* Main Content */}
       <div className="flex-1 flex overflow-hidden p-6 gap-6 relative z-0">
          {/* Left Panel: Chat */}
          <section className="w-1/3 min-w-[400px] flex flex-col gap-4 z-10 transition-all duration-500 ease-in-out">
            <div className="flex items-center justify-between px-1 border-b border-border-primary pb-2">
              <h2 className="text-sm font-orbitron text-accent-1 tracking-[2px] uppercase flex items-center gap-2">
                <Command size={16} /> COMMAND LINE
              </h2>
            </div>
            <div className="flex-1 h-full min-h-0">
               <ChatInterface onGraphUpdate={setGraphData} />
            </div>
          </section>

          {/* Right Panel: Visualization */}
          <section className="flex-1 flex flex-col gap-4 z-0 transition-all duration-500 ease-in-out">
             <div className="flex items-center justify-between px-1 border-b border-border-primary pb-2">
              <h2 className="text-sm font-orbitron text-accent-1 tracking-[2px] uppercase flex items-center gap-2">
                <Activity size={16} /> NEURAL TOPOLOGY
              </h2>
            </div>
            <div className="flex-1 border border-border-primary rounded bg-bg-secondary relative overflow-hidden shadow-[0_0_30px_rgba(0,0,0,0.5)] transition-colors duration-300">
               <AgentGraph graphData={graphData} />
            </div>
          </section>
       </div>

       <SettingsModal isOpen={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </main>
  );
}
