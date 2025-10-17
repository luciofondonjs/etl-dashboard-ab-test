# 📊 Guía para Agregar Nuevas Métricas - AB Test Dashboard

Esta guía explica cómo agregar nuevas métricas de manera fácil y organizada al AB Test Dashboard de Streamlit.

## 🏗️ Estructura de Carpetas por Step del Flujo de Compra

Las métricas están organizadas por carpetas según el step del flujo de compra:

```
📁 baggage_metrics/     # Métricas de equipaje
📁 flight_metrics/      # Métricas de vuelos
📁 seats_metrics/       # Métricas de asientos
📁 extras_metrics/      # Métricas de extras
📁 passengers_metrics/  # Métricas de pasajeros
📁 payment_metrics/     # Métricas de pagos
```

## 📋 Estructura de Archivos por Carpeta

Cada carpeta de métricas debe contener:

```
📁 [step]_metrics/
├── 📄 [step]_metrics.py      # Definiciones de métricas (OBLIGATORIO)
├── 📄 [step]_utils.py        # Funciones de API (opcional)
├── 📄 amplitude_filters.py   # Filtros específicos (opcional)
├── 📄 README.md             # Documentación específica (opcional)
└── 📄 pruebas_metricas_[step].ipynb  # Notebook de pruebas (opcional)
```

## 🎯 Cómo Agregar una Nueva Métrica

### Paso 1: Crear/Actualizar el archivo `[step]_metrics.py`

Este archivo debe contener las definiciones de métricas siguiendo **exactamente** el formato de `baggage_metrics.py`:

```python
# filtros amplitude
from amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter
)

# Next Step Rate [Step] - General
NSR_[STEP] = [
    'evento_inicial',
    'evento_final'
]

# Website Conversion Rate from [Step] - General
WCR_[STEP] = [
    'evento_inicial',
    'revenue_amount'
]

# [Step] A2C con filtros específicos
[STEP]_A2C = {'events': [
    'evento_inicial',
    'evento_final',
], 'filters': [filtro_especifico()]}
```

**IMPORTANTE:** 
- Usa **listas simples** `[]` para métricas básicas (NSR, WCR)
- Usa **diccionarios** `{'events': [], 'filters': []}` solo cuando necesites filtros específicos
- Sigue la nomenclatura exacta: `NSR_[STEP]`, `WCR_[STEP]`, `[STEP]_A2C`

### Paso 2: Actualizar `streamlit/app.py`

Agregar la importación de las nuevas métricas en la sección correspondiente:

```python
# Importar métricas de [step]
try:
    from [step]_metrics.[step]_metrics import (
        NSR_[STEP],
        WCR_[STEP],
        [NUEVA_METRICA]
    )
    
    # Agregar al diccionario de métricas predefinidas
    PREDEFINED_METRICS_QUICK = {
        "🎒 NSR [Step] (Next Step Rate)": NSR_[STEP],
        "💰 WCR [Step] (Website Conversion Rate)": WCR_[STEP],
        "🆕 Nueva Métrica": [NUEVA_METRICA],
        # ... otras métricas existentes
    }
```

### Paso 3: Actualizar la documentación de métricas

En la sección "📚 Ver Métricas Disponibles", agregar información sobre la nueva métrica:

```python
metrics_info_quick = [
    # ... métricas existentes
    {
        "Métrica": "🆕 Nueva Métrica",
        "Evento Inicial": [NUEVA_METRICA][0] if isinstance([NUEVA_METRICA], list) else [NUEVA_METRICA].get('events', [])[0],
        "Evento Final": [NUEVA_METRICA][1] if isinstance([NUEVA_METRICA], list) else [NUEVA_METRICA].get('events', [])[1] if len([NUEVA_METRICA].get('events', [])) > 1 else "-",
        "Filtros": "DB + filtros_específicos"
    }
]
```

## 📝 Formatos de Métricas Soportados

### Formato 1: Lista Simple (para funnels básicos) - **RECOMENDADO**
```python
# Next Step Rate [Step] - General
NSR_[STEP] = [
    'evento_inicial',
    'evento_final'
]

# Website Conversion Rate from [Step] - General
WCR_[STEP] = [
    'evento_inicial',
    'revenue_amount'
]
```

### Formato 2: Diccionario con Filtros (solo cuando necesites filtros específicos)
```python
# [Step] A2C con filtros específicos
[STEP]_A2C = {'events': [
    'evento_inicial',
    'evento_final',
], 'filters': [filtro_especifico()]}
```

**⚠️ IMPORTANTE:** 
- **Usa listas simples** `[]` para la mayoría de métricas (NSR, WCR)
- **Usa diccionarios** `{'events': [], 'filters': []}` SOLO cuando necesites filtros específicos
- **NO uses** formatos complejos con `conversion_window` o `description` - mantén la simplicidad

## 🔧 Filtros Disponibles

