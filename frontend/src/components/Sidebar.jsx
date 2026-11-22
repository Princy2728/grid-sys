import React from 'react';
import { 
  LayoutDashboard, 
  Car, 
  Zap, 
  SlidersHorizontal, 
  FlaskConical, 
  AlertTriangle, 
  Settings,
  ShieldCheck,
  Sun
} from 'lucide-react';

const navItems = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'ev', label: 'EV Management', icon: Car },
  { id: 'intelligence', label: 'Energy Intelligence', icon: Zap },
  { id: 'allocation', label: 'Smart Allocation', icon: SlidersHorizontal },
  { id: 'simulation', label: 'Simulation Lab', icon: FlaskConical },
  { id: 'alerts', label: 'Alerts & Reports', icon: AlertTriangle },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ currentPage, onSelectPage, alertCount = 0 }) {
  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0 border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-16 px-6 flex items-center gap-3 border-b border-slate-800 bg-slate-950">
        <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
          <Zap className="w-5 h-5 text-white fill-white" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-wide flex items-center gap-1.5">
            GRIDWISE <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 font-semibold border border-blue-500/30">AI</span>
          </h1>
          <p className="text-[10px] text-slate-400 uppercase tracking-wider font-medium">Smart Grid Controller</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Core Operations
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectPage(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-semibold'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </div>
              {item.id === 'alerts' && alertCount > 0 && (
                <span className="px-1.5 py-0.5 text-xs font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {alertCount}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/60 m-3 rounded-xl border">
        <div className="flex items-center gap-2 mb-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-medium text-emerald-400">Grid Autonomous Mode</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Zero-deficit constrained optimizer active.
        </p>
      </div>
    </aside>
  );
}
