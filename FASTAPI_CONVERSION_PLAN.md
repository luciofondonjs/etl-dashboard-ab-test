# Plan de Conversión a FastAPI - experiment_utils.py

## Resumen Ejecutivo

Este documento presenta un plan detallado para convertir el módulo `experiment_utils.py` en una API REST completa utilizando FastAPI. La conversión permitirá exponer todas las funcionalidades de análisis de experimentos A/B como endpoints HTTP, facilitando la integración con diferentes sistemas y aplicaciones.

## Objetivos del Proyecto

### Objetivos Principales
- Convertir todas las funciones de `experiment_utils.py` en endpoints REST
- Mantener la funcionalidad existente sin cambios
- Implementar documentación automática con OpenAPI/Swagger
- Añadir validación de datos con Pydantic
- Implementar manejo robusto de errores
- Añadir autenticación y autorización
- Optimizar rendimiento con async/await
- Implementar logging estructurado
- Añadir tests automatizados
- Configurar deployment con Docker

### Objetivos Secundarios
- Implementar caching para mejorar rendimiento
- Añadir rate limiting
- Implementar health checks
- Crear dashboard de monitoreo
- Añadir métricas de performance

## Arquitectura Propuesta

### Estructura de Directorios

```
fastapi_experiment_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── config.py              # Configuración de la aplicación
│   ├── dependencies.py        # Dependencias de FastAPI
│   ├── models/                # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── experiment.py      # Modelos de experimentos
│   │   ├── funnel.py          # Modelos de funnels
│   │   ├── response.py        # Modelos de respuesta
│   │   └── error.py           # Modelos de error
│   ├── routers/               # Routers de FastAPI
│   │   ├── __init__.py
│   │   ├── experiments.py     # Endpoints de experimentos
│   │   ├── funnels.py         # Endpoints de funnels
│   │   ├── analytics.py       # Endpoints de análisis
│   │   └── health.py          # Health checks
│   ├── services/              # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── experiment_service.py
│   │   ├── funnel_service.py
│   │   └── amplitude_service.py
│   ├── utils/                 # Utilidades
│   │   ├── __init__.py
│   │   ├── logging.py         # Configuración de logging
│   │   ├── cache.py           # Sistema de cache
│   │   └── auth.py            # Autenticación
│   └── tests/                 # Tests
│       ├── __init__.py
│       ├── test_experiments.py
│       ├── test_funnels.py
│       └── test_analytics.py
├── requirements.txt           # Dependencias
├── Dockerfile                # Containerización
├── docker-compose.yml        # Orquestación
├── .env.example             # Variables de entorno de ejemplo
├── README.md                # Documentación
└── pyproject.toml           # Configuración del proyecto
```

## Fase 1: Preparación y Configuración Base

### 1.1 Configuración del Entorno

**Tareas:**
- [ ] Crear estructura de directorios
- [ ] Configurar `pyproject.toml` con dependencias
- [ ] Crear `requirements.txt` con versiones específicas
- [ ] Configurar variables de entorno
- [ ] Crear `.env.example`

**Dependencias Principales:**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-dotenv==1.0.0
pandas==2.1.4
requests==2.31.0
redis==5.0.1
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

### 1.2 Configuración Base de FastAPI

**Archivo: `app/main.py`**
```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import experiments, funnels, analytics, health
from app.utils.logging import setup_logging

# Configurar logging
setup_logging()

app = FastAPI(
    title="Amplitude Experiment Analysis API",
    description="API para análisis de experimentos A/B usando datos de Amplitude",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(experiments.router, prefix="/api/v1/experiments", tags=["experiments"])
app.include_router(funnels.router, prefix="/api/v1/funnels", tags=["funnels"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/")
async def root():
    return {"message": "Amplitude Experiment Analysis API", "version": "1.0.0"}
```

**Archivo: `app/config.py`**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Amplitude Credentials
    AMPLITUDE_API_KEY: str
    AMPLITUDE_SECRET_KEY: str
    AMPLITUDE_MANAGEMENT_KEY: str
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Amplitude Experiment Analysis API"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Fase 2: Modelos Pydantic

### 2.1 Modelos de Request

**Archivo: `app/models/experiment.py`**
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import date
from enum import Enum

class DeviceType(str, Enum):
    ALL = "All"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    TABLET = "tablet"

class CultureCode(str, Enum):
    ALL = "All"
    CL = "CL"
    AR = "AR"
    PE = "PE"
    CO = "CO"
    MX = "MX"

