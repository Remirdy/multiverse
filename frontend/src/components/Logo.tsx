import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 32 }) => {
  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 48 48"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="transition-transform duration-500 hover:rotate-45"
      >
        <defs>
          <linearGradient id="orbit-grad-1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="50%" stopColor="#818CF8" />
            <stop offset="100%" stopColor="#C084FC" />
          </linearGradient>
          <linearGradient id="orbit-grad-2" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#38BDF8" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#A855F7" stopOpacity="0.2" />
          </linearGradient>
          <radialGradient id="core-glow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="60%" stopColor="#6366F1" />
            <stop offset="100%" stopColor="#0B0F17" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Outer Orbit ellipse */}
        <ellipse
          cx="24"
          cy="24"
          rx="21"
          ry="9"
          stroke="url(#orbit-grad-1)"
          strokeWidth="1.75"
          transform="rotate(-25 24 24)"
          strokeDasharray="4 2"
          className="opacity-70"
        />

        {/* Counter Orbit ellipse */}
        <ellipse
          cx="24"
          cy="24"
          rx="21"
          ry="9"
          stroke="url(#orbit-grad-2)"
          strokeWidth="1.75"
          transform="rotate(45 24 24)"
          className="opacity-80"
        />

        {/* Vertical ring */}
        <circle
          cx="24"
          cy="24"
          r="13"
          stroke="#475569"
          strokeWidth="1"
          strokeDasharray="2 3"
          className="opacity-40"
        />

        {/* Orbiting nodes (representing multiple minds) */}
        <circle cx="8" cy="18" r="2.5" fill="#38BDF8" className="animate-pulse" />
        <circle cx="39" cy="31" r="2.2" fill="#818CF8" />
        <circle cx="35" cy="12" r="2" fill="#C084FC" />
        <circle cx="15" cy="38" r="1.8" fill="#38BDF8" />

        {/* Luminous Core / Singularity */}
        <circle cx="24" cy="24" r="7" fill="url(#core-glow)" />
        <circle cx="24" cy="24" r="3.5" fill="#F8FAFC" />
      </svg>
    </div>
  );
};
