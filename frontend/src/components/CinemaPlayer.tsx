import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Maximize2, Download, Check, Film, Eye } from 'lucide-react';

interface CinemaPlayerProps {
  src?: string;
  title?: string;
  aspectRatio?: '9:16' | '16:9';
  durationSeconds?: number;
}

export const CinemaPlayer: React.FC<CinemaPlayerProps> = ({
  src,
  title = 'NVIDIA Cosmos WFM • 9:16 ARRI Cinema Preview',
  durationSeconds = 15,
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState<number>(0);
  const [downloadSuccess, setDownloadSuccess] = useState<boolean>(false);

  const videoRef = useRef<HTMLVideoElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Fallback video source pointing to our local high-definition video stream
  const videoSource = src || 'http://127.0.0.1:8000/static/istanbul_rain_arri35.mp4';

  // 4 Chronological Beats from user prompt
  const segments = [
    {
      id: 0,
      start: 0,
      end: 4,
      label: '00:00–00:04',
      title: 'Kaldırım & Sarı Taksi Sıçraması',
      camera: '35mm Low-Angle Dolly • Shallow DOF',
      desc: 'Kaldırım su birikintisi, bağımsız yayalar ve sudan geçen sarı taksinin hidrodinamik su sıçraması.',
    },
    {
      id: 1,
      start: 4,
      end: 8,
      label: '00:04–00:08',
      title: 'Çay Tezgâhı & Yerçekimiyle Çay Dökümü',
      camera: 'Medium Push-in • Brass Samovar Focus',
      desc: 'Geleneksel tezgâhta demlikten ince belli bardağa Navier-Stokes yerçekimi akışıyla dolan sıcak çay ve buhar.',
    },
    {
      id: 2,
      start: 8,
      end: 12,
      label: '00:08–00:12',
      title: 'Bardağın Teslimi & Sokak Kedisi',
      camera: 'Two-Shot Tracking • Hand-to-Glass Contact',
      desc: 'Bej trençkotlu kadının bardağı alması, sıvının dalgalanması (sloshing) ve tente altında yürüyen sokak kedisi.',
    },
    {
      id: 3,
      start: 12,
      end: 15,
      label: '00:12–00:15',
      title: 'İlk Yudum, Şeffaf Şemsiye & Şehir Otobüsü',
      camera: 'Close-up Portrait • Bokeh City Bus',
      desc: 'Şeffaf şemsiyede süzülen damlalar, kadının ilk yudumu, göz kırpma mikromimiği ve flu arka planda geçen İETT otobüsü.',
    },
  ];

  // Sync video play/pause
  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.play().catch(() => {});
    } else {
      video.pause();
    }
  }, [isPlaying]);

  // Video time update event
  const handleTimeUpdate = () => {
    const video = videoRef.current;
    if (!video) return;

    const t = video.currentTime;
    setCurrentTime(t);

    const idx = segments.findIndex((s) => t >= s.start && t < s.end);
    if (idx !== -1 && idx !== activeSegmentIndex) {
      setActiveSegmentIndex(idx);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const targetTime = parseFloat(e.target.value);
    setCurrentTime(targetTime);
    if (videoRef.current) {
      videoRef.current.currentTime = targetTime;
    }
  };

  const handleJumpToSegment = (startTime: number) => {
    setCurrentTime(startTime);
    if (videoRef.current) {
      videoRef.current.currentTime = startTime;
      videoRef.current.play().catch(() => {});
      setIsPlaying(true);
    }
  };

  // Direct MP4 Download from FastAPI Static & Attachment Endpoint
  const handleDownload = () => {
    setDownloadSuccess(true);
    const link = document.createElement('a');
    link.href = 'http://127.0.0.1:8000/api/video/download';
    link.setAttribute('download', 'istanbul_rain_arri35_9x16_cinema.mp4');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => setDownloadSuccess(false), 4000);
  };

  const formatTC = (sec: number) => {
    const s = Math.floor(sec);
    const ms = Math.floor((sec - s) * 24);
    return `00:00:${s.toString().padStart(2, '0')}:${ms.toString().padStart(2, '0')}`;
  };

  const toggleFullscreen = () => {
    if (!containerRef.current) return;
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch((err) => console.error(err));
    } else {
      document.exitFullscreen().catch((err) => console.error(err));
    }
  };

  return (
    <div
      ref={containerRef}
      className="my-5 rounded-2xl overflow-hidden border border-cyan-500/50 shadow-[0_0_40px_rgba(6,182,212,0.22)] bg-space-950/95 font-sans"
    >
      {/* Top Telemetry Header with Direct Video Download */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-space-900/90 border-b border-slate-800 text-xs">
        <div className="flex items-center gap-2.5">
          <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-950/80 border border-red-500/50 text-red-400 font-mono text-[11px] font-semibold">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            REC
          </span>
          <span className="font-semibold text-cyan-300 flex items-center gap-1.5">
            <Film className="w-3.5 h-3.5 text-cyan-400" />
            {title}
          </span>
        </div>

        {/* Download Action & Camera Specs */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={handleDownload}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all shadow-md active:scale-95 ${
              downloadSuccess
                ? 'bg-emerald-900/80 text-emerald-300 border border-emerald-500/60'
                : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400'
            }`}
            title="15 saniyelik sinematik videoyu bilgisayarınıza MP4 formatında indirin"
          >
            {downloadSuccess ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>İndirildi!</span>
              </>
            ) : (
              <>
                <Download className="w-3.5 h-3.5" />
                <span>Videoyu İndir (MP4)</span>
              </>
            )}
          </button>

          <span className="hidden md:inline text-[11px] text-slate-400 font-mono">
            ARRI 35mm • 24 FPS
          </span>
        </div>
      </div>

      {/* Main Viewfinder Screen (9:16 Vertical Aspect Framing) */}
      <div className="relative w-full max-w-[360px] mx-auto bg-black aspect-[9/16] overflow-hidden select-none">
        {/* Genuine High-Definition Video Stream */}
        <video
          ref={videoRef}
          src={videoSource}
          controls={false}
          autoPlay
          loop
          muted={isMuted}
          playsInline
          onTimeUpdate={handleTimeUpdate}
          className="w-full h-full object-cover"
        />

        {/* ARRI Alexa 35 Camera Viewfinder Reticle */}
        <div className="absolute inset-0 pointer-events-none border border-white/10 m-3 rounded-lg flex flex-col justify-between p-3">
          <div className="flex items-center justify-between text-[10px] font-mono text-white/70">
            <span>TC {formatTC(currentTime)}</span>
            <span>SHUTTER 180.0°</span>
            <span>EI 800</span>
          </div>

          <div className="relative self-center my-auto flex items-center justify-center opacity-40">
            <div className="w-10 h-[1px] bg-white"></div>
            <div className="w-[1px] h-10 bg-white absolute"></div>
            <div className="w-5 h-5 rounded-full border border-white absolute"></div>
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-white/70">
            <span className="text-emerald-400">NAVIER-STOKES FLUID ACTIVE</span>
            <span>1080×1920 (9:16)</span>
          </div>
        </div>

        {/* Dynamic Segment Header Overlay */}
        <div className="absolute top-4 inset-x-4 pointer-events-none flex justify-center">
          <div className="px-3.5 py-2 rounded-xl bg-black/80 backdrop-blur-md border border-cyan-500/40 text-center max-w-[300px] shadow-2xl">
            <div className="flex items-center justify-center gap-1.5 text-[10px] font-mono text-cyan-400 font-bold uppercase tracking-wider">
              <Eye className="w-3 h-3 text-cyan-300" />
              <span>{segments[activeSegmentIndex]?.label}</span>
              <span className="text-slate-500">•</span>
              <span className="text-slate-300">{segments[activeSegmentIndex]?.camera}</span>
            </div>
            <p className="text-xs font-semibold text-slate-100 mt-1 leading-snug">
              {segments[activeSegmentIndex]?.title}
            </p>
            <p className="text-[11px] text-slate-300 mt-0.5 leading-tight line-clamp-2">
              {segments[activeSegmentIndex]?.desc}
            </p>
          </div>
        </div>
      </div>

      {/* Scrubber & Timeline Control Bar */}
      <div className="px-4 py-3 bg-space-900/90 border-t border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between text-xs font-mono text-slate-300">
          <span className="text-cyan-300 font-semibold">{formatTC(currentTime)}</span>
          <span className="text-slate-500">/ 00:00:15:00 (Single-Take 360 Kare)</span>
        </div>

        {/* Progress Range Slider */}
        <input
          type="range"
          min={0}
          max={durationSeconds}
          step={0.05}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 hover:accent-cyan-300"
        />

        {/* Chronological 4-Scene Selector Buttons */}
        <div className="grid grid-cols-4 gap-1.5 pt-1 text-[10px] font-mono">
          {segments.map((seg, idx) => (
            <button
              key={seg.label}
              onClick={() => handleJumpToSegment(seg.start)}
              className={`py-1.5 px-1.5 rounded-lg text-center transition-all truncate flex flex-col items-center gap-0.5 ${
                activeSegmentIndex === idx
                  ? 'bg-cyan-950/90 text-cyan-300 border border-cyan-500/70 font-semibold shadow-md'
                  : 'bg-space-850 text-slate-400 border border-slate-800 hover:text-slate-200'
              }`}
              title={seg.desc}
            >
              <span className="font-bold">{seg.label}</span>
              <span className="text-[9px] opacity-80 truncate max-w-full">{seg.title}</span>
            </button>
          ))}
        </div>

        {/* Player Controls */}
        <div className="flex items-center justify-between pt-1.5 text-slate-300">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded-xl bg-cyan-500 text-slate-950 hover:bg-cyan-400 transition-colors shadow-md"
              title={isPlaying ? 'Durdur' : 'Oynat'}
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
            </button>
            <button
              onClick={() => handleJumpToSegment(0)}
              className="p-2 rounded-xl bg-space-800 text-slate-300 hover:text-white hover:bg-space-700 transition-colors"
              title="Başa Sar"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsMuted(!isMuted)}
              className={`p-2 rounded-xl transition-colors ${
                !isMuted
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                  : 'bg-space-800 text-slate-400 hover:text-slate-200'
              }`}
              title={isMuted ? 'Sesi Aç' : 'Sesi Kapat'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownload}
              className="px-2.5 py-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-slate-300 hover:text-cyan-300 text-xs flex items-center gap-1.5 transition-colors border border-slate-700/60"
            >
              <Download className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">MP4 İndir</span>
            </button>

            <button
              onClick={toggleFullscreen}
              className="p-2 rounded-xl bg-space-800 text-slate-400 hover:text-white hover:bg-space-700 transition-colors"
              title="Tam Ekran"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
