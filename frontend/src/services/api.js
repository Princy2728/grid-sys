const API_BASE = '/api';

export const api = {
  // Energy
  getEnergyOverview: async () => {
    const res = await fetch(`${API_BASE}/energy/overview`);
    if (!res.ok) throw new Error('Failed to fetch energy overview');
    return res.json();
  },
  getEnergyHistory: async (hours = 24) => {
    const res = await fetch(`${API_BASE}/energy/history?hours=${hours}`);
    if (!res.ok) throw new Error('Failed to fetch energy history');
    return res.json();
  },
  getSolarAnalytics: async () => {
    const res = await fetch(`${API_BASE}/energy/solar`);
    if (!res.ok) throw new Error('Failed to fetch solar analytics');
    return res.json();
  },
  getDemandForecast: async () => {
    const res = await fetch(`${API_BASE}/energy/forecast`);
    if (!res.ok) throw new Error('Failed to fetch demand forecast');
    return res.json();
  },
  getCampusBuildings: async () => {
    const res = await fetch(`${API_BASE}/energy/buildings`);
    if (!res.ok) throw new Error('Failed to fetch campus buildings');
    return res.json();
  },

  // EV Fleet & Stations
  getVehicles: async () => {
    const res = await fetch(`${API_BASE}/ev/vehicles`);
    if (!res.ok) throw new Error('Failed to fetch vehicles');
    return res.json();
  },
  createVehicle: async (data) => {
    const res = await fetch(`${API_BASE}/ev/vehicles`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to create vehicle');
    return res.json();
  },
  deleteVehicle: async (id) => {
    const res = await fetch(`${API_BASE}/ev/vehicles/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete vehicle');
    return true;
  },
  getStations: async () => {
    const res = await fetch(`${API_BASE}/ev/stations`);
    if (!res.ok) throw new Error('Failed to fetch stations');
    return res.json();
  },
  updateStation: async (id, data) => {
    const res = await fetch(`${API_BASE}/ev/stations/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update station');
    return res.json();
  },
  getChargingRequests: async () => {
    const res = await fetch(`${API_BASE}/ev/requests`);
    if (!res.ok) throw new Error('Failed to fetch requests');
    return res.json();
  },
  createChargingRequest: async (data) => {
    const res = await fetch(`${API_BASE}/ev/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create charging request');
    }
    return res.json();
  },
  updateChargingRequest: async (id, data) => {
    const res = await fetch(`${API_BASE}/ev/requests/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update charging request');
    return res.json();
  },

  // Smart Allocation
  getCurrentAllocation: async () => {
    const res = await fetch(`${API_BASE}/allocation/current`);
    if (!res.ok) throw new Error('Failed to fetch allocation');
    return res.json();
  },
  calculateAllocation: async (params) => {
    const res = await fetch(`${API_BASE}/allocation/calculate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to calculate allocation');
    return res.json();
  },

  // Simulation Lab
  getScenarios: async () => {
    const res = await fetch(`${API_BASE}/simulation/scenarios`);
    if (!res.ok) throw new Error('Failed to fetch scenarios');
    return res.json();
  },
  runSimulation: async (params) => {
    const res = await fetch(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params)
    });
    if (!res.ok) throw new Error('Failed to run simulation');
    return res.json();
  },

  // Alerts & Reports
  getAlerts: async (resolved) => {
    const url = resolved !== undefined ? `${API_BASE}/alerts?resolved=${resolved}` : `${API_BASE}/alerts`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch alerts');
    return res.json();
  },
  resolveAlert: async (id) => {
    const res = await fetch(`${API_BASE}/alerts/${id}/resolve`, { method: 'PATCH' });
    if (!res.ok) throw new Error('Failed to resolve alert');
    return res.json();
  },
  getIncidentReport: async () => {
    const res = await fetch(`${API_BASE}/alerts/report`);
    if (!res.ok) throw new Error('Failed to generate incident report');
    return res.json();
  },

  // Settings
  getSettings: async () => {
    const res = await fetch(`${API_BASE}/settings`);
    if (!res.ok) throw new Error('Failed to fetch settings');
    return res.json();
  },
  updateSettings: async (data) => {
    const res = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!res.ok) throw new Error('Failed to update settings');
    return res.json();
  },
  resetSettings: async () => {
    const res = await fetch(`${API_BASE}/settings/reset-defaults`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reset settings');
    return res.json();
  }
};
