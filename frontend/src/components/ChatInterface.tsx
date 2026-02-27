"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Send, User, Sparkles, Image as ImageIcon, FileText, X, Paperclip, Loader2, UserPlus, UserMinus, ArrowRight } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import VoiceInput from "./VoiceInput";
import { toast } from "sonner";
import Image from "next/image";
import { API_CHAT, SUPPORTED_FILE_EXTENSIONS_REGEX } from "@/constants";
import { AgentGraphData } from "@/types/agent";

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_FILE_SIZE_TEXT = "10MB";

interface Attachment {
  name: string;
  type: string;
  content: string; // Base64 or text
}

interface ActivityItem {
  type: "interaction" | "lifecycle";
  subtype?: "create" | "remove";
  source?: string;
  target?: string;
  summary?: string;
  agent?: string;
  timestamp: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
  activities?: ActivityItem[];
  timestamp: number;
}

export default function ChatInterface({
  onGraphUpdate
}: {
  onGraphUpdate: (data: AgentGraphData) => void
}) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "System Online. Neural interface active. Awaiting directive.",
      timestamp: Date.now(),
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleTranscript = useCallback((text: string) => {
    setInput(text);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
          validateAndAddFiles(Array.from(e.target.files));
          // Reset input so same file can be selected again if needed
          e.target.value = '';
      }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, attachments]);

  // Global Drag Safety Net to prevent browser from opening files
  useEffect(() => {
    const handleWindowDragOver = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };
    const handleWindowDrop = (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
    };

    window.addEventListener('dragover', handleWindowDragOver);
    window.addEventListener('drop', handleWindowDrop);

    return () => {
      window.removeEventListener('dragover', handleWindowDragOver);
      window.removeEventListener('drop', handleWindowDrop);
    };
  }, []);

  const onDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer) {
        e.dataTransfer.dropEffect = "copy";
    }
    setIsDragging(true);
  };

  const onDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();

    // Fix flicker: check if moving to a child element
    if (e.relatedTarget && containerRef.current && containerRef.current.contains(e.relatedTarget as Node)) {
        return;
    }
    setIsDragging(false);
  };

  const validateAndAddFiles = (fileList: File[]) => {
      const validFiles = fileList.filter(file => {
          // Allow images, text files, code files
          const isValid = file.type.startsWith("image/") || file.type.startsWith("text/") ||
              SUPPORTED_FILE_EXTENSIONS_REGEX.test(file.name);

          if (!isValid) {
               toast.error(`File type not supported: ${file.name}`);
          }

          if (file.size > MAX_FILE_SIZE) {
               toast.error(`File too large: ${file.name} (max ${MAX_FILE_SIZE_TEXT})`);
               return false;
          }

          return isValid;
      });
      setAttachments(prev => [...prev, ...validFiles]);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      validateAndAddFiles(droppedFiles);
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if ((!input.trim() && attachments.length === 0) || loading) return;

    // Process attachments
    const processedAttachments: Attachment[] = [];
    try {
        for (const file of attachments) {
          if (file.size > MAX_FILE_SIZE) {
            toast.error(`File too large: ${file.name} (max ${MAX_FILE_SIZE_TEXT})`);
            return;
          }

          const content = await new Promise<string>((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result as string);
            reader.onerror = reject;
            if (file.type.startsWith("image/")) {
               reader.readAsDataURL(file);
            } else {
               reader.readAsText(file);
            }
          });
          processedAttachments.push({
            name: file.name,
            type: file.type,
            content: content
          });
        }
    } catch {
        toast.error("Failed to read file attachments");
        return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      attachments: processedAttachments,
      timestamp: Date.now(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setAttachments([]);
    setLoading(true);

    try {
      const res = await fetch(API_CHAT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            message: userMessage.content,
            attachments: processedAttachments
        }),
      });

      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.response,
        activities: data.activity_log,
        timestamp: Date.now(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      if (data.graph) {
        onGraphUpdate(data.graph);
      } else if (data.agents) {
          // Backward compatibility
          onGraphUpdate({
             nodes: data.agents.map((a: string) => ({ id: a, name: a, parent: null })),
             edges: []
          });
      }
    } catch {
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
    <div
      ref={containerRef}
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className="flex flex-col h-full bg-bg-secondary/50 backdrop-blur-md rounded-xl border border-border-primary overflow-hidden relative shadow-[0_0_20px_rgba(0,0,0,0.5)] transition-colors duration-300"
    >
      {/* Drag Overlay */}
      <AnimatePresence>
        {isDragging && (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-bg-secondary/90 backdrop-blur-sm z-50 flex flex-col items-center justify-center border-2 border-dashed border-accent-1 m-4 rounded-xl"
            >
                <Paperclip size={48} className="text-accent-1 mb-4 animate-bounce" />
                <h3 className="text-xl font-orbitron text-text-primary">DROP FILES TO UPLOAD</h3>
                <p className="text-accent-1/70 font-mono mt-2">Images & Documents</p>
            </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div className="p-4 border-b border-border-primary bg-bg-tertiary/50 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
           <Sparkles className="text-accent-1" size={18} />
           <span className="font-orbitron text-accent-1 tracking-wider text-sm">LIVE FEED</span>
        </div>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${loading ? "bg-status-warning animate-pulse shadow-[0_0_10px_var(--status-warning)]" : "bg-status-active shadow-[0_0_10px_var(--status-active)]"}`}></div>
          <span className="text-xs text-text-secondary font-mono tracking-widest">{loading ? "PROCESSING" : "IDLE"}</span>
        </div>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin scrollbar-thumb-accent-1/20 scrollbar-track-transparent"
        role="log"
        aria-live="polite"
      >
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
                  ? "bg-accent-2/10 border-accent-2/40 text-accent-2 shadow-[0_0_15px_color-mix(in_srgb,var(--accent-2),transparent_90%)]"
                  : "bg-accent-1/10 border-accent-1/40 text-accent-1 shadow-[0_0_15px_color-mix(in_srgb,var(--accent-1),transparent_90%)]"
              }`}>
                {msg.role === "user" ? <User size={20} /> : <Image src="/logo.svg" alt="OpenCore" width={24} height={24} className="w-6 h-6" />}
              </div>

              <div className={`max-w-[80%] flex flex-col gap-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>

                {/* Activities / Thought Process */}
                {msg.activities && msg.activities.length > 0 && (
                  <div className="flex flex-col gap-1 mb-1 w-full">
                    {msg.activities.map((activity, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-[10px] text-text-secondary/70 font-mono pl-1">
                        {activity.type === "lifecycle" && activity.subtype === "create" && (
                          <>
                            <UserPlus size={12} className="shrink-0 text-accent-1/70 mt-0.5" />
                            <span>Agent <span className="text-accent-1/90 font-bold">{activity.agent}</span> joined the chat.</span>
                          </>
                        )}
                        {activity.type === "lifecycle" && activity.subtype === "remove" && (
                          <>
                            <UserMinus size={12} className="shrink-0 text-status-error/70 mt-0.5" />
                            <span>Agent <span className="text-status-error/90 font-bold">{activity.agent}</span> left the chat.</span>
                          </>
                        )}
                        {activity.type === "interaction" && (
                           <>
                             <ArrowRight size={12} className="shrink-0 text-text-secondary/50 mt-0.5" />
                             <span className="break-words">
                               <span className="text-accent-1/80">{activity.source}</span>
                               <span className="mx-1 text-text-secondary/50">→</span>
                               <span className="text-accent-1/80">{activity.target}</span>: {activity.summary}
                             </span>
                           </>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Text Content */}
                {msg.content && (
                    <div className={`p-4 rounded-xl border text-sm font-mono leading-relaxed shadow-md backdrop-blur-sm ${
                        msg.role === "user"
                        ? "bg-accent-2/10 border-accent-2/20 text-text-primary rounded-tr-none"
                        : "bg-accent-1/10 border-accent-1/20 text-text-primary rounded-tl-none"
                    }`}>
                        {msg.content}
                    </div>
                )}

                {/* Attachments */}
                {msg.attachments && msg.attachments.length > 0 && (
                    <div className={`flex flex-wrap gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        {msg.attachments.map((att, i) => (
                            <div key={i} className="group relative rounded-lg overflow-hidden border border-border-primary bg-bg-tertiary p-2 flex flex-col items-center gap-2 max-w-[200px]">
                                {att.type.startsWith("image/") ? (
                                    // eslint-disable-next-line @next/next/no-img-element
                                    <img src={att.content} alt={att.name} className="max-h-32 object-contain rounded" />
                                ) : (
                                    <div className="w-16 h-16 bg-bg-primary/50 rounded flex items-center justify-center text-accent-1">
                                        <FileText size={24} />
                                    </div>
                                )}
                                <span className="text-[10px] text-text-secondary truncate w-full text-center">{att.name}</span>
                            </div>
                        ))}
                    </div>
                )}

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
             <div className="w-10 h-10 rounded-lg border border-accent-1/40 bg-accent-1/10 flex items-center justify-center text-accent-1 shadow-[0_0_15px_color-mix(in_srgb,var(--accent-1),transparent_70%)]">
                <Image src="/logo.svg" alt="Processing..." width={24} height={24} className="w-6 h-6 animate-pulse" />
             </div>
             <div className="flex items-center gap-1.5 h-10 px-2">
               <span className="w-2 h-2 bg-accent-1 rounded-full animate-bounce [animation-delay:-0.3s] shadow-[0_0_5px_color-mix(in_srgb,var(--accent-1),transparent_50%)]"></span>
               <span className="w-2 h-2 bg-accent-1 rounded-full animate-bounce [animation-delay:-0.15s] shadow-[0_0_5px_color-mix(in_srgb,var(--accent-1),transparent_50%)]"></span>
               <span className="w-2 h-2 bg-accent-1 rounded-full animate-bounce shadow-[0_0_5px_color-mix(in_srgb,var(--accent-1),transparent_50%)]"></span>
             </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border-primary bg-bg-tertiary/50 backdrop-blur-md shrink-0 flex flex-col gap-2">

        {/* Attachment Preview Area */}
        {attachments.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-accent-1/20">
                {attachments.map((file, i) => (
                    <div key={i} className="relative group shrink-0 w-16 h-16 bg-bg-primary/50 border border-border-primary rounded-lg flex items-center justify-center">
                        <button
                            onClick={() => removeAttachment(i)}
                            aria-label={`Remove attachment ${file.name}`}
                            className="absolute -top-2 -right-2 w-5 h-5 bg-status-error text-white rounded-full flex items-center justify-center shadow-md hover:bg-red-600 transition-colors z-10"
                        >
                            <X size={12} aria-hidden="true" />
                        </button>
                        {file.type.startsWith("image/") ? (
                             <ImageIcon size={20} className="text-accent-1" />
                        ) : (
                             <FileText size={20} className="text-accent-1" />
                        )}
                        <span className="absolute bottom-1 text-[8px] text-text-secondary truncate max-w-full px-1">{file.name}</span>
                    </div>
                ))}
            </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-3 relative items-center">
           <VoiceInput onTranscript={handleTranscript} disabled={loading} />

           <input
               type="file"
               multiple
               ref={fileInputRef}
               className="hidden"
               onChange={handleFileSelect}
               aria-label="File upload"
           />

           <button
             type="button"
             onClick={() => fileInputRef.current?.click()}
             disabled={loading}
             aria-label="Attach files"
             className="p-2 rounded-lg transition-all duration-300 backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-1/50 bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/30 active:scale-95"
           >
              <Paperclip size={20} aria-hidden="true" />
           </button>

           <input
             type="text"
             aria-label="Chat input"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             placeholder={attachments.length > 0 ? "Add message to files..." : "Enter command directive..."}
             disabled={loading}
             className="flex-1 bg-bg-primary/50 border border-border-primary rounded-xl px-5 py-3 text-text-primary focus:outline-none focus:border-accent-1/50 focus:ring-1 focus:ring-accent-1/50 transition-all font-mono text-sm placeholder-text-secondary shadow-inner"
           />

           <button
             type="submit"
             disabled={(!input.trim() && attachments.length === 0) || loading}
             aria-label={loading ? "Sending message..." : "Send message"}
             aria-busy={loading}
             className="p-3 bg-accent-1/20 hover:bg-accent-1/40 text-accent-1 border border-accent-1/50 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_15px_color-mix(in_srgb,var(--accent-1),transparent_70%)] active:scale-95 flex items-center justify-center min-w-[3rem]"
           >
             {loading ? (
               <Loader2 size={20} className="animate-spin" aria-hidden="true" />
             ) : (
               <Send size={20} aria-hidden="true" />
             )}
           </button>
        </form>
      </div>
    </div>
  );
}
