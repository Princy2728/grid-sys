import React from 'react';
import { ShieldCheck, CloudSun, RefreshCw } from 'lucide-react';

export default function Header({ title, subtitle, weather, temperature, onRefresh, isRefreshing }) {
  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between shrink-0 sticky top-0 z-10 shadow-sm">
      <div>
        <h2 className="text-lg font-bold text-slate-900 leading-tight">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Weather / Ambient Pill */}
        <div className="flex items-center gap-2 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700">
          <CloudSun className="w-4 h-4 text-amber-500" />
          <span>{weather || 'Clear'}</span>
          <span className="font-semibold text-slate-900">
            {temperature !== undefined ? `${temperature}°C` : '24.5°C'}
          </span>
        </div>

        {/* Refresh Action */}
        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-600 bg-white border border-slate-300 hover:bg-slate-50 active:scale-95 transition-all disabled:opacity-50"
            title="Refresh Live Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-600' : ''}`} />
            <span>Sync</span>
          </button>
        )}

        {/* Campus Tag */}
        <div className="hidden md:flex items-center gap-1.5 text-xs text-slate-600 font-medium bg-blue-50 border border-blue-200 px-3 py-1.5 rounded-lg">
          <ShieldCheck className="w-4 h-4 text-blue-600" />
          <span>Metro Smart Campus</span>
        </div>
      </div>
    </header>
  );
}
