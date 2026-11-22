import React, { useEffect, useState } from 'react';
import { 
  Zap, 
  Sun, 
  Building2, 
  Car, 
  BatteryCharging, 
  TrendingUp, 
  ShieldAlert, 
  CheckCircle2, 
  ArrowUpRight 
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import KpiCard from '../components/KpiCard';
import Badge from '../components/Badge';
import { api } from '../services/api';

export default function OverviewPage({ onNavigate }) {
  const [overview, setOverview] = useState(null);
  const [history, setHistory] = useState([]);
  const [forecast, setForecast] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [ov, hist, fc, al] = await Promise.all([
        api.getEnergyOverview(),
        api.getEnergyHistory(24),
        api.getDemandForecast(),
        api.getAlerts(false)
      ]);
      setOverview(ov);
      setHistory(hist);
      setForecast(fc);
      setAlerts(al.slice(0, 4));
    } catch (err) {
      console.error('Failed to load overview data', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading && !overview) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-slate-500">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading campus energy telemetry...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner if Active Critical Alerts */}
      {alerts.some(a => a.severity === 'critical') && (
        <div className="bg-rose-50 border border-rose-200 rounded-xl p-4 flex items-center justify-between text-rose-800 shadow-sm">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0" />
            <div>
              <p className="text-sm font-semibold">Active Critical Alert Detected</p>
              <p className="text-xs text-rose-700">Substation or charging hardware requires immediate inspection.</p>
            </div>
          </div>
          <button 
            onClick={() => onNavigate('alerts')}
            className="text-xs font-semibold px-3 py-1.5 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors"
          >
            Review Incidents
          </button>
        </div>
      )}

      {/* Primary KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiCard
          title="Total Campus Demand"
          value={overview?.total_consumption_kw ?? 0}
          unit="kW"
          subtitle={`Peak Today: ${overview?.peak_today_kw ?? 0} kW`}
          icon={Zap}
          color="blue"
          trend="Live Load"
        />
        <KpiCard
          title="Solar PV Generation"
          value={overview?.solar_generation_kw ?? 0}
          unit="kW"
          subtitle={`${overview?.solar_share_pct ?? 0}% Clean Energy Share`}
          icon={Sun}
          color="green"
          trend="Renewable"
        />
        <KpiCard
          title="Grid Substation Import"
          value={overview?.grid_import_kw ?? 0}
          unit="kW"
          subtitle={`${overview?.grid_utilization_pct ?? 0}% of ${overview?.grid_capacity_kw ?? 1200} kW`}
          icon={BatteryCharging}
          color={overview?.grid_utilization_pct > 80 ? 'amber' : 'slate'}
          trend={overview?.grid_utilization_pct > 80 ? 'High' : 'Normal'}
        />
        <KpiCard
          title="EV Fleet Charging"
          value={overview?.ev_charging_kw ?? 0}
          unit="kW"
          subtitle="Real-time EV load"
          icon={Car}
          color="amber"
          trend="Active"
        />
      </div>

      {/* Main Energy Telemetry Chart */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="font-bold text-slate-900 text-base">24-Hour Campus Energy Dynamics</h3>
            <p className="text-xs text-slate-500">Historical profile of campus demand, solar generation, and grid dependency</p>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-blue-600"></span>
              <span className="text-slate-600">Total Demand</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="text-slate-600">Solar Gen</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-slate-400"></span>
              <span className="text-slate-600">Grid Import</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full bg-amber-500"></span>
              <span className="text-slate-600">EV Load</span>
            </div>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="totalColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25}/>
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="solarColor" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
              <XAxis dataKey="time_label" tick={{ fontSize: 11, fill: '#64748b' }} stroke="#cbd5e1" />
              <YAxis tick={{ fontSize: 11, fill: '#64748b' }} stroke="#cbd5e1" unit=" kW" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
              />
              <Area type="monotone" dataKey="total_consumption_kw" stroke="#2563eb" strokeWidth={2} fillOpacity={1} fill="url(#totalColor)" name="Total Demand" />
              <Area type="monotone" dataKey="solar_generation_kw" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#solarColor)" name="Solar Gen" />
              <Area type="monotone" dataKey="grid_import_kw" stroke="#64748b" strokeWidth={1.5} fillOpacity={0} name="Grid Import" strokeDasharray="3 3" />
              <Area type="monotone" dataKey="ev_charging_kw" stroke="#f59e0b" strokeWidth={1.5} fillOpacity={0} name="EV Load" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two Column Grid: Capacity Breakdown & Forecast Glance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Available Capacity & Energy Flow */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-slate-900 text-sm">Instantaneous Headroom</h4>
            <Badge variant="green">{overview?.headroom_kw ?? 0} kW Buffer</Badge>
          </div>

          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span>Substation Grid Utilization</span>
                <span>{overview?.grid_utilization_pct}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className={`h-2.5 rounded-full transition-all duration-500 ${
                    overview?.grid_utilization_pct > 85 ? 'bg-rose-500' :
                    overview?.grid_utilization_pct > 70 ? 'bg-amber-500' : 'bg-blue-600'
                  }`}
                  style={{ width: `${Math.min(100, overview?.grid_utilization_pct ?? 0)}%` }}
                ></div>
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-medium text-slate-600 mb-1">
                <span>Clean Solar Contribution</span>
                <span>{overview?.solar_share_pct}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div 
                  className="bg-emerald-500 h-2.5 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, overview?.solar_share_pct ?? 0)}%` }}
                ></div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs">
            <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Critical Labs/Health</span>
              <span className="text-slate-800 font-bold text-sm">{overview?.critical_building_load_kw ?? 0} kW</span>
            </div>
            <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Non-Critical / Academic</span>
              <span className="text-slate-800 font-bold text-sm">{overview?.non_critical_building_load_kw ?? 0} kW</span>
            </div>
          </div>

          <button
            onClick={() => onNavigate('allocation')}
            className="w-full py-2 px-3 text-xs font-semibold text-blue-600 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>Open Smart Allocation Engine</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* 24h AI Forecast Glance */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-slate-900 text-sm">AI Demand Horizon</h4>
            <Badge variant="blue">Ridge ML</Badge>
          </div>
          <p className="text-xs text-slate-500">Autonomous predictions for next 24 hours.</p>

          <div className="p-3 bg-blue-50/60 rounded-lg border border-blue-100 text-xs space-y-1">
            <div className="flex items-center justify-between text-blue-900 font-semibold">
              <span>Expected Peak Period</span>
              <span>{forecast?.peak_period?.hour ? `${forecast.peak_period.hour}:00 UTC` : '14:00 UTC'}</span>
            </div>
            <p className="text-slate-600 text-[11px]">
              Predicted load: <strong className="text-blue-700">{forecast?.peak_period?.predicted_demand_kw ?? 940} kW</strong>
            </p>
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Next 4 Hours</span>
            <div className="grid grid-cols-4 gap-2">
              {forecast?.forecast_series?.slice(0, 4).map((f, i) => (
                <div key={i} className="p-2 text-center rounded-lg bg-slate-50 border border-slate-200 text-xs">
                  <span className="text-slate-400 block text-[10px]">{f.hour}:00</span>
                  <span className="font-bold text-slate-800">{Math.round(f.predicted_demand_kw)}</span>
                  <span className="text-[9px] text-slate-400 block">kW</span>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => onNavigate('intelligence')}
            className="w-full py-2 px-3 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-200 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>Explore Forecasting & Solar</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Recent Alerts & Incident Status */}
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-slate-900 text-sm">Active System Alerts</h4>
            <Badge variant={alerts.length > 0 ? 'amber' : 'green'}>
              {alerts.length} Pending
            </Badge>
          </div>

          {alerts.length === 0 ? (
            <div className="p-8 text-center text-slate-400 text-xs">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2 opacity-80" />
              All systems operating within safe thermal & electrical margins.
            </div>
          ) : (
            <div className="space-y-2.5">
              {alerts.map((alt) => (
                <div key={alt.id} className="p-2.5 rounded-lg border border-slate-100 bg-slate-50 flex items-start gap-2.5">
                  <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                    alt.severity === 'critical' ? 'bg-rose-500' :
                    alt.severity === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                  }`}></div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold text-slate-800 truncate">{alt.title}</p>
                    <p className="text-[11px] text-slate-500 line-clamp-1">{alt.description}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          <button
            onClick={() => onNavigate('alerts')}
            className="w-full py-2 px-3 text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg border border-slate-200 transition-colors flex items-center justify-center gap-1.5"
          >
            <span>View All Alerts & Reports</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
