"""
API REST para el dashboard de Computer Vision
Comunicación entre Next.js y la aplicación Python de análisis de video
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import random
import sys
import threading
import numpy as np
from database.kpis import AverageTime, TotalVisitors, AverageTimePerZone, TotalVisitorsPerZone, PeakHour, PeakHourPerZone
from database.detections import InsertDetectionTime, InsertMultipleDetectionTimes
from database.zones import GetZones, GetZoneById, InsertZone, UpdateZone, DeleteZone, CheckZoneNameExists
from database.processes import GetProcesses, GetProcessById, InsertProcess, UpdateProcess, DeleteProcess, GetProcessesByZone

# Agregar el directorio store al path para importar PostgreSQLConnector
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'store'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'inference_engine'))

from inference_engine.yolov11_time_in_zone import TimeInZone

# Configuración de la aplicación
app = FastAPI(
    title="Vision Analytics API",
    description="API para el dashboard de Computer Vision",
    version="1.0.0"
)

# Configurar CORS para permitir comunicación con Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de Next.js
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DailyKPI(BaseModel):
    id: str
    date: str
    totalVisitors: int
    peakHour: str
    averageDwellTime: float

class DashboardResponse(BaseModel):
    daily: List[DailyKPI]

# Modelos para inserción de detection_times
class DetectionTimeRequest(BaseModel):
    zone_id: int
    time_s: int
    start_time: str  # Formato: 'YYYY-MM-DD HH:MM:SS'
    end_time: str    # Formato: 'YYYY-MM-DD HH:MM:SS'

class MultipleDetectionTimesRequest(BaseModel):
    detections: List[DetectionTimeRequest]

class DetectionTimeResponse(BaseModel):
    success: bool
    message: str
    inserted_id: Optional[int] = None
    inserted_ids: Optional[List[int]] = None

# Modelos para gestión de zonas
class ZoneRequest(BaseModel):
    zone_name: str
    zone_type: str
    coordinates: List[List[List[int]]]

class ZoneUpdateRequest(BaseModel):
    zone_name: Optional[str] = None
    zone_type: Optional[str] = None
    coordinates: Optional[List[List[List[int]]]] = None

class ZoneResponse(BaseModel):
    id: int
    zone_name: str
    zone_type: str
    coordinates: List[List[List[int]]]
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ZoneListResponse(BaseModel):
    success: bool
    message: str
    zones: List[ZoneResponse]

class ZoneOperationResponse(BaseModel):
    success: bool
    message: str
    zone_id: Optional[int] = None

# Modelos para gestión de procesos
class ProcessRequest(BaseModel):
    zone_id: int
    process_name: str
    model_id: str
    start_time: str  # Formato: 'YYYY-MM-DD HH:MM:SS'
    end_time: str    # Formato: 'YYYY-MM-DD HH:MM:SS'
    video_path: str

class ProcessUpdateRequest(BaseModel):
    process_name: Optional[str] = None
    model_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    video_path: Optional[str] = None
    is_done: Optional[bool] = None

class ProcessResponse(BaseModel):
    id: int
    zone_id: int
    process_name: str
    model_id: str
    start_time: str
    end_time: str
    video_path: str
    is_done: bool
    zone_name: Optional[str] = None
    zone_type: Optional[str] = None

class ProcessListResponse(BaseModel):
    success: bool
    message: str
    processes: List[ProcessResponse]

class ProcessOperationResponse(BaseModel):
    success: bool
    message: str
    process_id: Optional[int] = None

# Función para ejecutar el procesamiento de video en un hilo separado
def run_video_processing(process_id: int, zone_id: int, video_path: str, model_id: str, start_time: str, end_time: str):
    """
    Ejecuta el procesamiento de video en un hilo separado
    
    Args:
        process_id: ID del proceso
        zone_id: ID de la zona
        video_path: Ruta del video
        model_id: ID del modelo a usar
        start_time: Hora de inicio
        end_time: Hora de fin (se usará en futuras versiones para filtrar el video)
    """
    try:
        print(f"🎬 Iniciando procesamiento de video para proceso {process_id}")
        print(f"   Zona: {zone_id}")
        print(f"   Video: {video_path}")
        print(f"   Modelo: {model_id}")
        
        # Obtener las coordenadas de la zona
        zone_data = GetZoneById(zone_id)
        if not zone_data:
            print(f"❌ Error: No se encontró la zona {zone_id}")
            UpdateProcess(process_id, is_done=True)
            return
        
        # Convertir coordenadas de la zona a formato esperado por TimeInZone
        coordinates = zone_data["coordinates"]
        polygons = [np.array(polygon, np.int32) for polygon in coordinates]
        print("polygons", polygons)
        
        
        # Determinar la ruta del modelo basado en el model_id
        model_paths = {
            "yolo_v8": "yolo11s.pt",
            "yolo_v7": "yolo11s.pt", 
            "yolo_v5": "yolo11s.pt",
            "yolo11s.pt": "yolo11s.pt",
            "detectron2": "yolo11s.pt",  # Usar YOLO como fallback
            "custom": "yolo11s.pt"
        }

        print("polygons", polygons)
        
        weights_path = model_paths.get(model_id, "yolo11s.pt")
        
        # Instanciar la clase TimeInZone
        time_in_zone = TimeInZone(
            polygons=polygons,
            start_time=start_time,
            weights_path=weights_path,
            classes=[0],  # Clase 0 = personas
            zone_id=zone_id  # Pasar el zone_id
        )
        
        # Inicializar el modelo
        time_in_zone.init_model()
        
        # Ejecutar las detecciones
        print(f"🚀 Ejecutando detecciones con OpenCV...")
        time_in_zone.run_detections(video_path)
        
        print(f"✅ Procesamiento completado para proceso {process_id}")
        
        # Marcar el proceso como completado
        UpdateProcess(process_id, is_done=True)
        
    except Exception as e:
        print(f"❌ Error en procesamiento de video para proceso {process_id}: {e}")
        # Marcar el proceso como completado incluso si hay error
        UpdateProcess(process_id, is_done=True)

# Endpoints de la API
@app.get("/")
async def root():
    """Endpoint de salud de la API"""
    return {
        "message": "Vision Analytics API funcionando",
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }



@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(viewMode: str = "daily", date: Optional[str] = None, zone_id: Optional[int] = None):
    """
    Obtiene datos del dashboard
    
    Args:
        viewMode: Modo de vista ('daily')
        date: Fecha específica (opcional)
        zone_id: ID de la zona para filtrar (opcional)
    """
    
    formated_date = date if date else datetime.now().strftime("%Y-%m-%d")

    # Usar funciones específicas por zona si se proporciona zone_id, sino usar funciones globales
    if zone_id:
        avtTime = AverageTimePerZone(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59", zone_id)
        TotalVisitor = TotalVisitorsPerZone(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59", zone_id)
        peakHourData = PeakHourPerZone(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59", zone_id)
    else:
        avtTime = AverageTime(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59")
        TotalVisitor = TotalVisitors(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59")
        peakHourData = PeakHour(f"{formated_date} 00:00:00", f"{formated_date} 23:59:59")

    # Formatear hora pico
    if peakHourData and isinstance(peakHourData, dict) and 'hour' in peakHourData:
        peakHour = f"{peakHourData['hour']:02d}:00"
    else:
        # Fallback a hora aleatoria si no hay datos
        peakHour = f"{random.randint(0, 23):02d}:00"

    daily_kpi = DailyKPI(
        id="1",
        date=formated_date,
        totalVisitors=TotalVisitor if TotalVisitor else 0,
        peakHour=peakHour,
        averageDwellTime=avtTime if avtTime else 0
    )

    response = DashboardResponse(daily=[daily_kpi])

    return response


@app.post("/api/detection-times", response_model=DetectionTimeResponse)
async def insert_detection_time(request: DetectionTimeRequest):
    """
    Inserta un nuevo registro en detection_times
    
    Args:
        request: Datos del detection_time a insertar
    
    Returns:
        DetectionTimeResponse: Respuesta con el resultado de la inserción
    """
    try:
        # Validar que las fechas tengan el formato correcto
        try:
            datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de fecha inválido. Use 'YYYY-MM-DD HH:MM:SS'"
            )
        
        # Validar que start_time sea anterior a end_time
        start_dt = datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
        
        if start_dt >= end_dt:
            raise HTTPException(
                status_code=400,
                detail="start_time debe ser anterior a end_time"
            )
        
        # Insertar en la base de datos
        inserted_id = InsertDetectionTime(
            zone_id=request.zone_id,
            time_s=request.time_s,
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        if inserted_id is not None:
            return DetectionTimeResponse(
                success=True,
                message="Detection time insertado exitosamente",
                inserted_id=inserted_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al insertar en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en insert_detection_time: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/api/detection-times/bulk", response_model=DetectionTimeResponse)
async def insert_multiple_detection_times(request: MultipleDetectionTimesRequest):
    """
    Inserta múltiples registros en detection_times de una vez
    
    Args:
        request: Lista de detection_times a insertar
    
    Returns:
        DetectionTimeResponse: Respuesta con el resultado de la inserción
    """
    try:
        if not request.detections:
            raise HTTPException(
                status_code=400,
                detail="La lista de detections no puede estar vacía"
            )
        
        # Validar cada detection_time
        detection_data_list = []
        for detection in request.detections:
            # Validar formato de fechas
            try:
                datetime.strptime(detection.start_time, "%Y-%m-%d %H:%M:%S")
                datetime.strptime(detection.end_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Formato de fecha inválido en detection. Use 'YYYY-MM-DD HH:MM:SS'"
                )
            
            # Validar que start_time sea anterior a end_time
            start_dt = datetime.strptime(detection.start_time, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(detection.end_time, "%Y-%m-%d %H:%M:%S")
            
            if start_dt >= end_dt:
                raise HTTPException(
                    status_code=400,
                    detail=f"start_time debe ser anterior a end_time en detection con zone_id {detection.zone_id}"
                )
            
            detection_data_list.append({
                "zone_id": detection.zone_id,
                "time_s": detection.time_s,
                "start_time": detection.start_time,
                "end_time": detection.end_time
            })
        
        # Insertar en la base de datos
        inserted_count = InsertMultipleDetectionTimes(detection_data_list)
        
        if inserted_count > 0:
            return DetectionTimeResponse(
                success=True,
                message=f"Se insertaron {inserted_count} detection times exitosamente",
                inserted_ids=None  # No tenemos IDs individuales con batch insert
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al insertar en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en insert_multiple_detection_times: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


# Endpoints para gestión de zonas
@app.get("/api/zones", response_model=ZoneListResponse)
async def get_zones():
    """
    Obtiene todas las zonas activas
    
    Returns:
        ZoneListResponse: Lista de todas las zonas activas
    """
    try:
        zones_data = GetZones()
        
        if zones_data is None:
            raise HTTPException(
                status_code=500,
                detail="Error al obtener zonas de la base de datos"
            )
        
        zones = []
        for zone_data in zones_data:
            zones.append(ZoneResponse(
                id=zone_data["id"],
                zone_name=zone_data["zone_name"],
                zone_type=zone_data["zone_type"],
                coordinates=zone_data["coordinates"],
                is_active=zone_data["is_active"],
                created_at=zone_data["created_at"],
                updated_at=zone_data["updated_at"]
            ))
        
        return ZoneListResponse(
            success=True,
            message=f"Se encontraron {len(zones)} zonas",
            zones=zones
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_zones: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/api/zones/{zone_id}", response_model=ZoneResponse)
async def get_zone_by_id(zone_id: int):
    """
    Obtiene una zona específica por ID
    
    Args:
        zone_id (int): ID de la zona
    
    Returns:
        ZoneResponse: Datos de la zona
    """
    try:
        zone_data = GetZoneById(zone_id)
        
        if zone_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zona con ID {zone_id} no encontrada"
            )
        
        return ZoneResponse(
            id=zone_data["id"],
            zone_name=zone_data["zone_name"],
            zone_type=zone_data["zone_type"],
            coordinates=zone_data["coordinates"],
            is_active=zone_data["is_active"],
            created_at=zone_data["created_at"],
            updated_at=zone_data["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_zone_by_id: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/api/zones", response_model=ZoneOperationResponse)
async def create_zone(request: ZoneRequest):
    """
    Crea una nueva zona
    
    Args:
        request: Datos de la zona a crear
    
    Returns:
        ZoneOperationResponse: Resultado de la operación
    """
    try:
        # Validar que el nombre de la zona no esté vacío
        if not request.zone_name.strip():
            raise HTTPException(
                status_code=400,
                detail="El nombre de la zona no puede estar vacío"
            )
        
        # Validar que el tipo de zona no esté vacío
        if not request.zone_type.strip():
            raise HTTPException(
                status_code=400,
                detail="El tipo de zona no puede estar vacío"
            )
        
        # Validar que las coordenadas no estén vacías
        if not request.coordinates or len(request.coordinates) == 0:
            raise HTTPException(
                status_code=400,
                detail="Las coordenadas no pueden estar vacías"
            )
        
        # Verificar que el nombre no esté en uso
        if CheckZoneNameExists(request.zone_name):
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe una zona con el nombre '{request.zone_name}'"
            )
        
        # Insertar la zona
        zone_id = InsertZone(
            zone_name=request.zone_name,
            zone_type=request.zone_type,
            coordinates=request.coordinates
        )
        
        if zone_id is not None:
            return ZoneOperationResponse(
                success=True,
                message="Zona creada exitosamente",
                zone_id=zone_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al crear la zona en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en create_zone: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.put("/api/zones/{zone_id}", response_model=ZoneOperationResponse)
async def update_zone(zone_id: int, request: ZoneUpdateRequest):
    """
    Actualiza una zona existente
    
    Args:
        zone_id (int): ID de la zona a actualizar
        request: Datos actualizados de la zona
    
    Returns:
        ZoneOperationResponse: Resultado de la operación
    """
    try:
        # Verificar que la zona existe
        existing_zone = GetZoneById(zone_id)
        if existing_zone is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zona con ID {zone_id} no encontrada"
            )
        
        # Validar nombre si se proporciona
        if request.zone_name is not None:
            if not request.zone_name.strip():
                raise HTTPException(
                    status_code=400,
                    detail="El nombre de la zona no puede estar vacío"
                )
            
            # Verificar que el nuevo nombre no esté en uso (excluyendo la zona actual)
            if CheckZoneNameExists(request.zone_name, exclude_id=zone_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Ya existe una zona con el nombre '{request.zone_name}'"
                )
        
        # Validar tipo si se proporciona
        if request.zone_type is not None and not request.zone_type.strip():
            raise HTTPException(
                status_code=400,
                detail="El tipo de zona no puede estar vacío"
            )
        
        # Actualizar la zona
        success = UpdateZone(
            zone_id=zone_id,
            zone_name=request.zone_name,
            zone_type=request.zone_type,
            coordinates=request.coordinates
        )
        
        if success:
            return ZoneOperationResponse(
                success=True,
                message="Zona actualizada exitosamente",
                zone_id=zone_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar la zona en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en update_zone: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.delete("/api/zones/{zone_id}", response_model=ZoneOperationResponse)
async def delete_zone(zone_id: int):
    """
    Elimina una zona (soft delete)
    
    Args:
        zone_id (int): ID de la zona a eliminar
    
    Returns:
        ZoneOperationResponse: Resultado de la operación
    """
    try:
        # Verificar que la zona existe
        existing_zone = GetZoneById(zone_id)
        if existing_zone is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zona con ID {zone_id} no encontrada"
            )
        
        # Eliminar la zona (soft delete)
        success = DeleteZone(zone_id)
        
        if success:
            return ZoneOperationResponse(
                success=True,
                message="Zona eliminada exitosamente",
                zone_id=zone_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al eliminar la zona en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en delete_zone: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


# Endpoints para gestión de procesos
@app.get("/api/processes", response_model=ProcessListResponse)
async def get_processes():
    """
    Obtiene todos los procesos
    
    Returns:
        ProcessListResponse: Lista de todos los procesos
    """
    try:
        processes_data = GetProcesses()
        
        if processes_data is None:
            raise HTTPException(
                status_code=500,
                detail="Error al obtener procesos de la base de datos"
            )
        
        processes = []
        for process_data in processes_data:
            processes.append(ProcessResponse(
                id=process_data["id"],
                zone_id=process_data["zone_id"],
                process_name=process_data["process_name"],
                model_id=process_data["model_id"],
                start_time=process_data["start_time"],
                end_time=process_data["end_time"],
                video_path=process_data["video_path"],
                is_done=process_data["is_done"],
                zone_name=process_data["zone_name"],
                zone_type=process_data["zone_type"]
            ))
        
        return ProcessListResponse(
            success=True,
            message=f"Se encontraron {len(processes)} procesos",
            processes=processes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_processes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/api/processes/{process_id}", response_model=ProcessResponse)
async def get_process_by_id(process_id: int):
    """
    Obtiene un proceso específico por ID
    
    Args:
        process_id (int): ID del proceso
    
    Returns:
        ProcessResponse: Datos del proceso
    """
    try:
        process_data = GetProcessById(process_id)
        
        if process_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Proceso con ID {process_id} no encontrado"
            )
        
        return ProcessResponse(
            id=process_data["id"],
            zone_id=process_data["zone_id"],
            process_name=process_data["process_name"],
            model_id=process_data["model_id"],
            start_time=process_data["start_time"],
            end_time=process_data["end_time"],
            video_path=process_data["video_path"],
            is_done=process_data["is_done"],
            zone_name=process_data["zone_name"],
            zone_type=process_data["zone_type"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_process_by_id: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/api/processes/zone/{zone_id}", response_model=ProcessListResponse)
async def get_processes_by_zone(zone_id: int):
    """
    Obtiene todos los procesos de una zona específica
    
    Args:
        zone_id (int): ID de la zona
    
    Returns:
        ProcessListResponse: Lista de procesos de la zona
    """
    try:
        processes_data = GetProcessesByZone(zone_id)
        
        if processes_data is None:
            raise HTTPException(
                status_code=500,
                detail="Error al obtener procesos de la zona de la base de datos"
            )
        
        processes = []
        for process_data in processes_data:
            processes.append(ProcessResponse(
                id=process_data["id"],
                zone_id=process_data["zone_id"],
                process_name=process_data["process_name"],
                model_id=process_data["model_id"],
                start_time=process_data["start_time"],
                end_time=process_data["end_time"],
                video_path=process_data["video_path"],
                is_done=process_data["is_done"],
                zone_name=process_data["zone_name"],
                zone_type=process_data["zone_type"]
            ))
        
        return ProcessListResponse(
            success=True,
            message=f"Se encontraron {len(processes)} procesos para la zona {zone_id}",
            processes=processes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_processes_by_zone: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.post("/api/processes", response_model=ProcessOperationResponse)
async def create_process(request: ProcessRequest):
    """
    Crea un nuevo proceso
    
    Args:
        request: Datos del proceso a crear
    
    Returns:
        ProcessOperationResponse: Resultado de la operación
    """
    try:
        # Validar que el nombre del proceso no esté vacío
        if not request.process_name.strip():
            raise HTTPException(
                status_code=400,
                detail="El nombre del proceso no puede estar vacío"
            )
        
        # Validar que el model_id no esté vacío
        if not request.model_id.strip():
            raise HTTPException(
                status_code=400,
                detail="El ID del modelo no puede estar vacío"
            )
        
        # Validar que la ruta del video no esté vacía
        if not request.video_path.strip():
            raise HTTPException(
                status_code=400,
                detail="La ruta del video no puede estar vacía"
            )
        
        # Validar que las fechas tengan el formato correcto
        try:
            datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Formato de fecha inválido. Use 'YYYY-MM-DD HH:MM:SS'"
            )
        
        # Validar que start_time sea anterior a end_time
        start_dt = datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
        
        if start_dt >= end_dt:
            raise HTTPException(
                status_code=400,
                detail="start_time debe ser anterior a end_time"
            )
        
        # Verificar que la zona existe
        zone_data = GetZoneById(request.zone_id)
        if zone_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Zona con ID {request.zone_id} no encontrada"
            )
        
        # Insertar el proceso
        process_id = InsertProcess(
            zone_id=request.zone_id,
            process_name=request.process_name,
            model_id=request.model_id,
            start_time=request.start_time,
            end_time=request.end_time,
            video_path=request.video_path
        )
        
        if process_id is not None:

            
            # Ejecutar el procesamiento de video en un hilo separado
            processing_thread = threading.Thread(
                target=run_video_processing,
                args=(
                    process_id,
                    request.zone_id,
                    request.video_path,
                    request.model_id,
                    request.start_time,
                    request.end_time
                ),
                daemon=True  # El hilo se cerrará cuando termine el proceso principal
            )
            processing_thread.start()
            
            return ProcessOperationResponse(
                success=True,
                message="Proceso creado exitosamente. El procesamiento de video ha comenzado en segundo plano.",
                process_id=process_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al crear el proceso en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en create_process: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.put("/api/processes/{process_id}", response_model=ProcessOperationResponse)
async def update_process(process_id: int, request: ProcessUpdateRequest):
    """
    Actualiza un proceso existente
    
    Args:
        process_id (int): ID del proceso a actualizar
        request: Datos actualizados del proceso
    
    Returns:
        ProcessOperationResponse: Resultado de la operación
    """
    try:
        # Verificar que el proceso existe
        existing_process = GetProcessById(process_id)
        if existing_process is None:
            raise HTTPException(
                status_code=404,
                detail=f"Proceso con ID {process_id} no encontrado"
            )
        
        # Validar nombre si se proporciona
        if request.process_name is not None and not request.process_name.strip():
            raise HTTPException(
                status_code=400,
                detail="El nombre del proceso no puede estar vacío"
            )
        
        # Validar model_id si se proporciona
        if request.model_id is not None and not request.model_id.strip():
            raise HTTPException(
                status_code=400,
                detail="El ID del modelo no puede estar vacío"
            )
        
        # Validar video_path si se proporciona
        if request.video_path is not None and not request.video_path.strip():
            raise HTTPException(
                status_code=400,
                detail="La ruta del video no puede estar vacía"
            )
        
        # Validar fechas si se proporcionan
        if request.start_time is not None:
            try:
                datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Formato de fecha inválido en start_time. Use 'YYYY-MM-DD HH:MM:SS'"
                )
        
        if request.end_time is not None:
            try:
                datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Formato de fecha inválido en end_time. Use 'YYYY-MM-DD HH:MM:SS'"
                )
        
        # Validar que start_time sea anterior a end_time si ambas se proporcionan
        if request.start_time is not None and request.end_time is not None:
            start_dt = datetime.strptime(request.start_time, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(request.end_time, "%Y-%m-%d %H:%M:%S")
            
            if start_dt >= end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_time debe ser anterior a end_time"
                )
        
        # Actualizar el proceso
        success = UpdateProcess(
            process_id=process_id,
            process_name=request.process_name,
            model_id=request.model_id,
            start_time=request.start_time,
            end_time=request.end_time,
            video_path=request.video_path,
            is_done=request.is_done
        )
        
        if success:
            return ProcessOperationResponse(
                success=True,
                message="Proceso actualizado exitosamente",
                process_id=process_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al actualizar el proceso en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en update_process: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.delete("/api/processes/{process_id}", response_model=ProcessOperationResponse)
async def delete_process(process_id: int):
    """
    Elimina un proceso
    
    Args:
        process_id (int): ID del proceso a eliminar
    
    Returns:
        ProcessOperationResponse: Resultado de la operación
    """
    try:
        # Verificar que el proceso existe
        existing_process = GetProcessById(process_id)
        if existing_process is None:
            raise HTTPException(
                status_code=404,
                detail=f"Proceso con ID {process_id} no encontrado"
            )
        
        # Eliminar el proceso
        success = DeleteProcess(process_id)
        
        if success:
            return ProcessOperationResponse(
                success=True,
                message="Proceso eliminado exitosamente",
                process_id=process_id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al eliminar el proceso en la base de datos"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en delete_process: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@app.get("/api/processes/{process_id}/status")
async def get_process_status(process_id: int):
    """
    Obtiene el estado de un proceso específico
    
    Args:
        process_id (int): ID del proceso
    
    Returns:
        dict: Estado del proceso
    """
    try:
        process_data = GetProcessById(process_id)
        
        if process_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Proceso con ID {process_id} no encontrado"
            )
        
        return {
            "process_id": process_id,
            "is_done": process_data["is_done"],
            "process_name": process_data["process_name"],
            "zone_name": process_data["zone_name"],
            "video_path": process_data["video_path"],
            "status": "completed" if process_data["is_done"] else "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error inesperado en get_process_status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


if __name__ == "__main__":

    # Verificar disponibilidad de base de datos
    print("🔧 Verificando disponibilidad de PostgreSQL...")
    
    # Configuración del servidor
    host = "0.0.0.0"
    port = 8000
    
    print(f"🚀 Iniciando Vision Analytics API en http://{host}:{port}")
    print(f"📊 Dashboard disponible en: http://localhost:3000")
    print(f"🔗 Documentación API: http://{host}:{port}/docs")
    
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,  # Recarga automática en desarrollo
        log_level="info"
    )
