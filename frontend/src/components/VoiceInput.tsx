"use client";

import { useState, useRef, useCallback } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { API_TRANSCRIBE } from "@/constants";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const mimeType = mediaRecorder.mimeType || "audio/webm";
        const audioBlob = new Blob(chunksRef.current, { type: mimeType });
        await handleTranscription(audioBlob, mimeType);

        // Stop all tracks to release microphone
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      toast.info("Listening...");
    } catch (err) {
      console.error("Error accessing microphone:", err);
      toast.error("Microphone access denied or not available.");
    }
  };

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const handleTranscription = async (audioBlob: Blob, mimeType: string) => {
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      // Whisper handles most extensions. Using .webm or .wav is usually safe.
      // We'll append a generic extension based on mimeType if possible, or just .webm
      const ext = mimeType.includes("mp4") ? "m4a" : "webm";
      formData.append("file", audioBlob, `recording.${ext}`);

      const res = await fetch(API_TRANSCRIBE, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Transcription failed");
      }

      const data = await res.json();
      if (data.error) {
        throw new Error(data.error);
      }

      if (data.text) {
        onTranscript(data.text);
        toast.success("Transcribed successfully");
      } else {
        toast.warning("No speech detected");
      }
    } catch (err) {
      console.error("Transcription error:", err);
      toast.error("Failed to transcribe audio.");
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const isLoading = isTranscribing;

  const label = isRecording
    ? "Stop voice recording"
    : isLoading
    ? "Transcribing audio..."
    : "Start voice input";

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || isLoading}
      aria-label={label}
      aria-pressed={isRecording}
      className={`p-2 rounded-lg transition-all duration-300 backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-1/50 ${
        isRecording
          ? "bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse"
          : isLoading
            ? "bg-yellow-500/20 text-yellow-400 border border-yellow-500/50"
            : "bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/30 active:scale-95"
      }`}
      title={label}
    >
      {isLoading ? (
        <Loader2 size={20} className="animate-spin" aria-hidden="true" />
      ) : isRecording ? (
        <MicOff size={20} aria-hidden="true" />
      ) : (
        <Mic size={20} aria-hidden="true" />
      )}
    </button>
  );
}
