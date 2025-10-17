# Documentación de experiment_utils.py

## Descripción General

El módulo `experiment_utils.py` es una biblioteca especializada para el análisis de experimentos A/B Test utilizando la API de Amplitude. Proporciona un conjunto completo de funciones para obtener, procesar y analizar datos de experimentos, con capacidades avanzadas de logging y manejo de errores.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Configuración](#configuración)
3. [Funciones Principales](#funciones-principales)
4. [Funciones de Utilidad](#funciones-de-utilidad)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Manejo de Errores](#manejo-de-errores)
7. [Logging y Debugging](#logging-y-debugging)
8. [Integración en Diferentes Entornos](#integración-en-diferentes-entornos)
9. [API Reference](#api-reference)

## Requisitos Previos

### Dependencias de Python
```python
import os
import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from amplitude_filters import get_culture_digital_filter, get_device_type
import sys
from io import StringIO
```

### Variables de Entorno Requeridas
El módulo requiere las siguientes variables de entorno configuradas:

```bash
AMPLITUDE_API_KEY=tu_api_key_aqui
AMPLITUDE_SECRET_KEY=tu_secret_key_aqui
AMPLITUDE_MANAGEMENT_KEY=tu_management_key_aqui
```

### Módulos Dependientes
- `amplitude_filters.py`: Debe estar en el mismo directorio o en el PYTHONPATH

## Configuración

### 1. Configuración de Variables de Entorno

```python
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Verificar que las credenciales estén disponibles
api_key = os.getenv('AMPLITUDE_API_KEY')
secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
management_key = os.getenv('AMPLITUDE_MANAGEMENT_KEY')
```

### 2. Importación del Módulo

```python
from experiment_utils import (
    get_credentials,
    get_funnel_data_experiment,
    get_variant_funnel,
    get_variant_funnel_cum,
    get_control_treatment_raw_data,
    final_pipeline,
    get_experiments_list,
    get_logs
)
```

## Funciones Principales

### 1. `get_credentials()`

**Propósito**: Obtiene y valida las credenciales de Amplitude desde variables de entorno.

**Parámetros**: Ninguno

**Retorna**: 
- `tuple`: (api_key, secret_key, management_api_key)

**Ejemplo de Uso**:
```python
api_key, secret_key, management_key = get_credentials()
```

**Notas**:
- Debe ser llamada DESPUÉS de que `load_dotenv()` se haya ejecutado
- Incluye logging detallado para verificación de credenciales
- Muestra los primeros 10 caracteres de cada credencial para debugging

### 2. `get_funnel_data_experiment(api_key, secret_key, start_date, end_date, experiment_id, device, variant, culture, event_list)`

**Propósito**: Obtiene datos de funnel desde la API de Amplitude para un experimento específico.

**Parámetros**:
- `api_key` (str): Clave API de Amplitude
- `secret_key` (str): Clave secreta de Amplitude
- `start_date` (str): Fecha de inicio en formato 'YYYY-MM-DD'
- `end_date` (str): Fecha de fin en formato 'YYYY-MM-DD'
- `experiment_id` (str): ID del experimento en Amplitude
- `device` (str): Tipo de dispositivo ('mobile', 'desktop', 'tablet', 'All')
- `variant` (str): Variante del experimento ('control', 'treatment')
- `culture` (str): Código de cultura ('CL', 'AR', 'PE', 'All')
- `event_list` (list): Lista de eventos a analizar

**Retorna**: 
- `dict`: Respuesta JSON de la API de Amplitude

**Ejemplo de Uso**:
```python
response = get_funnel_data_experiment(
    api_key="tu_api_key",
    secret_key="tu_secret_key",
    start_date="2024-01-01",
    end_date="2024-01-31",
    experiment_id="exp_123",
    device="mobile",
    variant="control",
    culture="CL",
    event_list=["page_view", "purchase"]
)
```

### 3. `get_variant_funnel(variant)`

**Propósito**: Procesa datos de una variante y genera un DataFrame con datos diarios.

**Parámetros**:
- `variant` (dict): Diccionario con datos de la variante que incluye:
  - `Data`: Datos de la API de Amplitude
  - `ExperimentID`: ID del experimento
  - `Culture`: Cultura filtrada
  - `Device`: Dispositivo filtrado
  - `Variant`: Nombre de la variante

**Retorna**: 
- `pd.DataFrame`: DataFrame con columnas:
  - `Date`: Fecha del evento
  - `ExperimentID`: ID del experimento
  - `Funnel Stage`: Paso del funnel
  - `Culture`: Cultura
  - `Device`: Dispositivo
  - `Variant`: Variante
  - `Event Count`: Cantidad de eventos

**Ejemplo de Uso**:
```python
variant_data = {
    'Data': api_response,
    'ExperimentID': 'exp_123',
    'Culture': 'CL',
    'Device': 'mobile',
    'Variant': 'control'
}

df = get_variant_funnel(variant_data)
```

### 4. `get_variant_funnel_cum(variant)`

**Propósito**: Procesa datos de una variante y genera un DataFrame con datos acumulados.

**Parámetros**: Mismo que `get_variant_funnel()`

**Retorna**: 
- `pd.DataFrame`: DataFrame con columnas:
  - `Start Date`: Fecha de inicio del período
  - `End Date`: Fecha de fin del período
  - `ExperimentID`: ID del experimento
  - `Culture`: Cultura
  - `Device`: Dispositivo
  - `Variant`: Variante
  - `Funnel Stage`: Paso del funnel
  - `Event Count`: Cantidad acumulada de eventos

### 5. `get_control_treatment_raw_data(start_date, end_date, experiment_id, device, culture, event_list)`

**Propósito**: Obtiene los datos raw de control y treatment para un experimento.

**Parámetros**:
- `start_date` (str): Fecha de inicio (formato YYYY-MM-DD)
- `end_date` (str): Fecha de fin (formato YYYY-MM-DD)
- `experiment_id` (str): ID del experimento en Amplitude
- `device` (str): Tipo de dispositivo ('mobile', 'desktop', 'tablet', 'All')
- `culture` (str): Código de cultura ('CL', 'AR', 'PE', 'All')
- `event_list` (list): Lista de eventos a analizar

**Retorna**: 
- `tuple`: (control_data, treatment_data) donde cada uno es un diccionario con:
  - `Data`: Respuesta de la API
  - `ExperimentID`: ID del experimento
  - `Culture`: Cultura filtrada
  - `Device`: Dispositivo filtrado
  - `Variant`: Nombre de la variante

**Ejemplo de Uso**:
```python
control, treatment = get_control_treatment_raw_data(
    start_date="2024-01-01",
    end_date="2024-01-31",
    experiment_id="exp_123",
    device="mobile",
    culture="CL",
    event_list=["page_view", "purchase", "checkout"]
)
```

### 6. `final_pipeline(start_date, end_date, experiment_id, device, culture, event_list)`

**Propósito**: Pipeline completo para análisis de experimentos AB Test.

**Parámetros**: Mismo que `get_control_treatment_raw_data()`

**Retorna**: 
- `pd.DataFrame`: DataFrame combinado con datos de control y treatment

**Ejemplo de Uso**:
```python
df_complete = final_pipeline(
    start_date="2024-01-01",
    end_date="2024-01-31",
    experiment_id="exp_123",
    device="mobile",
    culture="CL",
    event_list=["page_view", "purchase", "checkout"]
)
```

### 7. `get_experiments_list()`

**Propósito**: Obtiene la lista de todos los experimentos disponibles en Amplitude.

**Parámetros**: Ninguno

**Retorna**: 
- `pd.DataFrame`: DataFrame con la información de todos los experimentos

**Ejemplo de Uso**:
```python
experiments_df = get_experiments_list()
print(f"Total de experimentos: {len(experiments_df)}")
```

## Funciones de Utilidad

### 1. `get_logs()`

**Propósito**: Obtiene y limpia los logs capturados durante la ejecución.

**Parámetros**: Ninguno

**Retorna**: 
- `list`: Lista de mensajes de log

**Ejemplo de Uso**:
```python
# Ejecutar alguna función
df = final_pipeline(...)

# Obtener logs
logs = get_logs()
for log in logs:
    print(log)
```

## Ejemplos de Uso

### Ejemplo 1: Análisis Básico de Experimento

```python
from experiment_utils import final_pipeline, get_logs
import pandas as pd

# Configurar parámetros del experimento
start_date = "2024-01-01"
end_date = "2024-01-31"
experiment_id = "exp_123"
device = "mobile"
culture = "CL"
event_list = ["page_view", "add_to_cart", "purchase"]

# Ejecutar pipeline completo
df_results = final_pipeline(
    start_date=start_date,
    end_date=end_date,
    experiment_id=experiment_id,
    device=device,
    culture=culture,
    event_list=event_list
)

# Mostrar resultados
print("Resultados del experimento:")
print(df_results.head())

# Obtener logs para debugging
logs = get_logs()
print("\nLogs de ejecución:")
for log in logs:
    print(log)
```

### Ejemplo 2: Análisis Detallado por Variantes

```python
from experiment_utils import get_control_treatment_raw_data, get_variant_funnel, get_variant_funnel_cum

# Obtener datos raw
control, treatment = get_control_treatment_raw_data(
    start_date="2024-01-01",
    end_date="2024-01-31",
    experiment_id="exp_123",
    device="mobile",
    culture="CL",
    event_list=["page_view", "purchase"]
)

# Procesar datos diarios
df_control_daily = get_variant_funnel(control)
df_treatment_daily = get_variant_funnel(treatment)

# Procesar datos acumulados
df_control_cum = get_variant_funnel_cum(control)
df_treatment_cum = get_variant_funnel_cum(treatment)

# Análisis comparativo
print("Datos diarios - Control:")
print(df_control_daily.groupby('Funnel Stage')['Event Count'].sum())

print("\nDatos diarios - Treatment:")
print(df_treatment_daily.groupby('Funnel Stage')['Event Count'].sum())
```

### Ejemplo 3: Listado de Experimentos Disponibles

```python
from experiment_utils import get_experiments_list

# Obtener lista de experimentos
experiments_df = get_experiments_list()

# Mostrar información básica
print(f"Total de experimentos: {len(experiments_df)}")
print("\nColumnas disponibles:")
print(experiments_df.columns.tolist())

# Mostrar primeros experimentos
print("\nPrimeros 5 experimentos:")
print(experiments_df.head())
```

## Manejo de Errores

### Errores Comunes y Soluciones

#### 1. Error de Credenciales
```python
# Error: Credenciales no encontradas
# Solución: Verificar variables de entorno
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('AMPLITUDE_API_KEY')
if not api_key:
    raise ValueError("AMPLITUDE_API_KEY no encontrada en variables de entorno")
```

#### 2. Error de Estructura de Datos
```python
# Error: KeyError - No existe la clave 'data'
# Solución: Verificar respuesta de la API
try:
    df = get_variant_funnel(variant_data)
except KeyError as e:
    print(f"Error en estructura de datos: {e}")
    print("Verificar que la respuesta de la API contenga la clave 'data'")
```

#### 3. Error de Conexión a la API
```python
# Error: requests.exceptions.RequestException
# Solución: Implementar retry logic
import time
from requests.exceptions import RequestException

def safe_api_call(func, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

## Logging y Debugging

### Sistema de Logging Integrado

El módulo incluye un sistema de logging integrado que captura información detallada durante la ejecución:

```python
from experiment_utils import get_logs

# Ejecutar función
df = final_pipeline(...)

# Obtener logs detallados
logs = get_logs()
for log in logs:
    print(log)
```

### Información de Debug Incluida

- Verificación de credenciales
- Estructura de datos recibidos
- Parámetros de filtros aplicados
- Progreso de procesamiento
- Errores y advertencias

### Ejemplo de Log Output

```
================================================================================
[CREDENCIALES] Verificación de carga de variables de entorno:
  - API_KEY existe: True
  - API_KEY (primeros 10 chars): abc123def4...
  - SECRET_KEY existe: True
  - SECRET_KEY (primeros 10 chars): xyz789ghi0...
  - MANAGEMENT_API_KEY existe: True
  - MANAGEMENT_API_KEY (primeros 10 chars): mno456pqr7...
================================================================================

[get_control_treatment_raw_data] Iniciando obtención de datos
  - experiment_id: exp_123
  - device: mobile
  - culture: CL
  - event_list: ['page_view', 'purchase']
================================================================================
```

## Integración en Diferentes Entornos

### 1. Jupyter Notebooks

```python
# En una celda de Jupyter
%load_ext autoreload
%autoreload 2

from experiment_utils import final_pipeline
import pandas as pd
import matplotlib.pyplot as plt

# Ejecutar análisis
df = final_pipeline(...)

# Visualización
df.groupby(['Variant', 'Funnel Stage'])['Event Count'].sum().plot(kind='bar')
plt.show()
```

### 2. Streamlit Apps

```python
# En app.py de Streamlit
import streamlit as st
from experiment_utils import final_pipeline, get_experiments_list

st.title("Análisis de Experimentos A/B")

# Selector de experimento
experiments_df = get_experiments_list()
selected_experiment = st.selectbox(
    "Seleccionar Experimento",
    experiments_df['name'].tolist()
)

# Parámetros
start_date = st.date_input("Fecha de inicio")
end_date = st.date_input("Fecha de fin")
device = st.selectbox("Dispositivo", ["All", "mobile", "desktop", "tablet"])
culture = st.selectbox("Cultura", ["All", "CL", "AR", "PE"])

# Ejecutar análisis
if st.button("Analizar"):
    df = final_pipeline(
        start_date=str(start_date),
        end_date=str(end_date),
        experiment_id=selected_experiment,
        device=device,
        culture=culture,
        event_list=["page_view", "purchase"]
    )
    
    st.dataframe(df)
```

### 3. Scripts de Python

```python
# En un script independiente
#!/usr/bin/env python3
"""
Script para análisis de experimentos A/B
"""

import sys
import os
from dotenv import load_dotenv
from experiment_utils import final_pipeline, get_logs

def main():
    # Cargar variables de entorno
    load_dotenv()
    
    # Parámetros del experimento
    params = {
        'start_date': '2024-01-01',
        'end_date': '2024-01-31',
        'experiment_id': 'exp_123',
        'device': 'mobile',
        'culture': 'CL',
        'event_list': ['page_view', 'purchase']
    }
    
    try:
        # Ejecutar análisis
        df = final_pipeline(**params)
        
        # Guardar resultados
        df.to_csv('experiment_results.csv', index=False)
        print(f"Resultados guardados en experiment_results.csv")
        print(f"Total de registros: {len(df)}")
        
    except Exception as e:
        print(f"Error: {e}")
        logs = get_logs()
        for log in logs:
            print(log)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 4. APIs REST

```python
# En una API Flask/FastAPI
from flask import Flask, jsonify, request
from experiment_utils import final_pipeline, get_experiments_list
import pandas as pd

app = Flask(__name__)

@app.route('/experiments', methods=['GET'])
def get_experiments():
    try:
        df = get_experiments_list()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_experiment():
    try:
        data = request.json
        df = final_pipeline(**data)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## API Reference

### Funciones Principales

| Función | Parámetros | Retorna | Descripción |
|---------|------------|---------|-------------|
| `get_credentials()` | None | `tuple` | Obtiene credenciales de Amplitude |
| `get_funnel_data_experiment()` | 9 parámetros | `dict` | Obtiene datos de funnel desde API |
| `get_variant_funnel()` | `variant` | `pd.DataFrame` | Procesa datos diarios de variante |
| `get_variant_funnel_cum()` | `variant` | `pd.DataFrame` | Procesa datos acumulados de variante |
| `get_control_treatment_raw_data()` | 6 parámetros | `tuple` | Obtiene datos raw de control y treatment |
| `final_pipeline()` | 6 parámetros | `pd.DataFrame` | Pipeline completo de análisis |
| `get_experiments_list()` | None | `pd.DataFrame` | Lista de experimentos disponibles |

### Funciones de Utilidad

| Función | Parámetros | Retorna | Descripción |
|---------|------------|---------|-------------|
| `get_logs()` | None | `list` | Obtiene logs de ejecución |
| `_log()` | `message` | None | Función interna de logging |

### Estructuras de Datos

#### Variant Dictionary
```python
variant = {
    'Data': dict,           # Respuesta de la API de Amplitude
    'ExperimentID': str,    # ID del experimento
    'Culture': str,         # Código de cultura
    'Device': str,          # Tipo de dispositivo
    'Variant': str          # Nombre de la variante
}
```

#### DataFrame de Salida (Datos Diarios)
```python
columns = [
    'Date',           # pd.Timestamp
    'ExperimentID',   # str
    'Funnel Stage',   # str
    'Culture',        # str
    'Device',         # str
    'Variant',        # str
    'Event Count'     # int
]
```

#### DataFrame de Salida (Datos Acumulados)
```python
columns = [
    'Start Date',     # pd.Timestamp
    'End Date',       # pd.Timestamp
    'ExperimentID',   # str
    'Culture',        # str
    'Device',         # str
    'Variant',        # str
    'Funnel Stage',   # str
    'Event Count'     # int
]
```

## Consideraciones de Rendimiento

### Optimizaciones Recomendadas

1. **Caching de Credenciales**: Las credenciales se obtienen en cada llamada. Considera implementar caching.

2. **Procesamiento en Lotes**: Para múltiples experimentos, procesa en lotes para evitar límites de API.

3. **Filtrado Temprano**: Usa filtros específicos para reducir la cantidad de datos transferidos.

### Límites de la API

- **Rate Limiting**: Amplitude tiene límites de rate. Implementa retry logic con backoff exponencial.
- **Tamaño de Respuesta**: Respuestas grandes pueden causar timeouts. Considera dividir períodos largos.
- **Concurrencia**: Evita múltiples llamadas simultáneas a la misma API.

## Troubleshooting

### Problemas Comunes

1. **Credenciales Incorrectas**
   - Verificar variables de entorno
   - Confirmar que las credenciales sean válidas
   - Verificar permisos de la API key

2. **Datos Vacíos**
   - Verificar que el experimento exista
   - Confirmar que haya datos en el período especificado
   - Verificar filtros aplicados

3. **Errores de Estructura**
   - Verificar formato de fechas (YYYY-MM-DD)
   - Confirmar que los eventos existan en Amplitude
   - Verificar códigos de cultura y dispositivos

### Comandos de Debug

```python
# Verificar credenciales
api_key, secret_key, management_key = get_credentials()

# Verificar estructura de respuesta
response = get_funnel_data_experiment(...)
print("Keys en respuesta:", list(response.keys()))

# Verificar logs detallados
logs = get_logs()
for log in logs:
    print(log)
```

## Contribución y Mantenimiento

### Agregar Nuevas Funcionalidades

1. Seguir el patrón de logging existente
2. Incluir documentación detallada
3. Agregar manejo de errores robusto
4. Probar con diferentes tipos de datos

### Testing

```python
# Ejemplo de test básico
def test_get_credentials():
    api_key, secret_key, management_key = get_credentials()
    assert api_key is not None
    assert secret_key is not None
    assert management_key is not None

def test_final_pipeline():
    df = final_pipeline(
        start_date="2024-01-01",
        end_date="2024-01-02",
        experiment_id="test_exp",
        device="All",
        culture="All",
        event_list=["test_event"]
    )
    assert isinstance(df, pd.DataFrame)
    assert len(df.columns) > 0
```

---

## Changelog

### Versión 1.0.0
- Implementación inicial del módulo
- Funciones básicas de obtención y procesamiento de datos
- Sistema de logging integrado
- Documentación completa

---

*Esta documentación fue generada automáticamente y actualizada por última vez el $(date).*
