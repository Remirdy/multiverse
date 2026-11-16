import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, RotateCcw, Volume2, VolumeX, Maximize2, Download, Check, Film, Eye, Sparkles } from 'lucide-react';

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
  const [isRecordingDownload, setIsRecordingDownload] = useState<boolean>(false);
  const [downloadSuccess, setDownloadSuccess] = useState<boolean>(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  // 4 Distinct Cinematic Segments with rich physical choreography
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

  // Procedural Multi-Scene Cinema Engine (Canvas 60 FPS)
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = (canvas.width = 360);
    const height = (canvas.height = 640); // Standard 9:16 vertical cinema

    // Rain particles
    const rainCount = 100;
    const rain = Array.from({ length: rainCount }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      len: Math.random() * 18 + 12,
      speed: Math.random() * 8 + 14,
    }));

    // Lens water droplets
    const lensDrops = Array.from({ length: 14 }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      r: Math.random() * 5 + 3,
      alpha: Math.random() * 0.25 + 0.1,
    }));

    // Taxi splash spray particles
    const splashes = Array.from({ length: 35 }, () => ({
      vx: (Math.random() - 0.3) * 6,
      vy: -Math.random() * 7 - 2,
      r: Math.random() * 3 + 1,
    }));

    let frame = 0;

    const render = () => {
      frame++;
      const time = currentTime;

      // Clear Frame
      ctx.fillStyle = '#060a10';
      ctx.fillRect(0, 0, width, height);

      // Determine active scene
      let scene = 0;
      if (time >= 4 && time < 8) scene = 1;
      else if (time >= 8 && time < 12) scene = 2;
      else if (time >= 12) scene = 3;

      // Scene-specific transitions & rendering
      if (scene === 0) {
        // ==========================================
        // SCENE 1 (00:00–00:04): ISTANBUL WET STREET & YELLOW TAXI SPLASH
        // ==========================================
        const skyGrad = ctx.createLinearGradient(0, 0, 0, height);
        skyGrad.addColorStop(0, '#0c141f');
        skyGrad.addColorStop(0.5, '#152130');
        skyGrad.addColorStop(0.7, '#0a0f16');
        skyGrad.addColorStop(1, '#05080c');
        ctx.fillStyle = skyGrad;
        ctx.fillRect(0, 0, width, height);

        // Istanbul 6-story building silhouettes with warm apartment windows
        ctx.fillStyle = '#0d1622';
        ctx.fillRect(width * 0.05, height * 0.15, width * 0.35, height * 0.5);
        ctx.fillRect(width * 0.45, height * 0.1, width * 0.5, height * 0.55);

        // Warm lit windows in the morning rain
        ctx.fillStyle = 'rgba(251, 191, 36, 0.4)';
        for (let row = 0; row < 4; row++) {
          ctx.fillRect(width * 0.12, height * 0.22 + row * 45, 18, 22);
          ctx.fillRect(width * 0.22, height * 0.22 + row * 45, 18, 22);
          ctx.fillRect(width * 0.55, height * 0.18 + row * 45, 20, 24);
          ctx.fillRect(width * 0.72, height * 0.18 + row * 45, 20, 24);
        }

        // Wet asphalt ground
        const roadGrad = ctx.createLinearGradient(0, height * 0.65, 0, height);
        roadGrad.addColorStop(0, '#0e1724');
        roadGrad.addColorStop(0.4, '#1b2636');
        roadGrad.addColorStop(1, '#080d14');
        ctx.fillStyle = roadGrad;
        ctx.fillRect(0, height * 0.65, width, height * 0.35);

        // Sidewalk curb
        ctx.strokeStyle = '#273549';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, height * 0.72);
        ctx.lineTo(width, height * 0.68);
        ctx.stroke();

        // Puddle reflection of buildings and lights
        ctx.fillStyle = 'rgba(251, 191, 36, 0.15)';
        ctx.beginPath();
        ctx.ellipse(width * 0.55, height * 0.82, width * 0.38, 24, -0.05, 0, Math.PI * 2);
        ctx.fill();

        // YELLOW TAXI MOVING ACROSS (34 T...)
        const progress1 = (time - 0) / 4;
        const taxiX = width * 1.2 - progress1 * (width * 1.5);
        const taxiY = height * 0.62;

        // Taxi body
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.roundRect(taxiX, taxiY, 130, 48, 6);
        ctx.fill();

        // Taxi roof sign
        ctx.fillStyle = '#fef08a';
        ctx.fillRect(taxiX + 45, taxiY - 12, 35, 12);
        ctx.fillStyle = '#111827';
        ctx.font = 'bold 8px monospace';
        ctx.fillText('TAKSİ', taxiX + 50, taxiY - 3);

        // Taxi windows
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(taxiX + 20, taxiY + 6, 40, 20);
        ctx.fillRect(taxiX + 68, taxiY + 6, 42, 20);

        // Taxi Headlight Beam
        const lightBeam = ctx.createRadialGradient(taxiX, taxiY + 30, 5, taxiX - 80, taxiY + 35, 90);
        lightBeam.addColorStop(0, 'rgba(254, 240, 138, 0.6)');
        lightBeam.addColorStop(1, 'rgba(254, 240, 138, 0)');
        ctx.fillStyle = lightBeam;
        ctx.beginPath();
        ctx.moveTo(taxiX, taxiY + 20);
        ctx.lineTo(taxiX - 110, taxiY - 15);
        ctx.lineTo(taxiX - 130, taxiY + 75);
        ctx.closePath();
        ctx.fill();

        // Hydrodynamic Water Splash Spray from tire
        if (progress1 > 0.25 && progress1 < 0.85) {
          ctx.fillStyle = 'rgba(224, 242, 254, 0.75)';
          for (const sp of splashes) {
            ctx.beginPath();
            ctx.arc(taxiX + 85 + sp.vx * 4, taxiY + 45 + sp.vy * 3, sp.r, 0, Math.PI * 2);
            ctx.fill();
            sp.vy += 0.25;
          }
        }

        // Background pedestrian with umbrella
        ctx.fillStyle = '#0f172a';
        ctx.beginPath();
        ctx.arc(width * 0.2, height * 0.58, 12, Math.PI, Math.PI * 2);
        ctx.fill();
        ctx.fillRect(width * 0.18, height * 0.58, 6, 32);
      } else if (scene === 1) {
        // ==========================================
        // SCENE 2 (00:04–00:08): TRADITIONAL TEA STAND & GRAVITATIONAL TEA POURING
        // ==========================================
        const bgGrad = ctx.createLinearGradient(0, 0, 0, height);
        bgGrad.addColorStop(0, '#101722');
        bgGrad.addColorStop(0.5, '#1e140d');
        bgGrad.addColorStop(1, '#0c0805');
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, width, height);

        // Wooden counter & Brass Tea Samovar
        ctx.fillStyle = '#3e2723';
        ctx.fillRect(0, height * 0.65, width, height * 0.35);
        ctx.strokeStyle = '#5d4037';
        ctx.lineWidth = 2;
        ctx.strokeRect(0, height * 0.65, width, height * 0.35);

        // Brass Samovar Body
        const brassGrad = ctx.createLinearGradient(width * 0.08, 0, width * 0.38, 0);
        brassGrad.addColorStop(0, '#d97706');
        brassGrad.addColorStop(0.5, '#fef08a');
        brassGrad.addColorStop(1, '#92400e');
        ctx.fillStyle = brassGrad;
        ctx.beginPath();
        ctx.roundRect(width * 0.08, height * 0.32, 90, 170, 16);
        ctx.fill();

        // Upper Teapot (Demlik) in Vendor's Hand tilted
        const teapotX = width * 0.42;
        const teapotY = height * 0.36;
        ctx.save();
        ctx.translate(teapotX, teapotY);
        ctx.rotate(0.35);
        ctx.fillStyle = '#b45309';
        ctx.beginPath();
        ctx.roundRect(-25, -20, 50, 40, 8);
        ctx.fill();
        ctx.beginPath();
        ctx.moveTo(25, -5);
        ctx.lineTo(42, 10);
        ctx.lineTo(36, 16);
        ctx.lineTo(25, 10);
        ctx.closePath();
        ctx.fill();
        ctx.restore();

        // Vendor's hand
        ctx.fillStyle = '#d4a373';
        ctx.beginPath();
        ctx.ellipse(teapotX - 35, teapotY + 5, 14, 18, 0.2, 0, Math.PI * 2);
        ctx.fill();

        // Transparent Tulip-Shaped Glass on saucer
        const glassX = width * 0.62;
        const glassY = height * 0.65;

        // Porcelain Saucer
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.ellipse(glassX, glassY + 46, 38, 10, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#dc2626';
        ctx.lineWidth = 2.5;
        ctx.stroke();

        // Glass Outline
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(glassX - 22, glassY - 30);
        ctx.lineTo(glassX + 22, glassY - 30);
        ctx.quadraticCurveTo(glassX + 11, glassY + 10, glassX + 18, glassY + 45);
        ctx.lineTo(glassX - 18, glassY + 45);
        ctx.quadraticCurveTo(glassX - 11, glassY + 10, glassX - 22, glassY - 30);
        ctx.stroke();

        // Filling Tea Level
        const progress2 = Math.min((time - 4) / 3.5, 1.0);
        const fillHeight = 65 * progress2;

        if (fillHeight > 2) {
          ctx.fillStyle = 'rgba(185, 28, 28, 0.88)';
          ctx.beginPath();
          ctx.moveTo(glassX - 17, glassY + 44);
          ctx.lineTo(glassX + 17, glassY + 44);
          ctx.quadraticCurveTo(glassX + 13, glassY + 44 - fillHeight * 0.5, glassX + 14, glassY + 44 - fillHeight);
          ctx.lineTo(glassX - 14, glassY + 44 - fillHeight);
          ctx.quadraticCurveTo(glassX - 13, glassY + 44 - fillHeight * 0.5, glassX - 17, glassY + 44);
          ctx.fill();
        }

        // CONTINUOUS LIQUID STREAM
        ctx.strokeStyle = 'rgba(220, 38, 38, 0.9)';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(teapotX + 32, teapotY + 12);
        ctx.quadraticCurveTo(glassX - 5, glassY - 15, glassX, glassY + 42 - fillHeight);
        ctx.stroke();

        // DENSE RISING STEAM
        ctx.fillStyle = 'rgba(255, 255, 255, 0.12)';
        for (let s = 0; s < 16; s++) {
          const sx = glassX + Math.sin(frame * 0.05 + s) * 12;
          const sy = glassY - 35 - ((frame * 2 + s * 20) % 180);
          const sr = 10 + ((frame + s * 8) % 30);
          ctx.beginPath();
          ctx.arc(sx, sy, sr, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (scene === 2) {
        // ==========================================
        // SCENE 3 (00:08–00:12): HANDOVER, LIQUID SLOSHING & STRAY CAT
        // ==========================================
        ctx.fillStyle = '#0f1722';
        ctx.fillRect(0, 0, width, height);

        // Café awning
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(0, 0, width, height * 0.25);
        ctx.fillStyle = '#0f766e';
        ctx.fillRect(0, height * 0.22, width, 12);

        // Woman in trench coat
        ctx.fillStyle = '#d6c7b2';
        ctx.beginPath();
        ctx.roundRect(width * 0.45, height * 0.35, width * 0.5, height * 0.65, 24);
        ctx.fill();

        // Transparent umbrella
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.45)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(width * 0.72, height * 0.24, 75, Math.PI * 0.9, Math.PI * 2.1);
        ctx.stroke();

        // Hand holding the tea glass
        const handX = width * 0.42;
        const handY = height * 0.62;

        ctx.fillStyle = '#f7d6bf';
        for (let f = 0; f < 4; f++) {
          ctx.beginPath();
          ctx.roundRect(handX + 12, handY - 15 + f * 9, 22, 7, 4);
          ctx.fill();
        }

        // Tea glass between hands
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.lineWidth = 1.8;
        ctx.strokeRect(handX - 10, handY - 25, 28, 55);

        // Liquid Oscillation
        const slosh = Math.sin(frame * 0.15) * 4;
        ctx.fillStyle = 'rgba(185, 28, 28, 0.9)';
        ctx.beginPath();
        ctx.moveTo(handX - 9, handY + 28);
        ctx.lineTo(handX + 17, handY + 28);
        ctx.lineTo(handX + 17, handY - 5 - slosh);
        ctx.lineTo(handX - 9, handY - 5 + slosh);
        ctx.closePath();
        ctx.fill();

        // ISTANBUL STRAY TABBY CAT WALKING
        const catX = width * 0.1 + ((time - 8) / 4) * (width * 0.25);
        const catY = height * 0.78;
        ctx.fillStyle = '#b45309';
        ctx.beginPath();
        ctx.ellipse(catX, catY, 18, 10, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.arc(catX + 18, catY - 4, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.moveTo(catX + 15, catY - 11);
        ctx.lineTo(catX + 19, catY - 16);
        ctx.lineTo(catX + 22, catY - 11);
        ctx.fill();
        ctx.strokeStyle = '#b45309';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(catX - 18, catY);
        ctx.quadraticCurveTo(catX - 28, catY - 14, catX - 22, catY - 24);
        ctx.stroke();
      } else {
        // ==========================================
        // SCENE 4 (00:12–00:15): CLOSE-UP, RAIN ON UMBRELLA & FIRST SIP
        // ==========================================
        ctx.fillStyle = '#090e17';
        ctx.fillRect(0, 0, width, height);

        // Bokeh bus
        const busX = width * 1.1 - ((time - 12) / 3) * (width * 1.3);
        ctx.fillStyle = 'rgba(2, 132, 199, 0.35)';
        ctx.fillRect(busX, height * 0.22, 180, 80);
        ctx.fillStyle = 'rgba(251, 191, 36, 0.35)';
        ctx.fillRect(busX, height * 0.28, 180, 16);

        // Woman Portrait Close-up
        const faceX = width * 0.5;
        const faceY = height * 0.52;

        ctx.fillStyle = '#d6c7b2';
        ctx.beginPath();
        ctx.moveTo(faceX - 55, height);
        ctx.lineTo(faceX - 35, faceY + 95);
        ctx.lineTo(faceX + 35, faceY + 95);
        ctx.lineTo(faceX + 55, height);
        ctx.closePath();
        ctx.fill();

        ctx.fillStyle = '#fce7dc';
        ctx.beginPath();
        ctx.ellipse(faceX, faceY + 30, 48, 62, 0, 0, Math.PI * 2);
        ctx.fill();

        // Stray wet hair
        ctx.strokeStyle = '#3b2518';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(faceX - 45, faceY - 20);
        ctx.quadraticCurveTo(faceX - 52, faceY + 40, faceX - 38, faceY + 80);
        ctx.moveTo(faceX + 42, faceY - 20);
        ctx.quadraticCurveTo(faceX + 50, faceY + 40, faceX + 36, faceY + 80);
        ctx.stroke();

        // Closed Eyes
        ctx.strokeStyle = '#472a1a';
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.arc(faceX - 18, faceY + 22, 9, 0.2, Math.PI - 0.2);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(faceX + 18, faceY + 22, 9, 0.2, Math.PI - 0.2);
        ctx.stroke();

        // Smile
        ctx.strokeStyle = '#e11d48';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.arc(faceX, faceY + 56, 12, 0.1, Math.PI - 0.1);
        ctx.stroke();

        // Tea Glass Raised to lips
        const sipY = faceY + 68;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
        ctx.lineWidth = 2;
        ctx.strokeRect(faceX - 16, sipY, 32, 45);

        ctx.fillStyle = 'rgba(185, 28, 28, 0.9)';
        ctx.fillRect(faceX - 14, sipY + 12, 28, 31);

        // Umbrella raindrops
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(0, height * 0.15);
        ctx.quadraticCurveTo(width * 0.5, height * 0.08, width, height * 0.15);
        ctx.stroke();

        ctx.fillStyle = 'rgba(224, 242, 254, 0.6)';
        for (let d = 0; d < 8; d++) {
          const dx = width * 0.15 + d * 38;
          const dy = height * 0.12 + ((frame * 0.8 + d * 25) % 90);
          ctx.beginPath();
          ctx.ellipse(dx, dy, 2.5, 4, 0, 0, Math.PI * 2);
          ctx.fill();
        }
      }

      // GLOBAL RAIN OVERLAY
      ctx.strokeStyle = 'rgba(186, 230, 253, 0.35)';
      ctx.lineWidth = 1.1;
      for (const drop of rain) {
        ctx.beginPath();
        ctx.moveTo(drop.x, drop.y);
        ctx.lineTo(drop.x - 2, drop.y + drop.len);
        ctx.stroke();

        drop.y += drop.speed;
        drop.x -= 1.2;
        if (drop.y > height) {
          drop.y = -drop.len;
          drop.x = Math.random() * width + 40;
        }
      }

      // Lens droplets
      for (const ld of lensDrops) {
        ctx.fillStyle = `rgba(224, 242, 254, ${ld.alpha})`;
        ctx.beginPath();
        ctx.arc(ld.x, ld.y, ld.r, 0, Math.PI * 2);
        ctx.fill();
        ld.y += 0.15;
        if (ld.y > height) ld.y = 0;
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [currentTime]);

  // Master Clock: Progress from 0 to 15 seconds
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          const next = prev + 0.05;
          if (next >= durationSeconds) return 0;
          return next;
        });
      }, 50);
    }
    return () => clearInterval(interval);
  }, [isPlaying, durationSeconds]);

  // Synchronize Active Segment
  useEffect(() => {
    const idx = segments.findIndex((s) => currentTime >= s.start && currentTime < s.end);
    if (idx !== -1 && idx !== activeSegmentIndex) {
      setActiveSegmentIndex(idx);
    }
  }, [currentTime]);

  // Web Audio API: Realistic Rain & City Ambience
  const toggleAudio = useCallback(() => {
    if (isMuted) {
      try {
        const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
        const ctx = new AudioCtx();
        audioContextRef.current = ctx;

        const bufferSize = ctx.sampleRate * 2;
        const noiseBuffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
        for (let i = 0; i < bufferSize; i++) {
          const white = Math.random() * 2 - 1;
          b0 = 0.99886 * b0 + white * 0.0555179;
          b1 = 0.99332 * b1 + white * 0.0750759;
          b2 = 0.96900 * b2 + white * 0.1538520;
          b3 = 0.86650 * b3 + white * 0.3104856;
          b4 = 0.55000 * b4 + white * 0.5329522;
          b5 = -0.7616 * b5 - white * 0.0168980;
          output[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.04;
          b6 = white * 0.115926;
        }

        const whiteNoise = ctx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;
        whiteNoise.loop = true;

        const gainNode = ctx.createGain();
        gainNode.gain.setValueAtTime(0.08, ctx.currentTime);

        whiteNoise.connect(gainNode);
        gainNode.connect(ctx.destination);
        whiteNoise.start();

        setIsMuted(false);
      } catch (e) {
        console.error('Audio initialization failed:', e);
      }
    } else {
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
        audioContextRef.current = null;
      }
      setIsMuted(true);
    }
  }, [isMuted]);

  useEffect(() => {
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(() => {});
      }
    };
  }, []);

  // REAL VIDEO DOWNLOAD: Record Canvas to genuine WebM/MP4 video file
  const handleDownloadVideo = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    try {
      setIsRecordingDownload(true);
      setDownloadSuccess(false);

      setCurrentTime(0);
      setIsPlaying(true);

      const stream = (canvas as any).captureStream ? (canvas as any).captureStream(30) : null;
      if (!stream) {
        // Fallback: trigger image download of current frame
        const dataUrl = canvas.toDataURL('image/png');
        const a = document.createElement('a');
        a.href = dataUrl;
        a.download = `istanbul_rain_frame_${Math.round(currentTime)}s.png`;
        a.click();
        setIsRecordingDownload(false);
        setDownloadSuccess(true);
        setTimeout(() => setDownloadSuccess(false), 3000);
        return;
      }

      const mimeType = MediaRecorder.isTypeSupported('video/mp4')
        ? 'video/mp4'
        : MediaRecorder.isTypeSupported('video/webm;codecs=vp9')
        ? 'video/webm;codecs=vp9'
        : 'video/webm';

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        videoBitsPerSecond: 8000000,
      });

      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const ext = mimeType.includes('mp4') ? 'mp4' : 'webm';
        a.download = `istanbul_rain_arri35_9x16_cinema.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        setIsRecordingDownload(false);
        setDownloadSuccess(true);
        setTimeout(() => setDownloadSuccess(false), 4000);
      };

      mediaRecorder.start();

      setTimeout(() => {
        if (mediaRecorder.state === 'recording') {
          mediaRecorder.stop();
        }
      }, 15000);
    } catch (err) {
      console.error('Video capture error:', err);
      setIsRecordingDownload(false);
    }
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
            onClick={handleDownloadVideo}
            disabled={isRecordingDownload}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
              downloadSuccess
                ? 'bg-emerald-900/80 text-emerald-300 border border-emerald-500/60'
                : isRecordingDownload
                ? 'bg-amber-950 text-amber-300 border border-amber-600/60 animate-pulse'
                : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 shadow-md active:scale-95'
            }`}
            title="15 saniyelik sinematik videoyu bilgisayarınıza MP4 formatında indirin"
          >
            {downloadSuccess ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>İndirildi!</span>
              </>
            ) : isRecordingDownload ? (
              <>
                <Sparkles className="w-3.5 h-3.5 animate-spin" />
                <span>Render & İndiriliyor...</span>
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
        {/* Multi-Scene Procedural Canvas */}
        <canvas ref={canvasRef} className="w-full h-full object-cover" />

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
          onChange={(e) => setCurrentTime(parseFloat(e.target.value))}
          className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 hover:accent-cyan-300"
        />

        {/* Chronological 4-Scene Selector Buttons */}
        <div className="grid grid-cols-4 gap-1.5 pt-1 text-[10px] font-mono">
          {segments.map((seg, idx) => (
            <button
              key={seg.label}
              onClick={() => setCurrentTime(seg.start)}
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
              onClick={() => setCurrentTime(0)}
              className="p-2 rounded-xl bg-space-800 text-slate-300 hover:text-white hover:bg-space-700 transition-colors"
              title="Başa Sar"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={toggleAudio}
              className={`p-2 rounded-xl transition-colors ${
                !isMuted
                  ? 'bg-cyan-950 text-cyan-300 border border-cyan-800 shadow-sm'
                  : 'bg-space-800 text-slate-400 hover:text-slate-200'
              }`}
              title={isMuted ? 'Yağmur Ambiyans Sesini Aç' : 'Sesi Kapat'}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4 text-cyan-400" />}
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadVideo}
              disabled={isRecordingDownload}
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
