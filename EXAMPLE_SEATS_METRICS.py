# 📊 EJEMPLO: Cómo agregar métricas de Seats al Dashboard
# Este archivo muestra el proceso completo paso a paso

# =============================================================================
# PASO 1: Crear el archivo seats_metrics/seats_metrics.py
# =============================================================================

"""
# Contenido del archivo: seats_metrics/seats_metrics.py

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

# Premium Seat Selection
PREMIUM_SEAT_SELECTION = {'events': [
    'seatmap_dom_loaded',
    'continue_clicked_seat',
], 'filters': [checked_bag_filter()]}
"""

# =============================================================================
# PASO 2: Actualizar streamlit/app.py - Importaciones
# =============================================================================

"""
# Agregar estas líneas en la sección de importaciones de métricas (línea ~378)

# Importar métricas de seats
try:
    from seats_metrics.seats_metrics import (
        NSR_SEATS,
        WCR_SEATS,
        SEAT_SELECTION_A2C,
        PREMIUM_SEAT_SELECTION
    )
    
    # Agregar al diccionario de métricas predefinidas
    PREDEFINED_METRICS_QUICK.update({
        "🪑 NSR Seats (Next Step Rate)": NSR_SEATS,
        "💰 WCR Seats (Website Conversion Rate)": WCR_SEATS,
        "🎯 Seat Selection A2C": SEAT_SELECTION_A2C,
        "⭐ Premium Seat Selection": PREMIUM_SEAT_SELECTION
    })
    
except ImportError:
    # Si no están definidas las métricas de seats, continuar sin ellas
    pass
"""

# =============================================================================
# PASO 3: Actualizar streamlit/app.py - Documentación
# =============================================================================

"""
# Agregar estas líneas en la sección metrics_info_quick (línea ~398)

# Métricas de Seats
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
},
{
    "Métrica": "⭐ Premium Seat Selection",
    "Evento Inicial": "seatmap_dom_loaded",
    "Evento Final": "continue_clicked_seat",
    "Filtros": "DB"
}
"""

# =============================================================================
# PASO 4: Verificar eventos en AVAILABLE_EVENTS
# =============================================================================

"""
# Asegurarse de que estos eventos estén en AVAILABLE_EVENTS (línea ~20):
- 'seatmap_dom_loaded' ✅
- 'continue_clicked_seat' ✅
- 'outbound_seat_selected' ✅
- 'revenue_amount' ✅
"""

# =============================================================================
# PASO 5: Código completo para copiar y pegar
# =============================================================================

# Para seats_metrics/seats_metrics.py:
SEATS_METRICS_CODE = '''
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

# Premium Seat Selection
PREMIUM_SEAT_SELECTION = {'events': [
    'seatmap_dom_loaded',
    'continue_clicked_seat',
], 'filters': [checked_bag_filter()]}
'''

# Para streamlit/app.py - Importaciones:
IMPORT_CODE = '''
# Importar métricas de seats
try:
    from seats_metrics.seats_metrics import (
        NSR_SEATS,
        WCR_SEATS,
        SEAT_SELECTION_A2C,
        PREMIUM_SEAT_SELECTION
    )
    
    # Agregar al diccionario de métricas predefinidas
    PREDEFINED_METRICS_QUICK.update({
        "🪑 NSR Seats (Next Step Rate)": NSR_SEATS,
        "💰 WCR Seats (Website Conversion Rate)": WCR_SEATS,
        "🎯 Seat Selection A2C": SEAT_SELECTION_A2C,
        "⭐ Premium Seat Selection": PREMIUM_SEAT_SELECTION
    })
    
except ImportError:
    # Si no están definidas las métricas de seats, continuar sin ellas
    pass
'''

# Para streamlit/app.py - Documentación:
DOCUMENTATION_CODE = '''
# Métricas de Seats
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
},
{
    "Métrica": "⭐ Premium Seat Selection",
    "Evento Inicial": "seatmap_dom_loaded",
    "Evento Final": "continue_clicked_seat",
    "Filtros": "DB"
}
'''

# =============================================================================
# PASO 6: Checklist de verificación
# =============================================================================

CHECKLIST = '''
✅ Checklist para agregar métricas de Seats:

□ Crear archivo seats_metrics/seats_metrics.py con las métricas
□ Importar las métricas en streamlit/app.py
□ Agregar al diccionario PREDEFINED_METRICS_QUICK
□ Actualizar metrics_info_quick con la documentación
□ Verificar que los eventos estén en AVAILABLE_EVENTS
□ Probar la métrica en la interfaz de Streamlit
□ Verificar que no hay errores de importación
□ Documentar cualquier filtro específico

🎯 Resultado esperado:
- Las métricas de Seats aparecerán en el multiselect de "Métricas Predefinidas"
- Se mostrarán en la tabla de "Métricas Disponibles"
- Funcionarán correctamente al ejecutar análisis
'''

print("📊 Ejemplo completo para agregar métricas de Seats al Dashboard")
print("Revisa este archivo para ver el proceso paso a paso")
