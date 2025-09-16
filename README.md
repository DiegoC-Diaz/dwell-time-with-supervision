# Vision Analytics - Guía de Instalación y Ejecución

## 📋 Descripción del Proyecto

Vision Analytics es una aplicación completa de análisis de video con Computer Vision que incluye:

- **Backend API** (FastAPI + Python): Procesamiento de video con YOLO y análisis de zonas
- **Frontend Dashboard** (Next.js + React): Interfaz web para gestión y visualización
- **Base de Datos** (PostgreSQL): Almacenamiento de métricas, zonas y procesos
- **Herramientas de Administración** (pgAdmin): Gestión visual de la base de datos

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   API Server     │    │   PostgreSQL    │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   Database      │
│   Port: 3000    │    │   Port: 8000     │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   pgAdmin       │
                       │   Port: 8080    │
                       └─────────────────┘
```

## 🚀 Requisitos Previos

### Software Necesario
- **Docker** (versión 20.10 o superior)
- **Docker Compose** (versión 2.0 o superior)
- **Git** (para clonar el repositorio)

### Hardware Recomendado
- **RAM**: Mínimo 8GB (recomendado 16GB)
- **CPU**: Procesador de 4+ núcleos
- **Almacenamiento**: 10GB libres
- **GPU**: Opcional, pero recomendada para procesamiento de video

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd analsisis_de_tiempo
```

### 2. Configurar Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```bash
# Base de Datos PostgreSQL
POSTGRES_DB=vision_analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_PORT=5432

# pgAdmin
PGADMIN_EMAIL=admin@visionanalytics.com
PGADMIN_PASSWORD=your_pgadmin_password_here
PGADMIN_PORT=8080

# API Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=vision_analytics
DB_USER=postgres
DB_PASSWORD=your_secure_password_here
```

### 3. Inicializar la Base de Datos

Crear el directorio `init` y copiar el esquema de la base de datos:

```bash
mkdir -p init
cp databaseDLL.sql init/01-init.sql
```

## 🐳 Ejecución con Docker Compose

### 1. Levantar los Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver el estado de los servicios
docker-compose ps
```

### 2. Verificar que los Servicios Estén Funcionando

```bash
# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs postgres
docker-compose logs pgadmin
```

### 3. Acceder a las Aplicaciones

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Dashboard** | http://localhost:3000 | - |
| **API Server** | http://localhost:8000 | - |
| **pgAdmin** | http://localhost:8080 | Ver variables de entorno |

## 🔧 Configuración Manual (Sin Docker)

### Backend API (Python/FastAPI)

```bash
cd api

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install fastapi uvicorn psycopg2-binary python-dotenv ultralytics supervision opencv-python numpy requests

# Ejecutar servidor
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Dashboard (Next.js)

```bash
cd dashboard

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# O construir y ejecutar en producción
npm run build
npm start
```

### Base de Datos PostgreSQL

```bash
# Instalar PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Crear base de datos
sudo -u postgres createdb vision_analytics

# Ejecutar esquema
sudo -u postgres psql vision_analytics < databaseDLL.sql
```

## 📊 Uso de la Aplicación

### 1. Configuración Inicial

1. **Acceder al Dashboard**: http://localhost:3000
2. **Ir a Configuración**: Click en el botón "Configuración" en el header
3. **Crear Zonas**: 
   - Pestaña "Configuración de Zonas"
   - Cargar un video
   - Dibujar polígonos de detección
   - Guardar la zona

### 2. Procesamiento de Videos

1. **Gestión de Zonas**: Pestaña "Gestión de Zonas"
2. **Procesar Video**: Click en "Process" en una zona
3. **Configurar Proceso**: Seleccionar video y parámetros
4. **Iniciar Análisis**: El sistema procesará el video automáticamente

### 3. Visualización de Métricas

1. **Dashboard Principal**: Ver métricas en tiempo real
2. **Filtros**: Usar el filtro de zona para métricas específicas
3. **Fechas**: Seleccionar fechas específicas para análisis histórico

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Levantar servicios
docker-compose up -d

# Parar servicios
docker-compose down

# Reiniciar un servicio específico
docker-compose restart postgres

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar comandos en contenedores
docker-compose exec postgres psql -U postgres -d vision_analytics
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U postgres -d vision_analytics

# Backup de la base de datos
docker-compose exec postgres pg_dump -U postgres vision_analytics > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U postgres vision_analytics < backup.sql
```

