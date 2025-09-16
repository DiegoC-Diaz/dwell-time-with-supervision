'use client';

import { ArrowLeft, Eye, Info, Settings as SettingsIcon, MapPin, Plus, Trash2, Edit3, X, Play } from 'lucide-react';
import { useState, useEffect } from 'react';
import VideoUpload from '@/components/VideoUpload';
import PolygonCanvas from '@/components/PolygonCanvas';
import ProcessForm from '@/components/ProcessForm';
import { useZones, type Point } from '@/lib/zonesHooks';

export default function Settings() {
  const [activeTab, setActiveTab] = useState<'system' | 'zone-management' | 'zone-config'>('system');
  const [extractedFrameUrl, setExtractedFrameUrl] = useState<string>('');
  const [showSuccessMessage, setShowSuccessMessage] = useState<string>('');
  const [showProcessForm, setShowProcessForm] = useState(false);
  const [selectedZone, setSelectedZone] = useState<{ id: number; name: string; type: string } | null>(null);
  
  const { zones, loading, error, fetchZones, createZone, deleteZone, clearError } = useZones();

  useEffect(() => {
    fetchZones();
  }, [fetchZones]);

  const handleBackToDashboard = () => {
    window.location.href = '/';
  };

  const handleFrameExtracted = (imageUrl: string) => {
    setExtractedFrameUrl(imageUrl);
  };

  const handleSaveZone = async (zoneName: string, zoneType: string, coordinates: Point[][]) => {
    const success = await createZone(zoneName, zoneType, coordinates);
    
    if (success) {
      setShowSuccessMessage(`Zona "${zoneName}" creada exitosamente`);
      setTimeout(() => setShowSuccessMessage(''), 3000);
    }
  };

  const handleDeleteZone = async (zoneId: number, zoneName: string) => {
    if (confirm(`¿Estás seguro de que quieres eliminar la zona "${zoneName}"?`)) {
      const success = await deleteZone(zoneId);
      
      if (success) {
        setShowSuccessMessage(`Zona "${zoneName}" eliminada exitosamente`);
        setTimeout(() => setShowSuccessMessage(''), 3000);
      }
    }
  };

  const handleProcessZone = (zoneId: number, zoneName: string, zoneType: string) => {
    setSelectedZone({ id: zoneId, name: zoneName, type: zoneType });
    setShowProcessForm(true);
  };

  const handleCloseProcessForm = () => {
    setShowProcessForm(false);
    setSelectedZone(null);
  };

  const handleProcessSuccess = (message: string) => {
    setShowSuccessMessage(message);
    setTimeout(() => setShowSuccessMessage(''), 5000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <button
                onClick={handleBackToDashboard}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="h-5 w-5 text-gray-600" />
              </button>
              <div className="p-2 bg-blue-600 rounded-lg">
                <Eye className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Configuración</h1>
                <p className="text-sm text-gray-600">Información del sistema</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-6xl mx-auto">
          
          {/* Tabs Navigation */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                <button
                  onClick={() => setActiveTab('system')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'system'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <SettingsIcon className="h-4 w-4" />
                    Información del Sistema
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('zone-management')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'zone-management'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4" />
                    Gestión de Zonas
                  </div>
                </button>
                <button
                  onClick={() => setActiveTab('zone-config')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'zone-config'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <Plus className="h-4 w-4" />
                    Configuración de Zonas
                  </div>
                </button>
              </nav>
            </div>
          </div>

          {/* Success Message */}
          {showSuccessMessage && (
            <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                <p className="text-sm text-green-800">{showSuccessMessage}</p>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-red-400 rounded-full mr-3"></div>
                  <p className="text-sm text-red-800">{error}</p>
                </div>
                <button
                  onClick={clearError}
                  className="text-red-400 hover:text-red-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}

          {/* Tab Content */}
          {activeTab === 'system' && (
            <>
              {/* Información del Sistema */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-8">
                <div className="flex items-center mb-6">
                  <div className="p-3 bg-blue-100 rounded-lg mr-4">
                    <SettingsIcon className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Información del Sistema</h2>
                    <p className="text-sm text-gray-600">Estado actual del dashboard y API</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">API Status</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Endpoint Principal:</span>
                        <span className="text-sm font-medium text-green-600">Activo</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Dashboard API:</span>
                        <span className="text-sm font-medium text-green-600">Disponible</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Puerto:</span>
                        <span className="text-sm font-medium text-gray-900">8000</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Funcionalidades Disponibles</h3>
                    <div className="space-y-3">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        <span className="text-sm text-gray-600">Métricas Diarias</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        <span className="text-sm text-gray-600">Visitantes Totales</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        <span className="text-sm text-gray-600">Tiempo Promedio</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        <span className="text-sm text-gray-600">Hora Pico</span>
                      </div>
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        <span className="text-sm text-gray-600">Filtrado por Zona</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Información de Desarrollo */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                <div className="flex items-center mb-6">
                  <div className="p-3 bg-green-100 rounded-lg mr-4">
                    <Info className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Estado del Sistema</h2>
                    <p className="text-sm text-gray-600">Todas las funcionalidades principales están operativas</p>
                  </div>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="text-lg font-medium text-green-800 mb-3">Sistema Completamente Funcional</h3>
                  <p className="text-sm text-green-700 mb-4">
                    El dashboard de Vision Analytics está completamente operativo con todas las funcionalidades principales implementadas:
                  </p>
                  <ul className="text-sm text-green-700 space-y-2">
                    <li>• ✅ Configuración de zonas de análisis</li>
                    <li>• ✅ Procesamiento de videos por zona</li>
                    <li>• ✅ Métricas detalladas por zona</li>
                    <li>• ✅ Gestión completa de zonas</li>
                    <li>• ✅ Dashboard con filtros por zona</li>
                  </ul>
                </div>
              </div>
            </>
          )}

          {/* Tab de Gestión de Zonas */}
          {activeTab === 'zone-management' && (
            <div className="space-y-6">
              {/* Lista de Zonas Existentes */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center">
                    <div className="p-3 bg-blue-100 rounded-lg mr-4">
                      <MapPin className="h-6 w-6 text-blue-600" />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">Zonas Configuradas</h2>
                      <p className="text-sm text-gray-600">
                        {loading ? 'Cargando...' : `${zones.length} zona(s) configurada(s)`}
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => fetchZones()}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                  >
                    <SettingsIcon className="h-4 w-4" />
                    Actualizar
                  </button>
                </div>

                {loading && (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="mt-2 text-sm text-gray-600">Cargando zonas...</p>
                  </div>
                )}

                {!loading && zones.length === 0 && (
                  <div className="text-center py-12">
                    <MapPin className="mx-auto h-12 w-12 text-gray-400" />
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No hay zonas configuradas</h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Ve a la pestaña "Configuración de Zonas" para crear tu primera zona de detección.
                    </p>
                  </div>
                )}

                {!loading && zones.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {zones.map((zone) => (
                      <div key={zone.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h3 className="font-medium text-gray-900">{zone.zone_name}</h3>
                            <p className="text-sm text-gray-500 capitalize">{zone.zone_type}</p>
                          </div>
                          
                          <div className="flex items-center space-x-1">
                            <button
                              onClick={() => handleProcessZone(zone.id, zone.zone_name, zone.zone_type)}
                              className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
                              title="Procesar zona"
                            >
                              <Play className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteZone(zone.id, zone.zone_name)}
                              className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                              title="Eliminar zona"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <div className="text-xs text-gray-600">
                            <span className="font-medium">Polígonos:</span> {zone.coordinates.length}
                          </div>
                          
                          {zone.coordinates.map((polygon, index) => (
                            <div key={index} className="text-xs text-gray-500">
                              <span className="font-medium">Polígono {index + 1}:</span> {polygon.length} puntos
                            </div>
                          ))}
                        </div>

                        <div className="mt-3 pt-3 border-t border-gray-100">
                          <div className="flex items-center justify-between">
                            <div className="text-xs text-gray-400">
                              Creada: {zone.created_at ? new Date(zone.created_at).toLocaleDateString() : 'N/A'}
                            </div>
                            <button
                              onClick={() => handleProcessZone(zone.id, zone.zone_name, zone.zone_type)}
                              className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                            >
                              <Play className="h-3 w-3" />
                              Process
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Tab de Configuración de Zonas */}
          {activeTab === 'zone-config' && (
            <div className="space-y-6">
              {/* Crear Nueva Zona */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center mb-6">
                  <div className="p-3 bg-purple-100 rounded-lg mr-4">
                    <Plus className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900">Crear Nueva Zona</h2>
                    <p className="text-sm text-gray-600">Carga un video y dibuja polígonos de detección</p>
                  </div>
                </div>

                <div className="space-y-6">
                  {/* Panel de carga de video */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">1. Cargar Video</h3>
                    <VideoUpload
                      onFrameExtracted={handleFrameExtracted}
                      className="max-w-2xl"
                    />
                  </div>

                  {/* Panel de canvas de polígonos */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-medium text-gray-900">2. Dibujar Múltiples Polígonos</h3>
                    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                      <PolygonCanvas
                        imageUrl={extractedFrameUrl}
                        onSaveZone={handleSaveZone}
                        className="min-h-[700px]"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Process Form Modal */}
      {showProcessForm && selectedZone && (
        <ProcessForm
          zoneId={selectedZone.id}
          zoneName={selectedZone.name}
          zoneType={selectedZone.type}
          onClose={handleCloseProcessForm}
          onSuccess={handleProcessSuccess}
        />
      )}
    </div>
  );
}
