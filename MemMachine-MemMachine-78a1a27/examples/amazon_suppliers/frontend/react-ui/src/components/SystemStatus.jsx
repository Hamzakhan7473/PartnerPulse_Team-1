import { useEffect, useState } from 'react';
import { CheckCircle2, AlertTriangle, Loader2, Server, Database, Cpu } from 'lucide-react';

import { supplierApi } from '../services/api';

const STATUS_META = {
  healthy: {
    icon: CheckCircle2,
    classes: 'text-emerald-600 bg-emerald-50 border-emerald-200',
  },
  degraded: {
    icon: AlertTriangle,
    classes: 'text-amber-600 bg-amber-50 border-amber-200',
  },
  unreachable: {
    icon: AlertTriangle,
    classes: 'text-rose-600 bg-rose-50 border-rose-200',
  },
  unavailable: {
    icon: AlertTriangle,
    classes: 'text-rose-600 bg-rose-50 border-rose-200',
  },
};

const DEFAULT_META = {
  icon: AlertTriangle,
  classes: 'text-slate-600 bg-slate-50 border-slate-200',
};

function StatusBadge({ label, status, icon: IconOverride, detail }) {
  const normalizedStatus = (status || 'unknown').toLowerCase();
  const meta = STATUS_META[normalizedStatus] || DEFAULT_META;
  const Icon = IconOverride || meta.icon;

  return (
    <div
      className={`flex items-start gap-3 rounded-xl border px-3 py-3 ${meta.classes}`}
    >
      <div className="mt-0.5">
        <Icon className="w-5 h-5" />
      </div>
      <div className="flex-1">
        <p className="text-sm font-semibold uppercase tracking-wide">{label}</p>
        <p className="text-xs font-medium text-slate-600">
          Status: {status || 'unknown'}
        </p>
        {detail && (
          <p className="mt-1 text-xs text-slate-500 whitespace-pre-line">{detail}</p>
        )}
      </div>
    </div>
  );
}

export default function SystemStatus() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const fetchHealth = async () => {
      setLoading(true);
      try {
        const data = await supplierApi.getSystemHealth();
        if (!active) return;
        setHealth(data);
        setError(null);
      } catch (err) {
        if (!active) return;
        setError(err.message || 'Unable to fetch system status');
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 30_000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const serviceStatus = health?.status || (error ? 'unreachable' : 'loading');
  const ServiceIcon = serviceStatus === 'healthy' ? CheckCircle2 : Server;

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">System Status</h3>
          <p className="text-sm text-slate-500">
            Live health checks for MemMachine and supporting services.
          </p>
        </div>
        {loading ? (
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <Loader2 className="w-4 h-4 animate-spin" />
            Checking...
          </div>
        ) : null}
      </div>

      {error ? (
        <div className="rounded-lg border border-rose-200 bg-rose-50 px-3 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : (
        <div className="space-y-4">
          <StatusBadge
            label="Supplier API"
            status={health?.status}
            icon={ServiceIcon}
            detail={health?.detail}
          />

          <StatusBadge
            label="MemMachine"
            status={health?.dependencies?.memmachine?.status}
            icon={Cpu}
            detail={
              health?.dependencies?.memmachine?.status !== 'healthy'
                ? health?.dependencies?.memmachine?.detail
                : null
            }
          />

          <StatusBadge
            label="PostgreSQL"
            status={health?.dependencies?.postgres?.status}
            icon={Database}
            detail={health?.dependencies?.postgres?.detail}
          />
        </div>
      )}
    </div>
  );
}


