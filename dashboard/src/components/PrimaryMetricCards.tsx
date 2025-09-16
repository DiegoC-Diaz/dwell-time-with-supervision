import { Users, Clock, TrendingUp, Timer } from 'lucide-react';
import { DashboardMetrics, MaxTimePerPersonData } from '@/types/metrics';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  subtitle?: string;
  color?: string;
}

function MetricCard({ title, value, icon, subtitle, color = 'blue' }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    pink: 'bg-pink-50 text-pink-600'
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

interface PrimaryMetricCardsProps {
  metrics: DashboardMetrics;
  maxTimeData?: MaxTimePerPersonData | null;
  selectedZoneName?: string;
}

export function PrimaryMetricCards({ metrics, maxTimeData, selectedZoneName }: PrimaryMetricCardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Visitantes Totales"
        value={metrics.totalVisitors.toLocaleString()}
        icon={<Users className="h-6 w-6" />}
        subtitle={`Fecha: ${metrics.date}`}
        color="blue"
      />
      <MetricCard
        title="Hora Pico"
        value={metrics.peakHour}
        icon={<TrendingUp className="h-6 w-6" />}
        subtitle="Mayor actividad"
        color="green"
      />
      <MetricCard
        title="Tiempo Promedio"
        value={`${metrics.averageDwellTime} seg`}
        icon={<Clock className="h-6 w-6" />}
        subtitle={selectedZoneName ? `Por visitante en ${selectedZoneName}` : "Por visitante"}
        color="purple"
      />
      <MetricCard
        title="Tiempo Máximo"
        value={maxTimeData ? `${maxTimeData.duration_minutes} min` : "N/A"}
        icon={<Timer className="h-6 w-6" />}
        subtitle={maxTimeData ? 
          `Zona ${maxTimeData.zone_id} - ${new Date(maxTimeData.start_time).toLocaleTimeString()}` : 
          "Sin datos"
        }
        color="orange"
      />
    </div>
  );
}
