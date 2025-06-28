import React from 'react'
import { Heart } from 'lucide-react'

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-white font-semibold mb-4">AudioPDF</h3>
            <p className="text-sm leading-relaxed">
              Converting PDFs to high-quality audio using advanced AI technology.
              Making documents accessible and portable for everyone.
            </p>
          </div>
          
          <div>
            <h4 className="text-white font-medium mb-4">Features</h4>
            <ul className="space-y-2 text-sm">
              <li>• High-quality TTS conversion</li>
              <li>• Multiple language support</li>
              <li>• Batch processing</li>
              <li>• Mobile-friendly design</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-medium mb-4">Support</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a href="#faq" className="hover:text-white transition-colors">
                  FAQ
                </a>
              </li>
              <li>
                <a href="#help" className="hover:text-white transition-colors">
                  Help Center
                </a>
              </li>
              <li>
                <a href="#contact" className="hover:text-white transition-colors">
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-slate-800 mt-8 pt-8 flex flex-col md:flex-row items-center justify-between">
          <p className="text-sm">
            © 2025 AudioPDF. All rights reserved.
          </p>
          <div className="flex items-center space-x-1 text-sm mt-4 md:mt-0">
            <span>Made with</span>
            <Heart className="w-4 h-4 text-red-500" fill="currentColor" />
            <span>using React & FastAPI</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
