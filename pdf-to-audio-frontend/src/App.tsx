import React, { useState } from "react";
import { FileUploader } from "@/components/FileUploader";
import { ConversionProgress } from "@/components/ConversionProgress";
import { AudioPlayer } from "@/components/AudioPlayer";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";

import { uploadPdf } from "@/lib/api";          // ← NEW

export interface ConversionState {
  status: "idle" | "uploading" | "processing" | "completed" | "error";
  progress: number;
  message: string;
  fileName?: string;
  audioUrl?: string;
  estimatedDuration?: number;
}

function App() {
  const [conversionState, setConversionState] = useState<ConversionState>({
    status: "idle",
    progress: 0,
    message: "",
  });

  // ⬇️ main handler
 const handleFileUpload = async (file: File) => {
  console.log("⏩ handleFileUpload fired with:", file.name); // LOG ①

  setConversionState({
    status: 'uploading',
    fileName: file.name,
    duration: null,
    audioUrl: null,
    error: null,
  });

  try {
    console.log("🌍 BASE =", import.meta.env.VITE_API_BASE_URL); // LOG ②

    const { audio_url } = await uploadPdf(file);
    console.log("✅ backend returned:", audio_url); // LOG ③

    setConversionState({
      status: 'completed',
      fileName: file.name,
      duration: null,
      audioUrl: audio_url,
      error: null,
    });
  } catch (error) {
    console.error("❌ Upload failed:", error);
    setConversionState({
      status: 'error',
      fileName: file.name,
      duration: null,
      audioUrl: null,
      error: 'Conversion failed. Please try again.',
    });
  }
};


  const handleReset = () => {
    setConversionState({
      status: "idle",
      progress: 0,
      message: "",
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex flex-col">
      <Header />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-slate-800 mb-4">
            PDF to Audio
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Transform your PDF documents into high-quality audio files using
            advanced text-to-speech technology. Perfect for audiobooks,
            accessibility, and learning on-the-go.
          </p>
        </div>

        <div className="space-y-8">
          {conversionState.status === "idle" && (
            <FileUploader onFileUpload={handleFileUpload} />
          )}

          {conversionState.status === "uploading" && (
            <ConversionProgress
              progress={conversionState.progress}
              message={conversionState.message}
              fileName={conversionState.fileName}
            />
          )}

          {conversionState.status === "completed" && conversionState.audioUrl && (
            <AudioPlayer
              audioUrl={conversionState.audioUrl}
              fileName={conversionState.fileName}
              onReset={handleReset}
              estimatedDuration={conversionState.estimatedDuration}
            />
          )}

          {conversionState.status === "error" && (
            <div className="bg-white rounded-2xl shadow-lg border border-red-100 p-8 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-red-800 mb-2">
                Conversion Failed
              </h3>
              <p className="text-red-600 mb-6">{conversionState.message}</p>
              <button
                onClick={handleReset}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      </main>

      <Footer />
      <Toaster />
    </div>
  );
}

export default App;
