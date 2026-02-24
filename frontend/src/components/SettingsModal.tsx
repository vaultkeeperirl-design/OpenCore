"use client";

import { useState, useEffect } from "react";
import { X, Save, Key, Cpu, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import Image from "next/image";
import { API_CONFIG, API_AUTH_STATUS, API_AUTH_QWEN_LOGIN, API_AUTH_GOOGLE_LOGIN } from "@/constants";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const [config, setConfig] = useState<any>({});
  const [authStatus, setAuthStatus] = useState<any>({ google: false, qwen: false });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchConfig();
    }
  }, [isOpen]);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const [configRes, authRes] = await Promise.all([
        fetch(API_CONFIG),
        fetch(API_AUTH_STATUS)
      ]);

      const configData = await configRes.json();
      const authData = await authRes.json();

      setConfig(configData);
      setAuthStatus(authData);
    } catch (err) {
      toast.error("Failed to load configuration");
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    try {
      const res = await fetch(API_CONFIG, {
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl bg-[#0a0a0a] border border-[#00ffff] rounded shadow-[0_0_30px_rgba(0,255,255,0.1)] overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-4 border-b border-[#333] bg-[#111] shrink-0">
          <h2 className="text-xl font-bold flex items-center gap-2 text-[#00ffff] font-orbitron tracking-[2px]">
            <Cpu size={24} /> SYSTEM CONFIGURATION
          </h2>
          <button onClick={onClose} className="p-1 hover:bg-[#333] rounded transition-colors text-[#888] hover:text-[#ff00ff]">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-6 flex-1 scrollbar-thin scrollbar-thumb-[#00ffff] scrollbar-track-[#111]">
           {loading ? (
             <div className="flex justify-center p-8"><RefreshCw className="animate-spin text-[#00ffff]" /></div>
           ) : (
             <>
               {/* LLM Model Selection */}
               <div className="space-y-2">
                 <label className="text-xs text-[#00ffff] font-mono tracking-widest uppercase mb-1 block">ACTIVE MODEL NODE</label>
                 <select
                   value={config.LLM_MODEL || "gpt-4o"}
                   onChange={(e) => setConfig({...config, LLM_MODEL: e.target.value})}
                   className="w-full bg-black border border-[#333] rounded p-3 text-[#e0e0e0] focus:border-[#00ffff] focus:outline-none focus:ring-1 focus:ring-[#00ffff]/50 font-mono text-sm transition-all appearance-none"
                   style={{backgroundImage: 'none'}}
                 >
                   <option value="gpt-4o">OpenAI GPT-4o</option>
                   <option value="anthropic/claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
                   <option value="dashscope/qwen-turbo">Qwen Turbo (Free Tier)</option>
                   <option value="gemini/gemini-1.5-flash-001">Gemini Flash (Free Tier)</option>
                   <option value="groq/llama3-8b-8192">Llama 3 (Groq/Free)</option>
                   <option value="xai/grok-2-vision-1212">Grok 2 (xAI)</option>
                   <option value="mistral/mistral-large-latest">Mistral Large</option>
                   <option value="ollama/llama3">Local Ollama (Llama 3)</option>
                 </select>
               </div>

               {/* API Keys Section */}
               <div className="space-y-4">
                 <h3 className="text-lg font-semibold text-[#e0e0e0] border-b border-[#333] pb-2 mt-4 font-orbitron tracking-wide">NEURAL CREDENTIALS</h3>

                 {[
                   { key: "OPENAI_API_KEY", label: "OpenAI Key", hasKey: config.HAS_OPENAI_KEY },
                   { key: "ANTHROPIC_API_KEY", label: "Anthropic Key", hasKey: config.HAS_ANTHROPIC_KEY },
                   { key: "GEMINI_API_KEY", label: "Gemini Key", hasKey: config.HAS_GEMINI_KEY,
                     isOAuth: authStatus.google, oauthLabel: "GOOGLE ADC ACTIVE" },
                   { key: "GROQ_API_KEY", label: "Groq Key", hasKey: config.HAS_GROQ_KEY },
                   { key: "DASHSCOPE_API_KEY", label: "DashScope Key (Qwen)", hasKey: config.HAS_DASHSCOPE_KEY,
                     isOAuth: authStatus.qwen, oauthLabel: "QWEN OAUTH ACTIVE" },
                   { key: "XAI_API_KEY", label: "xAI (Grok) Key", hasKey: config.HAS_XAI_KEY },
                   { key: "MISTRAL_API_KEY", label: "Mistral Key", hasKey: config.HAS_MISTRAL_KEY },
                 ].map((item: any) => (
                   <div key={item.key} className="flex flex-col gap-1 group">
                     <div className="flex justify-between items-center">
                        <label className="text-xs text-[#888] font-mono uppercase group-hover:text-[#00ffff]/70 transition-colors">{item.label}</label>
                        {item.isOAuth && (
                           <span className="text-[10px] text-[#00ff41] font-mono animate-pulse">{item.oauthLabel}</span>
                        )}
                     </div>

                     {item.isOAuth ? (
                        <div className="flex items-center gap-3 p-2.5 border border-[#00ff41]/30 bg-[#00ff41]/5 rounded">
                           <Key size={14} className="text-[#00ff41]" />
                           <span className="text-xs text-[#e0e0e0] font-mono">Authenticated via System Credentials</span>
                           <div className="ml-auto px-2 py-0.5 text-[10px] bg-[#00ff41]/20 text-[#00ff41] rounded border border-[#00ff41]/30">SECURE</div>
                        </div>
                     ) : (
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Key size={14} className="absolute left-3 top-3.5 text-[#666] group-focus-within:text-[#00ffff] transition-colors" />
                            <input
                              type="password"
                              placeholder={item.hasKey ? "•••••••••••••••• (Set)" : "Enter API Key"}
                              value={config[item.key] || ""}
                              onChange={(e) => setConfig({...config, [item.key]: e.target.value})}
                              className="w-full bg-black border border-[#333] rounded pl-9 p-2.5 text-sm focus:border-[#00ffff] focus:outline-none focus:ring-1 focus:ring-[#00ffff]/30 transition-all font-mono placeholder-[#444] text-[#e0e0e0]"
                            />
                          </div>
                          {item.hasKey && <div className="px-3 py-1 text-[10px] font-mono tracking-wider bg-[#00ff41]/10 text-[#00ff41] border border-[#00ff41]/20 rounded flex items-center shadow-[0_0_10px_rgba(0,255,65,0.1)]">LINKED</div>}
                        </div>
                     )}

                     {/* Instructions for OAuth if not connected */}
                     {!item.isOAuth && item.key === "DASHSCOPE_API_KEY" && (
                        <div className="mt-2 flex items-center gap-2">
                           <a
                             href={API_AUTH_QWEN_LOGIN}
                             target="_blank"
                             rel="noopener noreferrer"
                             className="px-3 py-1.5 bg-[#222] hover:bg-[#333] border border-[#333] hover:border-[#00ffff] rounded flex items-center gap-2 transition-all group/btn"
                           >
                              <span className="text-[10px] text-[#00ffff] font-mono font-bold tracking-wide group-hover/btn:text-white">CONNECT VIA ALIBABA CLOUD</span>
                           </a>
                           <span className="text-[10px] text-[#444] font-mono">(Get API Key)</span>
                        </div>
                     )}
                     {!item.isOAuth && item.key === "GEMINI_API_KEY" && (
                        <div className="mt-2 flex items-center gap-2">
                           <a
                             href={API_AUTH_GOOGLE_LOGIN}
                             target="_blank"
                             rel="noopener noreferrer"
                             className="px-3 py-1.5 bg-[#222] hover:bg-[#333] border border-[#333] hover:border-[#00ffff] rounded flex items-center gap-2 transition-all group/btn"
                           >
                              <Image src="/globe.svg" alt="Google" width={12} height={12} className="opacity-70 group-hover/btn:opacity-100" />
                              <span className="text-[10px] text-[#00ffff] font-mono font-bold tracking-wide group-hover/btn:text-white">SETUP GOOGLE ADC</span>
                           </a>
                        </div>
                     )}
                   </div>
                 ))}
               </div>
             </>
           )}
        </div>

        <div className="p-4 border-t border-[#333] bg-[#111] flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded border border-[#333] hover:bg-[#333] transition-colors text-sm font-mono text-[#888] hover:text-[#fff]"
          >
            CANCEL
          </button>
          <button
            onClick={saveConfig}
            disabled={loading}
            className="px-6 py-2 bg-[#00ffff] hover:bg-[#fff] text-black rounded font-bold shadow-[0_0_15px_rgba(0,255,255,0.4)] hover:shadow-[0_0_25px_rgba(0,255,255,0.6)] transition-all flex items-center gap-2 font-orbitron tracking-wider text-sm border border-transparent"
          >
            <Save size={16} /> SAVE CONFIG
          </button>
        </div>
      </div>
    </div>
  );
}