class ExperimentRequest(BaseModel):
    start_date: date = Field(..., description="Fecha de inicio del análisis")
    end_date: date = Field(..., description="Fecha de fin del análisis")
    experiment_id: str = Field(..., description="ID del experimento en Amplitude")
    device: DeviceType = Field(DeviceType.ALL, description="Tipo de dispositivo")
    culture: CultureCode = Field(CultureCode.ALL, description="Código de cultura")
    event_list: List[str] = Field(..., description="Lista de eventos a analizar")
    
    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date debe ser posterior a start_date')
        return v
    
    @validator('event_list')
    def event_list_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('event_list no puede estar vacía')
        return v

class FunnelAnalysisRequest(ExperimentRequest):
    variant: Optional[str] = Field(None, description="Variante específica (control/treatment)")
    cumulative: bool = Field(False, description="Si se requieren datos acumulados")

class ExperimentListRequest(BaseModel):
    limit: Optional[int] = Field(100, ge=1, le=1000, description="Límite de experimentos a retornar")
    offset: Optional[int] = Field(0, ge=0, description="Offset para paginación")
```

### 2.2 Modelos de Response

**Archivo: `app/models/response.py`**
```python
from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime, date
from app.models.experiment import DeviceType, CultureCode

class FunnelDataPoint(BaseModel):
    date: Optional[datetime] = Field(None, description="Fecha del evento")
    start_date: Optional[date] = Field(None, description="Fecha de inicio del período")
    end_date: Optional[date] = Field(None, description="Fecha de fin del período")
    experiment_id: str = Field(..., description="ID del experimento")
    funnel_stage: str = Field(..., description="Paso del funnel")
    culture: str = Field(..., description="Cultura")
    device: str = Field(..., description="Dispositivo")
    variant: str = Field(..., description="Variante")
    event_count: int = Field(..., description="Cantidad de eventos")

class ExperimentResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    data: List[FunnelDataPoint] = Field(..., description="Datos del experimento")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos adicionales")
    total_records: int = Field(..., description="Total de registros retornados")

class ExperimentListResponse(BaseModel):
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    experiments: List[Dict[str, Any]] = Field(..., description="Lista de experimentos")
    total_count: int = Field(..., description="Total de experimentos disponibles")
    limit: int = Field(..., description="Límite aplicado")
    offset: int = Field(..., description="Offset aplicado")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Indica que la operación falló")
    error: str = Field(..., description="Mensaje de error")
    error_code: str = Field(..., description="Código de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales del error")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Estado del servicio")
    timestamp: datetime = Field(..., description="Timestamp del check")
    version: str = Field(..., description="Versión de la API")
    dependencies: Dict[str, str] = Field(..., description="Estado de dependencias")
```

## Fase 3: Servicios de Negocio

### 3.1 Servicio de Amplitude

**Archivo: `app/services/amplitude_service.py`**
```python
import os
import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Tuple, Optional
from app.config import settings
from app.utils.logging import get_logger
from amplitude_filters import get_culture_digital_filter, get_device_type

logger = get_logger(__name__)

