import React, { useEffect, useState } from 'react';
import { 
  AlertTriangle, 
  ShieldCheck, 
  CheckCircle2, 
  FileText, 
  Download, 
  Filter,
  Check
} from 'lucide-react';
import Badge from '../components/Badge';
import { api } from '../services/api';

export default function AlertsReportsPage() {
  const [alerts, setAlerts] = useState([]);
  const [filterResolved, setFilterResolved] = useState('all');
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, [filterResolved]);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const resVal = filterResolved === 'all' ? undefined : filterResolved === 'resolved';
      const [al, rep] = await Promise.all([
        api.getAlerts(resVal),
        api.getIncidentReport()
      ]);
      setAlerts(al);
      setReport(rep);
    } catch (err) {
      console.error('Failed to load alerts', err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id) => {
    try {
      await api.resolveAlert(id);
      loadAlerts();
    } catch (err) {
      alert('Error resolving alert: ' + err.message);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header & Export Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-slate-900">System Alerts & Operational Incident Reports</h3>
          <p className="text-xs text-slate-500">
            Real-time security surveillance, substation headroom warnings, inverter isolation, and audit reports.
          </p>
        </div>
        <button
          onClick={handlePrint}
          className="flex items-center gap-1.5 px-3 py-2 text-xs font-semibold text-slate-700 bg-white border border-slate-300 hover:bg-slate-50 rounded-lg shadow-sm transition-colors"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Incident Audit</span>
        </button>
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Unresolved Incidents</span>
          <div className="mt-2 text-2xl font-bold text-slate-900">{report?.active_unresolved_alerts ?? 0}</div>
          <span className="text-xs text-slate-400">Requires engineer attention</span>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Critical Severity</span>
          <div className="mt-2 text-2xl font-bold text-rose-600">{report?.critical_incident_count ?? 0}</div>
          <span className="text-xs text-rose-700">Substation or isolation fault</span>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Warning Level</span>
          <div className="mt-2 text-2xl font-bold text-amber-600">{report?.warning_incident_count ?? 0}</div>
          <span className="text-xs text-amber-700">Peak threshold warnings</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2 text-xs font-medium">
        <button
          onClick={() => setFilterResolved('all')}
          className={`px-3 py-1.5 rounded-lg transition-colors ${
            filterResolved === 'all' ? 'bg-slate-900 text-white font-semibold' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          All Incidents
        </button>
        <button
          onClick={() => setFilterResolved('active')}
          className={`px-3 py-1.5 rounded-lg transition-colors ${
            filterResolved === 'active' ? 'bg-slate-900 text-white font-semibold' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Active Only
        </button>
        <button
          onClick={() => setFilterResolved('resolved')}
          className={`px-3 py-1.5 rounded-lg transition-colors ${
            filterResolved === 'resolved' ? 'bg-slate-900 text-white font-semibold' : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Resolved Archive
        </button>
      </div>

      {/* Alerts Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-5 py-3">Severity</th>
                <th className="px-5 py-3">Incident Title</th>
                <th className="px-5 py-3">Category</th>
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {alerts.map((alt) => (
                <tr key={alt.id} className="hover:bg-slate-50/60 transition-colors">
                  <td className="px-5 py-3.5">
                    <Badge variant={
                      alt.severity === 'critical' ? 'red' :
                      alt.severity === 'warning' ? 'amber' : 'blue'
                    }>
                      {alt.severity.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className="font-bold text-slate-800">{alt.title}</span>
                    <span className="block text-[11px] text-slate-500 mt-0.5">{alt.description}</span>
                  </td>
                  <td className="px-5 py-3.5 text-slate-600 font-mono text-[11px]">{alt.type}</td>
                  <td className="px-5 py-3.5 text-slate-500 text-[11px]">
                    {new Date(alt.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold ${
                      alt.is_resolved ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                    }`}>
                      {alt.is_resolved ? 'Resolved' : 'Active'}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    {!alt.is_resolved && (
                      <button
                        onClick={() => handleResolve(alt.id)}
                        className="flex items-center gap-1 ml-auto px-2.5 py-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 rounded transition-colors"
                      >
                        <Check className="w-3 h-3" />
                        <span>Resolve</span>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
