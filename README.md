## AB Test Dashboard - Streamlit

App de Streamlit que consume funciones desde `Amplitude_AB_Test_Working (PRUEBAS).ipynb` para:
- Listar experimentos de Amplitude
- Ejecutar el pipeline (diario o acumulado) por `experiment_id`, `device`, `culture` y `event_list`

### Requisitos
- Python 3.10+
- Archivo `.env` en el raíz del proyecto con:
  - `AMPLITUDE_API_KEY`
  - `AMPLITUDE_SECRET_KEY`
  - `AMPLITUDE_MANAGEMENT_KEY`

### Instalación (usando venv)

En Windows PowerShell, desde el raíz del repo:

```powershell
python -m venv .venv
./.venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
pip install -r streamlit/requirements.txt
```

### Ejecutar

Desde el raíz del repo (con la venv activa):

```powershell
streamlit run streamlit/app.py
```

La app carga dinámicamente el notebook `Amplitude_AB_Test_Working (PRUEBAS).ipynb`. Asegúrate de que exista en el raíz del proyecto y que el `.env` tenga las credenciales correctas.