### Filtros Básicos (en `amplitude_filters.py`)
- `get_culture_digital_filter(country_code)` - Filtro por cultura/país
- `get_device_type(device)` - Filtro por tipo de dispositivo
- `get_traffic_type(traffic_type)` - Filtro por tipo de tráfico
- `get_DB_filter()` - Filtro para flujo DB (Direct Booking)

### Filtros Específicos
- `cabin_bag_filter()` - Filtro para equipaje de cabina
- `checked_bag_filter()` - Filtro para equipaje facturado

### Crear Nuevos Filtros
```python
def nuevo_filtro():
    return {
        "subprop_type": "event",
        "subprop_key": "propiedad",
        "subprop_op": "is",  # o "is not", "greater", etc.
        "subprop_value": ["valor1", "valor2"]
    }
```

## 🎨 Convenciones de Nomenclatura

### Métricas
- **NSR_[STEP]**: Next Step Rate (tasa de siguiente paso)
- **WCR_[STEP]**: Website Conversion Rate (tasa de conversión del sitio)
- **A2C_[STEP]**: Action to Conversion (acción a conversión)
- **[STEP]_[TIPO]**: Métricas específicas del step

### Eventos
- Eventos estándar: `evento_dom_loaded`, `evento_clicked`
- Custom Events: `ce:(NEW) evento_especifico`
- Eventos de conversión: `revenue_amount`, `payment_confirmation_loaded`

## 📊 Ejemplo Completo: Agregar Métrica de Seats

### 1. Crear `seats_metrics/seats_metrics.py`
```python
# filtros amplitude
from amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter
)

# Next Step Rate Seats - General
NSR_SEATS = [
    'seatmap_dom_loaded',
    'continue_clicked_seat'
]

# Website Conversion Rate from Seats - General
WCR_SEATS = [
    'seatmap_dom_loaded',
    'revenue_amount'
]

# Seat Selection A2C
SEAT_SELECTION_A2C = {'events': [
    'seatmap_dom_loaded',
    'continue_clicked_seat',
], 'filters': [cabin_bag_filter()]}
```

### 2. Actualizar `streamlit/app.py`
```python
# Importar métricas de seats
try:
    from seats_metrics.seats_metrics import (
        NSR_SEATS,
        WCR_SEATS,
        SEAT_SELECTION_A2C
    )
    
    # Agregar al diccionario
    PREDEFINED_METRICS_QUICK.update({
        "🪑 NSR Seats (Next Step Rate)": NSR_SEATS,
        "💰 WCR Seats (Website Conversion Rate)": WCR_SEATS,
        "🎯 Seat Selection A2C": SEAT_SELECTION_A2C
    })
```

### 3. Actualizar documentación
```python
metrics_info_quick.extend([
    {
        "Métrica": "🪑 NSR Seats",
        "Evento Inicial": "seatmap_dom_loaded",
        "Evento Final": "continue_clicked_seat",
        "Filtros": "DB"
    },
    {
        "Métrica": "💰 WCR Seats",
        "Evento Inicial": "seatmap_dom_loaded",
        "Evento Final": "revenue_amount",
        "Filtros": "DB"
    },
    {
        "Métrica": "🎯 Seat Selection A2C",
        "Evento Inicial": "seatmap_dom_loaded",
        "Evento Final": "continue_clicked_seat",
        "Filtros": "DB"
    }
])
```

## ✅ Checklist para Agregar Nueva Métrica

- [ ] Crear/actualizar `[step]_metrics.py` con la nueva métrica
- [ ] Importar la métrica en `streamlit/app.py`
- [ ] Agregar al diccionario `PREDEFINED_METRICS_QUICK`
- [ ] Actualizar `metrics_info_quick` con la documentación
- [ ] Probar la métrica en la interfaz de Streamlit
- [ ] Verificar que los eventos existen en `AVAILABLE_EVENTS`
- [ ] Documentar filtros específicos si los hay

## 🚀 Tips y Mejores Prácticas

1. **Usa emojis descriptivos** en los nombres de métricas para mejor UX
2. **Mantén nombres consistentes** con las convenciones existentes
3. **Documenta filtros complejos** en comentarios
4. **Prueba métricas** antes de agregarlas al dashboard
5. **Usa eventos existentes** de `AVAILABLE_EVENTS` cuando sea posible
6. **Agrupa métricas relacionadas** en la misma carpeta
7. **Mantén la estructura** de archivos consistente

## 🔍 Debugging

Si una métrica no aparece en el dashboard:

1. Verifica que la importación sea correcta
2. Confirma que el archivo `[step]_metrics.py` existe
3. Revisa que la métrica esté en `PREDEFINED_METRICS_QUICK`
4. Verifica que los eventos estén en `AVAILABLE_EVENTS`
5. Revisa los logs de Streamlit para errores de importación

## 📞 Soporte

Para dudas sobre esta guía o problemas al agregar métricas, revisa:
- `EXPERIMENT_UTILS_DOCUMENTATION.md` - Documentación técnica completa
- `FASTAPI_CONVERSION_PLAN.md` - Plan de migración a FastAPI
- Los notebooks de pruebas en cada carpeta de métricas
