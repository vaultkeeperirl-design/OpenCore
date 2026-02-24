"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Mic, MicOff } from "lucide-react";
import { toast } from "sonner";

interface VoiceInputProps {
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export default function VoiceInput({ onTranscript, disabled }: VoiceInputProps) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const onTranscriptRef = useRef(onTranscript);

  // Update the ref whenever onTranscript changes to ensure we use the latest callback
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  }, [onTranscript]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
          const transcript = event.results[0][0].transcript;
          if (onTranscriptRef.current) {
            onTranscriptRef.current(transcript);
          }
          setIsListening(false);
        };

        recognition.onerror = (event: any) => {
          console.error("Speech recognition error", event.error);
          setIsListening(false);

          if (event.error === 'not-allowed') {
             toast.error("Microphone access denied. Please allow permissions.");
          } else if (event.error === 'no-speech') {
             // customized handling could go here
          } else {
             toast.error("Voice input error: " + event.error);
          }
        };

        recognition.onend = () => {
          setIsListening(false);
        };

        recognitionRef.current = recognition;
      }
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) {
      toast.error("Speech recognition not supported in this browser.");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      // State will be updated in onend
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        toast.info("Listening...");
      } catch (error) {
        console.error("Error starting speech recognition:", error);
        // If it fails to start, reset state
        setIsListening(false);
      }
    }
  }, [isListening]);

  return (
    <button
      type="button"
      onClick={toggleListening}
      disabled={disabled}
      className={`p-2 rounded-lg transition-all duration-300 ${
        isListening
          ? "bg-red-500/20 text-red-400 border border-red-500/50 animate-pulse"
          : "bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/30"
      } backdrop-blur-sm`}
      title={isListening ? "Stop listening" : "Start voice input"}
    >
      {isListening ? <MicOff size={20} /> : <Mic size={20} />}
    </button>
  );
}
