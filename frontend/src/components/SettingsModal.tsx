"use client";

import { useState, useEffect } from "react";
import { X, Save, Key, Cpu, RefreshCw } from "lucide-react";
import { toast } from "sonner";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [config, setConfig] = useState<any>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchConfig();
    }
  }, [isOpen]);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const res = await fetch("/config");
      const data = await res.json();
      setConfig(data);
    } catch (err) {
      toast.error("Failed to load configuration");
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    try {
      const res = await fetch("/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      if (data.status === "success") {
        toast.success("Configuration saved");
        onClose();
      } else {
        toast.error("Error saving config: " + data.message);
      }
    } catch (err) {
      toast.error("Failed to save configuration");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-[#0a0a15] border border-cyan-500/30 rounded-xl shadow-[0_0_30px_rgba(0,243,255,0.1)] overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/5 shrink-0">
          <h2 className="text-xl font-bold flex items-center gap-2 text-cyan-400 font-orbitron tracking-wider">
            <Cpu size={24} /> SYSTEM CONFIGURATION
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-6 flex-1 scrollbar-thin scrollbar-thumb-cyan-900 scrollbar-track-transparent">
           {loading ? (
             <div className="flex justify-center p-8"><RefreshCw className="animate-spin text-cyan-500" /></div>
           ) : (
             <>
               {/* LLM Model Selection */}
               <div className="space-y-2">
                 <label className="text-xs text-cyan-500 font-mono tracking-widest uppercase mb-1 block">ACTIVE MODEL NODE</label>
                 <select
                   value={config.LLM_MODEL || "gpt-4o"}
                   onChange={(e) => setConfig({...config, LLM_MODEL: e.target.value})}
                   className="w-full bg-black/40 border border-white/20 rounded p-3 text-white focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/50 font-mono text-sm transition-all appearance-none"
                   style={{backgroundImage: 'none'}}
                 >
                   <option value="gpt-4o">OpenAI GPT-4o</option>
                   <option value="anthropic/claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
                   <option value="dashscope/qwen-turbo">Qwen Turbo (Free Tier)</option>
                   <option value="gemini/gemini-1.5-flash-latest">Gemini Flash (Free Tier)</option>
                   <option value="groq/llama3-8b-8192">Llama 3 (Groq/Free)</option>
                   <option value="xai/grok-2-vision-1212">Grok 2 (xAI)</option>
                   <option value="mistral/mistral-large-latest">Mistral Large</option>
                   <option value="ollama/llama3">Local Ollama (Llama 3)</option>
                 </select>
               </div>

               {/* API Keys Section */}
               <div className="space-y-4">
                 <h3 className="text-lg font-semibold text-white/80 border-b border-white/10 pb-2 mt-4 font-orbitron tracking-wide">NEURAL CREDENTIALS</h3>

                 {[
                   { key: "OPENAI_API_KEY", label: "OpenAI Key", hasKey: config.HAS_OPENAI_KEY },
                   { key: "ANTHROPIC_API_KEY", label: "Anthropic Key", hasKey: config.HAS_ANTHROPIC_KEY },
                   { key: "GEMINI_API_KEY", label: "Gemini Key", hasKey: config.HAS_GEMINI_KEY },
                   { key: "GROQ_API_KEY", label: "Groq Key", hasKey: config.HAS_GROQ_KEY },
                   { key: "DASHSCOPE_API_KEY", label: "DashScope Key", hasKey: config.HAS_DASHSCOPE_KEY },
                   { key: "XAI_API_KEY", label: "xAI (Grok) Key", hasKey: config.HAS_XAI_KEY },
                   { key: "MISTRAL_API_KEY", label: "Mistral Key", hasKey: config.HAS_MISTRAL_KEY },
                 ].map((item) => (
                   <div key={item.key} className="flex flex-col gap-1 group">
                     <label className="text-xs text-gray-500 font-mono uppercase group-hover:text-cyan-400/70 transition-colors">{item.label}</label>
                     <div className="flex gap-2">
                       <div className="relative flex-1">
                         <Key size={14} className="absolute left-3 top-3.5 text-gray-600 group-focus-within:text-cyan-500 transition-colors" />
                         <input
                           type="password"
                           placeholder={item.hasKey ? "•••••••••••••••• (Set)" : "Enter API Key"}
                           value={config[item.key] || ""}
                           onChange={(e) => setConfig({...config, [item.key]: e.target.value})}
                           className="w-full bg-black/40 border border-white/10 rounded pl-9 p-2.5 text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500/30 transition-all font-mono placeholder-gray-700"
                         />
                       </div>
                       {item.hasKey && <div className="px-3 py-1 text-[10px] font-mono tracking-wider bg-green-500/10 text-green-400 border border-green-500/20 rounded flex items-center shadow-[0_0_10px_rgba(34,197,94,0.1)]">LINKED</div>}
                     </div>
                   </div>
                 ))}
               </div>
             </>
           )}
        </div>

        <div className="p-4 border-t border-white/10 bg-white/5 flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded hover:bg-white/10 transition-colors text-sm font-mono text-gray-400 hover:text-white"
          >
            CANCEL
          </button>
          <button
            onClick={saveConfig}
            disabled={loading}
            className="px-6 py-2 bg-cyan-600/80 hover:bg-cyan-500 text-white rounded font-medium shadow-[0_0_15px_rgba(6,182,212,0.4)] hover:shadow-[0_0_25px_rgba(6,182,212,0.6)] transition-all flex items-center gap-2 font-orbitron tracking-wider text-sm border border-cyan-400/50"
          >
            <Save size={16} /> SAVE CONFIG
          </button>
        </div>
      </div>
    </div>
  );
}
