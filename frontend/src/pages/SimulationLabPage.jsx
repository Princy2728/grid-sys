import React, { useEffect, useState } from 'react';
import { 
  FlaskConical, 
  Thermometer, 
  Sun, 
  BatteryCharging, 
  Car, 
  TrendingUp, 
  AlertTriangle, 
  Play, 
  CheckCircle2, 
  Lightbulb,
  ArrowRight,
  RotateCcw
} from 'lucide-react';
import Badge from '../components/Badge';
import { api } from '../services/api';

export default function SimulationLabPage() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedPreset, setSelectedPreset] = useState('');
  const [simParams, setSimParams] = useState({
    temperature_c: 38.0,
    cooling_multiplier: 1.6,
    solar_multiplier: 0.85,
    grid_capacity_multiplier: 0.90,
    ev_demand_multiplier: 1.3
  });
  const [simResult, setSimResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const data = await api.getScenarios();
      setScenarios(data);
      if (data.length > 1) {
        // Default to Heatwave preset
        const heatwave = data.find(s => s.name.includes('Heatwave')) || data[1];
        selectPreset(heatwave);
      }
    } catch (err) {
      console.error('Failed to load scenarios', err);
    }
  };

  const selectPreset = (preset) => {
    setSelectedPreset(preset.name);
    setSimParams({
      temperature_c: preset.temperature_c,
      cooling_multiplier: preset.cooling_multiplier,
      solar_multiplier: preset.solar_multiplier,
      grid_capacity_multiplier: preset.grid_capacity_multiplier,
      ev_demand_multiplier: preset.ev_demand_multiplier
    });
  };

  const handleRunSimulation = async () => {
    try {
      setRunning(true);
      const res = await api.runSimulation({
        preset_name: selectedPreset || null,
        temperature_c: parseFloat(simParams.temperature_c),
        cooling_multiplier: parseFloat(simParams.cooling_multiplier),
        solar_multiplier: parseFloat(simParams.solar_multiplier),
        grid_capacity_multiplier: parseFloat(simParams.grid_capacity_multiplier),
        ev_demand_multiplier: parseFloat(simParams.ev_demand_multiplier)
      });
      setSimResult(res);
    } catch (err) {
      alert('Simulation execution failed: ' + err.message);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div>
        <h3 className="text-xl font-bold text-slate-900">Heatwave & Grid Stress Simulation Lab</h3>
        <p className="text-xs text-slate-500">
          Model extreme heatwave surges, solar particulate attenuation, substation trips, and fleet EV spikes.
        </p>
      </div>

      {/* Preset Buttons */}
      <div className="space-y-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Select Scenario Preset</span>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3">
          {scenarios.map((sc) => (
            <button
              key={sc.id}
              onClick={() => selectPreset(sc)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedPreset === sc.name
                  ? 'border-blue-600 bg-blue-50/70 text-blue-900 shadow-sm ring-1 ring-blue-600'
                  : 'border-slate-200 bg-white hover:border-slate-300 text-slate-700'
              }`}
            >
              <div className="font-bold text-xs truncate">{sc.name}</div>
              <div className="text-[10px] text-slate-500 mt-1 line-clamp-2">{sc.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Interactive Parameter Sliders & Run Trigger */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <h4 className="font-bold text-slate-900 text-sm">Interactive Stress Multipliers</h4>
          <span className="text-xs text-slate-400">Tune ambient weather and infrastructure conditions</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6 text-xs">
          {/* Temperature */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <Thermometer className="w-3.5 h-3.5 text-rose-500" /> Temp (°C)
              </span>
              <span className="font-bold text-slate-900">{simParams.temperature_c}°C</span>
            </div>
            <input
              type="range"
              min="15"
              max="48"
              step="1"
              value={simParams.temperature_c}
              onChange={(e) => {
                setSelectedPreset('');
                setSimParams({ ...simParams, temperature_c: e.target.value });
              }}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>15°C</span>
              <span>48°C</span>
            </div>
          </div>

          {/* Cooling Multiplier */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <TrendingUp className="w-3.5 h-3.5 text-blue-500" /> HVAC Surge
              </span>
              <span className="font-bold text-slate-900">{simParams.cooling_multiplier}x</span>
            </div>
            <input
              type="range"
              min="0.8"
              max="2.5"
              step="0.05"
              value={simParams.cooling_multiplier}
              onChange={(e) => {
                setSelectedPreset('');
                setSimParams({ ...simParams, cooling_multiplier: e.target.value });
              }}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.8x</span>
              <span>2.5x</span>
            </div>
          </div>

          {/* Solar Multiplier */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <Sun className="w-3.5 h-3.5 text-amber-500" /> Solar Yield
              </span>
              <span className="font-bold text-slate-900">{simParams.solar_multiplier}x</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="1.5"
              step="0.05"
              value={simParams.solar_multiplier}
              onChange={(e) => {
                setSelectedPreset('');
                setSimParams({ ...simParams, solar_multiplier: e.target.value });
              }}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.1x (Drop)</span>
              <span>1.5x (Peak)</span>
            </div>
          </div>

          {/* Grid Multiplier */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <BatteryCharging className="w-3.5 h-3.5 text-slate-600" /> Grid Capacity
              </span>
              <span className="font-bold text-slate-900">{simParams.grid_capacity_multiplier}x</span>
            </div>
            <input
              type="range"
              min="0.3"
              max="1.2"
              step="0.05"
              value={simParams.grid_capacity_multiplier}
              onChange={(e) => {
                setSelectedPreset('');
                setSimParams({ ...simParams, grid_capacity_multiplier: e.target.value });
              }}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.3x (Trip)</span>
              <span>1.2x (Max)</span>
            </div>
          </div>

          {/* EV Demand Multiplier */}
          <div className="space-y-2">
            <div className="flex justify-between font-medium">
              <span className="flex items-center gap-1.5 text-slate-700">
                <Car className="w-3.5 h-3.5 text-purple-600" /> EV Demand
              </span>
              <span className="font-bold text-slate-900">{simParams.ev_demand_multiplier}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="3.0"
              step="0.1"
              value={simParams.ev_demand_multiplier}
              onChange={(e) => {
                setSelectedPreset('');
                setSimParams({ ...simParams, ev_demand_multiplier: e.target.value });
              }}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>0.5x</span>
              <span>3.0x</span>
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={handleRunSimulation}
            disabled={running}
            className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl shadow-md transition-all active:scale-95 disabled:opacity-50"
          >
            <Play className={`w-3.5 h-3.5 fill-white ${running ? 'animate-pulse' : ''}`} />
            <span>{running ? 'Executing Simulation...' : 'Execute Stress Simulation'}</span>
          </button>
        </div>
      </div>

      {/* Simulation Results & Before / After Comparison */}
      {simResult && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-slate-900 text-base">Simulation Impact & Before / After Audit</h4>
            <Badge variant={simResult.simulated.is_constrained ? 'red' : 'green'}>
              {simResult.simulated.is_constrained ? 'Stress Curtailment Triggered' : 'Stable Capacity'}
            </Badge>
          </div>

          {/* Before & After Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Baseline */}
            <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h5 className="font-bold text-slate-700 text-sm">Baseline (Normal Operations)</h5>
                <Badge variant="slate">Pre-Event</Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[11px]">Total Available Power</span>
                  <span className="font-bold text-slate-800 text-sm">{simResult.baseline.total_supply_kw} kW</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[11px]">Total Campus Demand</span>
                  <span className="font-bold text-slate-800 text-sm">{simResult.baseline.details.total_demand_kw} kW</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[11px]">Solar Generation</span>
                  <span className="font-bold text-emerald-600 text-sm">{simResult.baseline.solar_allocated_kw} kW</span>
                </div>
                <div className="p-3 bg-slate-50 rounded-lg">
                  <span className="text-slate-400 block text-[11px]">Deficit / Shortfall</span>
                  <span className="font-bold text-slate-800 text-sm">{simResult.baseline.deficit_kw} kW</span>
                </div>
              </div>
            </div>

            {/* Simulated Stress */}
            <div className={`rounded-xl border p-6 shadow-sm space-y-4 ${
              simResult.simulated.is_constrained ? 'bg-amber-50/30 border-amber-300' : 'bg-white border-slate-200'
            }`}>
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <h5 className="font-bold text-slate-900 text-sm">Simulated Condition ({simResult.scenario_name})</h5>
                <Badge variant={simResult.simulated.is_constrained ? 'amber' : 'green'}>Post-Stress</Badge>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-white/90 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[11px]">Total Available Power</span>
                  <span className="font-bold text-slate-900 text-sm">{simResult.simulated.total_supply_kw} kW</span>
                </div>
                <div className="p-3 bg-white/90 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[11px]">Total Stressed Demand</span>
                  <span className="font-bold text-slate-900 text-sm">{simResult.simulated.details.total_demand_kw} kW</span>
                </div>
                <div className="p-3 bg-white/90 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[11px]">Solar Generation</span>
                  <span className="font-bold text-emerald-600 text-sm">{simResult.simulated.solar_allocated_kw} kW</span>
                </div>
                <div className="p-3 bg-white/90 rounded-lg border border-slate-100">
                  <span className="text-slate-400 block text-[11px]">Deficit / Shortfall</span>
                  <span className={`font-bold text-sm ${simResult.simulated.deficit_kw > 0 ? 'text-rose-600' : 'text-slate-800'}`}>
                    {simResult.simulated.deficit_kw} kW
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Module H: AI Recommendation Assistant Directives */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-3">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-500" />
              <h4 className="font-bold text-slate-900 text-sm">AI Energy Recommendation Assistant</h4>
            </div>
            <p className="text-xs text-slate-500">
              Autonomous algorithmic directives for load balancing and peak shaving under current scenario conditions.
            </p>

            <div className="space-y-2 pt-2">
              {simResult.recommendations.map((rec, i) => (
                <div key={i} className="p-3 bg-slate-50 rounded-lg border border-slate-100 flex items-start gap-2.5 text-xs text-slate-800">
                  <ArrowRight className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