## 🔍 Solución de Problemas

### Problemas Comunes

#### 1. Puerto en Uso
```bash
# Verificar puertos ocupados
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Cambiar puertos en docker-compose.yaml si es necesario
```

#### 2. Error de Conexión a Base de Datos
```bash
# Verificar que PostgreSQL esté funcionando
docker-compose logs postgres

# Verificar conectividad
docker-compose exec postgres pg_isready -U postgres
```

#### 3. Problemas de Permisos
```bash
# En Linux/Mac, ajustar permisos
sudo chown -R $USER:$USER .
chmod -R 755 .
```

### Logs y Debugging

```bash
# Ver todos los logs
docker-compose logs

# Logs específicos por servicio
docker-compose logs postgres
docker-compose logs pgadmin

# Logs en tiempo real
docker-compose logs -f --tail=100
```

## 📁 Estructura del Proyecto

```
analsisis_de_tiempo/
├── api/                          # Backend FastAPI
│   ├── api_server.py            # Servidor principal
│   ├── database/                # Módulos de base de datos
│   ├── inference_engine/        # Motor de análisis de video
│   └── store/                   # Utilidades de almacenamiento
├── dashboard/                    # Frontend Next.js
│   ├── src/
│   │   ├── app/                 # Páginas de la aplicación
│   │   ├── components/         # Componentes React
│   │   ├── lib/                # Hooks y utilidades
│   │   └── types/              # Tipos TypeScript
│   └── package.json
├── docker-compose.yaml          # Configuración de Docker
├── databaseDLL.sql             # Esquema de base de datos
└── README.md                   # Este archivo
```

## 🔐 Seguridad

### Recomendaciones de Producción

1. **Cambiar contraseñas por defecto**
2. **Usar HTTPS en producción**
3. **Configurar firewall**
4. **Hacer backups regulares**
5. **Monitorear logs de seguridad**

### Variables de Entorno Sensibles

```bash
# Nunca commitear el archivo .env
echo ".env" >> .gitignore

# Usar contraseñas seguras
POSTGRES_PASSWORD=your_very_secure_password_123!
PGADMIN_PASSWORD=another_secure_password_456!
```

## 📈 Monitoreo y Mantenimiento

### Health Checks

El sistema incluye health checks automáticos:

```bash
# Verificar estado de servicios
docker-compose ps

# Health check de PostgreSQL
docker-compose exec postgres pg_isready -U postgres
```

### Backups Automáticos

```bash
# Script de backup diario
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U postgres vision_analytics > "backup_${DATE}.sql"
```

## 🤝 Soporte

### Recursos Útiles

- **Documentación FastAPI**: https://fastapi.tiangolo.com/
- **Documentación Next.js**: https://nextjs.org/docs
- **Documentación PostgreSQL**: https://www.postgresql.org/docs/
- **Documentación Docker**: https://docs.docker.com/

### Contacto

Para soporte técnico o reportar problemas, contactar al equipo de desarrollo.

---

## 📝 Notas de Versión

- **v1.0.0**: Versión inicial con funcionalidades básicas
- **v1.1.0**: Agregado filtrado por zona en dashboard
- **v1.2.0**: Implementadas funciones de hora pico
- **v1.3.0**: Reorganización de interfaz de configuración

---

**¡Disfruta usando Vision Analytics! 🎉**
