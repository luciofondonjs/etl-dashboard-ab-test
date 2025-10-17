# 🎒 Baggage Metrics - KPIs de Equipaje

Este módulo contiene los KPIs específicos para análisis de métricas de equipaje en la aplicación de Streamlit.

## 📊 KPIs Disponibles

### 1. NSR Baggage (Next Step Rate)
**Descripción**: Mide la conversión de usuarios que cargan la página de equipaje (`baggage_dom_loaded`) a la página de selección de asientos (`seatmap_dom_loaded`).

**Eventos**:
- `baggage_dom_loaded`
- `seatmap_dom_loaded`

**Filtros aplicados**:
- Cultura (según selección)
- Tipo de dispositivo (según selección)
- Filtro DB (solo flujo de compra directo)

---

### 2. WCR Baggage (Website Conversion Rate)
**Descripción**: Mide la conversión de usuarios que cargan la página de equipaje (`baggage_dom_loaded`) a conversión final (`revenue_amount`).

**Eventos**:
- `baggage_dom_loaded`
- `revenue_amount`

**Filtros aplicados**:
- Cultura (según selección)
- Tipo de dispositivo (según selección)
- Filtro DB (solo flujo de compra directo)

---

### 3. WCR Baggage Vuela Ligero
**Descripción**: Similar a WCR Baggage pero específicamente para usuarios con Vuela Ligero.

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (Custom Event)
- `revenue_amount`

**Filtros aplicados**:
- Cultura (según selección)
- Tipo de dispositivo (según selección)
- Filtro DB (solo flujo de compra directo)

---

### 4. Cabin Bag A2C (Add to Cart)
**Descripción**: Mide la conversión de usuarios con equipaje de cabina desde baggage a seatmap.

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (Custom Event)
- `seatmap_dom_loaded`

**Filtros aplicados**:
- Cultura (según selección)
- Tipo de dispositivo (según selección)
- Filtro DB (solo flujo de compra directo)
- Filtro de equipaje de cabina (`cabin_bag_count > 0`)

---

### 5. Checked Bag A2C (Add to Cart)
**Descripción**: Mide la conversión de usuarios con equipaje documentado desde baggage a seatmap.

**Eventos**:
- `ce:(NEW) baggage_dom_loaded_with_vuela_ligero` (Custom Event)
- `seatmap_dom_loaded`

**Filtros aplicados**:
- Cultura (según selección)
- Tipo de dispositivo (según selección)
- Filtro DB (solo flujo de compra directo)
- Filtro de equipaje documentado (`checked_bag_count > 0`)

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