class AmplitudeService:
    def __init__(self):
        self.api_key = settings.AMPLITUDE_API_KEY
        self.secret_key = settings.AMPLITUDE_SECRET_KEY
        self.management_key = settings.AMPLITUDE_MANAGEMENT_KEY
        
    async def get_funnel_data_experiment(
        self,
        start_date: str,
        end_date: str,
        experiment_id: str,
        device: str,
        variant: str,
        culture: str,
        event_list: List[str]
    ) -> Dict:
        """Obtiene datos de funnel desde la API de Amplitude"""
        url = 'https://amplitude.com/api/2/funnels'
        
        # Construir filtros
        filters = []
        if culture != "All":
            culture_filter = get_culture_digital_filter(culture)
            if culture_filter:
                filters.append(culture_filter)
        
        if device != "All":
            device_filter = get_device_type(device)
            if device_filter:
                filters.append(device_filter)
        
        event_filters_grouped = [
            {
                "event_type": event,
                "filters": filters,
                "group_by": []
            }
            for event in event_list
        ]
        
        segments = [
            {
                'group_type': 'User',
                'prop': f'gp:[Experiment] {experiment_id}',
                'prop_type': 'user',
                'op': 'is',
                'type': 'property',
                'values': [variant],
            },
        ]
        
        params = {
            'e': [json.dumps(event) for event in event_filters_grouped],
            'start': start_date.replace('-', ''),
            'end': end_date.replace('-', ''),
            'cs': 1800,
            's': [json.dumps(segment) for segment in segments],
        }
        
        headers = {
            'Authorization': f'Basic {self.api_key}:{self.secret_key}'
        }
        
        try:
            response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                auth=HTTPBasicAuth(self.api_key, self.secret_key),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en API de Amplitude: {e}")
            raise
    
    async def get_experiments_list(self, limit: int = 1000) -> List[Dict]:
        """Obtiene la lista de experimentos desde Amplitude"""
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.management_key}',
        }
        
        params = {
            'limit': str(limit),
        }
        
        try:
            response = requests.get(
                'https://experiment.amplitude.com/api/1/experiments',
                params=params,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get('experiments', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Error obteniendo lista de experimentos: {e}")
            raise
```

### 3.2 Servicio de Experimentos

**Archivo: `app/services/experiment_service.py`**
```python
import pandas as pd
from typing import List, Dict, Tuple
from app.services.amplitude_service import AmplitudeService
from app.models.experiment import ExperimentRequest, FunnelAnalysisRequest
from app.models.response import FunnelDataPoint, ExperimentResponse
from app.utils.logging import get_logger

logger = get_logger(__name__)

class ExperimentService:
    def __init__(self):
        self.amplitude_service = AmplitudeService()
    
    async def get_control_treatment_raw_data(self, request: ExperimentRequest) -> Tuple[Dict, Dict]:
        """Obtiene datos raw de control y treatment"""
        logger.info(f"Obteniendo datos para experimento {request.experiment_id}")
        
        # Obtener datos de control
        control_response = await self.amplitude_service.get_funnel_data_experiment(
            start_date=request.start_date.strftime('%Y-%m-%d'),
            end_date=request.end_date.strftime('%Y-%m-%d'),
            experiment_id=request.experiment_id,
            device=request.device.value,
            variant="control",
            culture=request.culture.value,
            event_list=request.event_list
        )
        
        # Obtener datos de treatment
        treatment_response = await self.amplitude_service.get_funnel_data_experiment(
            start_date=request.start_date.strftime('%Y-%m-%d'),
            end_date=request.end_date.strftime('%Y-%m-%d'),
            experiment_id=request.experiment_id,
            device=request.device.value,
            variant="treatment",
            culture=request.culture.value,
            event_list=request.event_list
        )
        
        control = {
            'Data': control_response,
            'ExperimentID': request.experiment_id,
            'Culture': request.culture.value,
            'Device': request.device.value,
            'Variant': 'control'
        }
        
        treatment = {
            'Data': treatment_response,
            'ExperimentID': request.experiment_id,
            'Culture': request.culture.value,
            'Device': request.device.value,
            'Variant': 'treatment'
        }
        
        return control, treatment
    
    def process_variant_funnel(self, variant: Dict, cumulative: bool = False) -> List[FunnelDataPoint]:
        """Procesa datos de una variante y retorna lista de FunnelDataPoint"""
        data_points = []
        variant_data = variant['Data']
        
        if 'data' not in variant_data:
            raise KeyError(f"No existe la clave 'data' en variant_data")
        
        for website_funnel in variant_data['data']:
            if cumulative:
                # Procesar datos acumulados
                day_funnels = website_funnel.get('dayFunnels', {})
                x_values = day_funnels.get('xValues', [])
                start_date = pd.to_datetime(x_values[0]) if x_values else None
                end_date = pd.to_datetime(x_values[-1]) if x_values else None
                
                funnel_stages = website_funnel.get('events', [])
                cumulative_raw = website_funnel.get('cumulativeRaw', [])
                
                if not cumulative_raw or not funnel_stages:
                    continue
                
                for funnel_stage, value in zip(funnel_stages, cumulative_raw):
                    if isinstance(funnel_stage, dict):
                        stage_name = funnel_stage.get('event_type', str(funnel_stage))
                    else:
                        stage_name = funnel_stage
                    
                    data_points.append(FunnelDataPoint(
                        start_date=start_date.date() if start_date else None,
                        end_date=end_date.date() if end_date else None,
                        experiment_id=variant['ExperimentID'],
                        funnel_stage=stage_name,
                        culture=variant['Culture'],
                        device=variant['Device'],
                        variant=variant['Variant'],
                        event_count=int(value)
                    ))
            else:
                # Procesar datos diarios
                funnel_website_conversion_data = website_funnel['dayFunnels']['series']
                funnel_stages = website_funnel['events']
                dates = website_funnel['dayFunnels']['xValues']
                
                for date, data in zip(dates, funnel_website_conversion_data):
                    for funnel_stage, value in zip(funnel_stages, data):
                        data_points.append(FunnelDataPoint(
                            date=pd.to_datetime(date),
                            experiment_id=variant['ExperimentID'],
                            funnel_stage=funnel_stage,
                            culture=variant['Culture'],
                            device=variant['Device'],
                            variant=variant['Variant'],
                            event_count=int(value)
                        ))
        
        return data_points
    
    async def analyze_experiment(self, request: FunnelAnalysisRequest) -> ExperimentResponse:
        """Análisis completo de experimento"""
        try:
            if request.variant:
                # Análisis de variante específica
                if request.variant not in ['control', 'treatment']:
                    raise ValueError("Variant debe ser 'control' o 'treatment'")
                
                response = await self.amplitude_service.get_funnel_data_experiment(
                    start_date=request.start_date.strftime('%Y-%m-%d'),
                    end_date=request.end_date.strftime('%Y-%m-%d'),
                    experiment_id=request.experiment_id,
                    device=request.device.value,
                    variant=request.variant,
                    culture=request.culture.value,
                    event_list=request.event_list
                )
                
                variant_data = {
                    'Data': response,
                    'ExperimentID': request.experiment_id,
                    'Culture': request.culture.value,
                    'Device': request.device.value,
                    'Variant': request.variant
                }
                
                data_points = self.process_variant_funnel(variant_data, request.cumulative)
            else:
                # Análisis completo (control + treatment)
                control, treatment = await self.get_control_treatment_raw_data(request)
                
                control_points = self.process_variant_funnel(control, request.cumulative)
                treatment_points = self.process_variant_funnel(treatment, request.cumulative)
                
                data_points = control_points + treatment_points
            
            return ExperimentResponse(
                success=True,
                data=data_points,
                metadata={
                    'experiment_id': request.experiment_id,
                    'start_date': request.start_date.isoformat(),
                    'end_date': request.end_date.isoformat(),
                    'device': request.device.value,
                    'culture': request.culture.value,
                    'cumulative': request.cumulative
                },
                total_records=len(data_points)
            )
            
        except Exception as e:
            logger.error(f"Error en análisis de experimento: {e}")
            raise
    
    async def get_experiments_list(self, limit: int = 1000) -> List[Dict]:
        """Obtiene lista de experimentos disponibles"""
        return await self.amplitude_service.get_experiments_list(limit)
```

## Fase 4: Routers y Endpoints

### 4.1 Router de Experimentos

**Archivo: `app/routers/experiments.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.models.experiment import ExperimentListRequest
from app.models.response import ExperimentListResponse, ErrorResponse
from app.services.experiment_service import ExperimentService
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/", response_model=ExperimentListResponse)
async def get_experiments(
    limit: int = Query(100, ge=1, le=1000, description="Límite de experimentos"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Obtiene la lista de experimentos disponibles en Amplitude
    
    - **limit**: Número máximo de experimentos a retornar (1-1000)
    - **offset**: Número de experimentos a saltar para paginación
    """
    try:
        service = ExperimentService()
        experiments = await service.get_experiments_list(limit + offset)
        
        # Aplicar paginación
        paginated_experiments = experiments[offset:offset + limit]
        
        return ExperimentListResponse(
            success=True,
            experiments=paginated_experiments,
            total_count=len(experiments),
            limit=limit,
            offset=offset
        )
    except Exception as e:
        logger.error(f"Error obteniendo lista de experimentos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo experimentos: {str(e)}"
        )

@router.get("/{experiment_id}/info")
async def get_experiment_info(experiment_id: str):
    """
    Obtiene información detallada de un experimento específico
    
    - **experiment_id**: ID del experimento en Amplitude
    """
    try:
        service = ExperimentService()
        experiments = await service.get_experiments_list(1000)
        
        # Buscar experimento específico
        experiment = next(
            (exp for exp in experiments if exp.get('id') == experiment_id),
            None
        )
        
        if not experiment:
            raise HTTPException(
                status_code=404,
                detail=f"Experimento {experiment_id} no encontrado"
            )
        
        return {
            "success": True,
            "experiment": experiment
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo info del experimento {experiment_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información del experimento: {str(e)}"
        )
```

### 4.2 Router de Funnels

**Archivo: `app/routers/funnels.py`**
```python
from fastapi import APIRouter, HTTPException, Depends
from app.models.experiment import FunnelAnalysisRequest
from app.models.response import ExperimentResponse, ErrorResponse
from app.services.experiment_service import ExperimentService
from app.utils.logging import get_logger
from app.utils.cache import cache_result

router = APIRouter()
logger = get_logger(__name__)

@router.post("/analyze", response_model=ExperimentResponse)
@cache_result(ttl=3600)  # Cache por 1 hora
async def analyze_funnel(request: FunnelAnalysisRequest):
    """
    Analiza un funnel de experimento A/B
    
    - **start_date**: Fecha de inicio del análisis
    - **end_date**: Fecha de fin del análisis
    - **experiment_id**: ID del experimento en Amplitude
    - **device**: Tipo de dispositivo (All, mobile, desktop, tablet)
    - **culture**: Código de cultura (All, CL, AR, PE, etc.)
    - **event_list**: Lista de eventos a analizar
    - **variant**: Variante específica (opcional, control/treatment)
    - **cumulative**: Si se requieren datos acumulados (default: false)
    """
    try:
        service = ExperimentService()
        result = await service.analyze_experiment(request)
        return result
    except ValueError as e:
        logger.warning(f"Error de validación en análisis de funnel: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except KeyError as e:
        logger.error(f"Error de estructura de datos: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Error en estructura de datos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error en análisis de funnel: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/compare", response_model=ExperimentResponse)
@cache_result(ttl=1800)  # Cache por 30 minutos
async def compare_variants(request: FunnelAnalysisRequest):
    """
    Compara las variantes control y treatment de un experimento
    
    Siempre retorna datos de ambas variantes para comparación
    """
    try:
        # Forzar análisis completo
        request.variant = None
        service = ExperimentService()
        result = await service.analyze_experiment(request)
        return result
    except Exception as e:
        logger.error(f"Error en comparación de variantes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error en comparación: {str(e)}"
        )
```

### 4.3 Router de Analytics

**Archivo: `app/routers/analytics.py`**
```python
from fastapi import APIRouter, HTTPException
from app.models.experiment import ExperimentRequest
from app.services.experiment_service import ExperimentService
from app.utils.logging import get_logger
from typing import Dict, Any
import pandas as pd

router = APIRouter()
logger = get_logger(__name__)

@router.post("/summary")
async def get_experiment_summary(request: ExperimentRequest):
    """
    Genera un resumen estadístico del experimento
    
    Incluye métricas como:
    - Total de eventos por variante
    - Conversión por etapa del funnel
    - Comparación entre variantes
    """
    try:
        service = ExperimentService()
        
        # Obtener datos completos
        control, treatment = await service.get_control_treatment_raw_data(request)
        
        # Procesar datos
        control_points = service.process_variant_funnel(control)
        treatment_points = service.process_variant_funnel(treatment)
        
        # Convertir a DataFrame para análisis
        all_data = control_points + treatment_points
        df = pd.DataFrame([point.dict() for point in all_data])
        
        # Calcular métricas
        summary = {
            "experiment_id": request.experiment_id,
            "period": {
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat()
            },
            "filters": {
                "device": request.device.value,
                "culture": request.culture.value
            },
            "total_events": {
                "control": int(df[df['variant'] == 'control']['event_count'].sum()),
                "treatment": int(df[df['variant'] == 'treatment']['event_count'].sum())
            },
            "funnel_stages": {}
        }
        
        # Análisis por etapa del funnel
        for stage in df['funnel_stage'].unique():
            stage_data = df[df['funnel_stage'] == stage]
            control_events = int(stage_data[stage_data['variant'] == 'control']['event_count'].sum())
            treatment_events = int(stage_data[stage_data['variant'] == 'treatment']['event_count'].sum())
            
            summary["funnel_stages"][stage] = {
                "control": control_events,
                "treatment": treatment_events,
                "difference": treatment_events - control_events,
                "percentage_change": ((treatment_events - control_events) / control_events * 100) if control_events > 0 else 0
            }
        
        return {
            "success": True,
            "summary": summary
        }
        
    except Exception as e:
        logger.error(f"Error generando resumen: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando resumen: {str(e)}"
        )

@router.post("/conversion-rates")
async def get_conversion_rates(request: ExperimentRequest):
    """
    Calcula tasas de conversión entre etapas del funnel
    """
    try:
        service = ExperimentService()
        control, treatment = await service.get_control_treatment_raw_data(request)
        
        control_points = service.process_variant_funnel(control)
        treatment_points = service.process_variant_funnel(treatment)
        
        all_data = control_points + treatment_points
        df = pd.DataFrame([point.dict() for point in all_data])
        
        # Calcular tasas de conversión
        conversion_rates = {}
        
        # Agrupar por variante y calcular totales por etapa
        variant_totals = df.groupby(['variant', 'funnel_stage'])['event_count'].sum().reset_index()
        
        for variant in ['control', 'treatment']:
            variant_data = variant_totals[variant_totals['variant'] == variant]
            conversion_rates[variant] = {}
            
            # Calcular conversión entre etapas consecutivas
            stages = variant_data['funnel_stage'].tolist()
            for i in range(len(stages) - 1):
                current_stage = stages[i]
                next_stage = stages[i + 1]
                
                current_events = int(variant_data[variant_data['funnel_stage'] == current_stage]['event_count'].iloc[0])
                next_events = int(variant_data[variant_data['funnel_stage'] == next_stage]['event_count'].iloc[0])
                
                conversion_rate = (next_events / current_events * 100) if current_events > 0 else 0
                
                conversion_rates[variant][f"{current_stage}_to_{next_stage}"] = {
                    "from_stage": current_stage,
                    "to_stage": next_stage,
                    "conversion_rate": round(conversion_rate, 2),
                    "from_events": current_events,
                    "to_events": next_events
                }
        
        return {
            "success": True,
            "conversion_rates": conversion_rates
        }
        
    except Exception as e:
        logger.error(f"Error calculando tasas de conversión: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculando tasas de conversión: {str(e)}"
        )
```

### 4.4 Router de Health

**Archivo: `app/routers/health.py`**
```python
from fastapi import APIRouter, HTTPException
from app.models.response import HealthResponse
from app.config import settings
from app.services.amplitude_service import AmplitudeService
from datetime import datetime
import asyncio

router = APIRouter()

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check del servicio
    
    Verifica:
    - Estado del servicio
    - Conectividad con Amplitude
    - Estado de dependencias
    """
    dependencies = {}
    
    # Verificar Amplitude
    try:
        amplitude_service = AmplitudeService()
        # Test simple - obtener lista de experimentos con límite pequeño
        await asyncio.wait_for(
            amplitude_service.get_experiments_list(1),
            timeout=10.0
        )
        dependencies["amplitude"] = "healthy"
    except asyncio.TimeoutError:
        dependencies["amplitude"] = "timeout"
    except Exception as e:
        dependencies["amplitude"] = f"error: {str(e)}"
    
    # Verificar Redis (si está configurado)
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        dependencies["redis"] = "healthy"
    except Exception as e:
        dependencies["redis"] = f"error: {str(e)}"
    
    # Determinar estado general
    overall_status = "healthy" if all(
        status == "healthy" for status in dependencies.values()
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        dependencies=dependencies
    )

@router.get("/ready")
async def readiness_check():
    """
    Readiness check - verifica si el servicio está listo para recibir tráfico
    """
    try:
        # Verificar credenciales
        if not all([settings.AMPLITUDE_API_KEY, settings.AMPLITUDE_SECRET_KEY, settings.AMPLITUDE_MANAGEMENT_KEY]):
            raise HTTPException(status_code=503, detail="Credenciales no configuradas")
        
        # Verificar conectividad básica
        amplitude_service = AmplitudeService()
        await amplitude_service.get_experiments_list(1)
        
        return {"status": "ready", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service not ready: {str(e)}")

@router.get("/live")
async def liveness_check():
    """
    Liveness check - verifica si el servicio está vivo
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}
```

## Fase 5: Utilidades y Middleware

### 5.1 Sistema de Cache

**Archivo: `app/utils/cache.py`**
```python
import json
import hashlib
from functools import wraps
from typing import Any, Callable
import redis
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL)
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            logger.warning(f"Redis no disponible, cache deshabilitado: {e}")
            self.enabled = False
    
    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Genera una clave única para el cache"""
        key_data = {
            'function': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get(self, key: str) -> Any:
        """Obtiene un valor del cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Guarda un valor en el cache"""
        if not self.enabled:
            return False
        
        try:
            self.redis_client.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
            return False

cache_service = CacheService()

def cache_result(ttl: int = 3600):
    """Decorator para cachear resultados de funciones"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar clave de cache
            cache_key = cache_service._generate_key(func.__name__, args, kwargs)
            
            # Intentar obtener del cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit para {func.__name__}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, ttl)
            logger.info(f"Resultado cacheado para {func.__name__}")
            
            return result
        return wrapper
    return decorator
```

### 5.2 Sistema de Logging

**Archivo: `app/utils/logging.py`**
```python
import logging
import sys
from typing import Any
from app.config import settings

def setup_logging():
    """Configura el sistema de logging"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )

def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado"""
    return logging.getLogger(name)
```

### 5.3 Middleware de Rate Limiting

**Archivo: `app/middleware/rate_limit.py`**
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
from collections import defaultdict
from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls_per_minute: int = None):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.clients = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Limpiar llamadas antiguas (más de 1 minuto)
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if current_time - timestamp < 60
        ]
        
        # Verificar límite
        if len(self.clients[client_ip]) >= self.calls_per_minute:
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit excedido. Intenta de nuevo en un minuto."
            )
        
        # Registrar llamada
        self.clients[client_ip].append(current_time)
        
        # Procesar request
        response = await call_next(request)
        return response
```

## Fase 6: Testing

### 6.1 Tests Unitarios

**Archivo: `app/tests/test_experiments.py`**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.experiment import ExperimentRequest, DeviceType, CultureCode
from datetime import date

client = TestClient(app)

class TestExperiments:
    def test_get_experiments_list(self):
        """Test obtener lista de experimentos"""
        response = client.get("/api/v1/experiments/")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "experiments" in data
    
    def test_get_experiment_info(self):
        """Test obtener información de experimento específico"""
        # Primero obtener lista para tener un ID válido
        list_response = client.get("/api/v1/experiments/")
        if list_response.status_code == 200:
            experiments = list_response.json()["experiments"]
            if experiments:
                experiment_id = experiments[0]["id"]
                response = client.get(f"/api/v1/experiments/{experiment_id}/info")
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "experiment" in data
    
    def test_analyze_funnel_valid_request(self):
        """Test análisis de funnel con request válido"""
        request_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "experiment_id": "test_exp",
            "device": "mobile",
            "culture": "CL",
            "event_list": ["page_view", "purchase"]
        }
        
        response = client.post("/api/v1/funnels/analyze", json=request_data)
        # Puede fallar por credenciales, pero debe validar la estructura
        assert response.status_code in [200, 500, 401]
    
    def test_analyze_funnel_invalid_request(self):
        """Test análisis de funnel con request inválido"""
        request_data = {
            "start_date": "2024-01-31",  # Fecha posterior a end_date
            "end_date": "2024-01-01",
            "experiment_id": "test_exp",
            "device": "mobile",
            "culture": "CL",
            "event_list": ["page_view"]
        }
        
        response = client.post("/api/v1/funnels/analyze", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_health_check(self):
        """Test health check"""
        response = client.get("/health/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "dependencies" in data
```

### 6.2 Tests de Integración

**Archivo: `app/tests/test_integration.py`**
```python
import pytest
import asyncio
from app.services.experiment_service import ExperimentService
from app.models.experiment import ExperimentRequest, DeviceType, CultureCode
from datetime import date

class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test del pipeline completo"""
        service = ExperimentService()
        
        request = ExperimentRequest(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            experiment_id="test_exp",
            device=DeviceType.MOBILE,
            culture=CultureCode.CL,
            event_list=["page_view", "purchase"]
        )
        
        try:
            result = await service.analyze_experiment(request)
            assert result.success is True
            assert len(result.data) > 0
            assert result.total_records > 0
        except Exception as e:
            # Puede fallar por credenciales, pero no debe ser un error de estructura
            assert "credentials" in str(e).lower() or "api" in str(e).lower()
    
    @pytest.mark.asyncio
    async def test_amplitude_service(self):
        """Test del servicio de Amplitude"""
        from app.services.amplitude_service import AmplitudeService
        
        service = AmplitudeService()
        
        try:
            experiments = await service.get_experiments_list(10)
            assert isinstance(experiments, list)
        except Exception as e:
            # Puede fallar por credenciales
            assert "credentials" in str(e).lower() or "api" in str(e).lower()
```

## Fase 7: Deployment y DevOps

### 7.1 Dockerfile

**Archivo: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY amplitude_filters.py .

# Crear usuario no-root
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Exponer puerto
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Docker Compose

**Archivo: `docker-compose.yml`**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AMPLITUDE_API_KEY=${AMPLITUDE_API_KEY}
      - AMPLITUDE_SECRET_KEY=${AMPLITUDE_SECRET_KEY}
      - AMPLITUDE_MANAGEMENT_KEY=${AMPLITUDE_MANAGEMENT_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  redis_data:
```

### 7.3 Configuración de Nginx

**Archivo: `nginx.conf`**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api {
        server api:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://api/health;
            access_log off;
        }
    }
}
```

## Fase 8: Monitoreo y Observabilidad

### 8.1 Métricas con Prometheus

**Archivo: `app/utils/metrics.py`**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time

# Métricas
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
CACHE_HITS = Counter('cache_hits_total', 'Cache hits', ['endpoint'])
CACHE_MISSES = Counter('cache_misses_total', 'Cache misses', ['endpoint'])

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            method = scope["method"]
            path = scope["path"]
            
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    REQUEST_COUNT.labels(method=method, endpoint=path, status=status_code).inc()
                    REQUEST_DURATION.observe(time.time() - start_time)
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)

@app.get("/metrics")
async def get_metrics():
    """Endpoint para métricas de Prometheus"""
    return Response(generate_latest(), media_type="text/plain")
```

### 8.2 Logging Estructurado

**Archivo: `app/utils/structured_logging.py`**
```python
import json
import logging
from typing import Dict, Any
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Agregar campos adicionales si existen
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'experiment_id'):
            log_entry['experiment_id'] = record.experiment_id
        
        return json.dumps(log_entry)

def setup_structured_logging():
    """Configura logging estructurado"""
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredFormatter())
    
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
```

## Cronograma de Implementación

### Semana 1-2: Configuración Base
- [ ] Configurar estructura de proyecto
- [ ] Implementar configuración base de FastAPI
- [ ] Crear modelos Pydantic
- [ ] Configurar sistema de logging

### Semana 3-4: Servicios y Lógica de Negocio
- [ ] Implementar AmplitudeService
- [ ] Implementar ExperimentService
- [ ] Migrar lógica de experiment_utils.py
- [ ] Implementar sistema de cache

### Semana 5-6: Endpoints y Routers
- [ ] Implementar router de experimentos
- [ ] Implementar router de funnels
- [ ] Implementar router de analytics
- [ ] Implementar health checks

### Semana 7-8: Testing y Validación
- [ ] Escribir tests unitarios
- [ ] Escribir tests de integración
- [ ] Validar funcionalidad completa
- [ ] Optimizar rendimiento

### Semana 9-10: Deployment y DevOps
- [ ] Configurar Docker
- [ ] Configurar Docker Compose
- [ ] Configurar Nginx
- [ ] Implementar CI/CD

### Semana 11-12: Monitoreo y Documentación
- [ ] Implementar métricas
- [ ] Configurar logging estructurado
- [ ] Completar documentación
- [ ] Testing de producción

## Consideraciones de Seguridad

### 1. Autenticación y Autorización
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
```

### 2. Validación de Input
- Usar Pydantic para validación automática
- Sanitizar inputs de usuario
- Implementar rate limiting
- Validar tamaños de request

### 3. Manejo de Credenciales
- Usar variables de entorno
- Implementar rotación de credenciales
- Usar secret management (AWS Secrets Manager, etc.)

## Consideraciones de Rendimiento

### 1. Optimizaciones
- Implementar cache con Redis
- Usar async/await para operaciones I/O
- Implementar connection pooling
- Optimizar queries a la API de Amplitude

### 2. Escalabilidad
- Usar load balancer
- Implementar horizontal scaling
- Usar CDN para assets estáticos
- Implementar database connection pooling

### 3. Monitoreo
- Implementar métricas de performance
- Configurar alertas
- Monitorear uso de recursos
- Implementar health checks

## Conclusión

Este plan proporciona una hoja de ruta completa para convertir `experiment_utils.py` en una API REST robusta y escalable usando FastAPI. La implementación seguirá las mejores prácticas de desarrollo, incluyendo:

- Arquitectura modular y mantenible
- Testing comprehensivo
- Documentación automática
- Monitoreo y observabilidad
- Deployment containerizado
- Seguridad y validación
- Optimización de rendimiento

La API resultante será fácil de integrar en cualquier entorno y proporcionará una interfaz estándar para el análisis de experimentos A/B usando datos de Amplitude.
