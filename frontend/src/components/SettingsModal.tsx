"use client";

import { useState, useEffect } from "react";
import { X, Save, Key, Cpu, RefreshCw, ShieldAlert } from "lucide-react";
import { toast } from "sonner";
import Image from "next/image";
import { API_CONFIG, API_AUTH_STATUS, API_AUTH_QWEN_LOGIN, API_AUTH_GOOGLE_LOGIN } from "@/constants";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [config, setConfig] = useState<any>({});
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [authStatus, setAuthStatus] = useState<any>({ google: false, qwen: false });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchConfig();
    }
  }, [isOpen]);

  // Handle Escape key
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      window.addEventListener("keydown", handleEsc);
    }
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, onClose]);

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
    } catch {
      toast.error("ERROR: CONFIGURATION RETRIEVAL FAILED");
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
        toast.success("SYSTEM CONFIGURATION UPDATED");
        onClose();
      } else {
        toast.error("CRITICAL ERROR: CONFIGURATION WRITE FAILED: " + data.message);
      }
    } catch {
      toast.error("ERROR: CONFIGURATION SYNC FAILED");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-bg-primary/85 backdrop-blur-sm p-4" role="dialog" aria-modal="true" aria-labelledby="settings-title">
      <div className="w-full max-w-2xl bg-bg-secondary border border-accent-1 rounded shadow-[0_0_30px_color-mix(in_srgb,var(--accent-1),transparent_90%)] overflow-hidden flex flex-col max-h-[90vh]">
        <div className="flex items-center justify-between p-4 border-b border-border-primary bg-bg-tertiary shrink-0">
          <h2 id="settings-title" className="text-xl font-bold flex items-center gap-2 text-accent-1 font-orbitron tracking-[2px]">
            <Cpu size={24} /> SYSTEM_CONFIGURATION // ROOT ACCESS
          </h2>
          <button onClick={onClose} aria-label="Close settings" className="p-1 hover:bg-bg-primary rounded transition-colors text-text-secondary hover:text-accent-2">
            <X size={24} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-6 flex-1 scrollbar-thin scrollbar-thumb-accent-1 scrollbar-track-bg-tertiary">
           {loading ? (
             <div className="flex justify-center p-8"><RefreshCw className="animate-spin text-accent-1" /></div>
           ) : (
             <>
               {/* LLM Model Selection */}
               <div className="space-y-2">
                 <label htmlFor="llm-model" className="text-xs text-accent-1 font-mono tracking-widest uppercase mb-1 block">NEURAL CORE SELECTION</label>
                 <select
                   id="llm-model"
                   value={config.LLM_MODEL || "gpt-4o"}
                   onChange={(e) => setConfig({...config, LLM_MODEL: e.target.value})}
                   className="w-full bg-bg-primary border border-border-primary rounded p-3 text-text-primary focus:border-accent-1 focus:outline-none focus:ring-1 focus:ring-accent-1/50 font-mono text-sm transition-all appearance-none"
                   style={{backgroundImage: 'none'}}
                 >
                   <option value="gpt-4o">OpenAI GPT-4o</option>
                   <option value="anthropic/claude-3-5-sonnet-20240620">Claude 3.5 Sonnet</option>
                   <option value="gemini/gemini-2.0-flash">Gemini 2.0 Flash (Google)</option>
                   <option value="gemini/gemini-1.5-pro">Gemini 1.5 Pro (Google)</option>
                   <option value="groq/llama-3.1-8b-instant">Llama 3.1 (Groq/Free)</option>
                   <option value="xai/grok-2-vision-1212">Grok 2 (xAI)</option>
                   <option value="mistral/mistral-large-latest">Mistral Large</option>
                   <option value="dashscope/qwen-turbo">Qwen Turbo (Free Tier)</option>
                   <option value="ollama/llama3">Local Ollama (Llama 3)</option>
                 </select>
               </div>

               {/* System Security Configuration */}
               <div className="space-y-4">
                 <h3 className="text-lg font-semibold text-text-primary border-b border-border-primary pb-2 mt-4 font-orbitron tracking-wide flex items-center gap-2">
                   <ShieldAlert size={18} className="text-accent-2" /> KERNEL SECURITY PROTOCOLS
                 </h3>

                 <div className="p-4 border border-accent-2/30 bg-accent-2/5 rounded flex flex-col gap-3">
                   <div className="flex items-center justify-between">
                     <label htmlFor="unsafe-toggle" className="text-sm font-mono font-bold text-text-primary tracking-wide">AUTHORIZE UNRESTRICTED KERNEL ACCESS</label>
                     <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                       <input
                         type="checkbox"
                         name="toggle"
                         id="unsafe-toggle"
                         className="toggle-checkbox absolute block w-5 h-5 rounded-full bg-white border-4 appearance-none cursor-pointer checked:right-0 checked:border-accent-2"
                         style={{right: config.ALLOW_UNSAFE_SYSTEM_ACCESS === 'true' || config.ALLOW_UNSAFE_SYSTEM_ACCESS === true ? '0' : 'auto', left: config.ALLOW_UNSAFE_SYSTEM_ACCESS === 'true' || config.ALLOW_UNSAFE_SYSTEM_ACCESS === true ? 'auto' : '0'}}
                         checked={config.ALLOW_UNSAFE_SYSTEM_ACCESS === 'true' || config.ALLOW_UNSAFE_SYSTEM_ACCESS === true}
                         onChange={(e) => setConfig({...config, ALLOW_UNSAFE_SYSTEM_ACCESS: e.target.checked})}
                       />
                       <label htmlFor="unsafe-toggle" className={`toggle-label block overflow-hidden h-5 rounded-full cursor-pointer ${config.ALLOW_UNSAFE_SYSTEM_ACCESS === 'true' || config.ALLOW_UNSAFE_SYSTEM_ACCESS === true ? 'bg-accent-2' : 'bg-border-primary'}`}></label>
                     </div>
                   </div>

                   <p className="text-xs text-text-secondary font-mono leading-relaxed">
                     <span className="text-accent-2 font-bold">SYSTEM ALERT:</span> AUTHORIZING UNRESTRICTED KERNEL ACCESS. THIS BYPASSES ALL SAFETY PROTOCOLS, GRANTING FULL FILE SYSTEM CONTROL AND SHELL EXECUTION PRIVILEGES.
                     <br/><br/>
                     AUTOMATED FAILSAFE ENGAGED TO PREVENT CATASTROPHIC DELETION. USE WITH EXTREME CAUTION.
                   </p>
                 </div>
               </div>

               {/* Vertex AI Configuration */}
               <div className="space-y-4">
                 <h3 className="text-lg font-semibold text-text-primary border-b border-border-primary pb-2 mt-4 font-orbitron tracking-wide">CLOUD COMPUTING MATRIX</h3>
                 <div className="grid grid-cols-2 gap-4">
                   <div className="space-y-1">
                     <label htmlFor="vertex-project" className="text-xs text-text-secondary font-mono uppercase">VERTEX PROJECT IDENTITY</label>
                     <input
                       id="vertex-project"
                       type="text"
                       placeholder="my-project-id"
                       value={config.VERTEX_PROJECT || ""}
                       onChange={(e) => setConfig({...config, VERTEX_PROJECT: e.target.value})}
                       className="w-full bg-bg-primary border border-border-primary rounded p-2.5 text-sm focus:border-accent-1 focus:outline-none focus:ring-1 focus:ring-accent-1/30 transition-all font-mono text-text-primary"
                     />
                   </div>
                   <div className="space-y-1">
                     <label htmlFor="vertex-region" className="text-xs text-text-secondary font-mono uppercase">COMPUTE REGION</label>
                     <input
                       id="vertex-region"
                       type="text"
                       placeholder="us-central1"
                       value={config.VERTEX_LOCATION || ""}
                       onChange={(e) => setConfig({...config, VERTEX_LOCATION: e.target.value})}
                       className="w-full bg-bg-primary border border-border-primary rounded p-2.5 text-sm focus:border-accent-1 focus:outline-none focus:ring-1 focus:ring-accent-1/30 transition-all font-mono text-text-primary"
                     />
                   </div>
                 </div>
               </div>

               {/* API Keys Section */}
               <div className="space-y-4">
                 <h3 className="text-lg font-semibold text-text-primary border-b border-border-primary pb-2 mt-4 font-orbitron tracking-wide">NEURAL ACCESS KEYS</h3>

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
                   // eslint-disable-next-line @typescript-eslint/no-explicit-any
                 ].map((item: any) => (
                   <div key={item.key} className="flex flex-col gap-1 group">
                     <div className="flex justify-between items-center">
                        <label htmlFor={item.isOAuth ? undefined : item.key} className="text-xs text-text-secondary font-mono uppercase group-hover:text-accent-1/70 transition-colors">{item.label}</label>
                        {item.isOAuth && (
                           <span className="text-[10px] text-status-active font-mono animate-pulse">{item.oauthLabel}</span>
                        )}
                     </div>

                     {item.isOAuth ? (
                        <div className="flex items-center gap-3 p-2.5 border border-status-active/30 bg-status-active/5 rounded">
                           <Key size={14} className="text-status-active" />
                           <span className="text-xs text-text-primary font-mono">Authenticated via System Credentials</span>
                           <div className="ml-auto px-2 py-0.5 text-[10px] bg-status-active/20 text-status-active rounded border border-status-active/30">SECURE</div>
                        </div>
                     ) : (
                        <div className="flex gap-2">
                          <div className="relative flex-1">
                            <Key size={14} className="absolute left-3 top-3.5 text-text-secondary group-focus-within:text-accent-1 transition-colors" />
                            <input
                              id={item.key}
                              type="password"
                              placeholder={item.hasKey ? "•••••••••••••••• (Set)" : "Enter API Key"}
                              value={config[item.key] || ""}
                              onChange={(e) => setConfig({...config, [item.key]: e.target.value})}
                              className="w-full bg-bg-primary border border-border-primary rounded pl-9 p-2.5 text-sm focus:border-accent-1 focus:outline-none focus:ring-1 focus:ring-accent-1/30 transition-all font-mono placeholder-text-secondary text-text-primary"
                            />
                          </div>
                          {item.hasKey && <div className="px-3 py-1 text-[10px] font-mono tracking-wider bg-status-active/10 text-status-active border border-status-active/20 rounded flex items-center shadow-[0_0_10px_var(--status-active)]">LINKED</div>}
                        </div>
                     )}

                     {/* Instructions for OAuth if not connected */}
                     {!item.isOAuth && item.key === "DASHSCOPE_API_KEY" && (
                        <div className="mt-2 flex items-center gap-2">
                           <a
                             href={API_AUTH_QWEN_LOGIN}
                             target="_blank"
                             rel="noopener noreferrer"
                             className="px-3 py-1.5 bg-bg-tertiary hover:bg-bg-primary border border-border-primary hover:border-accent-1 rounded flex items-center gap-2 transition-all group/btn"
                           >
                              <span className="text-[10px] text-accent-1 font-mono font-bold tracking-wide group-hover/btn:text-text-primary">CONNECT VIA ALIBABA CLOUD</span>
                           </a>
                           <span className="text-[10px] text-text-secondary font-mono">(Get API Key)</span>
                        </div>
                     )}
                     {!item.isOAuth && item.key === "GEMINI_API_KEY" && (
                        <div className="mt-2 flex flex-col gap-2 p-3 border border-border-primary rounded bg-bg-tertiary">
                           <span className="text-[10px] text-accent-1 font-mono uppercase mb-1">Google Cloud OAuth (Recommended)</span>

                           <div className="flex flex-col gap-1">
                               <label htmlFor="google-client-id" className="text-[10px] text-text-secondary font-mono">Client ID</label>
                               <input
                                   id="google-client-id"
                                   type="text"
                                   value={config.GOOGLE_CLIENT_ID || ""}
                                   onChange={(e) => setConfig({...config, GOOGLE_CLIENT_ID: e.target.value})}
                                   className="w-full bg-bg-primary border border-border-primary rounded p-1.5 text-xs font-mono text-text-primary focus:border-accent-1 focus:outline-none"
                                   placeholder="...apps.googleusercontent.com"
                               />
                           </div>

                           <div className="flex flex-col gap-1">
                               <label htmlFor="google-client-secret" className="text-[10px] text-text-secondary font-mono">Client Secret</label>
                               <input
                                   id="google-client-secret"
                                   type="password"
                                   value={config.GOOGLE_CLIENT_SECRET || ""}
                                   onChange={(e) => setConfig({...config, GOOGLE_CLIENT_SECRET: e.target.value})}
                                   className="w-full bg-bg-primary border border-border-primary rounded p-1.5 text-xs font-mono text-text-primary focus:border-accent-1 focus:outline-none"
                                   placeholder="GOCSPX-..."
                               />
                           </div>

                           <button
                             onClick={async () => {
                                 try {
                                     setLoading(true);
                                     const res = await fetch(API_CONFIG, {
                                        method: "POST",
                                        headers: { "Content-Type": "application/json" },
                                        body: JSON.stringify(config),
                                      });
                                      if (res.ok) {
                                          window.location.href = API_AUTH_GOOGLE_LOGIN;
                                      } else {
                                          toast.error("Failed to save credentials before connecting.");
                                          setLoading(false);
                                      }
                                 } catch {
                                     toast.error("Error saving config.");
                                     setLoading(false);
                                 }
                             }}
                             className="mt-2 w-full py-1.5 bg-bg-tertiary hover:bg-bg-primary border border-border-primary hover:border-accent-1 rounded flex items-center justify-center gap-2 transition-all group/btn"
                           >
                              <Image src="/globe.svg" alt="Google" width={12} height={12} className="opacity-70 group-hover/btn:opacity-100" />
                              <span className="text-[10px] text-accent-1 font-mono font-bold tracking-wide group-hover/btn:text-text-primary">CONNECT WITH GOOGLE CLOUD</span>
                           </button>
                        </div>
                     )}
                   </div>
                 ))}
               </div>
             </>
           )}
        </div>

        <div className="p-4 border-t border-border-primary bg-bg-tertiary flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded border border-border-primary hover:bg-bg-primary transition-colors text-sm font-mono text-text-secondary hover:text-text-primary"
          >
            ABORT SEQUENCE
          </button>
          <button
            onClick={saveConfig}
            disabled={loading}
            className="px-6 py-2 bg-accent-1 hover:bg-white text-bg-primary rounded font-bold shadow-[0_0_15px_color-mix(in_srgb,var(--accent-1),transparent_60%)] hover:shadow-[0_0_25px_color-mix(in_srgb,var(--accent-1),transparent_40%)] transition-all flex items-center gap-2 font-orbitron tracking-wider text-sm border border-transparent"
          >
            <Save size={16} /> COMMIT PROTOCOLS
          </button>
        </div>
      </div>
    </div>
  );
}
