'use client';

import React, { useRef, useEffect, useState, useCallback } from 'react';
import { X, Download, Save, Trash2, RotateCcw } from 'lucide-react';

interface Point {
  x: number;
  y: number;
}

interface Polygon {
  id: string;
  points: Point[];
  isComplete: boolean;
}

interface PolygonCanvasProps {
  imageUrl?: string;
  onPolygonsChange?: (polygons: Point[][]) => void;
  onSaveZone?: (zoneName: string, zoneType: string, coordinates: Point[][]) => void;
  className?: string;
}

const PolygonCanvas: React.FC<PolygonCanvasProps> = ({
  imageUrl,
  onPolygonsChange,
  onSaveZone,
  className = ''
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const [polygons, setPolygons] = useState<Polygon[]>([]);
  const [currentPolygon, setCurrentPolygon] = useState<Point[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const [scale, setScale] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState<Point>({ x: 0, y: 0 });
  const [zoneName, setZoneName] = useState('');
  const [zoneType, setZoneType] = useState('detection');
  const [showSaveDialog, setShowSaveDialog] = useState(false);

  // Cargar imagen cuando cambie la URL
  useEffect(() => {
    if (imageUrl) {
      loadImage();
    }
  }, [imageUrl]);

  // Notificar cambios en polígonos
  useEffect(() => {
    if (onPolygonsChange) {
      const completedPolygons = polygons
        .filter(p => p.isComplete)
        .map(p => p.points);
      onPolygonsChange(completedPolygons);
    }
  }, [polygons, onPolygonsChange]);

  const loadImage = () => {
    if (!imageUrl) return;

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      imageRef.current = img;
      drawCanvas();
    };
    img.src = imageUrl;
  };

  const drawCanvas = useCallback(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext('2d');
    const img = imageRef.current;

    if (!canvas || !ctx || !img) return;

    // Configurar tamaño del canvas
    const container = canvas.parentElement;
    if (container) {
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
    }

    // Limpiar canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Calcular dimensiones de la imagen escalada
    const imgAspect = img.width / img.height;
    const canvasAspect = canvas.width / canvas.height;

    let drawWidth, drawHeight, drawX, drawY;

    if (imgAspect > canvasAspect) {
      drawWidth = canvas.width;
      drawHeight = canvas.width / imgAspect;
      drawX = 0;
      drawY = (canvas.height - drawHeight) / 2;
    } else {
      drawWidth = canvas.height * imgAspect;
      drawHeight = canvas.height;
      drawX = (canvas.width - drawWidth) / 2;
      drawY = 0;
    }

    // Aplicar escala y offset
    const scaledWidth = drawWidth * scale;
    const scaledHeight = drawHeight * scale;
    const scaledX = drawX + offset.x;
    const scaledY = drawY + offset.y;

    // Dibujar imagen
    ctx.drawImage(img, scaledX, scaledY, scaledWidth, scaledHeight);

    // Dibujar polígonos completados
    polygons.forEach((polygon, index) => {
      if (polygon.isComplete && polygon.points.length > 0) {
        drawPolygon(ctx, polygon.points, scaledX, scaledY, scaledWidth, scaledHeight, index);
      }
    });

    // Dibujar polígono actual
    if (currentPolygon.length > 0) {
      drawCurrentPolygon(ctx, currentPolygon, scaledX, scaledY, scaledWidth, scaledHeight);
    }
  }, [polygons, currentPolygon, scale, offset]);

  const drawPolygon = (
    ctx: CanvasRenderingContext2D,
    points: Point[],
    imgX: number,
    imgY: number,
    imgWidth: number,
    imgHeight: number,
    polygonIndex: number
  ) => {
    if (points.length < 3) return;

    // Colores diferentes para cada polígono
    const colors = [
      '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', 
      '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6b7280'
    ];
    const color = colors[polygonIndex % colors.length];
    
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.fillStyle = `${color}20`; // 20% opacity
    ctx.lineWidth = 3;

    // Convertir coordenadas de imagen a canvas
    const canvasPoints = points.map(point => ({
      x: imgX + (point.x / imageRef.current!.width) * imgWidth,
      y: imgY + (point.y / imageRef.current!.height) * imgHeight
    }));

    ctx.moveTo(canvasPoints[0].x, canvasPoints[0].y);
    for (let i = 1; i < canvasPoints.length; i++) {
      ctx.lineTo(canvasPoints[i].x, canvasPoints[i].y);
    }
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Dibujar puntos
    canvasPoints.forEach((point, index) => {
      ctx.beginPath();
      ctx.fillStyle = color;
      ctx.arc(point.x, point.y, 5, 0, 2 * Math.PI);
      ctx.fill();
      
      // Dibujar número del punto
      ctx.fillStyle = 'white';
      ctx.font = '12px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(index.toString(), point.x, point.y);
    });

    // Dibujar número del polígono en el centro
    const centerX = canvasPoints.reduce((sum, p) => sum + p.x, 0) / canvasPoints.length;
    const centerY = canvasPoints.reduce((sum, p) => sum + p.y, 0) / canvasPoints.length;
    
    ctx.fillStyle = color;
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(`P${polygonIndex + 1}`, centerX, centerY);
  };

  const drawCurrentPolygon = (
    ctx: CanvasRenderingContext2D,
    points: Point[],
    imgX: number,
    imgY: number,
    imgWidth: number,
    imgHeight: number
  ) => {
    if (points.length === 0) return;

    ctx.beginPath();
    ctx.strokeStyle = '#ef4444';
    ctx.fillStyle = 'rgba(239, 68, 68, 0.2)';
    ctx.lineWidth = 2;

    // Convertir coordenadas
    const canvasPoints = points.map(point => ({
      x: imgX + (point.x / imageRef.current!.width) * imgWidth,
      y: imgY + (point.y / imageRef.current!.height) * imgHeight
    }));

    ctx.moveTo(canvasPoints[0].x, canvasPoints[0].y);
    for (let i = 1; i < canvasPoints.length; i++) {
      ctx.lineTo(canvasPoints[i].x, canvasPoints[i].y);
    }

    // Si hay más de 2 puntos, cerrar el polígono
    if (points.length > 2) {
      ctx.closePath();
      ctx.fill();
    } else {
      ctx.stroke();
    }

    // Dibujar puntos
    canvasPoints.forEach(point => {
      ctx.beginPath();
      ctx.fillStyle = '#ef4444';
      ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  };

  const getImageCoordinates = (canvasX: number, canvasY: number): Point | null => {
    const img = imageRef.current;
    const canvas = canvasRef.current;
    if (!img || !canvas) return null;

    const imgAspect = img.width / img.height;
    const canvasAspect = canvas.width / canvas.height;

    let drawWidth, drawHeight, drawX, drawY;

    if (imgAspect > canvasAspect) {
      drawWidth = canvas.width;
      drawHeight = canvas.width / imgAspect;
      drawX = 0;
      drawY = (canvas.height - drawHeight) / 2;
    } else {
      drawWidth = canvas.height * imgAspect;
      drawHeight = canvas.height;
      drawX = (canvas.width - drawWidth) / 2;
      drawY = 0;
    }

    const scaledWidth = drawWidth * scale;
    const scaledHeight = drawHeight * scale;
    const scaledX = drawX + offset.x;
    const scaledY = drawY + offset.y;

    // Verificar si el clic está dentro de la imagen
    if (canvasX < scaledX || canvasX > scaledX + scaledWidth ||
        canvasY < scaledY || canvasY > scaledY + scaledHeight) {
      return null;
    }

    // Convertir coordenadas de canvas a imagen
    const relativeX = (canvasX - scaledX) / scaledWidth;
    const relativeY = (canvasY - scaledY) / scaledHeight;

    return {
      x: Math.round(relativeX * img.width),
      y: Math.round(relativeY * img.height)
    };
  };

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!imageRef.current) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const canvasX = event.clientX - rect.left;
    const canvasY = event.clientY - rect.top;

    const imageCoords = getImageCoordinates(canvasX, canvasY);
    if (!imageCoords) return;

    setCurrentPolygon(prev => [...prev, imageCoords]);
  };

  const handleCanvasMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (isDragging) {
      const deltaX = event.clientX - lastMousePos.x;
      const deltaY = event.clientY - lastMousePos.y;
      setOffset(prev => ({
        x: prev.x + deltaX,
        y: prev.y + deltaY
      }));
      setLastMousePos({ x: event.clientX, y: event.clientY });
      drawCanvas();
    }
  };

  const handleCanvasMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (event.button === 1 || (event.button === 0 && event.ctrlKey)) {
      // Middle mouse button or Ctrl+click for panning
      setIsDragging(true);
      setLastMousePos({ x: event.clientX, y: event.clientY });
      event.preventDefault();
    }
  };

  const handleCanvasMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (event: React.WheelEvent<HTMLCanvasElement>) => {
    event.preventDefault();
    const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1;
    setScale(prev => Math.max(0.1, Math.min(5, prev * zoomFactor)));
  };

  const completePolygon = () => {
    if (currentPolygon.length < 3) return;

    const newPolygon: Polygon = {
      id: Date.now().toString(),
      points: [...currentPolygon],
      isComplete: true
    };

    setPolygons(prev => [...prev, newPolygon]);
    setCurrentPolygon([]);
  };

  const undoLastPoint = () => {
    if (currentPolygon.length > 0) {
      setCurrentPolygon(prev => prev.slice(0, -1));
    } else if (polygons.length > 0) {
      // Si no hay polígono actual, deshacer el último polígono completo
      setPolygons(prev => prev.slice(0, -1));
    }
  };

  const clearAll = () => {
    setPolygons([]);
    setCurrentPolygon([]);
  };

  const exportPolygons = () => {
    const completedPolygons = polygons
      .filter(p => p.isComplete)
      .map(p => p.points);
    
    const dataStr = JSON.stringify(completedPolygons, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'polygons.json';
    link.click();
    
    URL.revokeObjectURL(url);
  };

  const handleSaveZone = () => {
    if (!zoneName.trim()) {
      alert('Por favor ingresa un nombre para la zona');
      return;
    }

    const completedPolygons = polygons
      .filter(p => p.isComplete)
      .map(p => p.points);

    if (completedPolygons.length === 0) {
      alert('Por favor dibuja al menos un polígono antes de guardar');
      return;
    }

    if (onSaveZone) {
      onSaveZone(zoneName, zoneType, completedPolygons);
      setShowSaveDialog(false);
      setZoneName('');
    }
  };

  // Redibujar cuando cambien las dependencias
  useEffect(() => {
    drawCanvas();
  }, [drawCanvas]);

  return (
    <div className={`flex flex-col ${className}`}>
      {/* Controles */}
      <div className="flex flex-wrap gap-2 p-4 bg-gray-50 border-b">
        <button
          onClick={completePolygon}
          disabled={currentPolygon.length < 3}
          className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Save className="h-4 w-4" />
          Completar Polígono
        </button>
        
        <button
          onClick={undoLastPoint}
          className="flex items-center gap-2 px-3 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
        >
          <RotateCcw className="h-4 w-4" />
          Deshacer
        </button>
        
        <button
          onClick={clearAll}
          className="flex items-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
        >
          <Trash2 className="h-4 w-4" />
          Limpiar Todo
        </button>
        
        <button
          onClick={exportPolygons}
          disabled={polygons.filter(p => p.isComplete).length === 0}
          className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Download className="h-4 w-4" />
          Exportar JSON
        </button>

        <button
          onClick={() => setShowSaveDialog(true)}
          disabled={polygons.filter(p => p.isComplete).length === 0}
          className="flex items-center gap-2 px-3 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          <Save className="h-4 w-4" />
          Guardar Zona
        </button>
      </div>

      {/* Instrucciones */}
      <div className="p-3 bg-blue-50 border-b text-sm text-blue-800">
        <p><strong>Instrucciones para dibujar múltiples polígonos:</strong></p>
        <p>• Haz clic para agregar puntos al polígono actual</p>
        <p>• Presiona "Completar Polígono" cuando hayas terminado (mínimo 3 puntos)</p>
        <p>• Puedes dibujar tantos polígonos como necesites en la misma imagen</p>
        <p>• Cada polígono tendrá un color diferente (P1, P2, P3, etc.)</p>
        <p>• Usa Ctrl+clic o rueda del mouse para hacer pan y zoom</p>
        <p>• Presiona "Deshacer" para eliminar el último punto o polígono</p>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative bg-gray-100 min-h-[600px]">
        {!imageUrl ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <p className="text-lg font-medium">No hay imagen cargada</p>
              <p className="text-sm">Carga un video o imagen para comenzar a dibujar polígonos</p>
            </div>
          </div>
        ) : (
          <canvas
            ref={canvasRef}
            className="w-full h-full cursor-crosshair"
            onClick={handleCanvasClick}
            onMouseMove={handleCanvasMouseMove}
            onMouseDown={handleCanvasMouseDown}
            onMouseUp={handleCanvasMouseUp}
            onWheel={handleWheel}
          />
        )}
      </div>

      {/* Información de polígonos */}
      <div className="p-3 bg-gray-50 border-t">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            Polígonos completados: {polygons.filter(p => p.isComplete).length}
          </span>
          {currentPolygon.length > 0 && (
            <span className="text-sm text-blue-600">
              Puntos en polígono actual: {currentPolygon.length}
            </span>
          )}
        </div>
        
        {/* Lista de polígonos con detalles */}
        {polygons.filter(p => p.isComplete).length > 0 && (
          <div className="space-y-1">
            <p className="text-xs font-medium text-gray-600 mb-1">Detalles de polígonos:</p>
            {polygons.map((polygon, index) => {
              if (!polygon.isComplete) return null;
              const colors = [
                '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', 
                '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6b7280'
              ];
              const color = colors[index % colors.length];
              
              return (
                <div key={polygon.id} className="flex items-center gap-2 text-xs">
                  <div 
                    className="w-3 h-3 rounded-full border"
                    style={{ backgroundColor: color }}
                  ></div>
                  <span className="text-gray-600">
                    Polígono {index + 1}: {polygon.points.length} puntos
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Diálogo de guardar zona */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Guardar Zona</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de la Zona
                </label>
                <input
                  type="text"
                  value={zoneName}
                  onChange={(e) => setZoneName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Ej: Zona de Detección 1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Zona
                </label>
                <select
                  value={zoneType}
                  onChange={(e) => setZoneType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="detection">Detección</option>
                  <option value="counting">Conteo</option>
                  <option value="monitoring">Monitoreo</option>
                </select>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveZone}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Guardar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PolygonCanvas;
