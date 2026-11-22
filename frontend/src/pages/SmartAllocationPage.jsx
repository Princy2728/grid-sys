import React, { useEffect, useState } from 'react';
import { 
  SlidersHorizontal, 
  ShieldCheck, 
  AlertTriangle, 
  BatteryCharging, 
  Sun, 
  Cpu, 
  RefreshCw,
  CheckCircle2,
  TrendingDown,
  Info
} from 'lucide-react';
import KpiCard from '../components/KpiCard';
import Badge from '../components/Badge';
import { api } from '../services/api';

export default function SmartAllocationPage() {
  const [allocation, setAllocation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);

  useEffect(() => {
    loadAllocation();
  }, []);

  const loadAllocation = async () => {
    try {
      setLoading(true);
      const data = await api.getCurrentAllocation();
      setAllocation(data);
    } catch (err) {
      console.error('Failed to load allocation', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    try {
      setCalculating(true);
      const data = await api.calculateAllocation({ scenario_name: 'Manual Live Re-dispatch' });
      setAllocation(data);
    } catch (err) {
      alert('Error recalculating allocation: ' + err.message);
    } finally {
      setCalculating(false);
    }
  };

  if (loading && !allocation) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 text-slate-500">
          <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <span>Computing deterministic priority allocation...</span>
        </div>
      </div>
    );
  }

  const details = allocation?.details || {};
  const totalDemand = details.total_demand_kw || 0;
  const totalAllocated = details.total_allocated_kw || 0;
  const totalAvailable = allocation?.total_supply_kw || 0;
  const isConstrained = allocation?.is_constrained || false;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">Deterministic Smart Resource Allocation Engine</h3>
          <p className="text-xs text-slate-500">
            Hierarchical priority scheduling guaranteeing non-exceedance of safe grid & solar available capacity.
          </p>
        </div>
        <button
          onClick={handleRecalculate}
          disabled={calculating}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg transition-colors shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${calculating ? 'animate-spin' : ''}`} />
          <span>Recalculate Live Allocation</span>
        </button>
      </div>

      {/* Allocation Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiCard
          title="Total Supply Capacity"
          value={allocation?.total_supply_kw ?? 0}
          unit="kW"
          subtitle={`Solar: ${allocation?.solar_allocated_kw ?? 0} kW | Grid: ${allocation?.grid_allocated_kw ?? 0} kW`}
          icon={Sun}
          color="green"
          trend="Available"
        />
        <KpiCard
          title="Allocated Power"
          value={totalAllocated}
          unit="kW"
          subtitle={`Demand: ${totalDemand} kW`}
          icon={BatteryCharging}
          color="blue"
          trend="Dispatched"
        />
        <KpiCard
          title="Grid Deficit Shortfall"
          value={allocation?.deficit_kw ?? 0}
          unit="kW"
          subtitle={allocation?.deficit_kw > 0 ? 'Capacity deficit active' : 'Zero Shortfall'}
          icon={AlertTriangle}
          color={allocation?.deficit_kw > 0 ? 'red' : 'slate'}
          trend={allocation?.deficit_kw > 0 ? 'Deficit' : 'Safe'}
        />
        <KpiCard
          title="Curtailment / Deferral"
          value={(allocation?.optional_curtailed_kw || 0) + (details?.shortfalls?.flexible_ev || 0)}
          unit="kW"
          subtitle="Flexible EV & Optional Shed"
          icon={TrendingDown}
          color={isConstrained ? 'amber' : 'slate'}
          trend={isConstrained ? 'Throttled' : 'Full Power'}
        />
      </div>

      {/* Supply vs Demand Comparison Gauge */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-bold text-slate-900 text-sm">Aggregate Capacity vs Campus Demand</h4>
          <Badge variant={isConstrained ? 'amber' : 'green'}>
            {isConstrained ? 'Constrained Dispatch' : '100% Demand Met'}
          </Badge>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs text-slate-600 font-medium">
            <span>Allocated: {totalAllocated} kW of {totalDemand} kW Demand</span>
            <span>Available Capacity: {totalAvailable} kW</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden flex">
            <div 
              className="bg-emerald-500 h-3" 
              style={{ width: `${Math.min(100, ((allocation?.solar_allocated_kw || 0) / totalAvailable) * 100)}%` }}
              title="Solar Share"
            ></div>
            <div 
              className="bg-blue-600 h-3" 
              style={{ width: `${Math.min(100, ((allocation?.grid_allocated_kw || 0) / totalAvailable) * 100)}%` }}
              title="Grid Share"
            ></div>
          </div>
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>Green: Solar Generation ({allocation?.solar_allocated_kw} kW)</span>
            <span>Blue: Substation Grid ({allocation?.grid_allocated_kw} kW)</span>
            <span>Remaining Headroom: {details?.headroom_kw ?? 0} kW</span>
          </div>
        </div>
      </div>

      {/* 5-Tier Hierarchical Allocation Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-200">
          <h4 className="font-bold text-slate-900 text-sm">Hierarchical Priority Allocation Matrix</h4>
          <p className="text-xs text-slate-500">Deterministic allocation across critical campus infrastructure, building baselines, and EV tiers.</p>
        </div>

        <div className="divide-y divide-slate-100">
          {/* Tier 1 */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/50">
            <div className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-md bg-blue-100 text-blue-700 font-bold text-xs flex items-center justify-center shrink-0">1</span>
              <div>
                <div className="flex items-center gap-2">
                  <h5 className="font-bold text-slate-900 text-sm">Tier 1: Critical Campus Loads</h5>
                  <Badge variant="blue">Highest Priority</Badge>
                </div>
                <p className="text-xs text-slate-500">Medical emergency clinic, BioTech cold research storage, IT core.</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-bold text-slate-900">{allocation?.critical_load_kw} kW</span>
              <span className="block text-[11px] text-emerald-600 font-medium">100% Guaranteed</span>
            </div>
          </div>

          {/* Tier 2 */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/50">
            <div className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-md bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0">2</span>
              <div>
                <div className="flex items-center gap-2">
                  <h5 className="font-bold text-slate-900 text-sm">Tier 2: Essential Building Services</h5>
                  <Badge variant="slate">Priority 2</Badge>
                </div>
                <p className="text-xs text-slate-500">Academic classroom baseline power, dormitory life support, university library.</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-bold text-slate-900">{allocation?.essential_building_kw} kW</span>
              <span className="block text-[11px] text-emerald-600 font-medium">100% Satisfied</span>
            </div>
          </div>

          {/* Tier 3 */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/50">
            <div className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-md bg-amber-100 text-amber-700 font-bold text-xs flex items-center justify-center shrink-0">3</span>
              <div>
                <div className="flex items-center gap-2">
                  <h5 className="font-bold text-slate-900 text-sm">Tier 3: Urgent EV Charging</h5>
                  <Badge variant="amber">Urgent Dispatch</Badge>
                </div>
                <p className="text-xs text-slate-500">Electric campus ambulances, security cruisers, and imminent departure EVs (&lt;2h).</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-bold text-slate-900">{allocation?.urgent_ev_kw} kW</span>
              <span className="block text-[11px] text-emerald-600 font-medium">Full Rate Charging</span>
            </div>
          </div>

          {/* Tier 4 */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/50">
            <div className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-md bg-purple-100 text-purple-700 font-bold text-xs flex items-center justify-center shrink-0">4</span>
              <div>
                <div className="flex items-center gap-2">
                  <h5 className="font-bold text-slate-900 text-sm">Tier 4: Flexible EV Charging</h5>
                  <Badge variant="purple">Schedulable</Badge>
                </div>
                <p className="text-xs text-slate-500">Commuter student & staff vehicles with extended dwell times (&gt;5h).</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-bold text-slate-900">{allocation?.flexible_ev_kw} kW</span>
              {details?.shortfalls?.flexible_ev > 0 ? (
                <span className="block text-[11px] text-amber-600 font-medium">Throttled by {details.shortfalls.flexible_ev} kW</span>
              ) : (
                <span className="block text-[11px] text-emerald-600 font-medium">Normal Rate</span>
              )}
            </div>
          </div>

          {/* Tier 5 */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-50/50">
            <div className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-md bg-rose-100 text-rose-700 font-bold text-xs flex items-center justify-center shrink-0">5</span>
              <div>
                <div className="flex items-center gap-2">
                  <h5 className="font-bold text-slate-900 text-sm">Tier 5: Optional Consumption</h5>
                  <Badge variant="red">Curtailable</Badge>
                </div>
                <p className="text-xs text-slate-500">Athletic sports arena HVAC, decorative exterior lighting, auxiliary fountains.</p>
              </div>
            </div>
            <div className="text-right">
              <span className="text-base font-bold text-slate-900">
                {allocation?.optional_curtailed_kw > 0 ? `0 kW (Curtailed)` : 'Active'}
              </span>
              {allocation?.optional_curtailed_kw > 0 ? (
                <span className="block text-[11px] text-rose-600 font-medium">Curtailed {allocation.optional_curtailed_kw} kW</span>
              ) : (
                <span className="block text-[11px] text-emerald-600 font-medium">Supplied</span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Natural Language Decision Rationale (Module H / Explainability) */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
        <div className="flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          <h4 className="font-bold text-slate-900 text-sm">Autonomous Dispatch Explanation</h4>
        </div>
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 leading-relaxed font-mono">
          {allocation?.explanation}
        </div>
      </div>
    </div>
  );
}
