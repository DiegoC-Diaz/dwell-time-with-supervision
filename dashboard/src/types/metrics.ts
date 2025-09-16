// Tipos TypeScript para la respuesta del API actual

export interface DailyKPI {
  id: string;
  date: string;
  totalVisitors: number;
  peakHour: string;
  averageDwellTime: number;
}

export interface DashboardResponse {
  daily: DailyKPI[];
}

// Tipos para el dashboard simplificado
export interface DashboardMetrics {
  totalVisitors: number;
  peakHour: string;
  averageDwellTime: number;
  date: string;
}

// Tipos para filtros de zona
export interface ZoneFilter {
  id: number;
  name: string;
}
