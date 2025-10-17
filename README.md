## AB Test Dashboard - Streamlit

Aplicación de Streamlit para analizar experimentos de Amplitude (Jetsmart). Permite:
- Listar experimentos de Amplitude
- Ejecutar análisis diarios o acumulados por `experiment_id`, `device`, `culture` y `event_list`

### Requisitos
- Python 3.10+
- Archivo `.env` en la raíz del repo (`./.env`) con credenciales de Amplitude.

Variables requeridas en `./.env`:
```
AMPLITUDE_API_KEY=...
AMPLITUDE_SECRET_KEY=...
AMPLITUDE_MANAGEMENT_KEY=...
```

### Entorno virtual e instalación (Windows PowerShell)

Crea y usa tu propio entorno virtual en la raíz del repo y instala dependencias con `pip`:
```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
pip install -r streamlit/requirements.txt
```

### Ejecutar la app

Con el entorno virtual activo, desde el raíz del repo o desde `streamlit/`:

```powershell
# Opción A (desde el raíz)
streamlit run streamlit/app.py

# Opción B (desde la carpeta streamlit)
cd streamlit
streamlit run app.py
```

### Estructura relevante
```
streamlit/
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

Consulta la guía completa en `streamlit/METRICS_GUIDE.md` y el ejemplo `streamlit/EXAMPLE_SEATS_METRICS.py`.

### Troubleshooting
- Verifica que el `.env` esté en `./.env` (raíz del repo).
- Asegúrate de activar el entorno virtual correcto antes de ejecutar.
- Si faltan paquetes, ejecuta `pip install -r streamlit/requirements.txt` (o `streamlit/requirements.txt` si estás en el raíz).
- Revisa la pestaña "❓ Ayuda" dentro de la app para parámetros y ejemplos.

### Licencia y soporte
- Uso interno Jetsmart. Para dudas técnicas, revisa `EXPERIMENT_UTILS_DOCUMENTATION.md`.

