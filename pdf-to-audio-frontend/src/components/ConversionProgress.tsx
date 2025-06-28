import React from 'react'
import { Progress } from '@/components/ui/progress'
import { FileText, Loader2 } from 'lucide-react'

interface ConversionProgressProps {
  progress: number
  message: string
  fileName?: string
}

export const ConversionProgress: React.FC<ConversionProgressProps> = ({
  progress,
  message,
  fileName
}) => {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
          </div>
          <h3 className="text-xl font-semibold text-slate-800 mb-2">Converting PDF to Audio</h3>
          <p className="text-slate-600">Please wait while we process your document...</p>
        </div>

        {fileName && (
          <div className="flex items-center space-x-3 mb-6 p-4 bg-slate-50 rounded-lg">
            <FileText className="w-5 h-5 text-slate-500" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-800 truncate">{fileName}</p>
              <p className="text-xs text-slate-500">PDF Document</p>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">{message}</span>
            <span className="text-slate-800 font-medium">{Math.round(progress)}%</span>
          </div>
          
          <Progress value={progress} className="h-3" />
        </div>

        <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
          <div className={`text-center p-3 rounded-lg transition-colors ${
            progress >= 25 ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
          }`}>
            <div className="font-medium mb-1">Text Extraction</div>
            <div className="text-xs">Parsing PDF content</div>
          </div>
          
          <div className={`text-center p-3 rounded-lg transition-colors ${
            progress >= 50 ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
          }`}>
            <div className="font-medium mb-1">Text Processing</div>
            <div className="text-xs">Preparing for TTS</div>
          </div>
          
          <div className={`text-center p-3 rounded-lg transition-colors ${
            progress >= 75 ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
          }`}>
            <div className="font-medium mb-1">Voice Synthesis</div>
            <div className="text-xs">Converting to audio</div>
          </div>
          
          <div className={`text-center p-3 rounded-lg transition-colors ${
            progress >= 100 ? 'bg-green-50 text-green-700' : 'bg-slate-50 text-slate-500'
          }`}>
            <div className="font-medium mb-1">Finalization</div>
            <div className="text-xs">Preparing download</div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-slate-500">
            This process typically takes 1-3 minutes depending on document length
          </p>
        </div>
      </div>
    </div>
  )
}
