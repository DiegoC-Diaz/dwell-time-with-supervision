'use client';

import { useState } from 'react';
import { X, Play, Calendar, FileVideo, Settings, AlertCircle } from 'lucide-react';
import { useProcesses, type ProcessRequest } from '@/lib/processHooks';

interface ProcessFormProps {
  zoneId: number;
  zoneName: string;
  zoneType: string;
  onClose: () => void;
  onSuccess: (message: string) => void;
}

export default function ProcessForm({ zoneId, zoneName, zoneType, onClose, onSuccess }: ProcessFormProps) {
  const [formData, setFormData] = useState<ProcessRequest>({
    zone_id: zoneId,
    process_name: '',
    model_id: 'yolo_v8',
    start_time: '',
    end_time: '',
    video_path: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const { createProcess, loading } = useProcesses();

  const handleInputChange = (field: keyof ProcessRequest, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpiar error del campo cuando el usuario empiece a escribir
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.process_name.trim()) {
      newErrors.process_name = 'El nombre del proceso es requerido';
    }

    if (!formData.model_id.trim()) {
      newErrors.model_id = 'El ID del modelo es requerido';
    }

    if (!formData.video_path.trim()) {
      newErrors.video_path = 'La ruta del video es requerida';
    }

    if (!formData.start_time) {
      newErrors.start_time = 'La hora de inicio es requerida';
    }

    if (!formData.end_time) {
      newErrors.end_time = 'La hora de fin es requerida';
    }

    // Validar que start_time sea anterior a end_time
    if (formData.start_time && formData.end_time) {
      const startDate = new Date(formData.start_time);
      const endDate = new Date(formData.end_time);
      
      if (startDate >= endDate) {
        newErrors.end_time = 'La hora de fin debe ser posterior a la hora de inicio';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    // Convertir fechas del formato datetime-local al formato esperado por el API
    const processData = {
      ...formData,
      start_time: convertToApiDateTimeFormat(formData.start_time),
      end_time: convertToApiDateTimeFormat(formData.end_time)
    };

    const success = await createProcess(processData);
    
    if (success) {
      onSuccess(`Proceso "${formData.process_name}" creado exitosamente para la zona "${zoneName}"`);
      onClose();
    }
  };

  const convertToApiDateTimeFormat = (dateTimeLocal: string): string => {
    if (!dateTimeLocal) return '';
    // Convertir de "YYYY-MM-DDTHH:MM" a "YYYY-MM-DD HH:MM:SS"
    return dateTimeLocal.replace('T', ' ') + ':00';
  };

  const formatDateTimeLocal = (dateTime: string) => {
    if (!dateTime) return '';
    // Si viene del API en formato "YYYY-MM-DD HH:MM:SS", convertir a "YYYY-MM-DDTHH:MM"
    if (dateTime.includes(' ')) {
      return dateTime.slice(0, 16).replace(' ', 'T');
    }
    // Si ya está en formato datetime-local, devolverlo tal como está
    const date = new Date(dateTime);
    return date.toISOString().slice(0, 16);
  };

  const getCurrentDateTime = () => {
    const now = new Date();
    return now.toISOString().slice(0, 16);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Play className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Crear Proceso de Análisis</h2>
              <p className="text-sm text-gray-600">
                Zona: <span className="font-medium">{zoneName}</span> ({zoneType})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Información del Proceso */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Settings className="h-5 w-5 mr-2 text-gray-600" />
              Información del Proceso
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="process_name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre del Proceso *
                </label>
                <input
                  type="text"
                  id="process_name"
                  value={formData.process_name}
                  onChange={(e) => handleInputChange('process_name', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.process_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Ej: Análisis de tráfico matutino"
                />
                {errors.process_name && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.process_name}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="model_id" className="block text-sm font-medium text-gray-700 mb-1">
                  Modelo de IA *
                </label>
                <select
                  id="model_id"
                  value={formData.model_id}
                  onChange={(e) => handleInputChange('model_id', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.model_id ? 'border-red-300' : 'border-gray-300'
                  }`}
                >
                  <option value="yolo_v8">YOLO v8</option>
                  <option value="yolo_v7">YOLO v7</option>
                  <option value="yolo_v5">YOLO v5</option>
                  <option value="yolo11s.pt">YOLO11s.pt</option>
                  <option value="detectron2">Detectron2</option>
                  <option value="custom">Modelo Personalizado</option>
                </select>
                {errors.model_id && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.model_id}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Información del Video */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <FileVideo className="h-5 w-5 mr-2 text-gray-600" />
              Información del Video
            </h3>
            
            <div>
              <label htmlFor="video_path" className="block text-sm font-medium text-gray-700 mb-1">
                Ruta del Video *
              </label>
              <input
                type="text"
                id="video_path"
                value={formData.video_path}
                onChange={(e) => handleInputChange('video_path', e.target.value)}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                  errors.video_path ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="Ej: /videos/entrada_principal_2024.mp4"
              />
              {errors.video_path && (
                <p className="mt-1 text-sm text-red-600 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.video_path}
                </p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Ingresa la ruta completa del archivo de video a procesar
              </p>
            </div>
          </div>

          {/* Horarios de Procesamiento */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <Calendar className="h-5 w-5 mr-2 text-gray-600" />
              Horarios de Procesamiento
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="start_time" className="block text-sm font-medium text-gray-700 mb-1">
                  Hora de Inicio *
                </label>
                <input
                  type="datetime-local"
                  id="start_time"
                  value={formatDateTimeLocal(formData.start_time)}
                  onChange={(e) => handleInputChange('start_time', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.start_time ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.start_time && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.start_time}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="end_time" className="block text-sm font-medium text-gray-700 mb-1">
                  Hora de Fin *
                </label>
                <input
                  type="datetime-local"
                  id="end_time"
                  value={formatDateTimeLocal(formData.end_time)}
                  onChange={(e) => handleInputChange('end_time', e.target.value)}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                    errors.end_time ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {errors.end_time && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-4 w-4 mr-1" />
                    {errors.end_time}
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => {
                  const now = getCurrentDateTime();
                  handleInputChange('start_time', now);
                }}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                Ahora
              </button>
              <button
                type="button"
                onClick={() => {
                  const now = new Date();
                  now.setHours(now.getHours() + 1);
                  handleInputChange('end_time', now.toISOString().slice(0, 16));
                }}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
              >
                +1 hora
              </button>
            </div>
          </div>

          {/* Botones */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creando...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" />
                  Crear Proceso
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
