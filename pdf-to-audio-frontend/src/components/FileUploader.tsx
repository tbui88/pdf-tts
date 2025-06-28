import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

interface FileUploaderProps {
  onFileUpload: (file: File) => void
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onFileUpload }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
  console.log("📥 File dropped:", acceptedFiles); // ✅ NEW LOG

  if (acceptedFiles.length > 0) {
    const file = acceptedFiles[0];
    console.log("📨 Calling onFileUpload with:", file.name); // ✅ NEW LOG
    onFileUpload(file);
  }
}, [onFileUpload]);


  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject,
    fileRejections
  } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024, // 50MB
  })

  const hasRejectedFiles = fileRejections && fileRejections.length > 0

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer",
          "hover:border-indigo-400 hover:bg-indigo-50/50",
          isDragActive && !isDragReject && "border-indigo-500 bg-indigo-50",
          isDragReject && "border-red-400 bg-red-50",
          !isDragActive && "border-slate-300 bg-white"
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <div className={cn(
            "w-16 h-16 rounded-full flex items-center justify-center transition-colors",
            isDragActive && !isDragReject && "bg-indigo-100",
            isDragReject && "bg-red-100",
            !isDragActive && "bg-slate-100"
          )}>
            {isDragReject ? (
              <AlertCircle className="w-8 h-8 text-red-500" />
            ) : (
              <Upload className={cn(
                "w-8 h-8 transition-colors",
                isDragActive ? "text-indigo-600" : "text-slate-500"
              )} />
            )}
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">
              {isDragActive && !isDragReject
                ? "Drop your PDF here"
                : isDragReject
                ? "Invalid file type"
                : "Upload your PDF document"
              }
            </h3>
            <p className="text-slate-600 mb-4">
              {isDragReject
                ? "Please upload a valid PDF file"
                : "Drag and drop a PDF file here, or click to browse"
              }
            </p>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-slate-500">
            <FileText className="w-4 h-4" />
            <span>PDF files only • Max 50MB</span>
          </div>
        </div>

        {/* Animated border gradient */}
        <div className={cn(
          "absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300",
          "bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20",
          isDragActive && !isDragReject && "opacity-100"
        )} />
      </div>

      {hasRejectedFiles && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-2 text-red-800">
            <AlertCircle className="w-5 h-5" />
            <span className="font-medium">Upload Error</span>
          </div>
          <ul className="mt-2 text-sm text-red-700">
            {fileRejections.map((rejection, index) => (
              <li key={index}>
                {rejection.file.name}: {rejection.errors.map(e => e.message).join(', ')}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8 grid md:grid-cols-3 gap-4 text-center">
        <div className="p-4 bg-white rounded-xl border border-slate-200">
          <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <FileText className="w-4 h-4 text-blue-600" />
          </div>
          <h4 className="font-medium text-slate-800 mb-1">Text Extraction</h4>
          <p className="text-sm text-slate-600">Advanced PDF parsing technology</p>
        </div>
        
        <div className="p-4 bg-white rounded-xl border border-slate-200">
          <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <Upload className="w-4 h-4 text-green-600" />
          </div>
          <h4 className="font-medium text-slate-800 mb-1">AI Conversion</h4>
          <p className="text-sm text-slate-600">High-quality text-to-speech</p>
        </div>
        
        <div className="p-4 bg-white rounded-xl border border-slate-200">
          <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <h4 className="font-medium text-slate-800 mb-1">Audio Download</h4>
          <p className="text-sm text-slate-600">MP3 format ready to use</p>
        </div>
      </div>
    </div>
  )
}
