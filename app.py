import os
import sys
from pathlib import Path
from io import BytesIO

import streamlit as st
import pandas as pd
import requests

from utils.experiment_utils import (
    get_experiments_list,
    final_pipeline,
    final_pipeline_cumulative,
    get_control_treatment_raw_data,
    get_variant_funnel,
    get_variant_funnel_cum,
    get_experiment_variants
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Lista completa de eventos disponibles en Amplitude
AVAILABLE_EVENTS = [
    "homepage_dom_loaded", 
    "everymundo_landing_dom_loaded",
    "flight_dom_loaded_flight",
    "search_clicked_home",
    "outbound_flight_selected_flight",
    "baggage_dom_loaded",
    "itinerary_dom_loaded",
    "seatmap_dom_loaded",
    "continue_clicked_baggage",
    "inbound_flight_selected_flight",
    "extras_dom_loaded",
    "continue_clicked_seat",
    "continue_clicked_extras",
    "continue_clicked_flight",
    "dc_modal_dom_loaded",
    "check_in_clicked",
    "passengers_dom_loaded",
    "checkin_passengers_dom_loaded",
    "click_header_button",
    "search_clicked_flight",
    "extra_selected",
    "payment_dom_loaded",
    "click_searchbox_header",
    "continue_clicked_checkin",
    "checkin_additional_info_dom_loaded",
    "payment_selected",
    "modal_ancillary_clicked",
    "force_select_baggage",
    "continue_clicked_passengers",
    "boarding_card_downloaded",
    "edit_booking_clicked", 
    "payment_clicked",
    "open_breakdown_mobile",
    "login_dom_loaded",
    "monthly_view_clicked",
    "user_login",
    "payment_confirmation_loaded",
    "revenue_amount",
    "click_toggle_taxes",
    "outbound_bundle_selected",
    "carousel_banner_clicked",
    "outbound_seat_selected",
    "inbound_bundle_selected",
    "continue_gender_passengers",
    "inbound_seat_selected",
    "modal_skip_direct_payment_clicked",
    "flight_dom_loaded_EXP_283",
    "filter_direct_cnx_loaded",
    "click_checkbox_miles_aa",
    "flightstatus_dom_loaded",
    "cyd_dom_loaded",
    "click_aadvantage_passengers",
    "header_my_booking_clicked",
    "installments_selected",
    "click_destinations_card",
    "user_register",
    "cyd_options_loaded",
    "force_select_extras",
    "click_thrid_parties",
    "ancillary_clicked",
    "destinos_landing_dom_loaded",
    "be_login_rut_verified",
    "payment_card_country_clicked",
    "landing_entretencion_dom_loaded",
    "error_404_dom_loaded",
    "chatbot_widget_clicked",
    "click_widgets_home",
    "error_500_dom_loaded",
    "user_logout",
    "ancillary_clicked_custom",
    "click_flightstatus_search",
    "quick_booking_dom_loaded",
    "promo_homepage_dom_loaded",
    "quick_booking_click",
    "jgo_homepage_dom_loaded",
    "click_btn_landing_entretencion",
    "edit_outbound_bundle",
    "click_taxes_toggle",
    "seo_landing_dom_loaded",
    "grant_full_consent",
    "autofill_toggle_clicked",
    "dc_membership_type_clicked",
    "count_AA_Passengers",
    "click_see_all_destinations",
    "cart_search_click",
    "click_btn_cambios_y_devoluciones",
    "seats_info_clicked",
    "header_destination_clicked",
    "buscador_smart_dom_loaded",
    "cart_header_click",
    "portal_login",
    "blog_dom_loaded",
    "millas_aa_acumular_dom_loaded",
    "button_back_clicked",
    "edit_inbound_bundle",
    "continue_clicked_payment",
    "grupos_dom_loaded",
    "header_flight_info_clicked",
    "header_benefits_clicked",
    "toggle_switch_AR",
    "continue_without_seats_clicked",
    "cart_search_remove",
    "jgo_search_dom_loaded",
    "go_to_pay_clicked",
    "alianza_aa_dom_loaded",
    "dc_membership_creation_continue_clicked",
    "click_cotiza_aqui_grupos",
    "autofill_pax_clicked",
    "reservas_en_grupo_dom_loaded",
    "flight_filter_clicked",
    "jgo_search_results_loaded",
    "millas_aa_canjear_dom_loaded",
    "jgo_plans_dom_loaded",
    "insufficient_miles_modal_loaded",
    "jgo_click_subscribe",
    "jgo_baggage_dom_loaded",
    "jgo_plan_selected",
    "vuelasmart_dom_loaded",
    "jgo_payment_redemption_loaded",
    "jgo_faq_clicked",
    "jgo_payment_redemption_clicked",
    "jgo_register_email_dom_loaded",
    "cotizar_sin_millas_clicked",
    "jgo_payment_redemption_confirmation",
    "vuelasmart_form_submit",
    "force_select_flights",
    "jgo_baggage_continue_clicked",
    "jgo_verify_email",
    "jgo_payment_register_loaded",
    "jgo_register_info_dom_loaded",
    "click_insurance_postbooking",
    "jgo_payment_register_confirmation",
    "new_lim_dom_loaded",
    "jgo_payment_register_clicked",
    "elige_otro_vuelo_clicked",
    "form_equipaje_dom_loaded",
    "group_rm_payment_confirmation",
    "form_equipaje_submit",
    "smu_landing_dom_loaded",
    "click_corporate_header_btn",
    "aadvantage_dom_loaded",
    "clicks_carousel_btn_home",
    "EXP_179_dom_loaded",
    "clicks_login_type"
]


def ensure_sys_path() -> None:
    # Asegura que el proyecto raíz esté en sys.path para importar módulos locales
    root_str = str(PROJECT_ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


@st.cache_resource(show_spinner=False)
def load_env() -> tuple[bool, str]:
    """
    Carga las variables de entorno desde el archivo .env
    
    Returns:
        tuple: (success, message) - Indica si se cargó correctamente y un mensaje informativo
    """
    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return False, "python-dotenv no está instalado. Instálalo con: pip install python-dotenv"
    
    # Intentar cargar desde múltiples ubicaciones posibles
    env_paths = [
        PROJECT_ROOT / ".env",  # Raíz del proyecto
        Path(__file__).resolve().parent / ".env",  # Carpeta streamlit/
    ]
    
    env_loaded = False
    loaded_path = None
    
    for env_path in env_paths:
        if env_path.exists():
            result = load_dotenv(dotenv_path=env_path, override=True)
            if result:
                env_loaded = True
                loaded_path = env_path
                break
        else:
            # También intentar sin especificar path (busca automáticamente)
            result = load_dotenv(dotenv_path=env_path, override=True)
            if result:
                env_loaded = True
                loaded_path = env_path
                break
    
    # Verificar que las variables críticas estén disponibles
    required_vars = ['AMPLITUDE_API_KEY', 'AMPLITUDE_SECRET_KEY', 'AMPLITUDE_MANAGEMENT_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        message = (
            f"⚠️ Variables de entorno faltantes: {', '.join(missing_vars)}\n\n"
            f"📁 Archivo .env buscado en:\n"
            f"   - {PROJECT_ROOT / '.env'}\n"
            f"   - {Path(__file__).resolve().parent / '.env'}\n\n"
            f"💡 Crea un archivo .env en una de estas ubicaciones con:\n"
            f"   AMPLITUDE_API_KEY=tu_api_key\n"
            f"   AMPLITUDE_SECRET_KEY=tu_secret_key\n"
            f"   AMPLITUDE_MANAGEMENT_KEY=tu_management_key"
        )
        return False, message
    
    if env_loaded and loaded_path:
        return True, f"✅ Variables cargadas desde: {loaded_path}"
    else:
        # Intentar carga automática (sin path específico)
        load_dotenv(override=True)
        # Verificar nuevamente
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if not missing_vars:
            return True, "✅ Variables cargadas (ubicación automática)"
        else:
            return False, (
                f"⚠️ No se encontró archivo .env en las ubicaciones esperadas.\n\n"
                f"📁 Crea un archivo .env en: {PROJECT_ROOT / '.env'}\n\n"
                f"💡 Con el siguiente contenido:\n"
                f"   AMPLITUDE_API_KEY=tu_api_key\n"
                f"   AMPLITUDE_SECRET_KEY=tu_secret_key\n"
                f"   AMPLITUDE_MANAGEMENT_KEY=tu_management_key"
            )


def run_ui():
    st.set_page_config(
        page_title="AB Test Dashboard",
        layout="wide",
        page_icon="📊"
    )

    # Header principal
    st.title("📊 AB Test Dashboard - Amplitude")
    st.markdown("---")

    # Cargar funciones de experiment_utils
    ensure_sys_path()
    env_success, env_message = load_env()

    # Estado de sesión para persistir vistas e inputs entre reruns
    if "show_experiments" not in st.session_state:
        st.session_state["show_experiments"] = False
    if "selected_exp" not in st.session_state:
        st.session_state["selected_exp"] = None

    # Sidebar con configuración básica
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Mostrar estado de carga de variables de entorno
        if env_success:
            st.success("✅ Variables de entorno cargadas")
            with st.expander("ℹ️ Ver detalles"):
                st.text(env_message)
        else:
            st.error("❌ Error cargando variables de entorno")
            with st.expander("⚠️ Ver instrucciones", expanded=True):
                st.markdown(env_message)
        
        st.caption("Las credenciales se leen desde .env en el raíz del proyecto.")

        use_cumulative = st.toggle(
            "📈 Usar acumulados (cumulativeRaw)",
            value=True,
            help="Si está activado, retorna una fila por métrica con valores acumulados"
        )

        st.divider()

        st.subheader("ℹ️ Información")
        st.info("""
        **AB Test Dashboard**
        Herramienta para analizar experimentos de Amplitude con datos de Jetsmart.
        Configura los parámetros en la sección principal y ejecuta el análisis.
        """)

    # Tabs principales
    tab_experiments, tab_statistical, tab_help = st.tabs(["📋 Experimentos", "📊 Análisis Estadístico", "❓ Ayuda"])

    with tab_experiments:
        st.subheader("🔍 Experimentos y Análisis")
        st.caption("Explora todos los experimentos disponibles y ejecuta análisis directamente")

        with st.spinner("Cargando experimentos..."):
            try:
                df_exp = get_experiments_list()

                columns_to_show = ['name', 'key', 'state', 'startDate', 'endDate', 'createdAt', 'variants']
                available_columns = [col for col in columns_to_show if col in df_exp.columns]
                df_exp_filtered = df_exp[available_columns].copy()

                date_columns = ['startDate', 'endDate', 'createdAt']
                for col in date_columns:
                    if col in df_exp_filtered.columns:
                        df_exp_filtered[col] = pd.to_datetime(df_exp_filtered[col], errors='coerce')
                        df_exp_filtered[col] = df_exp_filtered[col].dt.strftime('%Y-%m-%d')

                # Procesar columna variants
                if 'variants' in df_exp_filtered.columns:
                    def process_variants(variant_obj):
                        if variant_obj is None:
                            return "N/A"
                        try:
                            if isinstance(variant_obj, float) and pd.isna(variant_obj):
                                return "N/A"
                            if isinstance(variant_obj, list):
                                if not variant_obj:
                                    return "N/A"
                                names = []
                                for v in variant_obj:
                                    if isinstance(v, dict):
                                        names.append(v.get('name', v.get('key', str(v))))
                                    else:
                                        names.append(str(v))
                                return ", ".join(names)
                            elif isinstance(variant_obj, dict):
                                return variant_obj.get('name', variant_obj.get('key', str(variant_obj)))
                            return str(variant_obj)
                        except Exception:
                            return str(variant_obj)

                    df_exp_filtered['variants'] = df_exp_filtered['variants'].apply(process_variants)

                # Métricas de resumen
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Experimentos", len(df_exp))
                with col2:
                    active_experiments = len(df_exp[df_exp['endDate'].isna()]) if 'endDate' in df_exp.columns else "N/A"
                    st.metric("Experimentos Activos", active_experiments)
                with col3:
                    latest_exp = "N/A"
                    if 'startDate' in df_exp.columns:
                        start_dates = pd.to_datetime(df_exp['startDate'], errors='coerce')
                        latest_date = start_dates.max()
                        if pd.notna(latest_date):
                            latest_exp = latest_date.strftime("%Y-%m-%d")
                    st.metric("Último Experimento", latest_exp)

                st.dataframe(df_exp_filtered, use_container_width=True)

                # Selección de experimento para análisis
                st.markdown("### 🚀 Análisis de Experimento")
                st.caption("Selecciona un experimento de la tabla para configurar y ejecutar su análisis")
                
                # Crear lista de experimentos para seleccionar
                if len(df_exp_filtered) > 0:
                    # Crear opciones para el selectbox
                    experiment_options = []
                    for idx, row in df_exp_filtered.iterrows():
                        exp_name = row.get('name', f"Experiment {idx}")
                        exp_key = row.get('key', '')
                        exp_state = row.get('state', '')
                        display_name = f"{exp_name} ({exp_key}) - {exp_state}"
                        experiment_options.append((display_name, idx))
                    
                    selected_exp_display = st.selectbox(
                        "Selecciona un experimento:",
                        options=[opt[0] for opt in experiment_options],
                        help="Elige un experimento de la lista para configurar su análisis",
                        key="selected_exp"
                    )
                    
                    # Obtener el índice del experimento seleccionado
                    try:
                        selected_exp_idx = next(opt[1] for opt in experiment_options if opt[0] == selected_exp_display)
                        selected_row = df_exp_filtered.iloc[selected_exp_idx]
                    except StopIteration:
                        # Si no se encuentra el experimento, usar el primero como default
                        selected_exp_idx = experiment_options[0][1]
                        selected_row = df_exp_filtered.iloc[selected_exp_idx]
                    
                    # Mostrar detalles del experimento seleccionado
                    with st.expander("📋 Detalles del Experimento Seleccionado"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Nombre:** {selected_row.get('name', 'N/A')}")
                            st.write(f"**Key:** {selected_row.get('key', 'N/A')}")
                            st.write(f"**Estado:** {selected_row.get('state', 'N/A')}")
                        with col2:
                            st.write(f"**Fecha Inicio:** {selected_row.get('startDate', 'N/A')}")
                            
                            # Mostrar fecha fin o fecha de hoy si está corriendo
                            end_date_display = selected_row.get('endDate', 'N/A')
                            if pd.isna(end_date_display) or end_date_display in ['None', 'nan', '']:
                                end_date_display = f"{pd.Timestamp.now().strftime('%Y-%m-%d')} (Hoy - experimento corriendo)"
                            st.write(f"**Fecha Fin:** {end_date_display}")
                            
                            st.write(f"**Variantes:** {selected_row.get('variants', 'N/A')}")
                    
                    # Configuración rápida para el análisis
                    st.markdown("### ⚙️ Configuración del Análisis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        device_quick = st.selectbox(
                            "📱 Device",
                            options=["ALL", "desktop", "mobile"],
                            index=0,
                            key="device_quick",
                            help="Tipo de dispositivo a analizar (ALL = todos los dispositivos)"
                        )
                    with col2:
                        culture_quick = st.selectbox(
                            "🌍 Culture",
                            options=["ALL", "CL", "AR", "PE", "CO", "BR", "UY", "PY", "EC", "US", "DO"],
                            index=0,
                            key="culture_quick",
                            help="Cultura/país a analizar (ALL = todos los países)"
                        )
                    with col3:
                        conversion_window_options_quick = {
                            "5 minutos": 300,
                            "15 minutos": 900,
                            "30 minutos": 1800,
                            "1 hora": 3600,
                            "1 día": 86400
                        }
                        conversion_window_label_quick = st.selectbox(
                            "⏱️ Ventana de Conversión",
                            options=list(conversion_window_options_quick.keys()),
                            index=2,  # 30 minutos por defecto
                            key="conversion_window_quick",
                            help="Tiempo máximo para considerar una conversión válida"
                        )
                        conversion_window_quick = conversion_window_options_quick[conversion_window_label_quick]
                    
                    # Inicializar mapeo de filtros (se usará más adelante)
                    event_filters_map_quick = {}
                    metrics_to_process = []  # Inicializar siempre
                    PREDEFINED_METRICS_QUICK = {}  # Inicializar como diccionario vacío
                    
                    # Cargar métricas automáticamente desde todas las carpetas
                    try:
                        from utils.metrics_loader import (
                            load_all_metrics,
                            get_all_metrics_flat,
                            get_metrics_info
                        )
                        
                        # Cargar todas las métricas organizadas por categoría
                        metrics_by_category = load_all_metrics()
                        
                        # Obtener todas las métricas en un diccionario plano
                        PREDEFINED_METRICS_QUICK = get_all_metrics_flat(metrics_by_category)
                        
                        # Mostrar información de métricas disponibles
                        if PREDEFINED_METRICS_QUICK:
                            with st.expander("📚 Ver Métricas Disponibles", expanded=False):
                                # Generar información automáticamente
                                metrics_info_quick = get_metrics_info(PREDEFINED_METRICS_QUICK)
                                
                                if metrics_info_quick:
                                    df_metrics_quick = pd.DataFrame(metrics_info_quick)
                                    st.dataframe(
                                        df_metrics_quick,
                                        use_container_width=True,
                                        hide_index=True
                                    )
                                else:
                                    st.info("No se encontraron métricas con información válida")
                        else:
                            st.warning("⚠️ No se encontraron métricas. Asegúrate de tener archivos *_metrics.py en las carpetas de metrics/")
                        
                        # Crear dos columnas para separar métricas y eventos
                        col_metrics, col_events = st.columns(2)
                        
                        with col_metrics:
                            st.markdown("#### 🎯 Métricas Predefinidas")
                            if PREDEFINED_METRICS_QUICK:
                                selected_metrics_quick = st.multiselect(
                                    "Métricas:",
                                    options=list(PREDEFINED_METRICS_QUICK.keys()),
                                    default=[],
                                    key="metrics_quick",
                                    help="Métricas completas predefinidas"
                                )
                            else:
                                st.info("No hay métricas disponibles. Agrega archivos *_metrics.py en las carpetas de metrics/")
                                selected_metrics_quick = []
                        
                        with col_events:
                            st.markdown("#### 📊 Eventos Individuales")
                            selected_events_raw_quick = st.multiselect(
                                "Eventos:",
                                options=AVAILABLE_EVENTS,
                                default=["homepage_dom_loaded"],
                                key="events_raw_quick",
                                help="Eventos individuales"
                            )
                        
                        # Procesar cada métrica seleccionada por separado
                        for metric_name in selected_metrics_quick:
                            metric_config = PREDEFINED_METRICS_QUICK[metric_name]
                            metric_events = []
                            metric_filters_map = {}
                            
                            # Nuevo formato: {'events': [('event1', [filter1, filter2]), ('event2', [filter1])]}
                            # Siempre tuplas: ('evento', [lista_de_filtros])
                            if isinstance(metric_config, dict) and 'events' in metric_config:
                                events_list = metric_config['events']
                                
                                # Verificar si es el nuevo formato (tuplas con lista de filtros)
                                if events_list:
                                    first_item = events_list[0]
                                    
                                    # Nuevo formato: tupla con ('evento', [filtros])
                                    if isinstance(first_item, tuple) and len(first_item) >= 2:
                                        # Formato: ('evento', [filtros])
                                        for event_tuple in events_list:
                                            if isinstance(event_tuple, tuple) and len(event_tuple) >= 2:
                                                event_name = event_tuple[0]
                                                event_filters = event_tuple[1] if isinstance(event_tuple[1], list) else []
                                                
                                                metric_events.append(event_name)
                                                
                                                # Mapear filtros específicos para este evento
                                                if event_filters:
                                                    metric_filters_map[event_name] = event_filters
                                                # Si la lista está vacía, no agregar al mapa (sin filtros adicionales)
                                    
                                    elif isinstance(first_item, tuple) and len(first_item) == 1:
                                        # Formato antiguo: tupla simple ('evento',) - sin filtros
                                        for event_tuple in events_list:
                                            if isinstance(event_tuple, tuple) and len(event_tuple) > 0:
                                                event_name = event_tuple[0]
                                                metric_events.append(event_name)
                                                # Sin filtros adicionales
                                    
                                    elif isinstance(first_item, str):
                                        # Formato antiguo: lista de strings con 'filters' separado
                                        metric_events = events_list
                                        metric_filters = metric_config.get('filters', [])
                                        
                                        # Aplicar los mismos filtros a todos los eventos (comportamiento antiguo)
                                        if metric_filters:
                                            filters_list = metric_filters if isinstance(metric_filters, list) else [metric_filters]
                                            for event in metric_events:
                                                metric_filters_map[event] = filters_list.copy()
                            
                            # Formato antiguo (compatibilidad): lista simple de eventos
                            elif isinstance(metric_config, list):
                                metric_events = metric_config
                                # Sin filtros para formato antiguo
                            
                            if metric_events:
                                metrics_to_process.append({
                                    'name': metric_name,
                                    'events': metric_events,
                                    'filters': metric_filters_map
                                })
                        
                        # Agregar eventos individuales como una "métrica" adicional si están seleccionados
                        if selected_events_raw_quick:
                            metrics_to_process.append({
                                'name': 'Eventos Individuales',
                                'events': selected_events_raw_quick,
                                'filters': {}
                            })
                        
                        # Para compatibilidad con el código existente, también crear lista combinada
                        selected_events_quick = []
                        event_filters_map_quick = {}
                        for metric_info in metrics_to_process:
                            selected_events_quick.extend(metric_info['events'])
                            event_filters_map_quick.update(metric_info['filters'])
                        
                        # Eliminar duplicados manteniendo el orden
                        seen_quick = set()
                        unique_events_quick = []
                        for x in selected_events_quick:
                            if x not in seen_quick:
                                seen_quick.add(x)
                                unique_events_quick.append(x)
                        selected_events_quick = unique_events_quick
                        
                    except Exception as e:
                        # Si hay error cargando métricas, mostrar mensaje y permitir usar solo eventos
                        st.warning(f"⚠️ Error cargando métricas automáticamente: {e}")
                        st.info("💡 Puedes usar eventos individuales mientras tanto")
                        
                        # Asegurar que PREDEFINED_METRICS_QUICK esté definido
                        if 'PREDEFINED_METRICS_QUICK' not in locals():
                            PREDEFINED_METRICS_QUICK = {}
                        
                        # Permitir seleccionar eventos individuales
                        selected_metrics_quick = []
                        selected_events_raw_quick = st.multiselect(
                            "Eventos a analizar:",
                            options=AVAILABLE_EVENTS,
                            default=["homepage_dom_loaded"],
                            key="events_quick",
                            help="Selecciona los eventos que quieres analizar"
                        )
                        if selected_events_raw_quick:
                            metrics_to_process.append({
                                'name': 'Eventos Individuales',
                                'events': selected_events_raw_quick,
                                'filters': {}
                            })
                        selected_events_quick = selected_events_raw_quick if selected_events_raw_quick else []
                    
                    # Botón para ejecutar análisis rápido
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        btn_run_quick = st.button(
                            "🚀 Ejecutar Análisis de este Experimento",
                            use_container_width=True,
                            type="primary",
                            disabled=len(metrics_to_process) == 0,
                            key="btn_run_quick"
                        )
                    
                    # Ejecutar análisis si se presiona el botón
                    if btn_run_quick and metrics_to_process:
                        with st.spinner("Ejecutando análisis..."):
                            try:
                                # Obtener fechas del experimento
                                start_date_quick = selected_row.get('startDate', '2024-01-01')
                                end_date_quick = selected_row.get('endDate', pd.Timestamp.now().strftime('%Y-%m-%d'))
                                
                                # Si endDate es NaN o None, usar la fecha de hoy
                                if pd.isna(end_date_quick) or end_date_quick in ['None', 'nan', '']:
                                    end_date_quick = pd.Timestamp.now().strftime('%Y-%m-%d')
                                
                                experiment_id_quick = selected_row.get('key', '')
                                
                                # Obtener variantes del experimento para mostrar información
                                experiment_variants = get_experiment_variants(experiment_id_quick)
                                
                                # Diccionario para almacenar resultados por métrica
                                metrics_results = {}
                                
                                # Procesar cada métrica por separado
                                progress_bar = st.progress(0)
                                total_metrics = len(metrics_to_process)
                                
                                for idx, metric_info in enumerate(metrics_to_process):
                                    metric_name = metric_info['name']
                                    metric_events = metric_info['events']
                                    metric_filters = metric_info['filters']
                                    
                                    # Actualizar progreso
                                    progress_bar.progress((idx + 1) / total_metrics)
                                    
                                    # Ejecutar pipeline para esta métrica
                                    pipeline_kwargs = {
                                        'start_date': start_date_quick,
                                        'end_date': end_date_quick,
                                        'experiment_id': experiment_id_quick,
                                        'device': device_quick,
                                        'culture': culture_quick,
                                        'event_list': metric_events,
                                        'conversion_window': conversion_window_quick
                                    }
                                    
                                    # Agregar event_filters_map solo si existe y no está vacío
                                    if metric_filters:
                                        pipeline_kwargs['event_filters_map'] = metric_filters
                                    
                                    try:
                                        if use_cumulative:
                                            df_metric = final_pipeline_cumulative(**pipeline_kwargs)
                                        else:
                                            df_metric = final_pipeline(**pipeline_kwargs)
                                        
                                        # Guardar resultado de esta métrica
                                        metrics_results[metric_name] = df_metric
                                    except Exception as e:
                                        st.warning(f"⚠️ Error procesando métrica '{metric_name}': {e}")
                                        metrics_results[metric_name] = pd.DataFrame()
                                
                                progress_bar.empty()
                                
                                # Guardar todos los resultados en session_state
                                # El nombre de la métrica ya es el display name (viene de PREDEFINED_METRICS_QUICK)
                                st.session_state['metrics_results'] = metrics_results
                                st.session_state['analysis_experiment_id'] = experiment_id_quick
                                st.session_state['analysis_experiment_name'] = selected_row.get('name', experiment_id_quick)
                                
                                # Mostrar resumen de resultados
                                st.success(f"✅ Análisis completado: {len(metrics_results)} métrica(s) procesada(s)")
                                
                                # Información sobre variantes detectadas
                                if experiment_variants:
                                    st.info(f"🎯 **Variantes detectadas:** {', '.join(experiment_variants)}")
                                
                                # Mostrar resumen por métrica
                                st.markdown("### 📊 Resumen por Métrica")
                                summary_data = []
                                for metric_name, df_metric in metrics_results.items():
                                    if not df_metric.empty:
                                        summary_data.append({
                                            'Métrica': metric_name,
                                            'Registros': len(df_metric),
                                            'Variantes': df_metric['Variant'].nunique() if 'Variant' in df_metric.columns else 0,
                                            'Etapas': df_metric['Funnel Stage'].nunique() if 'Funnel Stage' in df_metric.columns else 0,
                                            'Total Eventos': f"{df_metric['Event Count'].sum():,.0f}" if 'Event Count' in df_metric.columns else "0"
                                        })
                                
                                if summary_data:
                                    summary_df = pd.DataFrame(summary_data)
                                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                                
                                # Mostrar resultados por métrica en tabs
                                if len(metrics_results) > 1:
                                    metric_tabs = st.tabs([f"📊 {name}" for name in metrics_results.keys()])
                                    for tab, (metric_name, df_metric) in zip(metric_tabs, metrics_results.items()):
                                        with tab:
                                            if not df_metric.empty:
                                                st.markdown(f"### {metric_name}")
                                                st.dataframe(df_metric, use_container_width=True)
                                                
                                                # Botón de descarga individual
                                                excel_buffer = BytesIO()
                                                df_metric.to_excel(excel_buffer, index=False, engine='openpyxl')
                                                excel_buffer.seek(0)
                                                st.download_button(
                                                    label=f"📥 Descargar {metric_name}",
                                                    data=excel_buffer.getvalue(),
                                                    file_name=f"ab_test_{metric_name.replace(' ', '_')}_{experiment_id_quick}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                    key=f"download_{metric_name}"
                                                )
                                            else:
                                                st.warning(f"No hay datos disponibles para la métrica '{metric_name}'")
                                else:
                                    # Si solo hay una métrica, mostrar directamente
                                    metric_name = list(metrics_results.keys())[0]
                                    df_metric = metrics_results[metric_name]
                                    
                                    if not df_metric.empty:
                                        st.dataframe(df_metric, use_container_width=True)
                                        
                                        # Botón de descarga
                                        col1, col2, col3 = st.columns([1, 1, 1])
                                        with col2:
                                            excel_buffer_quick = BytesIO()
                                            df_metric.to_excel(excel_buffer_quick, index=False, engine='openpyxl')
                                            excel_buffer_quick.seek(0)
                                            st.download_button(
                                                label="📥 Descargar Excel",
                                                data=excel_buffer_quick.getvalue(),
                                                file_name=f"ab_test_results_{experiment_id_quick}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                use_container_width=True
                                            )
                                    
                            except Exception as e:
                                st.error(f"❌ Error ejecutando análisis: {e}")
                                st.exception(e)
                
                # Botón de descarga para experimentos
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    # Crear buffer para Excel
                    excel_buffer = BytesIO()
                    df_exp_filtered.to_excel(excel_buffer, index=False, engine='openpyxl')
                    excel_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Descargar Lista de Experimentos",
                        data=excel_buffer.getvalue(),
                        file_name=f"experiments_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )

            except ValueError as e:
                st.error(f"❌ Error de configuración o datos inválidos: {e}")
                st.info("💡 **Sugerencias:**\n"
                       "- Verifica que la variable de entorno `AMPLITUDE_MANAGEMENT_KEY` esté configurada correctamente\n"
                       "- Asegúrate de que el archivo `.env` existe y contiene las credenciales necesarias\n"
                       "- Revisa que la API key tenga los permisos necesarios para acceder a los experimentos")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Error de conexión con la API de Amplitude: {e}")
                st.info("💡 **Sugerencias:**\n"
                       "- Verifica tu conexión a internet\n"
                       "- Comprueba que la URL de la API sea correcta\n"
                       "- Revisa que no haya problemas de firewall o proxy")
            except Exception as e:
                st.error(f"❌ Error inesperado al listar experimentos: {e}")
                st.exception(e)

    with tab_statistical:
        st.subheader("📊 Análisis Estadístico A/B/N")
        st.caption("Análisis estadístico completo con p-values, lift, P2BB y significancia")
        
        # Verificar si hay datos disponibles (nuevo formato con múltiples métricas o formato antiguo)
        has_metrics_results = 'metrics_results' in st.session_state and st.session_state['metrics_results']
        has_single_df = 'analysis_df' in st.session_state and st.session_state['analysis_df'] is not None and not st.session_state['analysis_df'].empty
        
        if not has_metrics_results and not has_single_df:
            st.info("""
            ℹ️ **No hay datos disponibles para análisis estadístico**
            
            Para usar esta funcionalidad:
            1. Ve a la pestaña **📋 Experimentos**
            2. Selecciona un experimento y ejecuta un análisis
            3. Los resultados estarán disponibles aquí para análisis estadístico
            """)
        else:
            experiment_id_stat = st.session_state.get('analysis_experiment_id', 'N/A')
            experiment_name_stat = st.session_state.get('analysis_experiment_name', 'N/A')
            
            # Determinar qué métrica(s) analizar
            if has_metrics_results:
                # Nuevo formato: múltiples métricas - mostrar todas de una vez
                metrics_results = st.session_state['metrics_results']
                available_metrics = [(name, df) for name, df in metrics_results.items() if df is not None and not df.empty]
                
                if not available_metrics:
                    st.warning("⚠️ No hay métricas con datos disponibles para análisis")
                else:
                    # Mostrar información del experimento
                    st.markdown(f"""
                    <div style="background: linear-gradient(90deg, #1B365D 0%, #4A6489 100%); 
                                border: 2px solid #3CCFE7; 
                                border-radius: 12px; 
                                padding: 20px; 
                                margin: 20px 0; 
                                text-align: center;">
                        <h3 style="color: white; margin: 0; font-size: 1.3em;">
                            🧪 {experiment_name_stat} ({experiment_id_stat})
                        </h3>
                        <p style="color: #E0E0E0; margin: 10px 0 0 0;">
                            📊 Total de métricas analizadas: <strong>{len(available_metrics)}</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Importar funciones de análisis estadístico
                    from utils.statistical_analysis import (
                        prepare_variants_from_dataframe,
                        calculate_ab_test,
                        calculate_chi_square_test,
                        create_metric_card,
                        create_multivariant_card
                    )
                    
                    # Procesar cada métrica y mostrar en su propio recuadro
                    for metric_key, df_analysis in available_metrics:
                        # El nombre de la métrica ya es el display name
                        metric_display_name = metric_key
                        
                        # Crear un recuadro/separador para cada métrica
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #1B365D 0%, #3A5478 100%); 
                                    border: 3px solid #3CCFE7; 
                                    border-radius: 15px; 
                                    padding: 25px; 
                                    margin: 30px 0; 
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                            <h2 style="color: white; margin: 0 0 15px 0; font-size: 1.5em; text-align: center;">
                                📊 {metric_display_name}
                            </h2>
                            <p style="color: #E0E0E0; margin: 0; text-align: center; font-size: 0.9em;">
                                Total de registros: {len(df_analysis):,}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Análisis estadístico para esta métrica
                        if 'Funnel Stage' in df_analysis.columns:
                            # Obtener etapas únicas del funnel
                            available_stages = df_analysis['Funnel Stage'].unique().tolist()
                            
                            # Obtener el orden correcto de eventos desde la configuración de la métrica
                            # Cargar métricas automáticamente para buscar la configuración
                            metric_config = None
                            try:
                                from utils.metrics_loader import get_all_metrics_flat
                                all_metrics = get_all_metrics_flat()
                                metric_config = all_metrics.get(metric_display_name)
                            except Exception:
                                # Si no se pueden cargar, continuar sin configuración
                                pass
                            
                            # Determinar initial_stage y final_stage según el orden de eventos en la métrica
                            if metric_config and 'events' in metric_config and len(metric_config['events']) >= 2:
                                # Extraer nombres de eventos (pueden ser tuplas o strings)
                                event_names = []
                                for event_item in metric_config['events']:
                                    if isinstance(event_item, tuple) and len(event_item) > 0:
                                        event_names.append(event_item[0])
                                    elif isinstance(event_item, str):
                                        event_names.append(event_item)
                                
                                # Usar el orden de eventos de la métrica
                                # Para WCR: conversión = revenue_amount / baggage_dom_loaded
                                # En prepare_variants_from_dataframe:
                                #   - initial_stage → n (denominador) = baggage_dom_loaded
                                #   - final_stage → x (numerador) = revenue_amount
                                # Conversión = x/n = final_stage / initial_stage
                                
                                # Función auxiliar para normalizar nombres de eventos
                                def normalize_event_name(name):
                                    """Normaliza el nombre del evento removiendo prefijos y espacios"""
                                    # Remover prefijos comunes como [Amplitude]
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Manejar custom events con prefijo ce:
                                    if name.startswith('ce:'):
                                        name = name[3:].strip()  # Remover 'ce:'
                                        # Remover paréntesis si existen: 'ce:(NEW) evento' -> 'evento'
                                        if name.startswith('('):
                                            end_paren = name.find(')')
                                            if end_paren != -1:
                                                name = name[end_paren + 1:].strip()
                                    # Convertir a minúsculas y normalizar espacios
                                    return name.lower().strip()
                                
                                # Función auxiliar para extraer palabra clave del evento
                                def get_event_keyword(name):
                                    """Extrae la palabra clave principal del nombre del evento"""
                                    # Remover prefijos
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Manejar custom events
                                    if name.startswith('ce:'):
                                        name = name[3:].strip()
                                        if name.startswith('('):
                                            end_paren = name.find(')')
                                            if end_paren != -1:
                                                name = name[end_paren + 1:].strip()
                                    # Convertir a minúsculas
                                    name = name.lower()
                                    # Si tiene guiones bajos, tomar la primera parte (más significativa)
                                    if '_' in name:
                                        parts = name.split('_')
                                        # Para revenue_amount, tomar 'revenue'
                                        # Para baggage_dom_loaded, tomar 'baggage'
                                        return parts[0] if len(parts) > 0 else name
                                    # Si no tiene guiones bajos, devolver el nombre completo
                                    # (para '[Amplitude] Revenue' → 'revenue')
                                    return name
                                
                                # Función auxiliar para buscar stage por evento
                                def find_stage_by_event(event_name, available_stages, exclude_stage=None):
                                    """Busca un stage que coincida con el nombre del evento"""
                                    # Normalizar el evento
                                    normalized_event = normalize_event_name(event_name)
                                    keyword_event = get_event_keyword(event_name)
                                    
                                    # 1. Coincidencia exacta
                                    for stage in available_stages:
                                        if stage == event_name and stage != exclude_stage:
                                            return stage
                                    
                                    # 2. Coincidencia normalizada exacta
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            normalized_stage = normalize_event_name(stage)
                                            if normalized_event == normalized_stage:
                                                return stage
                                    
                                    # 3. Coincidencia por palabra clave
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            keyword_stage = get_event_keyword(stage)
                                            if keyword_event == keyword_stage and keyword_event:
                                                return stage
                                    
                                    # 4. Coincidencia parcial (el evento contiene el stage o viceversa)
                                    for stage in available_stages:
                                        if stage != exclude_stage:
                                            normalized_stage = normalize_event_name(stage)
                                            keyword_stage = get_event_keyword(stage)
                                            if (normalized_event in normalized_stage or normalized_stage in normalized_event or
                                                keyword_event in keyword_stage or keyword_stage in keyword_event):
                                                return stage
                                    
                                    return None
                                
                                # Buscar el primer evento (initial_stage) - debe ser el denominador
                                initial_stage = find_stage_by_event(event_names[0], available_stages)
                                
                                # Buscar el último evento (final_stage) - debe ser el numerador
                                # Excluir initial_stage para asegurar que sean diferentes
                                final_stage = find_stage_by_event(event_names[-1], available_stages, exclude_stage=initial_stage)
                                
                                # Si aún no se encuentran, usar orden alfabético como fallback
                                # PERO asegurando que siempre sean diferentes
                                if not initial_stage or not final_stage:
                                    funnel_stages = sorted(available_stages)
                                    
                                    if not initial_stage:
                                        initial_stage = funnel_stages[0]
                                    
                                    if not final_stage:
                                        # Buscar un stage diferente al initial_stage
                                        for stage in funnel_stages:
                                            if stage != initial_stage:
                                                final_stage = stage
                                                break
                                        # Si no hay otro stage, usar el último (que debería ser diferente si hay más de uno)
                                        if not final_stage:
                                            if len(funnel_stages) > 1:
                                                final_stage = funnel_stages[-1]
                                            else:
                                                # Solo hay un stage disponible - no podemos hacer análisis
                                                initial_stage = None
                                                final_stage = None
                                    
                                    # Verificación final: asegurar que sean diferentes
                                    if initial_stage == final_stage and len(funnel_stages) > 1:
                                        # Si son iguales pero hay más stages, usar el primero y el último
                                        initial_stage = funnel_stages[0]
                                        final_stage = funnel_stages[-1]
                            else:
                                # Fallback: usar orden alfabético inteligente (ignorando prefijos)
                                # Normalizar nombres para ordenar (remover [Amplitude] y otros prefijos)
                                def normalize_for_sorting(name):
                                    """Normaliza el nombre para ordenamiento, removiendo prefijos"""
                                    # Remover prefijos comunes
                                    name = name.replace('[Amplitude]', '').strip()
                                    # Convertir a minúsculas y remover espacios
                                    name = name.lower().strip()
                                    # Priorizar eventos que empiezan con ciertas palabras clave
                                    # (baggage, seatmap, etc. suelen ser eventos iniciales)
                                    priority_keywords = ['baggage', 'seatmap', 'checkout', 'payment']
                                    for keyword in priority_keywords:
                                        if name.startswith(keyword):
                                            return f"0_{name}"  # Prioridad alta (viene primero)
                                    return f"1_{name}"  # Prioridad normal
                                
                                # Ordenar por nombre normalizado, pero mantener los nombres originales
                                sorted_stages = sorted(available_stages, key=normalize_for_sorting)
                                initial_stage = sorted_stages[0]
                                final_stage = sorted_stages[-1] if len(sorted_stages) > 1 else sorted_stages[0]
                            
                            # Verificar que tenemos stages válidos y diferentes
                            if initial_stage and final_stage and initial_stage != final_stage:
                                    # Preparar variantes
                                    variants = prepare_variants_from_dataframe(
                                        df_analysis,
                                        initial_stage=initial_stage,
                                        final_stage=final_stage
                                    )
                                    
                                    if len(variants) >= 2:
                                        # Análisis según número de variantes
                                        if len(variants) == 2:
                                            # Análisis A/B simple
                                            control = variants[0]
                                            treatment = variants[1]
                                            
                                            results = calculate_ab_test(
                                                control['n'], control['x'],
                                                treatment['n'], treatment['x']
                                            )
                                            
                                            # Crear estructura de datos para la tarjeta
                                            comparison_data = {
                                                'baseline': control,
                                                'treatment': treatment
                                            }
                                            
                                            # Mostrar tarjeta de métrica usando el nombre de la métrica
                                            create_metric_card(metric_display_name, comparison_data, results, experiment_name_stat)
                                            
                                        else:
                                            # Análisis multivariante - usar diseño de tabla
                                            # Test Chi-cuadrado global
                                            chi_square_result = calculate_chi_square_test(variants)
                                            with st.expander(f"📊 Test Chi-cuadrado Global - {metric_display_name}", expanded=True):
                                                st.markdown(f"""
                                                **Test Chi-cuadrado:** {'✓ Significativo' if chi_square_result['significant'] else '✗ No significativo'} 
                                                (p-value: {chi_square_result['p_value']:.4f}, χ²: {chi_square_result['chi2']:.2f})
                                                
                                                Este test evalúa si existe una diferencia significativa entre **todas** las variantes de forma global.
                                                """)
                                            
                                            # Mostrar tarjeta multivariante con diseño de tabla
                                            create_multivariant_card(metric_display_name, variants, experiment_name_stat, chi_square_result)
                                    else:
                                        st.warning(f"⚠️ Se necesitan al menos 2 variantes para el análisis estadístico de '{metric_display_name}'. Se encontraron {len(variants)} variantes.")
                            else:
                                # Construir mensaje de error más informativo
                                error_msg = f"⚠️ **No se pudieron encontrar etapas diferentes** para la métrica '{metric_display_name}'\n\n"
                                
                                if metric_config and 'events' in metric_config:
                                    event_names = []
                                    for event_item in metric_config['events']:
                                        if isinstance(event_item, tuple) and len(event_item) > 0:
                                            event_names.append(event_item[0])
                                        elif isinstance(event_item, str):
                                            event_names.append(event_item)
                                    
                                    if event_names:
                                        error_msg += f"**Eventos esperados:**\n"
                                        error_msg += f"- Inicial: `{event_names[0]}`\n"
                                        error_msg += f"- Final: `{event_names[-1]}`\n\n"
                                
                                error_msg += f"**Etapas disponibles en los datos:** {', '.join(f'`{s}`' for s in available_stages)}\n\n"
                                
                                if initial_stage and final_stage:
                                    error_msg += f"**Etapas detectadas:** Inicial=`{initial_stage}`, Final=`{final_stage}` (son iguales)\n\n"
                                elif not initial_stage or not final_stage:
                                    error_msg += f"**Problema:** No se pudo encontrar una coincidencia para los eventos de la métrica en los datos disponibles.\n\n"
                                
                                error_msg += "💡 **Sugerencias:**\n"
                                error_msg += "- Verifica que los eventos de la métrica coincidan con los nombres en los datos\n"
                                error_msg += "- Asegúrate de que haya al menos 2 etapas diferentes en el funnel\n"
                                error_msg += "- Revisa que los custom events (ce:) estén correctamente formateados"
                                
                                st.warning(error_msg)
                        else:
                            # Si no hay Funnel Stage, hacer análisis simple por variante
                            st.info(f"ℹ️ No se detectó columna 'Funnel Stage' para '{metric_display_name}'. Realizando análisis simple por variante.")
                            
                            variants = prepare_variants_from_dataframe(df_analysis)
                            
                            if len(variants) >= 2:
                                # Análisis
                                if len(variants) == 2:
                                    control = variants[0]
                                    treatment = variants[1]
                                    
                                    results = calculate_ab_test(
                                        control['n'], control['x'],
                                        treatment['n'], treatment['x']
                                    )
                                    
                                    comparison_data = {
                                        'baseline': control,
                                        'treatment': treatment
                                    }
                                    
                                    create_metric_card(metric_display_name, comparison_data, results, experiment_name_stat)
                                else:
                                    # Multivariante - usar diseño de tabla
                                    chi_square_result = calculate_chi_square_test(variants)
                                    with st.expander(f"📊 Test Chi-cuadrado Global - {metric_display_name}", expanded=True):
                                        st.markdown(f"""
                                        **Test Chi-cuadrado:** {'✓ Significativo' if chi_square_result['significant'] else '✗ No significativo'} 
                                        (p-value: {chi_square_result['p_value']:.4f}, χ²: {chi_square_result['chi2']:.2f})
                                        
                                        Este test evalúa si existe una diferencia significativa entre **todas** las variantes de forma global.
                                        """)
                                    
                                    # Mostrar tarjeta multivariante con diseño de tabla
                                    create_multivariant_card(metric_display_name, variants, experiment_name_stat, chi_square_result)
                            else:
                                st.warning(f"⚠️ Se necesitan al menos 2 variantes para el análisis estadístico de '{metric_display_name}'")
                        
                        # Separador entre métricas
                        st.markdown("<hr style='margin: 40px 0; border: 1px solid #3CCFE7;'>", unsafe_allow_html=True)

    with tab_help:
        st.subheader("❓ Guía de Uso")
        st.markdown("""
        ### 🎯 Cómo usar el AB Test Dashboard
        1. **Configuración:** Ajusta los parámetros en la barra lateral  
        2. **Selección de Eventos:** Elige los eventos que quieres analizar  
        3. **Ejecución:** Haz clic en "Ejecutar Análisis" para obtener resultados

        ### 📊 Tipos de Análisis
        - **Diario:** Datos día por día  
        - **Acumulado:** Valores totales del período

        ### 🔧 Parámetros
        - **Device:** Tipo de dispositivo (ALL, desktop, mobile)  
        - **Culture:** País/región (ALL, CL, AR, PE, CO, BR, UY, PY, EC, US, DO)  
        - **Ventana de Conversión:** Tiempo máximo para una conversión válida  

        ### 📋 Eventos Disponibles
        Incluye todos los eventos de tracking de Jetsmart (`*_dom_loaded`, `*_clicked`, etc.)

        ### 🔑 Credenciales
        Las credenciales de Amplitude se leen desde el archivo `.env`:
        ```
        AMPLITUDE_API_KEY=tu_api_key
        AMPLITUDE_SECRET_KEY=tu_secret_key
        AMPLITUDE_MANAGEMENT_KEY=tu_management_key
        ```

        ### ➕ Cómo Agregar Nuevas Métricas

        Para agregar nuevas métricas al dashboard, sigue estos pasos:

        #### 1. Crear archivo de métricas
        Crea un archivo `[step]_metrics/[step]_metrics.py` siguiendo el formato de `baggage_metrics.py`:

        ```python
        # filtros amplitude
        from utils.amplitude_filters import (
            cabin_bag_filter,
            checked_bag_filter,
            get_DB_filter
        )

        # Next Step Rate [Step] - General (sin filtros adicionales)
        NSR_[STEP] = {'events': [
            ('evento_inicial', []),
            ('evento_final', [])
        ]}

        # Website Conversion Rate from [Step] - General (sin filtros adicionales)
        WCR_[STEP] = {'events': [
            ('evento_inicial', []),
            ('revenue_amount', [])
        ]}

        # [Step] A2C con filtros específicos aplicados a ambos eventos
        [STEP]_A2C = {'events': [
            ('evento_inicial', [filtro_especifico()]),
            ('evento_final', [filtro_especifico()])
        ]}

        # Métrica con filtros diferentes por evento
        METRIC_CUSTOM = {'events': [
            ('evento_inicial', [get_DB_filter()]),  # Primer evento con filtro DB
            ('evento_final', [])  # Segundo evento sin filtros - lista vacía
        ]}
        ```

        **📌 Formato de Métricas:**
        - **Todas las métricas** deben usar el formato `{'events': [...]}`
        - **SIEMPRE usa tuplas** `('evento', [filtros])`
        - **El segundo elemento es siempre una lista** de filtros: `[filtro1, filtro2, ...]`
        - **Si no hay filtros**, usa lista vacía: `[]`
        - **Puedes agregar tantos eventos como necesites** (2, 3, 4, 5+ eventos)
        - **Cada evento puede tener sus propios filtros** independientemente de los demás
        - **Los eventos se procesan en orden** como un funnel secuencial

        #### 2. ¡Listo! 🎉
        **Ya no necesitas modificar `app.py`**. El sistema detecta automáticamente todas las métricas desde las carpetas de `metrics/`.
        
        Las métricas se cargan automáticamente y aparecerán en el dashboard con:
        - ✅ Nombres descriptivos generados automáticamente
        - ✅ Información de eventos y filtros
        - ✅ Organización por categoría (baggage, seats, payment, etc.)
        
        **El sistema detecta automáticamente:**
        - Archivos `*_metrics.py` en cualquier subcarpeta de `metrics/`
        - Variables en mayúsculas que sean métricas válidas
        - Genera nombres de display con emojis según la categoría
        - Organiza y muestra toda la información automáticamente

        #### 📚 Documentación Completa
        Para más detalles, consulta:
        - `streamlit/METRICS_GUIDE.md` - Guía completa
        - `streamlit/EXAMPLE_SEATS_METRICS.py` - Ejemplo práctico
        """)


if __name__ == "__main__":
    run_ui()