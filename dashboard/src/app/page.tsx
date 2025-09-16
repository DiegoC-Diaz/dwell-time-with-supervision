'use client';

import { useState, useEffect } from 'react';
import { Calendar, Eye, RefreshCw, AlertCircle, Settings } from 'lucide-react';
import { PrimaryMetricCards } from '@/components/PrimaryMetricCards';
import { ZoneFilterDropdown } from '@/components/ZoneFilterDropdown';
import { useDashboardData, transformToDashboardMetrics, useMaxTimePerPerson } from '@/lib/metricsHooks';


export default function Dashboard() {
  const [selectedDate, setSelectedDate] = useState<string | undefined>(undefined);
  const [selectedZoneId, setSelectedZoneId] = useState<number | undefined>(undefined);
  const [selectedZoneName, setSelectedZoneName] = useState<string | undefined>(undefined);
  
  const { data, loading, error, refreshData } = useDashboardData("daily", selectedDate, selectedZoneId);
  const { data: maxTimeData, loading: maxTimeLoading, error: maxTimeError, refreshData: refreshMaxTimeData } = useMaxTimePerPerson(selectedDate, selectedDate, selectedZoneId);

  // Obtener el nombre de la zona seleccionada
  useEffect(() => {
    const fetchZoneName = async () => {
      if (selectedZoneId) {
        try {
          const response = await fetch(`http://localhost:8000/api/zones/${selectedZoneId}`);
          if (response.ok) {
            const zoneData = await response.json();
            setSelectedZoneName(zoneData.zone_name);
          }
        } catch (error) {
          console.error('Error fetching zone name:', error);
        }
      } else {
        setSelectedZoneName(undefined);
      }
    };

    fetchZoneName();
  }, [selectedZoneId]);

  // Transformar datos para el dashboard
  const dashboardMetrics = data ? transformToDashboardMetrics(data) : null;
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <Eye className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Vision Analytics</h1>
                <p className="text-sm text-gray-600">Dashboard de Computer Vision</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {/* Indicador de estado */}
              {error && (
                <div className="flex items-center space-x-2 text-amber-600 bg-amber-50 px-3 py-1 rounded-lg">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm font-medium">Usando datos mock</span>
                </div>
              )}
              
              {/* Selector de fecha */}
              <div className="flex items-center space-x-2">
                <Calendar className="h-4 w-4 text-gray-500" />
                <input
                  type="date"
                  value={selectedDate || ''}
                  onChange={(e) => setSelectedDate(e.target.value || undefined)}
                  className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              {/* Filtro de zona */}
              <ZoneFilterDropdown
                selectedZoneId={selectedZoneId}
                onZoneChange={setSelectedZoneId}
              />
              
              {/* Botón de configuración */}
              <button
                onClick={() => window.location.href = '/settings'}
                className="flex items-center space-x-2 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Settings className="h-4 w-4" />
                <span>Configuración</span>
              </button>
              
              {/* Botón de refresh */}
              <button
                onClick={() => {
                  refreshData();
                  refreshMaxTimeData();
                }}
                disabled={loading || maxTimeLoading}
                className="flex items-center space-x-2 px-3 py-1 text-sm font-medium text-gray-600 hover:text-gray-900 disabled:opacity-50"
              >
                <RefreshCw className={`h-4 w-4 ${(loading || maxTimeLoading) ? 'animate-spin' : ''}`} />
                <span>Actualizar</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Indicador de carga */}
        {(loading || maxTimeLoading) && (
          <div className="flex justify-center items-center py-12">
            <div className="flex items-center space-x-3">
              <RefreshCw className="h-6 w-6 animate-spin text-blue-600" />
              <span className="text-lg text-gray-600">Cargando métricas...</span>
            </div>
          </div>
        )}

        {/* Mensaje de error */}
        {(error || maxTimeError) && !loading && !maxTimeLoading && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-amber-600" />
              <span className="text-amber-800 font-medium">Conexión con API fallida</span>
            </div>
            <p className="text-amber-700 mt-1">Mostrando datos de ejemplo. Error: {error || maxTimeError}</p>
            <button
              onClick={() => {
                refreshData();
                refreshMaxTimeData();
              }}
              className="mt-2 text-amber-600 hover:text-amber-800 text-sm font-medium"
            >
              Intentar reconectar
            </button>
          </div>
        )}

        {/* Contenido principal */}
        {!loading && !maxTimeLoading && data && dashboardMetrics && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Métricas Principales
            </h2>
            <PrimaryMetricCards 
              metrics={dashboardMetrics} 
              maxTimeData={maxTimeData}
              selectedZoneName={selectedZoneName} 
            />
          </div>
        )}
      </main>
    </div>
  );
}

