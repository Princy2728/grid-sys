import React, { useEffect, useState } from 'react';
import { 
  Car, 
  BatteryCharging, 
  Plus, 
  Trash2, 
  Zap, 
  Clock, 
  AlertCircle, 
  CheckCircle2, 
  ShieldAlert,
  ChevronRight 
} from 'lucide-react';
import Badge from '../components/Badge';
import { api } from '../services/api';

export default function EvManagementPage() {
  const [vehicles, setVehicles] = useState([]);
  const [stations, setStations] = useState([]);
  const [requests, setRequests] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Modal States
  const [showAddEvModal, setShowAddEvModal] = useState(false);
  const [showReqModal, setShowReqModal] = useState(false);
  const [newEvData, setNewEvData] = useState({
    model: '',
    owner_name: '',
    license_plate: '',
    battery_capacity_kwh: 75.0,
    current_soc_pct: 35.0,
    target_soc_pct: 85.0,
    is_emergency_vehicle: false
  });
  const [newReqData, setNewReqData] = useState({
    ev_id: '',
    station_id: '',
    requested_energy_kwh: 35.0,
    current_soc_pct: 30.0,
    target_soc_pct: 80.0,
    departure_hours: 4,
    priority_level: 'Normal'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [vList, sList, rList, sessList] = await Promise.all([
        api.getVehicles(),
        api.getStations(),
        api.getChargingRequests(),
        api.getChargingRequests() // or sessions
      ]);
      setVehicles(vList);
      setStations(sList);
      setRequests(rList);
      setSessions(sessList.filter(r => r.status === 'active'));
    } catch (err) {
      console.error('Failed to load EV data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEv = async (e) => {
    e.preventDefault();
    try {
      await api.createVehicle(newEvData);
      setShowAddEvModal(false);
      setNewEvData({
        model: '',
        owner_name: '',
        license_plate: '',
        battery_capacity_kwh: 75.0,
        current_soc_pct: 35.0,
        target_soc_pct: 85.0,
        is_emergency_vehicle: false
      });
      loadData();
    } catch (err) {
      alert('Error creating vehicle: ' + err.message);
    }
  };

  const handleDeleteEv = async (id) => {
    if (!window.confirm('Are you sure you want to delete this vehicle from the fleet?')) return;
    try {
      await api.deleteVehicle(id);
      loadData();
    } catch (err) {
      alert('Error deleting vehicle: ' + err.message);
    }
  };

  const handleCreateRequest = async (e) => {
    e.preventDefault();
    try {
      const departureDate = new Date();
      departureDate.setHours(departureDate.getHours() + parseInt(newReqData.departure_hours || 4));

      await api.createChargingRequest({
        ev_id: parseInt(newReqData.ev_id),
        station_id: newReqData.station_id ? parseInt(newReqData.station_id) : null,
        requested_energy_kwh: parseFloat(newReqData.requested_energy_kwh),
        current_soc_pct: parseFloat(newReqData.current_soc_pct),
        target_soc_pct: parseFloat(newReqData.target_soc_pct),
        departure_time: departureDate.toISOString(),
        priority_level: newReqData.priority_level
      });
      setShowReqModal(false);
      loadData();
    } catch (err) {
      alert('Error creating charging request: ' + err.message);
    }
  };

  const handleUpdateStatus = async (reqId, newStatus) => {
    try {
      await api.updateChargingRequest(reqId, { status: newStatus });
      loadData();
    } catch (err) {
      alert('Error updating status: ' + err.message);
    }
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">EV Fleet & Charging Station Infrastructure</h3>
          <p className="text-xs text-slate-500">Manage registered electric vehicles, charging sessions, priority queuing and smart deferrals.</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowReqModal(true)}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <Zap className="w-3.5 h-3.5" />
            <span>New Charging Request</span>
          </button>
          <button
            onClick={() => setShowAddEvModal(true)}
            className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Register Vehicle</span>
          </button>
        </div>
      </div>

      {/* Charging Station Status Grid */}
      <div className="space-y-3">
        <h4 className="text-sm font-bold text-slate-800">Charging Station Network</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {stations.map((st) => (
            <div key={st.id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm hover:border-slate-300 transition-all">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-slate-900 text-sm">{st.name}</span>
                <Badge variant={
                  st.status === 'in_use' ? 'blue' :
                  st.status === 'available' ? 'green' : 'red'
                }>
                  {st.status.replace('_', ' ')}
                </Badge>
              </div>
              <p className="text-[11px] text-slate-500 mb-3">{st.location}</p>
              <div className="flex items-baseline justify-between pt-2 border-t border-slate-100 text-xs">
                <span className="text-slate-400">Current / Max:</span>
                <span className="font-bold text-slate-800">{st.current_power_kw} / {st.max_power_kw} kW</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-1">{st.connector_type}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Active Charging Sessions & Requests */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h4 className="font-bold text-slate-900 text-sm">Active Sessions & Charging Queue</h4>
            <p className="text-xs text-slate-500">Live power allocations and queued requests ranked by priority tier.</p>
          </div>
          <Badge variant="blue">{requests.length} Total Requests</Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-5 py-3">Vehicle</th>
                <th className="px-5 py-3">Station</th>
                <th className="px-5 py-3">Priority</th>
                <th className="px-5 py-3">Allocated Power</th>
                <th className="px-5 py-3">Energy Requested</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {requests.map((req) => (
                <tr key={req.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-5 py-3.5 font-medium text-slate-800">
                    {req.ev?.model || `EV #${req.ev_id}`}
                    <span className="block text-[11px] text-slate-400 font-normal">{req.ev?.license_plate}</span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {req.station_id ? `Station CS-0${req.station_id}` : 'Unassigned (Queue)'}
                  </td>
                  <td className="px-5 py-3.5">
                    <Badge variant={
                      req.priority_level === 'Urgent' ? 'red' :
                      req.priority_level === 'High' ? 'amber' :
                      req.priority_level === 'Flexible' ? 'purple' : 'blue'
                    }>
                      {req.priority_level}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5 font-bold text-slate-800">
                    {req.allocated_power_kw > 0 ? `${req.allocated_power_kw} kW` : '0 kW (Deferred)'}
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">
                    {req.requested_energy_kwh} kWh
                    <span className="block text-[10px] text-slate-400">{req.current_soc_pct}% → {req.target_soc_pct}%</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold ${
                      req.status === 'active' ? 'bg-blue-100 text-blue-700' :
                      req.status === 'deferred' ? 'bg-amber-100 text-amber-800' :
                      req.status === 'completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {req.status}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right space-x-2">
                    {req.status === 'active' && (
                      <button
                        onClick={() => handleUpdateStatus(req.id, 'deferred')}
                        className="px-2 py-1 text-[11px] text-amber-700 bg-amber-50 border border-amber-200 rounded hover:bg-amber-100"
                        title="Defer to off-peak"
                      >
                        Defer
                      </button>
                    )}
                    {req.status === 'deferred' && (
                      <button
                        onClick={() => handleUpdateStatus(req.id, 'active')}
                        className="px-2 py-1 text-[11px] text-blue-700 bg-blue-50 border border-blue-200 rounded hover:bg-blue-100"
                        title="Resume active charging"
                      >
                        Resume
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Registered Vehicles Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h4 className="font-bold text-slate-900 text-sm">Registered Fleet Vehicles</h4>
            <p className="text-xs text-slate-500">Campus emergency responders, operations shuttles, faculty and student EVs.</p>
          </div>
          <Badge variant="slate">{vehicles.length} Vehicles</Badge>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-5 py-3">Vehicle Details</th>
                <th className="px-5 py-3">Owner / Organization</th>
                <th className="px-5 py-3">Battery Capacity</th>
                <th className="px-5 py-3">State of Charge (SoC)</th>
                <th className="px-5 py-3">Classification</th>
                <th className="px-5 py-3 text-right">Delete</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {vehicles.map((v) => (
                <tr key={v.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-slate-900">{v.model}</span>
                    <span className="block text-[11px] text-slate-400">{v.license_plate}</span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600">{v.owner_name}</td>
                  <td className="px-5 py-3.5 font-medium text-slate-800">{v.battery_capacity_kwh} kWh</td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-24 bg-slate-200 rounded-full h-2 overflow-hidden">
                        <div 
                          className={`h-2 rounded-full ${
                            v.current_soc_pct < 25 ? 'bg-rose-500' :
                            v.current_soc_pct < 50 ? 'bg-amber-500' : 'bg-emerald-500'
                          }`}
                          style={{ width: `${v.current_soc_pct}%` }}
                        ></div>
                      </div>
                      <span className="font-bold text-slate-700">{v.current_soc_pct}%</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5">
                    {v.is_emergency_vehicle ? (
                      <Badge variant="red">Emergency / Priority</Badge>
                    ) : (
                      <Badge variant="slate">Standard Fleet</Badge>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <button
                      onClick={() => handleDeleteEv(v.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-colors"
                      title="Remove vehicle"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal: Register New EV */}
      {showAddEvModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-slate-900 text-base">Register New Fleet EV</h3>
            <form onSubmit={handleCreateEv} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Vehicle Model</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Tesla Model Y / BYD Transit"
                  value={newEvData.model}
                  onChange={(e) => setNewEvData({ ...newEvData, model: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Owner / Dept</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Campus Health Services"
                  value={newEvData.owner_name}
                  onChange={(e) => setNewEvData({ ...newEvData, owner_name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">License Plate</label>
                  <input
                    type="text"
                    required
                    placeholder="EV-999-XYZ"
                    value={newEvData.license_plate}
                    onChange={(e) => setNewEvData({ ...newEvData, license_plate: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Battery Size (kWh)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={newEvData.battery_capacity_kwh}
                    onChange={(e) => setNewEvData({ ...newEvData, battery_capacity_kwh: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Current SoC (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={newEvData.current_soc_pct}
                    onChange={(e) => setNewEvData({ ...newEvData, current_soc_pct: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Target SoC (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={newEvData.target_soc_pct}
                    onChange={(e) => setNewEvData({ ...newEvData, target_soc_pct: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>
              <div className="flex items-center gap-2 pt-2">
                <input
                  type="checkbox"
                  id="emCheck"
                  checked={newEvData.is_emergency_vehicle}
                  onChange={(e) => setNewEvData({ ...newEvData, is_emergency_vehicle: e.target.checked })}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="emCheck" className="text-slate-700 font-medium">Designate as Emergency / Critical Vehicle</label>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddEvModal(false)}
                  className="px-4 py-2 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm"
                >
                  Register EV
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: New Charging Request */}
      {showReqModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <h3 className="font-bold text-slate-900 text-base">Submit EV Charging Request</h3>
            <form onSubmit={handleCreateRequest} className="space-y-3 text-xs">
              <div>
                <label className="font-semibold text-slate-700 block mb-1">Select Vehicle</label>
                <select
                  required
                  value={newReqData.ev_id}
                  onChange={(e) => {
                    const selected = vehicles.find(v => v.id === parseInt(e.target.value));
                    setNewReqData({
                      ...newReqData,
                      ev_id: e.target.value,
                      current_soc_pct: selected ? selected.current_soc_pct : 30,
                      target_soc_pct: selected ? selected.target_soc_pct : 80
                    });
                  }}
                  className="w-full px-3 py-2 border rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="">-- Choose Registered Vehicle --</option>
                  {vehicles.map(v => (
                    <option key={v.id} value={v.id}>
                      {v.model} ({v.license_plate}) - {v.is_emergency_vehicle ? '🚨 Emergency' : 'Standard'}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Assign Charging Station (Optional)</label>
                <select
                  value={newReqData.station_id}
                  onChange={(e) => setNewReqData({ ...newReqData, station_id: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="">Auto-Queue / Smart Dispatch</option>
                  {stations.filter(s => s.status !== 'faulted').map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.max_power_kw} kW - {s.status})</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Requested Energy (kWh)</label>
                  <input
                    type="number"
                    step="0.1"
                    required
                    value={newReqData.requested_energy_kwh}
                    onChange={(e) => setNewReqData({ ...newReqData, requested_energy_kwh: parseFloat(e.target.value) })}
                    className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="font-semibold text-slate-700 block mb-1">Priority Tier</label>
                  <select
                    value={newReqData.priority_level}
                    onChange={(e) => setNewReqData({ ...newReqData, priority_level: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="Urgent">Urgent (Emergency / High-Need)</option>
                    <option value="High">High Priority</option>
                    <option value="Normal">Normal Commuter</option>
                    <option value="Flexible">Flexible (Can Defer)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="font-semibold text-slate-700 block mb-1">Scheduled Departure In (Hours)</label>
                <input
                  type="number"
                  min="1"
                  max="48"
                  value={newReqData.departure_hours}
                  onChange={(e) => setNewReqData({ ...newReqData, departure_hours: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setShowReqModal(false)}
                  className="px-4 py-2 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-sm"
                >
                  Enqueue Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
