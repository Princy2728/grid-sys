import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import EvManagementPage from './pages/EvManagementPage';
import EnergyIntelligencePage from './pages/EnergyIntelligencePage';
import SmartAllocationPage from './pages/SmartAllocationPage';
import SimulationLabPage from './pages/SimulationLabPage';
import AlertsReportsPage from './pages/AlertsReportsPage';
import SettingsPage from './pages/SettingsPage';
import { api } from './services/api';

const pageTitles = {
  overview: { title: 'Campus Energy Operations & KPI Telemetry', subtitle: 'Real-time monitoring of electrical demand, solar contribution, and grid headroom' },
  ev: { title: 'Electric Vehicle Fleet & Charging Station Hub', subtitle: 'Charger status, priority queues, battery states of charge and smart deferrals' },
  intelligence: { title: 'Predictive Energy Intelligence & Forecasts', subtitle: 'Autoregressive Ridge ML demand projections, solar physics, and anomaly detection' },
  allocation: { title: 'Constrained Priority Resource Allocation', subtitle: 'Deterministic 5-tier dispatch preventing grid overload and prioritizing life safety' },
  simulation: { title: 'Heatwave & Grid Stress Simulation Lab', subtitle: 'Interactive stress modeling, HVAC surges, solar degradation, and AI recommendations' },
  alerts: { title: 'Alerts Surveillance & Incident Audit Reports', subtitle: 'Ground faults, substation warnings, and downloadable operational reports' },
  settings: { title: 'Campus Infrastructure & Grid Constraints', subtitle: 'Substation capacity, PV array sizing, and critical reserve configuration' }
};

export default function App() {
  const [currentPage, setCurrentPage] = useState('overview');
  const [alertCount, setAlertCount] = useState(0);
  const [telemetry, setTelemetry] = useState({ weather: 'Clear', temp: 24.5 });
  const [refreshing, setRefreshing] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetchQuickStatus();
  }, [refreshKey]);

  const fetchQuickStatus = async () => {
    try {
      const [ov, al] = await Promise.all([
        api.getEnergyOverview(),
        api.getAlerts(false)
      ]);
      setTelemetry({
        weather: ov?.weather || 'Clear',
        temp: ov?.temperature_c || 24.5
      });
      setAlertCount(al?.length || 0);
    } catch (e) {
      console.warn('Initial status fetch warning:', e);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    setRefreshKey(prev => prev + 1);
    await fetchQuickStatus();
    setTimeout(() => setRefreshing(false), 500);
  };

  const currentMeta = pageTitles[currentPage] || pageTitles.overview;

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans text-slate-800">
      {/* Dark Navy Sidebar */}
      <Sidebar
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        alertCount={alertCount}
      />

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        <Header
          title={currentMeta.title}
          subtitle={currentMeta.subtitle}
          weather={telemetry.weather}
          temperature={telemetry.temp}
          onRefresh={handleRefresh}
          isRefreshing={refreshing}
        />

        <main className="flex-1 overflow-y-auto bg-slate-50/50">
          {currentPage === 'overview' && <OverviewPage key={refreshKey} onNavigate={setCurrentPage} />}
          {currentPage === 'ev' && <EvManagementPage key={refreshKey} />}
          {currentPage === 'intelligence' && <EnergyIntelligencePage key={refreshKey} />}
          {currentPage === 'allocation' && <SmartAllocationPage key={refreshKey} />}
          {currentPage === 'simulation' && <SimulationLabPage key={refreshKey} />}
          {currentPage === 'alerts' && <AlertsReportsPage key={refreshKey} />}
          {currentPage === 'settings' && <SettingsPage key={refreshKey} />}
        </main>
      </div>
    </div>
  );
}
