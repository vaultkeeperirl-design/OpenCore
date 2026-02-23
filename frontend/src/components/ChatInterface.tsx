"use client";

import { useState, useEffect, useRef } from "react";
import { Send, User, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import VoiceInput from "./VoiceInput";
import { toast } from "sonner";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

export default function ChatInterface({
  onAgentsUpdate
}: {
  onAgentsUpdate: (agents: string[]) => void
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "System Online. Neural interface active. How can I assist you today?",
      timestamp: Date.now(),
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content }),
      });

      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (data.agents) {
        onAgentsUpdate(data.agents);
      }
    } catch (err) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "System Error: Unable to reach neural core. Check connection.",
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error("Failed to communicate with backend");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black/20 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden relative shadow-[0_0_20px_rgba(0,0,0,0.5)]">
      {/* Header */}
      <div className="p-4 border-b border-white/5 bg-white/5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
           <Sparkles className="text-cyan-400" size={18} />
           <span className="font-orbitron text-cyan-400 tracking-wider text-sm">LIVE FEED</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${loading ? "bg-yellow-400 animate-pulse shadow-[0_0_10px_rgba(250,204,21,0.5)]" : "bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"}`}></div>
          <span className="text-xs text-gray-400 font-mono tracking-widest">{loading ? "PROCESSING" : "IDLE"}</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-cyan-900/50 scrollbar-track-transparent">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
            >
              <div className={`w-10 h-10 rounded-lg border flex items-center justify-center shrink-0 shadow-lg ${
                msg.role === "user"
                  ? "bg-purple-500/10 border-purple-500/40 text-purple-400 shadow-[0_0_15px_rgba(168,85,247,0.1)]"
                  : "bg-cyan-500/10 border-cyan-500/40 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.1)]"
              }`}>
                {msg.role === "user" ? <User size={20} /> : <img src="/logo.svg" alt="OpenCore" className="w-6 h-6" />}
              </div>

              <div className={`max-w-[80%] p-4 rounded-xl border text-sm font-mono leading-relaxed shadow-md backdrop-blur-sm ${
                msg.role === "user"
                  ? "bg-purple-900/10 border-purple-500/20 text-purple-100 rounded-tr-none"
                  : "bg-cyan-900/10 border-cyan-500/20 text-cyan-100 rounded-tl-none"
              }`}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-4"
          >
             <div className="w-10 h-10 rounded-lg border border-cyan-500/40 bg-cyan-500/10 flex items-center justify-center text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
                <img src="/logo.svg" alt="Processing..." className="w-6 h-6 animate-pulse" />
             </div>
             <div className="flex items-center gap-1.5 h-10 px-2">
               <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.3s] shadow-[0_0_5px_rgba(6,182,212,0.8)]"></span>
               <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.15s] shadow-[0_0_5px_rgba(6,182,212,0.8)]"></span>
               <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce shadow-[0_0_5px_rgba(6,182,212,0.8)]"></span>
             </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10 bg-black/40 backdrop-blur-md shrink-0">
        <form onSubmit={handleSubmit} className="flex gap-3 relative items-center">
           <VoiceInput onTranscript={(text) => setInput(text)} disabled={loading} />

           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             placeholder="Enter command directive..."
             disabled={loading}
             className="flex-1 bg-black/50 border border-white/10 rounded-xl px-5 py-3 text-white focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-mono text-sm placeholder-gray-600 shadow-inner"
           />

           <button
             type="submit"
             disabled={!input.trim() || loading}
             className="p-3 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-400 border border-cyan-500/50 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] active:scale-95"
           >
             <Send size={20} />
           </button>
        </form>
      </div>
    </div>
  );
}
