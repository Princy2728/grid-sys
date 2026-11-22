import React, { useEffect, useState } from 'react';
import { Settings, Save, RotateCcw, CheckCircle2, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

export default function SettingsPage() {
  const [formData, setFormData] = useState({
    name: 'Metro Innovation Smart Campus',
    grid_capacity_kw: 1200.0,
    solar_capacity_kw: 650.0,
    battery_capacity_kwh: 500.0,
    critical_load_ratio: 0.35,
    max_ev_allocation_kw: 400.0,
    alert_threshold_pct: 85.0
  });
  const [loading, setLoading] = useState(true);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await api.getSettings();
      setFormData(data);
    } catch (err) {
      console.error('Failed to load settings', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await api.updateSettings(formData);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Error saving settings: ' + err.message);
    }
  };

  const handleReset = async () => {
    if (!window.confirm('Reset all campus electrical parameters to factory defaults?')) return;
    try {
      const data = await api.resetSettings();
      setFormData(data);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Error resetting defaults: ' + err.message);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading campus infrastructure settings...</div>;
  }

  return (
    <div className="p-8 space-y-8 max-w-4xl mx-auto">
      <div>
        <h3 className="text-xl font-bold text-slate-900">Campus Infrastructure & Optimization Settings</h3>
        <p className="text-xs text-slate-500">
          Configure physical electrical substation constraints, solar ratings, and priority scheduling ratios.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Campus configuration updated successfully and active in real-time dispatch!</span>
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6 text-xs">
        <div className="space-y-4">
          <h4 className="font-bold text-slate-900 text-sm border-b pb-2">Primary Campus Identity</h4>
          <div>
            <label className="font-semibold text-slate-700 block mb-1">Campus Name</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
        </div>

        <div className="space-y-4 pt-2">
          <h4 className="font-bold text-slate-900 text-sm border-b pb-2">Electrical Capacity Ratings</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Grid Substation Capacity (kW)</label>
              <input
                type="number"
                step="10"
                required
                value={formData.grid_capacity_kw}
                onChange={(e) => setFormData({ ...formData, grid_capacity_kw: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Nominal utility transformer thermal rating</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Rooftop Solar PV Array Peak (kW)</label>
              <input
                type="number"
                step="10"
                required
                value={formData.solar_capacity_kw}
                onChange={(e) => setFormData({ ...formData, solar_capacity_kw: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Aggregate peak nameplate DC/AC rating</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Battery Storage Capacity (kWh)</label>
              <input
                type="number"
                step="10"
                required
                value={formData.battery_capacity_kwh}
                onChange={(e) => setFormData({ ...formData, battery_capacity_kwh: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Stationary BESS reserve buffer</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Max Substation EV Allocation (kW)</label>
              <input
                type="number"
                step="10"
                required
                value={formData.max_ev_allocation_kw}
                onChange={(e) => setFormData({ ...formData, max_ev_allocation_kw: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Maximum power dedicated to EV chargers</span>
            </div>
          </div>
        </div>

        <div className="space-y-4 pt-2">
          <h4 className="font-bold text-slate-900 text-sm border-b pb-2">Thresholds & Reliability Rules</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">Critical Load Baseline Ratio</label>
              <input
                type="number"
                step="0.01"
                min="0.1"
                max="0.9"
                required
                value={formData.critical_load_ratio}
                onChange={(e) => setFormData({ ...formData, critical_load_ratio: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Fraction reserved unconditionally for Tier 1 loads</span>
            </div>

            <div>
              <label className="font-semibold text-slate-700 block mb-1">Substation Alert Threshold (%)</label>
              <input
                type="number"
                min="50"
                max="98"
                required
                value={formData.alert_threshold_pct}
                onChange={(e) => setFormData({ ...formData, alert_threshold_pct: parseFloat(e.target.value) })}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
              <span className="text-[10px] text-slate-400 mt-1 block">Trigger warning alert when grid import reaches %</span>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t flex items-center justify-between">
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center gap-1.5 px-4 py-2 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>

          <button
            type="submit"
            className="flex items-center gap-1.5 px-5 py-2 text-white bg-blue-600 hover:bg-blue-700 font-semibold rounded-lg shadow-sm transition-colors"
          >
            <Save className="w-3.5 h-3.5" />
            <span>Save Configuration</span>
          </button>
        </div>
      </form>
    </div>
  );
}
