import React, { useState, useRef, useEffect } from 'react'
import { Play, Pause, Download, RotateCcw, Volume2, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { cn } from '@/lib/utils'

interface AudioPlayerProps {
  audioUrl: string
  fileName?: string
  onReset: () => void
  estimatedDuration?: number
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  audioUrl,
  fileName,
  onReset,
  estimatedDuration
}) => {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const audioRef = useRef<HTMLAudioElement>(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const handleLoadedMetadata = () => {
      setDuration(audio.duration)
      setIsLoading(false)
    }

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime)
    }

    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
    }

    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('ended', handleEnded)

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('ended', handleEnded)
    }
  }, [audioUrl])

  const togglePlayPause = () => {
    const audio = audioRef.current
    if (!audio) return

    if (isPlaying) {
      audio.pause()
    } else {
      audio.play()
    }
    setIsPlaying(!isPlaying)
  }

  const handleSeek = (value: number[]) => {
    const audio = audioRef.current
    if (!audio) return

    const newTime = (value[0] / 100) * duration
    audio.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handleVolumeChange = (value: number[]) => {
    const audio = audioRef.current
    if (!audio) return

    const newVolume = value[0] / 100
    audio.volume = newVolume
    setVolume(newVolume)
  }

  const formatTime = (time: number) => {
    if (isNaN(time)) return '0:00'
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const handleDownload = () => {
    const link = document.createElement('a')
    link.href = audioUrl
    link.download = fileName ? fileName.replace('.pdf', '.mp3') : 'converted-audio.mp3'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 overflow-hidden">
        {/* Success Header */}
        <div className="bg-gradient-to-r from-green-50 to-emerald-50 p-6 border-b border-green-100">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-green-800">Conversion Completed!</h3>
              <p className="text-green-600">Your PDF has been successfully converted to audio</p>
            </div>
          </div>
        </div>

        {/* File Info */}
        {fileName && (
          <div className="p-6 border-b border-slate-100">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-slate-500" />
              <div>
                <p className="font-medium text-slate-800">{fileName}</p>
                <p className="text-sm text-slate-500">
                  Duration: {isLoading ? 'Loading...' : formatTime(duration)}
                  {estimatedDuration && (
                    <span className="ml-2">• Estimated: {Math.round(estimatedDuration)} min</span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Audio Player */}
        <div className="p-6">
          <audio ref={audioRef} src={audioUrl} preload="metadata" />
          
          {/* Progress Bar */}
          <div className="mb-6">
            <Slider
              value={[progress]}
              onValueChange={handleSeek}
              max={100}
              step={0.1}
              className="w-full"
              disabled={isLoading}
            />
            <div className="flex justify-between text-sm text-slate-500 mt-2">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={togglePlayPause}
                disabled={isLoading}
                size="lg"
                className="w-12 h-12 rounded-full"
              >
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : isPlaying ? (
                  <Pause className="w-5 h-5" />
                ) : (
                  <Play className="w-5 h-5 ml-1" />
                )}
              </Button>
              
              <div className="flex items-center space-x-2">
                <Volume2 className="w-4 h-4 text-slate-500" />
                <Slider
                  value={[volume * 100]}
                  onValueChange={handleVolumeChange}
                  max={100}
                  step={1}
                  className="w-20"
                />
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                onClick={handleDownload}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <Download className="w-4 h-4" />
                <span>Download</span>
              </Button>
              
              <Button
                onClick={onReset}
                variant="outline"
                className="flex items-center space-x-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>New File</span>
              </Button>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="bg-slate-50 p-4 border-t border-slate-100">
          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>🎧 High-quality MP3 audio</span>
            <span>Powered by MiniMax TTS</span>
          </div>
        </div>
      </div>
    </div>
  )
}
