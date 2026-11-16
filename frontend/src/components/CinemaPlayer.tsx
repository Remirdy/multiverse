import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Maximize2, Film } from 'lucide-react';

interface CinemaPlayerProps {
  src?: string;
  title?: string;
  aspectRatio?: '9:16' | '16:9';
  durationSeconds?: number;
}

export const CinemaPlayer: React.FC<CinemaPlayerProps> = ({
  title = 'NVIDIA Cosmos WFM • 9:16 ARRI Cinema Preview',
  durationSeconds = 15,
}) => {
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [isMuted, setIsMuted] = useState<boolean>(true);
  const [activeSegmentIndex, setActiveSegmentIndex] = useState<number>(0);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Istanbul Rain Scene segments based on prompt
  const segments = [
    { start: 0, end: 4, label: '00:00–00:04', desc: 'Islak Asfalt, Su Birikintisi & Sarı Taksi Sıçraması' },
    { start: 4, end: 8, label: '00:04–00:08', desc: 'Geleneksel Çay Tezgâhı & İnce Belli Bardağa Çay Dökümü' },
    { start: 8, end: 12, label: '00:08–00:12', desc: 'Bardağın El Değiştirmesi, Dalgalanma Fiziği & Sokak Kedisi' },
    { start: 12, end: 15, label: '00:12–00:15', desc: 'Şeffaf Şemsiyede Yağmur Damlaları, İlk Yudum & Şehir Otobüsü' },
  ];

  // Procedural Canvas Animation for Rainy Istanbul Street
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let width = (canvas.width = canvas.parentElement?.clientWidth || 360);
    let height = (canvas.height = Math.round(width * (16 / 9)));

    // Rain particles
    const rainCount = 120;
    const raindrops = Array.from({ length: rainCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      len: Math.random() * 20 + 15,
      speed: Math.random() * 8 + 14,
      opacity: Math.random() * 0.4 + 0.2,
    }));

    // Lens water droplets
    const lensDrops = Array.from({ length: 18 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 7 + 3,
      alpha: Math.random() * 0.35 + 0.15,
      trail: Math.random() * 20 + 5,
    }));

    let frame = 0;

    const render = () => {
      frame++;
      // Background gradient: overcast autumn morning in Istanbul
      const grad = ctx.createLinearGradient(0, 0, 0, height);
      grad.addColorStop(0, '#0d1520'); // Dark overcast gray-blue sky
      grad.addColorStop(0.45, '#162232'); // Rainy street horizon
      grad.addColorStop(0.7, '#111822'); // Wet asphalt
      grad.addColorStop(1, '#080d14'); // Deep reflections

      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      // Distant amber/yellow warmth of tea stand & taxi lights
      const taxiGlow = ctx.createRadialGradient(
        width * 0.35 + Math.sin(frame * 0.02) * 20,
        height * 0.55,
        10,
        width * 0.35,
        height * 0.55,
        width * 0.45
      );
      taxiGlow.addColorStop(0, 'rgba(245, 158, 11, 0.25)'); // Taxi yellow
      taxiGlow.addColorStop(0.5, 'rgba(217, 119, 6, 0.08)');
      taxiGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = taxiGlow;
      ctx.fillRect(0, 0, width, height);

      // Tea stand warm steam glow
      const teaGlow = ctx.createRadialGradient(
        width * 0.65,
        height * 0.62,
        5,
        width * 0.65,
        height * 0.62,
        width * 0.35
      );
      teaGlow.addColorStop(0, 'rgba(239, 68, 68, 0.22)'); // Turkish tea amber-red
      teaGlow.addColorStop(0.4, 'rgba(249, 115, 22, 0.08)');
      teaGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = teaGlow;
      ctx.fillRect(0, 0, width, height);

      // Wet asphalt reflection ripples
      ctx.strokeStyle = 'rgba(125, 211, 252, 0.12)';
      ctx.lineWidth = 1;
      for (let i = 0; i < 6; i++) {
        const ry = height * 0.72 + i * 22;
        ctx.beginPath();
        ctx.ellipse(
          width * 0.5 + Math.sin(frame * 0.03 + i) * 30,
          ry,
          width * 0.4,
          6 + i * 2,
          0,
          0,
          Math.PI * 2
        );
        ctx.stroke();
      }

      // Draw Rain Falling
      ctx.strokeStyle = 'rgba(186, 230, 253, 0.45)';
      ctx.lineWidth = 1.2;
      for (const drop of raindrops) {
        ctx.beginPath();
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x - 3, drop.y + drop.len);
        ctx.stroke();

        drop.y += drop.speed;
        drop.x -= 1.5;
        if (drop.y > height) {
          drop.y = -drop.len;
          drop.x = Math.random() * width + 50;
        }
      }

      // Draw Lens Droplets (Water on ARRI Camera Lens)
      for (const ld of lensDrops) {
        ctx.beginPath();
        ctx.fillStyle = `rgba(224, 242, 254, ${ld.alpha})`;
        ctx.arc(ld.x, ld.y, ld.r, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = `rgba(255, 255, 255, ${ld.alpha * 1.5})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();

        // Subtle slow downward crawl
        ld.y += 0.15;
        if (ld.y > height) ld.y = 0;
      }

      // Rising Tea Steam Particles (Simulating 85°C hot tea in cold Istanbul morning)
      ctx.fillStyle = 'rgba(255, 255, 255, 0.07)';
      for (let s = 0; s < 12; s++) {
        const sx = width * 0.65 + Math.sin(frame * 0.04 + s) * 16;
        const sy = height * 0.62 - ((frame * 1.5 + s * 25) % 140);
        const sr = 8 + ((frame + s * 10) % 25);
        ctx.beginPath();
        ctx.arc(sx, sy, sr, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Timecode scrubber timer
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          const next = prev + 0.1;
          if (next >= durationSeconds) return 0;
          return next;
        });
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying, durationSeconds]);

  // Update active segment description
  useEffect(() => {
    const idx = segments.findIndex((s) => currentTime >= s.start && currentTime < s.end);
    if (idx !== -1 && idx !== activeSegmentIndex) {
      setActiveSegmentIndex(idx);
    }
  }, [currentTime]);

  const formatTC = (sec: number) => {
    const s = Math.floor(sec);
    const ms = Math.floor((sec - s) * 24);
    return `00:00:${s.toString().padStart(2, '0')}:${ms.toString().padStart(2, '0')}`;
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTime(parseFloat(e.target.value));
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
      className="my-5 rounded-2xl overflow-hidden border border-cyan-500/40 shadow-[0_0_35px_rgba(6,182,212,0.18)] bg-space-950/95 font-sans"
    >
      {/* Top Telemetry Header */}
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
        <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
          <span className="hidden sm:inline text-emerald-400">ARRI ALEXA 35</span>
          <span className="text-slate-500">•</span>
          <span>35mm T1.8</span>
          <span className="text-slate-500">•</span>
          <span className="text-cyan-400">24.000 FPS</span>
        </div>
      </div>

      {/* Main Viewfinder Screen (9:16 Aspect Framing) */}
      <div className="relative w-full max-w-[360px] mx-auto bg-black aspect-[9/16] overflow-hidden select-none">
        {/* Procedural Simulation Canvas */}
        <canvas ref={canvasRef} className="w-full h-full object-cover" />

        {/* Cinematic Viewfinder Grid & Framing Reticle */}
        <div className="absolute inset-0 pointer-events-none border border-white/10 m-3 rounded-lg flex flex-col justify-between p-3">
          {/* Top Camera Metadata */}
          <div className="flex items-center justify-between text-[10px] font-mono text-white/70">
            <span>TC {formatTC(currentTime)}</span>
            <span>SHUTTER 180.0°</span>
            <span>EI 800</span>
          </div>

          {/* Center Crosshair & Level */}
          <div className="relative self-center my-auto flex items-center justify-center opacity-40">
            <div className="w-10 h-[1px] bg-white"></div>
            <div className="w-[1px] h-10 bg-white absolute"></div>
            <div className="w-5 h-5 rounded-full border border-white absolute"></div>
          </div>

          {/* Bottom Telemetry */}
          <div className="flex items-center justify-between text-[10px] font-mono text-white/70">
            <span className="text-emerald-400">NAV-STOKES FLUID ACTIVE</span>
            <span>1080×1920 (9:16)</span>
          </div>
        </div>

        {/* Live Segment Beat Notification */}
        <div className="absolute top-5 inset-x-5 pointer-events-none flex justify-center">
          <div className="px-3 py-1.5 rounded-xl bg-black/75 backdrop-blur-md border border-cyan-500/30 text-center max-w-[280px] shadow-lg animate-fadeIn">
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold block">
              {segments[activeSegmentIndex]?.label}
            </span>
            <span className="text-xs text-slate-200 line-clamp-2 mt-0.5 leading-snug">
              {segments[activeSegmentIndex]?.desc}
            </span>
          </div>
        </div>
      </div>

      {/* Timeline Scrubber & Chronological Beat Marks */}
      <div className="px-4 py-3 bg-space-900/90 border-t border-slate-800 space-y-2.5">
        <div className="flex items-center justify-between text-xs font-mono text-slate-300">
          <span className="text-cyan-300 font-semibold">{formatTC(currentTime)}</span>
          <span className="text-slate-500">/ 00:00:15:00</span>
        </div>

        {/* Scrubber Progress Bar */}
        <div className="relative flex items-center">
          <input
            type="range"
            min={0}
            max={durationSeconds}
            step={0.05}
            value={currentTime}
            onChange={handleSeek}
            className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 hover:accent-cyan-300"
          />
        </div>

        {/* Chronological 4-Beat Pills */}
        <div className="grid grid-cols-4 gap-1.5 pt-1 text-[10px] font-mono">
          {segments.map((seg, idx) => (
            <button
              key={seg.label}
              onClick={() => setCurrentTime(seg.start)}
              className={`py-1 px-1.5 rounded text-center transition-all truncate ${
                activeSegmentIndex === idx
                  ? 'bg-cyan-950/80 text-cyan-300 border border-cyan-500/60 font-semibold shadow-sm'
                  : 'bg-space-850 text-slate-400 border border-slate-800 hover:text-slate-200'
              }`}
              title={seg.desc}
            >
              {seg.label}
            </button>
          ))}
        </div>

        {/* Player Controls Bar */}
        <div className="flex items-center justify-between pt-1 text-slate-300">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="p-2 rounded-xl bg-cyan-500 text-slate-950 hover:bg-cyan-400 transition-colors shadow-md"
              title={isPlaying ? 'Durdur' : 'Oynat'}
            >
              {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
            </button>
            <button
              onClick={() => setCurrentTime(0)}
              className="p-2 rounded-xl bg-space-800 text-slate-300 hover:text-white hover:bg-space-700 transition-colors"
              title="Başa Sar"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsMuted(!isMuted)}
              className={`p-2 rounded-xl transition-colors ${
                !isMuted ? 'bg-cyan-950 text-cyan-300 border border-cyan-800' : 'bg-space-800 text-slate-400 hover:text-slate-200'
              }`}
              title={isMuted ? 'Yağmur Ambiyans Sesi Aç' : 'Sesi Kapat'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline text-[11px] text-slate-400 font-mono">
              NVIDIA Cosmos WFM Engine
            </span>
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
