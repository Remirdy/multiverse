import React from 'react';
import { Compass, CheckCircle2, ArrowRight } from 'lucide-react';
import { RouteResponse } from '../types';
import { useLanguage } from '../i18n/LanguageContext';

interface RoutingBadgeProps {
  routeInfo: RouteResponse | null;
  onApplyRecommendation: (modelIds: string[]) => void;
  isAutoRouteEnabled: boolean;
  onToggleAutoRoute: () => void;
}

export const RoutingBadge: React.FC<RoutingBadgeProps> = ({
  routeInfo,
  onApplyRecommendation,
  isAutoRouteEnabled,
  onToggleAutoRoute,
}) => {
  const { t } = useLanguage();

  return (
    <div className="flex items-center justify-between gap-3 px-3.5 py-2 rounded-xl bg-space-900/90 border border-slate-800 text-xs shadow-sm">
      <div className="flex items-center gap-2.5 min-w-0">
        <button
          onClick={onToggleAutoRoute}
          className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg font-medium transition-all ${
            isAutoRouteEnabled
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50'
              : 'bg-space-800 text-slate-400 hover:text-slate-200 border border-slate-700/60'
          }`}
          title={isAutoRouteEnabled ? t.autoRouteOn : t.autoRouteOff}
        >
          <Compass className={`w-3.5 h-3.5 ${isAutoRouteEnabled ? 'animate-spin-slow' : ''}`} />
          <span>{isAutoRouteEnabled ? t.autoRouteOn : t.autoRouteOff}</span>
        </button>

        {routeInfo && (
          <div className="flex items-center gap-2 truncate">
            <span className="text-slate-500">|</span>
            <span className="text-slate-400 truncate">
              {t.smartRouteTitle}:{' '}
              <strong className="text-cyan-300 font-medium">
                {routeInfo.category_label}
              </strong>{' '}
              <span className="text-slate-500 font-mono text-[11px]">
                ({Math.round(routeInfo.confidence * 100)}%)
              </span>
            </span>
          </div>
        )}
      </div>

      {routeInfo && !isAutoRouteEnabled && (
        <button
          onClick={() => onApplyRecommendation(routeInfo.recommended_model_ids)}
          className="inline-flex items-center gap-1 text-[11px] font-medium text-cyan-400 hover:text-cyan-300 hover:underline shrink-0"
        >
          <span>{t.applyRecommended}</span>
          <ArrowRight className="w-3 h-3" />
        </button>
      )}

      {isAutoRouteEnabled && routeInfo && (
        <span className="hidden sm:inline-flex items-center gap-1 text-[11px] text-emerald-400/90 shrink-0">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Auto-targeted</span>
        </span>
      )}
    </div>
  );
};
