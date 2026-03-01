import { useState, useEffect, useRef } from 'react'
import './App.css'

// API base URL - empty for local dev (uses Vite proxy), or set VITE_API_URL for production
const API_BASE = import.meta.env.VITE_API_URL || ''

function App() {
  const [concept, setConcept] = useState('')
  const [language, setLanguage] = useState('en')
  const [enableAnimations, setEnableAnimations] = useState(true)
  const [jobId, setJobId] = useState(null)
  const [status, setStatus] = useState(null)
  const [videos, setVideos] = useState([])
  // Default languages - used as fallback if API fails
  const defaultLanguages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'Hindi' },
    { code: 'ta', name: 'Tamil' },
    { code: 'te', name: 'Telugu' },
    { code: 'bn', name: 'Bengali' },
    { code: 'mr', name: 'Marathi' },
    { code: 'gu', name: 'Gujarati' },
    { code: 'kn', name: 'Kannada' },
    { code: 'ml', name: 'Malayalam' },
    { code: 'pa', name: 'Punjabi' }
  ]
  
  const [languages, setLanguages] = useState(defaultLanguages)
  const [isGenerating, setIsGenerating] = useState(false)
  const pollInterval = useRef(null)

  // Fetch supported languages on mount
  useEffect(() => {
    fetch(`${API_BASE}/api/topics`)
      .then(res => res.json())
      .then(data => {
        if (data.supported_languages && data.supported_languages.length > 0) {
          setLanguages(data.supported_languages)
        }
      })
      .catch(err => console.error('Failed to fetch topics:', err))
    
    // Fetch existing videos
    fetchVideos()
  }, [])

  const fetchVideos = () => {
    fetch(`${API_BASE}/api/videos`)
      .then(res => res.json())
      .then(data => setVideos(data.videos || []))
      .catch(err => console.error('Failed to fetch videos:', err))
  }

  // Poll for job status
  useEffect(() => {
    if (jobId && isGenerating) {
      pollInterval.current = setInterval(() => {
        fetch(`${API_BASE}/api/status/${jobId}`)
          .then(res => res.json())
          .then(data => {
            setStatus(data)
            if (data.status === 'complete' || data.status === 'failed') {
              setIsGenerating(false)
              clearInterval(pollInterval.current)
              if (data.status === 'complete') {
                fetchVideos()
              }
            }
          })
          .catch(err => console.error('Poll error:', err))
      }, 2000)
    }
    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current)
    }
  }, [jobId, isGenerating])

  const handleGenerate = async () => {
    if (!concept.trim()) return
    
    setIsGenerating(true)
    setStatus(null)
    
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept: concept.trim(),
          language,
          enable_animations: enableAnimations
        })
      })
      const data = await res.json()
      setJobId(data.job_id)
      setStatus({ status: 'queued', step: 'Starting...', progress: 0 })
    } catch (err) {
      console.error('Generate error:', err)
      setIsGenerating(false)
      setStatus({ status: 'failed', error: err.message })
    }
  }

  return (
    <div className="min-h-screen text-white p-4 md:p-8">
      {/* Header */}
      <header className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          BharatVidya
        </h1>
        <p className="text-gray-400 mt-2">Generate educational explainer videos with AI</p>
      </header>

      <div className="max-w-4xl mx-auto">
        {/* Input Card */}
        <div className="glass-card p-6 md:p-8 mb-8">
          <div className="space-y-6">
            {/* Concept Input */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                What would you like to learn about?
              </label>
              <input
                type="text"
                value={concept}
                onChange={(e) => setConcept(e.target.value)}
                placeholder="e.g., Photosynthesis, Binary Search, Newton's Laws..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg 
                           text-white placeholder-gray-500 focus:outline-none focus:ring-2 
                           focus:ring-blue-500 focus:border-transparent transition-all"
                onKeyDown={(e) => e.key === 'Enter' && !isGenerating && handleGenerate()}
              />
            </div>

            {/* Options Row */}
            <div className="flex flex-col md:flex-row gap-4">
              {/* Language Select */}
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg 
                             text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {languages.map(lang => (
                    <option key={lang.code} value={lang.code} className="bg-gray-800">
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Animation Toggle */}
              <div className="flex items-end">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={enableAnimations}
                    onChange={(e) => setEnableAnimations(e.target.checked)}
                    className="w-5 h-5 rounded border-gray-600 bg-white/5 text-blue-500 
                               focus:ring-blue-500 focus:ring-offset-0"
                  />
                  <span className="text-gray-300">Include animations</span>
                </label>
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !concept.trim()}
              className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all
                ${isGenerating || !concept.trim()
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-blue-500/25'
                }`}
            >
              {isGenerating ? 'Generating...' : 'Generate Video'}
            </button>
          </div>
        </div>

        {/* Progress Card */}
        {status && (
          <div className={`glass-card p-6 mb-8 ${isGenerating ? 'pulse-glow' : ''}`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {status.status === 'complete' ? '✅ Complete!' : 
                 status.status === 'failed' ? '❌ Failed' : 
                 '🎬 Generating...'}
              </h3>
              <span className="text-sm text-gray-400">
                {status.progress || 0}%
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-4">
              <div 
                className="progress-bar h-full rounded-full"
                style={{ width: `${status.progress || 0}%` }}
              />
            </div>
            
            <p className="text-sm text-gray-400">{status.step || status.error || ''}</p>

            {/* Video Player */}
            {status.status === 'complete' && status.video_url && (
              <div className="mt-6">
                <video 
                  controls 
                  className="w-full rounded-lg shadow-xl"
                  src={status.video_url}
                >
                  Your browser does not support the video tag.
                </video>
                <div className="mt-4 flex gap-4">
                  <a
                    href={status.video_url}
                    download
                    className="flex-1 py-2 px-4 bg-blue-600 hover:bg-blue-700 rounded-lg 
                               text-center font-medium transition-colors"
                  >
                    ⬇️ Download Video
                  </a>
                  <button
                    onClick={() => {
                      setStatus(null)
                      setJobId(null)
                      setConcept('')
                    }}
                    className="flex-1 py-2 px-4 bg-white/10 hover:bg-white/20 rounded-lg 
                               text-center font-medium transition-colors"
                  >
                    ➕ Create Another
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Video History */}
        {videos.length > 0 && (
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold mb-4">📚 Recent Videos</h3>
            <div className="space-y-3">
              {videos.slice(0, 5).map(video => (
                <div 
                  key={video.job_id}
                  className="flex items-center justify-between p-3 bg-white/5 rounded-lg 
                             hover:bg-white/10 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium truncate">{video.title}</h4>
                    <p className="text-sm text-gray-400">{video.concept}</p>
                  </div>
                  <a
                    href={video.video_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 px-3 py-1 bg-blue-600/20 text-blue-400 rounded-lg 
                               hover:bg-blue-600/30 transition-colors text-sm"
                  >
                    Watch
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center text-gray-500 text-sm mt-12">
        Powered by Ollama + MoviePy + Edge-TTS
      </footer>
    </div>
  )
}

export default App
