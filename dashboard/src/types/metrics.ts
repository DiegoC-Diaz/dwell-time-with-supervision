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

// Tipos para las nuevas métricas de tiempo máximo
export interface MaxTimePerPersonData {
  max_time_s: number;
  zone_id: number;
  start_time: string;
  end_time: string;
  duration_minutes: number;
}

export interface MaxTimePerPersonResponse {
  success: boolean;
  message: string;
  data: MaxTimePerPersonData | null;
}

// Tipos para filtros de zona
export interface ZoneFilter {
  id: number;
  name: string;
}
