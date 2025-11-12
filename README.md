## AB Test Dashboard - Streamlit

Aplicación de Streamlit para analizar experimentos de Amplitude (Jetsmart). Permite:
- Listar experimentos de Amplitude
- Ejecutar análisis diarios o acumulados por `experiment_id`, `device`, `culture` y `event_list`

### Requisitos
- Python 3.10+
- Archivo `.env` en la raíz del proyecto con credenciales de Amplitude.

Variables requeridas en `.env`:
```
AMPLITUDE_API_KEY=...
AMPLITUDE_SECRET_KEY=...
AMPLITUDE_MANAGEMENT_KEY=...
```

### Entorno virtual e instalación (Windows PowerShell)

Crea y activa el entorno virtual en la raíz del proyecto:

```powershell
# Crear entorno virtual (si no existe)
python -m venv venv

# Activar el entorno virtual
./venv/Scripts/Activate.ps1

# Actualizar pip e instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Ejecutar la app

Con el entorno virtual activo, desde la raíz del proyecto:

```powershell
streamlit run app.py
```

### Estructura relevante
```
.
  app.py                    # App principal de Streamlit
  requirements.txt          # Dependencias
  utils/experiment_utils.py # Librería con lógica de Amplitude y pipelines
  metrics/                  # Métricas por step (baggage, seats, etc.)
  METRICS_GUIDE.md          # Guía para agregar métricas
  EXPERIMENT_UTILS_DOCUMENTATION.md # Docs técnicas de experiment_utils
```

### Cómo agregar nuevas métricas (resumen)
- Define las métricas en `metrics/<step>/<step>_metrics.py` siguiendo el ejemplo de `metrics/baggage/baggage_metrics.py`.
- Importa y añade las métricas al diccionario en `app.py` (sección de métricas predefinidas).
- Documenta la métrica en la tabla de "📚 Ver Métricas Disponibles".

Consulta la guía completa en `METRICS_GUIDE.md` y el ejemplo `EXAMPLE_SEATS_METRICS.py`.

### Troubleshooting
- Verifica que el `.env` esté en la raíz del proyecto.
- Asegúrate de activar el entorno virtual antes de ejecutar.
- Si faltan paquetes, ejecuta `pip install -r requirements.txt` desde la raíz del proyecto.
- Revisa la pestaña "❓ Ayuda" dentro de la app para parámetros y ejemplos.

### Licencia y soporte
- Uso interno Jetsmart. Para dudas técnicas, revisa `EXPERIMENT_UTILS_DOCUMENTATION.md`.

