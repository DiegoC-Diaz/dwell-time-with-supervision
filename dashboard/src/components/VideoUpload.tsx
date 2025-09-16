'use client';

import React, { useRef, useState, useCallback } from 'react';
import { Upload, Play, Camera, X, FileVideo } from 'lucide-react';

interface VideoUploadProps {
  onFrameExtracted?: (imageUrl: string) => void;
  onVideoLoaded?: (videoUrl: string) => void;
  className?: string;
}

const VideoUpload: React.FC<VideoUploadProps> = ({
  onFrameExtracted,
  onVideoLoaded,
  className = ''
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  const [videoUrl, setVideoUrl] = useState<string>('');
  const [extractedFrameUrl, setExtractedFrameUrl] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  const handleFileSelect = useCallback((file: File) => {
    if (!file.type.startsWith('video/')) {
      setError('Por favor selecciona un archivo de video válido');
      return;
    }

    if (file.size > 100 * 1024 * 1024) { // 100MB limit
      setError('El archivo es demasiado grande. Máximo 100MB');
      return;
    }

    setError('');
    setIsLoading(true);

    const url = URL.createObjectURL(file);
    setVideoUrl(url);
    
    if (onVideoLoaded) {
      onVideoLoaded(url);
    }

    // Cargar video y extraer primer frame
    const video = document.createElement('video');
    video.crossOrigin = 'anonymous';
    video.preload = 'metadata';

    video.onloadedmetadata = () => {
      video.currentTime = 0; // Ir al primer frame
    };

    video.onseeked = () => {
      try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        if (!ctx) {
          throw new Error('No se pudo obtener el contexto del canvas');
        }

        // Configurar canvas con las dimensiones del video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Dibujar el frame actual del video en el canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convertir a imagen
        const frameUrl = canvas.toDataURL('image/png');
        setExtractedFrameUrl(frameUrl);
        
        if (onFrameExtracted) {
          onFrameExtracted(frameUrl);
        }

        setIsLoading(false);
      } catch (err) {
        console.error('Error al extraer frame:', err);
        setError('Error al extraer el primer frame del video');
        setIsLoading(false);
      }
    };

    video.onerror = () => {
      setError('Error al cargar el video');
      setIsLoading(false);
    };

    video.src = url;
  }, [onFrameExtracted, onVideoLoaded]);

  const handleFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  }, [handleFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const clearVideo = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
    if (extractedFrameUrl) {
      URL.revokeObjectURL(extractedFrameUrl);
    }
    setVideoUrl('');
    setExtractedFrameUrl('');
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const extractFrameAtTime = (time: number) => {
    if (!videoRef.current) return;

    const video = videoRef.current;
    video.currentTime = time;

    video.onseeked = () => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext('2d');
      
      if (!canvas || !ctx) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      const frameUrl = canvas.toDataURL('image/png');
      setExtractedFrameUrl(frameUrl);
      
      if (onFrameExtracted) {
        onFrameExtracted(frameUrl);
      }
    };
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Área de carga */}
      {!videoUrl && (
        <div
          className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
            dragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onClick={handleClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="video/*"
            onChange={handleFileInputChange}
            className="hidden"
          />
          
          <div className="space-y-4">
            <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center">
              <FileVideo className="w-8 h-8 text-gray-400" />
            </div>
            
            <div>
              <p className="text-lg font-medium text-gray-900">
                Cargar Video
              </p>
              <p className="text-sm text-gray-500">
                Arrastra y suelta un archivo de video aquí, o haz clic para seleccionar
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Formatos soportados: MP4, AVI, MOV, WebM (máx. 100MB)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Estado de carga */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-sm text-gray-600">Procesando video...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <X className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Video cargado */}
      {videoUrl && !isLoading && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Video Cargado</h3>
            <button
              onClick={clearVideo}
              className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
            >
              <X className="h-4 w-4" />
              Limpiar
            </button>
          </div>

          {/* Reproductor de video */}
          <div className="relative">
            <video
              ref={videoRef}
              src={videoUrl}
              controls
              className="w-full max-h-64 rounded-lg"
              onLoadedMetadata={() => {
                if (videoRef.current) {
                  extractFrameAtTime(0); // Extraer primer frame automáticamente
                }
              }}
            />
            
            {/* Controles personalizados para extraer frame */}
            <div className="absolute bottom-2 left-2 bg-black bg-opacity-50 rounded-lg p-2">
              <button
                onClick={() => {
                  if (videoRef.current) {
                    extractFrameAtTime(videoRef.current.currentTime);
                  }
                }}
                className="flex items-center gap-2 px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <Camera className="h-4 w-4" />
                Extraer Frame
              </button>
            </div>
          </div>

          {/* Frame extraído */}
          {extractedFrameUrl && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Camera className="h-5 w-5 text-green-600" />
                <h4 className="text-md font-medium text-gray-900">Frame Extraído</h4>
              </div>
              
              <div className="relative">
                <img
                  src={extractedFrameUrl}
                  alt="Frame extraído"
                  className="w-full max-h-64 object-contain rounded-lg border border-gray-200"
                />
                
                <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded text-xs">
                  Listo para dibujar polígonos
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Canvas oculto para extraer frames */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default VideoUpload;
