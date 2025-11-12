# 🎒 Baggage Metrics - KPIs de Equipaje

Este módulo contiene los KPIs específicos para análisis de métricas de equipaje en la aplicación de Streamlit.

## 📊 KPIs Disponibles

### Formato de Métricas

Todas las métricas siguen el formato estándar donde cada evento tiene sus propios filtros:

```python
METRIC_NAME = {'events': [
    ('evento_1', [filtro_1, filtro_2, ..., filtro_m]),
    ('evento_2', [filtro_1, filtro_2, ..., filtro_m]),
    ('evento_3', [filtro_1, filtro_2, ..., filtro_m]),
    # ... puedes agregar tantos eventos como necesites
    ('evento_n', [filtro_1, filtro_2, ..., filtro_m]),
]}
```

Cada tupla contiene:
- **Primer elemento**: Nombre del evento (string)
- **Segundo elemento**: Lista de filtros para ese evento `[filtro1, filtro2, ...]`
  - Si no hay filtros, usar lista vacía: `[]`

**Nota importante**: Puedes agregar **tantos eventos como necesites** en una métrica. Los eventos se procesan en orden como un funnel secuencial. Ejemplos comunes:
- **2 eventos**: Funnel básico (inicio → fin)
- **3+ eventos**: Funnel completo con etapas intermedias

---

### 1. NSR Baggage (Next Step Rate)
**Descripción**: Mide la conversión de usuarios que cargan la página de equipaje (`baggage_dom_loaded`) a la página de selección de asientos (`seatmap_dom_loaded`).

**Definición**:
```python
NSR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [])
]}
```

**Eventos**:
- `baggage_dom_loaded` (sin filtros adicionales - lista vacía)
- `seatmap_dom_loaded` (sin filtros adicionales - lista vacía)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)

---

### 2. NSR Baggage DB (Next Step Rate - Direct Booking)
**Descripción**: Similar a NSR Baggage pero solo para flujo de compra directo (DB).

**Definición**:
```python
NSR_BAGGAGE_DB = {'events': [
    ('baggage_dom_loaded', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}
```

**Eventos**:
- `baggage_dom_loaded` (con filtro DB en lista)
- `seatmap_dom_loaded` (con filtro DB en lista)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)
- Filtro DB (aplicado a ambos eventos)

---

### 3. WCR Baggage (Website Conversion Rate)
**Descripción**: Mide la conversión de usuarios que cargan la página de equipaje (`baggage_dom_loaded`) a conversión final (`revenue_amount`).

**Definición**:
```python
WCR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('revenue_amount', [])
]}
```

**Eventos**:
- `baggage_dom_loaded` (sin filtros adicionales - lista vacía)
- `revenue_amount` (sin filtros adicionales - lista vacía)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)

---

### 4. WCR Baggage Vuela Ligero
**Descripción**: Similar a WCR Baggage pero específicamente para usuarios con Vuela Ligero.

**Definición**:
```python
WCR_BAGGAGE_VUELA_LIGERO = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('revenue_amount', [])
]}
```

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (Custom Event, sin filtros adicionales - lista vacía)
- `revenue_amount` (sin filtros adicionales - lista vacía)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)

---

### 5. Cabin Bag A2C (Add to Cart)
**Descripción**: Mide la conversión de usuarios con equipaje de cabina desde baggage a seatmap.

**Definición**:
```python
CABIN_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter()])  # Con filtro de equipaje de cabina
]}
```

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (sin filtros adicionales - lista vacía)
- `seatmap_dom_loaded` (con filtro de equipaje de cabina en lista)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)
- Filtro de equipaje de cabina (`cabin_bag_count > 0`) - aplicado a ambos eventos

---

### 6. Checked Bag A2C (Add to Cart)
**Descripción**: Mide la conversión de usuarios con equipaje documentado desde baggage a seatmap.

**Definición**:
```python
CHECKED_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [checked_bag_filter()]),
    ('seatmap_dom_loaded', [checked_bag_filter()])
]}
```

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (con filtro de equipaje documentado en lista)
- `seatmap_dom_loaded` (con filtro de equipaje documentado en lista)

**Filtros aplicados**:
- Cultura (según selección del usuario)
- Tipo de dispositivo (según selección del usuario)
- Filtro de equipaje documentado (`checked_bag_count > 0`) - aplicado a ambos eventos

---

## 🔧 Configuración

Todos los KPIs utilizan:
- **Ventana de conversión**: 30 minutos (1800 segundos)
- **Filtro DB**: Solo flujo de compra directo
- **Filtros de cultura y dispositivo**: Según selección del usuario
- **Filtro During Booking** (opcional): Filtra eventos durante el proceso de reserva

---

## 📁 Estructura de Archivos

```
baggage_metrics/
├── README.md                    # Este archivo
├── baggage_metrics.py          # Definición de KPIs y eventos
└── baggage_utils.py            # Funciones para obtener datos de Amplitude
```

---

## 🚀 Uso en Streamlit

Los KPIs están integrados en la aplicación de Streamlit en la pestaña **"🎒 Baggage KPIs"**.

### Pasos para usar:

1. Abrir la aplicación de Streamlit
2. Navegar a la pestaña **"🎒 Baggage KPIs"**
3. Configurar:
   - Fecha de inicio
   - Fecha de fin
   - Tipo de dispositivo (All, mobile, desktop, tablet)
   - Cultura (All, CL, AR, PE, CO, MX, UY)
   - **Filtro During Booking** (toggle opcional)
4. Hacer clic en el botón del KPI que deseas ejecutar
5. Ver los resultados con:
   - Métricas principales (Total Eventos, Conversiones, Tasa de Conversión)
   - Tabla de resultados
   - Opciones de descarga (CSV, Excel)

---

## 📝 Notas Importantes

- Los Custom Events parten con el prefijo `ce:` en Amplitude
- El filtro DB asegura que solo se analicen usuarios en el flujo de compra directo
- El filtro **During Booking** es opcional y filtra eventos durante el proceso de reserva
- La ventana de conversión de 30 minutos es estándar para todos los KPIs
- Los resultados muestran datos acumulados del período seleccionado

---

## 🔗 Referencias

- [Amplitude API Documentation](https://developers.amplitude.com/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Experiment Utils Documentation](../streamlit/EXPERIMENT_UTILS_DOCUMENTATION.md)

