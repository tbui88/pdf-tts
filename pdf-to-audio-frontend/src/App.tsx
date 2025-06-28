import React, { useState } from 'react'
import { FileUploader } from '@/components/FileUploader'
import { ConversionProgress } from '@/components/ConversionProgress'
import { AudioPlayer } from '@/components/AudioPlayer'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import { Toaster } from '@/components/ui/sonner'
import { toast } from 'sonner'

export interface ConversionState {
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  message: string
  fileName?: string
  audioUrl?: string
  estimatedDuration?: number
}

// Generate mock audio data for demo
function generateMockAudio(): Uint8Array {
  // Create a basic MP3 file with silence
  const id3Header = new Uint8Array([
    0x49, 0x44, 0x33, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  ])
  
  // MP3 frame header for 44.1kHz, stereo, 128kbps
  const mp3Frame = new Uint8Array([
    0xFF, 0xFB, 0x90, 0x00,
    ...new Array(32).fill(0x00)
  ])
  
  // Create silence frames (about 10 seconds)
  const silenceFrame = new Uint8Array(144).fill(0x00)
  const totalFrames = new Uint8Array(id3Header.length + mp3Frame.length + silenceFrame.length * 400)
  
  let offset = 0
  totalFrames.set(id3Header, offset)
  offset += id3Header.length
  totalFrames.set(mp3Frame, offset)
  offset += mp3Frame.length
  
  for (let i = 0; i < 400; i++) {
    totalFrames.set(silenceFrame, offset)
    offset += silenceFrame.length
  }
  
  return totalFrames
}

function App() {
  const [conversionState, setConversionState] = useState<ConversionState>({
    status: 'idle',
    progress: 0,
    message: '',
  })

  const handleFileUpload = async (file: File) => {
    setConversionState({
      status: 'uploading',
      progress: 0,
      message: 'Uploading PDF...',
      fileName: file.name,
    })

    try {
      // Simulate upload progress
      for (let i = 0; i <= 100; i += 10) {
        await new Promise(resolve => setTimeout(resolve, 100))
        setConversionState(prev => ({
          ...prev,
          progress: i,
          message: `Uploading PDF... ${i}%`,
        }))
      }

      // Start processing
      setConversionState(prev => ({
        ...prev,
        status: 'processing',
        progress: 0,
        message: 'Extracting text from PDF...',
      }))

      // Demo mode: Simulate backend processing
      const simulateConversion = async () => {
        const stages = [
          { progress: 10, message: 'Extracting text from PDF...' },
          { progress: 25, message: 'Processing and chunking text...' },
          { progress: 40, message: 'Converting text to speech...' },
          { progress: 55, message: 'Converting chunk 1/4...' },
          { progress: 70, message: 'Converting chunk 2/4...' },
          { progress: 85, message: 'Converting chunk 3/4...' },
          { progress: 95, message: 'Converting chunk 4/4...' },
          { progress: 98, message: 'Merging audio files...' },
        ]

        for (const stage of stages) {
          await new Promise(resolve => setTimeout(resolve, 1500))
          setConversionState(prev => ({
            ...prev,
            progress: stage.progress,
            message: stage.message,
          }))
        }

        // Complete conversion
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // Generate a simple mock audio URL (data URL with silent MP3)
        const mockAudioData = generateMockAudio()
        const audioBlob = new Blob([mockAudioData], { type: 'audio/mpeg' })
        const audioUrl = URL.createObjectURL(audioBlob)

        setConversionState({
          status: 'completed',
          progress: 100,
          message: 'Conversion completed successfully!',
          fileName: file.name,
          audioUrl: audioUrl,
          estimatedDuration: 45,
        })
      }

      await simulateConversion()

      toast.success('PDF converted to audio successfully!')

    } catch (error) {
      console.error('Conversion error:', error)
      setConversionState({
        status: 'error',
        progress: 0,
        message: 'An error occurred during conversion. Please try again.',
        fileName: file.name,
      })
      toast.error('Failed to convert PDF to audio')
    }
  }

  const handleReset = () => {
    setConversionState({
      status: 'idle',
      progress: 0,
      message: '',
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex flex-col">
      <Header />
      
      <main className="flex-1 container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold text-slate-800 mb-4">
            PDF to Audio
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto">
            Transform your PDF documents into high-quality audio files using advanced text-to-speech technology.
            Perfect for audiobooks, accessibility, and learning on-the-go.
          </p>
        </div>

        <div className="space-y-8">
          {conversionState.status === 'idle' && (
            <FileUploader onFileUpload={handleFileUpload} />
          )}

          {(conversionState.status === 'uploading' || conversionState.status === 'processing') && (
            <ConversionProgress
              progress={conversionState.progress}
              message={conversionState.message}
              fileName={conversionState.fileName}
            />
          )}

          {conversionState.status === 'completed' && conversionState.audioUrl && (
            <AudioPlayer
              audioUrl={conversionState.audioUrl}
              fileName={conversionState.fileName}
              onReset={handleReset}
              estimatedDuration={conversionState.estimatedDuration}
            />
          )}

          {conversionState.status === 'error' && (
            <div className="bg-white rounded-2xl shadow-lg border border-red-100 p-8 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-red-800 mb-2">Conversion Failed</h3>
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
  )
}

export default App
