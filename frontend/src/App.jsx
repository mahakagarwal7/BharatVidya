import { useState, useEffect, useRef } from "react";
import "./App.css";


const API_BASE = import.meta.env.VITE_API_URL || "";

function App() {
  const [theme, setTheme] = useState("dark");
  const [concept, setConcept] = useState("");
  const [language, setLanguage] = useState("en");
  const [enableAnimations, setEnableAnimations] = useState(true);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [videos, setVideos] = useState([]);
  const [showExamples, setShowExamples] = useState(false);
  const [selectedVideo, setSelectedVideo] = useState(null);

 
  const defaultLanguages = [
    { code: "en", name: "English" },
    { code: "hi", name: "Hindi" },
    { code: "ta", name: "Tamil" },
    { code: "te", name: "Telugu" },
    { code: "bn", name: "Bengali" },
    { code: "mr", name: "Marathi" },
    { code: "gu", name: "Gujarati" },
    { code: "kn", name: "Kannada" },
    { code: "ml", name: "Malayalam" },
    { code: "pa", name: "Punjabi" },
  ];

  const [languages, setLanguages] = useState(defaultLanguages);
  const [isGenerating, setIsGenerating] = useState(false);
  const pollInterval = useRef(null);


  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

 
  const exampleTopics = [
    {
      title: "Photosynthesis",
      icon: "🌱",
      desc: "How plants convert sunlight",
    },
    { title: "Binary Search", icon: "🔍", desc: "Algorithm deep dive" },
    { title: "Newton's Laws", icon: "⚙️", desc: "Physics fundamentals" },
    { title: "DNA Structure", icon: "🧬", desc: "Molecular biology" },
    { title: "Quantum Computing", icon: "⚛️", desc: "Future of computing" },
    { title: "Climate Change", icon: "🌍", desc: "Environmental science" },
  ];


  useEffect(() => {
    fetch(`${API_BASE}/api/topics`)
      .then((res) => res.json())
      .then((data) => {
        if (data.supported_languages && data.supported_languages.length > 0) {
          setLanguages(data.supported_languages);
        }
      })
      .catch((err) => console.error("Failed to fetch topics:", err));
    fetchVideos();
  }, []);

  const fetchVideos = () => {
    fetch(`${API_BASE}/api/videos`)
      .then((res) => res.json())
      .then((data) => setVideos(data.videos || []))
      .catch((err) => console.error("Failed to fetch videos:", err));
  };


  useEffect(() => {
    if (jobId && isGenerating) {
      pollInterval.current = setInterval(() => {
        fetch(`${API_BASE}/api/status/${jobId}`)
          .then((res) => res.json())
          .then((data) => {
            setStatus(data);
            if (data.status === "complete" || data.status === "failed") {
              setIsGenerating(false);
              clearInterval(pollInterval.current);
              if (data.status === "complete") {
                fetchVideos();
              }
            }
          })
          .catch((err) => console.error("Poll error:", err));
      }, 2000);
    }
    return () => {
      if (pollInterval.current) clearInterval(pollInterval.current);
    };
  }, [jobId, isGenerating]);

  const handleGenerate = async () => {
    if (!concept.trim()) return;

    setIsGenerating(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          concept: concept.trim(),
          language,
          enable_animations: enableAnimations,
        }),
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus({ status: "queued", step: "Starting...", progress: 0 });
    } catch (err) {
      console.error("Generate error:", err);
      setIsGenerating(false);
      setStatus({ status: "failed", error: err.message });
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "complete":
        return "✨";
      case "failed":
        return "❌";
      case "queued":
        return "📋";
      default:
        return "🎬";
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "complete":
        return "from-green-500 to-emerald-600";
      case "failed":
        return "from-red-500 to-pink-600";
      case "queued":
        return "from-yellow-500 to-orange-600";
      default:
        return "from-blue-500 to-cyan-600";
    }
  };

  return (
    <div className="min-h-screen overflow-x-hidden" data-theme={theme}>
      
      <nav className="fixed top-0 w-full z-50 glass-card backdrop-blur-xl border-b theme-border">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center font-bold text-lg text-white">
              🎬
            </div>
            <h1 className="text-2xl font-bold gradient-text">BharatVidya</h1>
          </div>
          <div className="flex items-center gap-4">
            <p className="hidden sm:block text-sm theme-text-secondary">
              AI-Powered Educational Videos
            </p>
            
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="p-2 rounded-lg theme-toggle-btn transition-all hover:scale-110"
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            >
              {theme === "dark" ? "☀️" : "🌙"}
            </button>
          </div>
        </div>
      </nav>


      <div className="pt-24 pb-12 px-4 md:px-8">
        <div className="max-w-6xl mx-auto">
          
          <section className="mb-16 text-center">
            <h2 className="text-4xl md:text-6xl font-bold mb-4 fade-in theme-text-primary">
              Create <span className="gradient-text">Amazing</span> Educational
              Videos
            </h2>
            <p
              className="text-xl mb-8 max-w-2xl mx-auto fade-in theme-text-secondary"
              style={{ animationDelay: "0.1s" }}
            >
              Transform any topic into engaging, animated video content with
              AI-powered narration in multiple languages
            </p>

            
            <div
              className="flex flex-wrap justify-center gap-3 mb-8"
              style={{ animationDelay: "0.2s" }}
            >
              <span className="px-4 py-2 rounded-full theme-pill-blue text-sm font-medium">
                ✨ AI-Powered
              </span>
              <span className="px-4 py-2 rounded-full theme-pill-purple text-sm font-medium">
                🌍 10+ Languages
              </span>
              <span className="px-4 py-2 rounded-full theme-pill-cyan text-sm font-medium">
                🎨 Animated
              </span>
            </div>
          </section>

          
          <div className="glass-card p-8 md:p-10 mb-12 glow-effect">
            <div className="space-y-6">
             
              <div>
                <label className="block text-sm font-semibold theme-text-primary mb-3 uppercase tracking-wide">
                  📝 What Topic Would You Like to Learn About?
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={concept}
                    onChange={(e) => setConcept(e.target.value)}
                    placeholder="e.g., Photosynthesis, Binary Search, Newton's Laws..."
                    className="w-full px-6 py-4 border rounded-xl 
                               focus:outline-none focus:ring-2 
                               focus:ring-blue-500 focus:border-transparent transition-all text-lg"
                    onKeyDown={(e) =>
                      e.key === "Enter" && !isGenerating && handleGenerate()
                    }
                  />
                  {concept && (
                    <button
                      onClick={() => setConcept("")}
                      className="absolute right-4 top-1/2 -translate-y-1/2 theme-text-secondary hover:theme-text-primary transition-colors"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>

              <div>
                <button
                  onClick={() => setShowExamples(!showExamples)}
                  className="text-sm theme-text-secondary hover:theme-pill-blue transition-colors flex items-center gap-2"
                >
                  {showExamples ? "▼" : "▶"} Need inspiration? See examples
                </button>
                {showExamples && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4">
                    {exampleTopics.map((topic) => (
                      <button
                        key={topic.title}
                        onClick={() => {
                          setConcept(topic.title);
                          setShowExamples(false);
                        }}
                        className="p-3 rounded-lg border theme-border 
                                 bg-gradient-to-br from-white/10 to-white/5 
                                 hover:from-white/15 hover:to-white/10
                                 hover:border-blue-500/50 transition-all text-left group"
                      >
                        <span className="text-xl mb-1 block">{topic.icon}</span>
                        <p className="text-sm font-medium theme-text-primary group-hover:theme-pill-blue transition-colors">
                          {topic.title}
                        </p>
                        <p className="text-xs theme-text-secondary">
                          {topic.desc}
                        </p>
                      </button>
                    ))}
                  </div>
                )}
              </div>

  
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t theme-border">
        
                <div>
                  <label className="block text-sm font-semibold theme-text-primary mb-3 uppercase tracking-wide">
                    🌐 Language
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-3 border rounded-lg 
                               focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                  >
                    {languages.map((lang) => (
                      <option
                        key={lang.code}
                        value={lang.code}
                        className="bg-gray-800"
                      >
                        {lang.name}
                      </option>
                    ))}
                  </select>
                </div>

     
                <div className="flex items-center justify-between p-4 rounded-lg border theme-border">
                  <div>
                    <p className="font-semibold theme-text-primary">
                      ✨ Include Animations
                    </p>
                    <p className="text-xs theme-text-secondary mt-1">
                      Make videos more engaging
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={enableAnimations}
                      onChange={(e) => setEnableAnimations(e.target.checked)}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-600 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>

         
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !concept.trim()}
                className={`w-full btn-primary py-5 px-6 rounded-xl font-bold text-lg transition-all ${
                  isGenerating || !concept.trim()
                    ? "bg-gray-700/50 theme-text-secondary cursor-not-allowed"
                    : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-2xl hover:shadow-blue-600/40 transform hover:scale-[1.02]"
                }`}
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spinner"></span>
                    Generating Your Video...
                  </span>
                ) : (
                  "🚀 Generate Video"
                )}
              </button>
            </div>
          </div>

      
          {status && (
            <div
              className={`glass-card p-8 mb-12 transition-all ${isGenerating ? "pulse-glow" : ""}`}
            >
              <div className="space-y-6">
             
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-4xl">
                      {getStatusIcon(status.status)}
                    </span>
                    <div>
                      <h3 className="text-2xl font-bold theme-text-primary">
                        {status.status === "complete"
                          ? "🎉 Video Ready!"
                          : status.status === "failed"
                            ? "⚠️ Generation Failed"
                            : "⏳ Generating..."}
                      </h3>
                      <p className="text-sm theme-text-secondary mt-1">
                        {status.step ||
                          (status.status === "failed" ? status.error : "")}
                      </p>
                    </div>
                  </div>
                  <span className="text-3xl font-bold text-transparent bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text">
                    {Math.min(status.progress || 0, 100)}%
                  </span>
                </div>

            
                <div className="space-y-2">
                  <div
                    className="h-3 rounded-full overflow-hidden"
                    style={{ backgroundColor: "var(--glass-bg)" }}
                  >
                    <div
                      className="progress-bar h-full rounded-full"
                      style={{
                        width: `${Math.min(status.progress || 0, 100)}%`,
                      }}
                    />
                  </div>

         
                  <div className="flex justify-between text-xs theme-text-secondary px-1">
                    <span>Planning</span>
                    <span>Rendering</span>
                    <span>Audio</span>
                    <span>Finalizing</span>
                  </div>
                </div>

          
                {status.status === "complete" && status.video_url && (
                  <div className="space-y-4 pt-4 border-t theme-border">
                    <div className="relative rounded-xl overflow-hidden shadow-2xl">
                      <video
                        controls
                        className="w-full bg-black/50"
                        src={status.video_url}
                      >
                        Your browser does not support the video tag.
                      </video>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3">
                      <a
                        href={status.video_url}
                        download
                        className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-lg text-center font-semibold transition-all transform hover:scale-[1.02] shadow-lg"
                      >
                        ⬇️ Download Video
                      </a>
                      <button
                        onClick={() => {
                          setStatus(null);
                          setJobId(null);
                          setConcept("");
                        }}
                        className="flex-1 py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-lg text-center font-semibold transition-all transform hover:scale-[1.02] shadow-lg"
                      >
                        ➕ Create Another
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

   
          {videos.length > 0 && !selectedVideo && (
            <section className="mb-12">
              <h3 className="text-3xl font-bold mb-8 gradient-text">
                🎬 Recent Videos
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {videos.slice(0, 9).map((video, index) => (
                  <button
                    key={video.job_id}
                    onClick={() => setSelectedVideo(video)}
                    className="glass-card overflow-hidden group cursor-pointer transform transition-all hover:scale-[1.05]"
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <div className="relative h-48 bg-gradient-to-br from-blue-500/20 to-purple-600/20 overflow-hidden">
                      <div className="absolute inset-0 flex items-center justify-center group-hover:scale-110 transition-transform">
                        <span className="text-6xl opacity-50">🎬</span>
                      </div>
                      <div className="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/80 backdrop-blur">
                        {video.language?.toUpperCase() || "EN"}
                      </div>
                    </div>
                    <div className="p-4">
                      <h4 className="font-bold text-lg mb-1 theme-text-primary group-hover:theme-pill-blue transition-colors line-clamp-2">
                        {video.title || video.concept}
                      </h4>
                      <p className="text-sm theme-text-secondary line-clamp-2">
                        {video.concept}
                      </p>
                      <div className="mt-4 flex items-center justify-between text-xs theme-text-secondary">
                        <span>
                          📅{" "}
                          {new Date(
                            video.created_at || Date.now(),
                          ).toLocaleDateString()}
                        </span>
                        <span className="text-blue-400">Play →</span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </section>
          )}

     
          {selectedVideo && (
            <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
              <div className="glass-card max-w-4xl w-full max-h-[90vh] overflow-auto p-6 md:p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl md:text-3xl font-bold theme-text-primary">
                    {selectedVideo.title || selectedVideo.concept}
                  </h2>
                  <button
                    onClick={() => setSelectedVideo(null)}
                    className="text-2xl theme-text-secondary hover:text-red-400 transition-colors"
                  >
                    ✕
                  </button>
                </div>

                <div className="space-y-4">
                  <video
                    controls
                    autoPlay
                    className="w-full rounded-lg shadow-2xl bg-black"
                    src={selectedVideo.video_url}
                  >
                    Your browser does not support the video tag.
                  </video>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t theme-border">
                    <div className="p-3 bg-gradient-to-br from-white/10 to-white/5 rounded-lg">
                      <p className="text-xs theme-text-secondary uppercase">
                        Concept
                      </p>
                      <p className="text-sm font-bold mt-1 theme-text-primary">
                        {selectedVideo.concept}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-white/10 to-white/5 rounded-lg">
                      <p className="text-xs theme-text-secondary uppercase">
                        Language
                      </p>
                      <p className="text-sm font-bold mt-1 theme-text-primary">
                        {selectedVideo.language?.toUpperCase() || "EN"}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-white/10 to-white/5 rounded-lg">
                      <p className="text-xs theme-text-secondary uppercase">
                        Created
                      </p>
                      <p className="text-sm font-bold mt-1 theme-text-primary">
                        {new Date(
                          selectedVideo.created_at || Date.now(),
                        ).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="p-3 bg-gradient-to-br from-white/10 to-white/5 rounded-lg">
                      <p className="text-xs theme-text-secondary uppercase">
                        Duration
                      </p>
                      <p className="text-sm font-bold mt-1 theme-text-primary">
                        ~2-3 min
                      </p>
                    </div>
                  </div>

                  <a
                    href={selectedVideo.video_url}
                    download
                    className="block w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-lg text-center font-semibold transition-all"
                  >
                    ⬇️ Download Video
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

   
      <footer className="border-t theme-border mt-20 py-8 px-4">
        <div className="max-w-6xl mx-auto text-center theme-text-secondary text-sm space-y-2">
          <p>✨ Powered by Ollama + MoviePy + Edge-TTS ✨</p>
          <p>Transform education with AI-powered video generation</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
