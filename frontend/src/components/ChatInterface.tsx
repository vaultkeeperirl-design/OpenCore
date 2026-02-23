"use client";

import { useState, useEffect, useRef } from "react";
import { Send, User, Sparkles, Image as ImageIcon, FileText, X, Paperclip } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import VoiceInput from "./VoiceInput";
import { toast } from "sonner";

interface Attachment {
  name: string;
  type: string;
  content: string; // Base64 or text
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
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
  const [attachments, setAttachments] = useState<File[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFiles = Array.from(e.dataTransfer.files);
      const validFiles = droppedFiles.filter(file => {
          // Allow images, text files, code files
          const isValid = file.type.startsWith("image/") || file.type.startsWith("text/") ||
              /\.(json|js|ts|tsx|py|md|csv|html|css|txt)$/i.test(file.name);

          if (!isValid) {
               toast.error(`File type not supported: ${file.name}`);
          }
          return isValid;
      });
      setAttachments(prev => [...prev, ...validFiles]);
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
    } catch (err) {
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
      const res = await fetch("/chat", {
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
    <div
      ref={containerRef}
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      className="flex flex-col h-full bg-black/20 backdrop-blur-md rounded-xl border border-white/10 overflow-hidden relative shadow-[0_0_20px_rgba(0,0,0,0.5)]"
    >
      {/* Drag Overlay */}
      <AnimatePresence>
        {isDragging && (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-cyan-900/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center border-2 border-dashed border-cyan-400 m-4 rounded-xl"
            >
                <Paperclip size={48} className="text-cyan-400 mb-4 animate-bounce" />
                <h3 className="text-xl font-orbitron text-cyan-100">DROP FILES TO UPLOAD</h3>
                <p className="text-cyan-400/70 font-mono mt-2">Images & Documents</p>
            </motion.div>
        )}
      </AnimatePresence>

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

              <div className={`max-w-[80%] flex flex-col gap-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>

                {/* Text Content */}
                {msg.content && (
                    <div className={`p-4 rounded-xl border text-sm font-mono leading-relaxed shadow-md backdrop-blur-sm ${
                        msg.role === "user"
                        ? "bg-purple-900/10 border-purple-500/20 text-purple-100 rounded-tr-none"
                        : "bg-cyan-900/10 border-cyan-500/20 text-cyan-100 rounded-tl-none"
                    }`}>
                        {msg.content}
                    </div>
                )}

                {/* Attachments */}
                {msg.attachments && msg.attachments.length > 0 && (
                    <div className={`flex flex-wrap gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                        {msg.attachments.map((att, i) => (
                            <div key={i} className="group relative rounded-lg overflow-hidden border border-white/10 bg-black/40 p-2 flex flex-col items-center gap-2 max-w-[200px]">
                                {att.type.startsWith("image/") ? (
                                    <img src={att.content} alt={att.name} className="max-h-32 object-contain rounded" />
                                ) : (
                                    <div className="w-16 h-16 bg-white/5 rounded flex items-center justify-center text-cyan-400">
                                        <FileText size={24} />
                                    </div>
                                )}
                                <span className="text-[10px] text-gray-400 truncate w-full text-center">{att.name}</span>
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
      <div className="p-4 border-t border-white/10 bg-black/40 backdrop-blur-md shrink-0 flex flex-col gap-2">

        {/* Attachment Preview Area */}
        {attachments.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-cyan-900/50">
                {attachments.map((file, i) => (
                    <div key={i} className="relative group shrink-0 w-16 h-16 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center">
                        <button
                            onClick={() => removeAttachment(i)}
                            className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center shadow-md hover:bg-red-600 transition-colors z-10"
                        >
                            <X size={12} />
                        </button>
                        {file.type.startsWith("image/") ? (
                             <ImageIcon size={20} className="text-cyan-400" />
                        ) : (
                             <FileText size={20} className="text-cyan-400" />
                        )}
                        <span className="absolute bottom-1 text-[8px] text-gray-400 truncate max-w-full px-1">{file.name}</span>
                    </div>
                ))}
            </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-3 relative items-center">
           <VoiceInput onTranscript={(text) => setInput(text)} disabled={loading} />

           <input
             type="text"
             value={input}
             onChange={(e) => setInput(e.target.value)}
             placeholder={attachments.length > 0 ? "Add message to files..." : "Enter command directive..."}
             disabled={loading}
             className="flex-1 bg-black/50 border border-white/10 rounded-xl px-5 py-3 text-white focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all font-mono text-sm placeholder-gray-600 shadow-inner"
           />

           <button
             type="submit"
             disabled={(!input.trim() && attachments.length === 0) || loading}
             className="p-3 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-400 border border-cyan-500/50 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-[0_0_15px_rgba(6,182,212,0.3)] active:scale-95"
           >
             <Send size={20} />
           </button>
        </form>
      </div>
    </div>
  );
}
