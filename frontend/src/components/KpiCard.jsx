import React from 'react';

export default function KpiCard({ title, value, unit, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50 text-blue-600 border-blue-200',
      badge: 'text-blue-700 bg-blue-100',
      border: 'border-blue-100'
    },
    green: {
      bg: 'bg-emerald-50 text-emerald-600 border-emerald-200',
      badge: 'text-emerald-700 bg-emerald-100',
      border: 'border-emerald-100'
    },
    amber: {
      bg: 'bg-amber-50 text-amber-600 border-amber-200',
      badge: 'text-amber-700 bg-amber-100',
      border: 'border-amber-100'
    },
    red: {
      bg: 'bg-rose-50 text-rose-600 border-rose-200',
      badge: 'text-rose-700 bg-rose-100',
      border: 'border-rose-100'
    },
    slate: {
      bg: 'bg-slate-100 text-slate-700 border-slate-200',
      badge: 'text-slate-700 bg-slate-200',
      border: 'border-slate-200'
    }
  };

  const scheme = colorMap[color] || colorMap.blue;

  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden`}>
      <div className="flex items-start justify-between">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${scheme.bg} border`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-1.5">
        <span className="text-2xl font-bold tracking-tight text-slate-900">{value}</span>
        {unit && <span className="text-xs font-medium text-slate-500">{unit}</span>}
      </div>

      {(subtitle || trend) && (
        <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
          <span>{subtitle}</span>
          {trend && (
            <span className={`px-1.5 py-0.5 rounded font-medium ${scheme.badge}`}>
              {trend}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
