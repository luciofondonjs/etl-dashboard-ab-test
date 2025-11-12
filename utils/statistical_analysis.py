"""
Módulo de análisis estadístico para pruebas A/B/N.
Proporciona funciones para calcular p-values, lift, P2BB y otras métricas estadísticas.
"""

import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
import plotly.graph_objects as go
from itertools import combinations
import streamlit as st


def calculate_ab_test(control_n, control_x, treatment_n, treatment_x):
    """
    Calcula estadísticas de prueba A/B.
    
    Args:
        control_n: Número total de sesiones/usuarios en control
        control_x: Número de conversiones en control
        treatment_n: Número total de sesiones/usuarios en treatment
        treatment_x: Número de conversiones en treatment
        
    Returns:
        dict: Diccionario con estadísticas calculadas
    """
    control_p = control_x / control_n if control_n > 0 else 0
    treatment_p = treatment_x / treatment_n if treatment_n > 0 else 0
    
    # Calcular error estándar
    se = np.sqrt(
        (control_p * (1 - control_p) / control_n) +
        (treatment_p * (1 - treatment_p) / treatment_n)
    ) if control_n > 0 and treatment_n > 0 else 0
    
    # Calcular z-score
    z_score = (treatment_p - control_p) / se if se > 0 else 0
    
    # Calcular p-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score))) if se > 0 else 1
    
    # Calcular lift relativo
    relative_lift = ((treatment_p - control_p) / control_p) * 100 if control_p > 0 else 0
    
    # Calcular probabilidad bayesiana (P2BB)
    n_simulations = 10000
    baseline_posterior = np.random.beta(control_x + 1, control_n - control_x + 1, n_simulations)
    treatment_posterior = np.random.beta(treatment_x + 1, treatment_n - treatment_x + 1, n_simulations)
    p2bb = np.mean(treatment_posterior > baseline_posterior)
    
    return {
        'control_p': control_p,
        'treatment_p': treatment_p,
        'se': se,
        'z_score': z_score,
        'p_value': p_value,
        'relative_lift': relative_lift,
        'p2bb': p2bb
    }


def calculate_single_comparison(variant_a, variant_b, is_control_comparison=False):
    """
    Calcula estadísticas para una comparación entre dos variantes.
    
    Args:
        variant_a: Diccionario con 'name', 'n' (sesiones), 'x' (conversiones)
        variant_b: Diccionario con 'name', 'n' (sesiones), 'x' (conversiones)
        is_control_comparison: Si es True, indica que variant_a es el control
        
    Returns:
        dict: Diccionario con estadísticas de la comparación
    """
    a_p = variant_a['x'] / variant_a['n'] if variant_a['n'] > 0 else 0
    b_p = variant_b['x'] / variant_b['n'] if variant_b['n'] > 0 else 0
    
    # Calcular error estándar
    se = np.sqrt(
        (a_p * (1 - a_p) / variant_a['n']) +
        (b_p * (1 - b_p) / variant_b['n'])
    ) if variant_a['n'] > 0 and variant_b['n'] > 0 else 0
    
    # Calcular z-score
    if se > 0:
        z_score = (b_p - a_p) / se
        # Calcular p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
    else:
        z_score = 0
        p_value = 1
    
    # Calcular lift relativo
    if a_p > 0:
        relative_lift = ((b_p - a_p) / a_p) * 100
    else:
        relative_lift = 0
    
    # Calcular probabilidad bayesiana
    n_simulations = 10000
    a_posterior = np.random.beta(variant_a['x'] + 1, variant_a['n'] - variant_a['x'] + 1, n_simulations)
    b_posterior = np.random.beta(variant_b['x'] + 1, variant_b['n'] - variant_b['x'] + 1, n_simulations)
    p2bb = np.mean(b_posterior > a_posterior)
    
    return {
        'variant_a_name': variant_a['name'],
        'variant_b_name': variant_b['name'],
        'variant_a_p': a_p,
        'variant_b_p': b_p,
        'relative_lift': relative_lift,
        'p_value': p_value,
        'p2bb': p2bb,
        'significant': p_value < 0.05,
        'is_control_comparison': is_control_comparison
    }


def calculate_chi_square_test(variants):
    """
    Calcula test Chi-cuadrado para múltiples variantes.
    
    Args:
        variants: Lista de diccionarios con 'n' (sesiones) y 'x' (conversiones)
        
    Returns:
        dict: Resultados del test Chi-cuadrado
    """
    # Crear tabla de contingencia
    conversions = [variant['x'] for variant in variants]
    non_conversions = [variant['n'] - variant['x'] for variant in variants]
    
    # Tabla de contingencia: [conversiones, no_conversiones] para cada variante
    contingency_table = np.array([conversions, non_conversions])
    
    # Test Chi-cuadrado
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    return {
        'chi2': chi2,
        'p_value': p_value,
        'dof': dof,
        'significant': p_value < 0.05
    }


def calculate_all_pairwise_comparisons(variants):
    """
    Calcula todas las comparaciones pareadas posibles entre variantes.
    
    Args:
        variants: Lista de diccionarios con 'name', 'n', 'x'
        
    Returns:
        list: Lista de diccionarios con resultados de cada comparación
    """
    all_comparisons = []
    
    # Generar todas las combinaciones posibles de variantes
    for i in range(len(variants)):
        for j in range(i + 1, len(variants)):
            variant_a = variants[i]
            variant_b = variants[j]
            
            comparison = calculate_single_comparison(variant_a, variant_b, is_control_comparison=(i == 0))
            all_comparisons.append(comparison)
    
    return all_comparisons


def get_smart_label(name):
    """
    Genera etiquetas inteligentes y diferenciadas para nombres de variantes.
    
    Args:
        name: Nombre de la variante
        
    Returns:
        str: Etiqueta abreviada
    """
    # Si el nombre es corto (≤4 chars), usarlo completo
    if len(name) <= 4:
        return name
    
    # Para nombres como "Variant-A", "Variant-B", tomar la parte después del guión
    if '-' in name:
        parts = name.split('-')
        if len(parts) >= 2 and parts[-1]:  # Si hay algo después del último guión
            return parts[-1][:4]  # Tomar hasta 4 chars de la parte final
    
    # Para nombres como "Control", "Baseline", "Treatment-1", etc.
    # Usar las primeras letras de cada palabra + números si los hay
    words = name.replace('-', ' ').replace('_', ' ').split()
    
    if len(words) == 1:
        # Una sola palabra: tomar primeras letras + números
        word = words[0]
        letters = ''.join([c for c in word if c.isalpha()])[:3]
        numbers = ''.join([c for c in word if c.isdigit()])
        return (letters + numbers)[:4]
    else:
        # Múltiples palabras: primera letra de cada palabra + números
        initials = ''.join([word[0] for word in words if word and word[0].isalpha()])
        numbers = ''.join([c for c in name if c.isdigit()])
        return (initials + numbers)[:4]


def prepare_variants_from_dataframe(df, initial_stage=None, final_stage=None):
    """
    Prepara datos de variantes desde un DataFrame del ETL para análisis estadístico.
    
    Args:
        df: DataFrame con columnas 'Variant', 'Event Count', y 'Funnel Stage'
        initial_stage: Etapa inicial del funnel (para calcular 'n' - sesiones)
        final_stage: Etapa final del funnel (para calcular 'x' - conversiones)
        
    Returns:
        list: Lista de diccionarios con formato {'name': str, 'n': int, 'x': int}
    """
    if 'Variant' not in df.columns or 'Event Count' not in df.columns:
        return []
    
    # Si no hay Funnel Stage, usar agregación simple
    if 'Funnel Stage' not in df.columns:
        variant_data = df.groupby('Variant')['Event Count'].agg(['sum', 'count']).reset_index()
        variant_data.columns = ['Variant', 'total_events', 'total_records']
        
        variants = []
        for _, row in variant_data.iterrows():
            variants.append({
                'name': str(row['Variant']),
                'n': int(row['total_records']),  # Total de registros como proxy de sesiones
                'x': int(row['total_events'])  # Total de eventos
            })
        return variants
    
    # Si se especifican etapas, usar lógica de funnel
    if initial_stage and final_stage:
        variants_dict = {}
        
        # Obtener todas las variantes
        all_variants = df['Variant'].unique()
        
        for variant in all_variants:
            variant_df = df[df['Variant'] == variant].copy()
            
            # n: total de eventos en la etapa inicial
            initial_df = variant_df[variant_df['Funnel Stage'] == initial_stage]
            n = int(initial_df['Event Count'].sum()) if not initial_df.empty else 0
            
            # x: total de eventos en la etapa final
            final_df = variant_df[variant_df['Funnel Stage'] == final_stage]
            x = int(final_df['Event Count'].sum()) if not final_df.empty else 0
            
            if n > 0:  # Solo incluir si hay datos en la etapa inicial
                variants_dict[variant] = {
                    'name': str(variant),
                    'n': n,
                    'x': x
                }
        
        return list(variants_dict.values())
    
    # Si solo se especifica una etapa, usar agregación por variante
    elif initial_stage or final_stage:
        stage = initial_stage or final_stage
        stage_df = df[df['Funnel Stage'] == stage].copy()
        
        variant_data = stage_df.groupby('Variant')['Event Count'].agg(['sum', 'count']).reset_index()
        variant_data.columns = ['Variant', 'total_events', 'total_records']
        
        variants = []
        for _, row in variant_data.iterrows():
            variants.append({
                'name': str(row['Variant']),
                'n': int(row['total_records']),
                'x': int(row['total_events'])
            })
        return variants
    
    # Si no se especifican etapas, agregar por variante
    else:
        variant_data = df.groupby('Variant')['Event Count'].agg(['sum', 'count']).reset_index()
        variant_data.columns = ['Variant', 'total_events', 'total_records']
        
        variants = []
        for _, row in variant_data.iterrows():
            variants.append({
                'name': str(row['Variant']),
                'n': int(row['total_records']),
                'x': int(row['total_events'])
            })
        return variants


def prepare_variants_by_funnel_stage(df):
    """
    Prepara variantes agrupadas por etapa del funnel.
    
    Args:
        df: DataFrame con columnas 'Variant', 'Funnel Stage', 'Event Count'
        
    Returns:
        dict: Diccionario con {funnel_stage: [variants]}
    """
    if 'Funnel Stage' not in df.columns:
        return {}
    
    result = {}
    funnel_stages = df['Funnel Stage'].unique()
    
    for stage in funnel_stages:
        variants = prepare_variants_from_dataframe(df, funnel_stage=stage)
        if variants:
            result[stage] = variants
    
    return result


def create_metric_card(metric_name, data, results, experiment_title=None):
    """
    Crea una tarjeta estilizada para una métrica.
    
    Args:
        metric_name: Nombre de la métrica
        data: Diccionario con 'baseline' y 'treatment' (cada uno con 'name', 'n', 'x')
        results: Diccionario con resultados estadísticos
        experiment_title: Título opcional del experimento
    """
    st.markdown("""
        <style>
        .metric-card {
            width: 600px;
            height: 350px;
            background: #4A6489;
            box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            margin: 20px auto;
            color: white;
            position: relative;
            overflow: hidden;
        }
        .metric-header {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            padding: 16px;
            gap: 10px;
            width: 100%;
            height: 54px;
            background: #FFFFFF;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .metric-header-emoji {
            font-size: 24px;
            line-height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 8px;
        }
        .metric-header-text {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 900;
            font-size: 22px;
            line-height: 26px;
            color: #1B365D;
            display: flex;
            align-items: center;
        }
        .metric-content {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            padding: 0 20px;
            gap: 20px;
            height: 100px;
            margin-top: 10px;
            margin-bottom: 40px;
        }
        .metric-section {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .metric-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #FFFFFF;
            margin-bottom: 4px;
            text-align: left;
        }
        .conversion-container {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .conversion-row {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .conversion-label {
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 14px;
            line-height: 18px;
            color: #FFFFFF;
            width: 40px;
            text-align: center;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .metric-value {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 80px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #1B365D;
        }
        .metric-improvement {
            box-sizing: border-box;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 6px 12px;
            min-width: 100px;
            height: 34px;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-style: normal;
            font-weight: 700;
            font-size: 16px;
            line-height: 20px;
            color: #69BE28;
        }
        .p2bb-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding-top: 0;
            width: 100%;
            margin-top: 0;
        }
        .p2bb-chart {
            width: 100%;
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 0px;
            align-items: center;
        }
        .p2bb-bar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: auto;
        }
        .bar-container {
            width: 94px;
            height: 34px;
            background: #FFFFFF;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
        }
        .bar-fill {
            height: 100%;
            position: absolute;
            left: 0;
            top: 0;
            background: #3CCFE7;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .bar-value {
            font-family: 'Clan OT', sans-serif;
            font-weight: 700;
            font-size: 14px;
            position: absolute;
            width: 100%;
            text-align: center;
            z-index: 1;
        }
        .significance-label {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            padding: 8px 20px;
            border-radius: 20px;
            font-family: 'Clan OT', sans-serif;
            font-weight: 700;
            font-size: 13px;
            color: white;
            text-align: center;
        }
        .experiment-title-small {
            background: #3CCFE7;
            color: #1B365D;
            padding: 6px 12px;
            border-radius: 8px;
            font-family: 'Clan OT', sans-serif;
            font-weight: 700;
            font-size: 14px;
            text-align: center;
            margin: 8px 20px 8px 20px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        </style>
    """, unsafe_allow_html=True)

    # Determinar los porcentajes y redondearlos
    v1_percentage = round(results['p2bb'] * 100)
    og_percentage = round((1 - results['p2bb']) * 100)
    
    # Determinar si es significativo
    is_significant = results['p_value'] < 0.05
    significance_text = "✓ Significativo" if is_significant else "✗ No significativo"
    significance_color = "#2E7D32" if is_significant else "#C62828"
    
    # Construir HTML con título del experimento
    experiment_title_html = ""
    if experiment_title:
        experiment_title_html = f'<div class="experiment-title-small">🧪 {experiment_title}</div>'
    
    st.markdown(f"""
        <div class="metric-card">
            {experiment_title_html}
            <div class="metric-header">
                <span class="metric-header-emoji">🎯</span>
                <span class="metric-header-text">{metric_name}</span>
            </div>
            <div class="metric-content">
                <div class="metric-section">
                    <div class="metric-label">Conversion</div>
                    <div class="conversion-container">
                        <div class="conversion-row">
                            <span class="conversion-label" title="{data['baseline']['name']}">{get_smart_label(data['baseline']['name'])}</span>
                            <div class="metric-value">{results['control_p']*100:.1f}%</div>
                        </div>
                        <div class="conversion-row">
                            <span class="conversion-label" title="{data['treatment']['name']}">{get_smart_label(data['treatment']['name'])}</span>
                            <div class="metric-value">{results['treatment_p']*100:.1f}%</div>
                        </div>
                    </div>
                </div>
                <div class="metric-section p2bb-section">
                    <div class="metric-label">P2BB</div>
                    <div class="p2bb-chart">
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {og_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if og_percentage > 50 else '#3CCFE7')}">{og_percentage}%</span>
                            </div>
                        </div>
                        <div class="p2bb-bar">
                            <div class="bar-container">
                                <div class="bar-fill" style="width: {v1_percentage}%"></div>
                                <span class="bar-value" style="color: {('#FFFFFF' if v1_percentage > 50 else '#3CCFE7')}">{v1_percentage}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">Improvement</div>
                    <div class="metric-improvement" style="color: {'#69BE28' if results['relative_lift'] > 0 else '#FF0000'}">
                        {'+' if results['relative_lift'] > 0 else ''}{results['relative_lift']:.2f}%
                    </div>
                </div>
                <div class="metric-section">
                    <div class="metric-label">P-value</div>
                    <div class="metric-value">{results['p_value']:.3f}</div>
                </div>
            </div>
            <div class="significance-label" style="background: {significance_color};">
                {significance_text} (α = 0.05)
            </div>
        </div>
    """, unsafe_allow_html=True)


def create_comparison_matrix(metric_name, variants):
    """
    Crea una matriz interactiva mostrando todos los resultados de comparación pareada.
    
    Args:
        metric_name: Nombre de la métrica
        variants: Lista de diccionarios con 'name', 'n', 'x'
    """
    st.markdown(f"### 📋 Matriz de Comparaciones - {metric_name}")
    
    # Crear datos para la matriz
    n_variants = len(variants)
    variant_names = [v['name'] for v in variants]
    
    # Inicializar matrices
    z_values = []
    hover_texts = []
    display_texts = []
    
    for i in range(n_variants):
        z_row = []
        hover_row = []
        display_row = []
        
        for j in range(n_variants):
            if i == j:
                # Diagonal - misma variante
                conversion_rate = (variants[i]['x'] / variants[i]['n']) * 100 if variants[i]['n'] > 0 else 0
                z_row.append(0)
                hover_row.append(f"{variants[i]['name']}<br>Conversión: {conversion_rate:.2f}%<br>Datos: {variants[i]['x']:,}/{variants[i]['n']:,}")
                display_row.append("—")
            else:
                # Comparación entre variantes
                variant_a = variants[i]
                variant_b = variants[j]
                comparison = calculate_single_comparison(variant_a, variant_b)
                
                # Texto del tooltip
                hover_text = f"""{variant_a['name']} vs {variant_b['name']}<br>
• {variant_a['name']}: {comparison['variant_a_p']*100:.2f}% ({variant_a['x']:,}/{variant_a['n']:,})<br>
• {variant_b['name']}: {comparison['variant_b_p']*100:.2f}% ({variant_b['x']:,}/{variant_b['n']:,})<br>
• Lift: {'+' if comparison['relative_lift'] > 0 else ''}{comparison['relative_lift']:.2f}%<br>
• P-value: {comparison['p_value']:.4f}<br>
• P2BB: {comparison['p2bb']*100:.1f}%<br>
• Significativo: {'Sí' if comparison['significant'] else 'No'}"""
                
                hover_row.append(hover_text)
                
                # Determinar valor y color
                if comparison['significant']:
                    if comparison['relative_lift'] > 0:
                        z_row.append(1)  # Verde (ganador)
                        display_row.append(f"+{comparison['relative_lift']:.1f}%")
                    else:
                        z_row.append(-1)  # Rojo (perdedor)
                        display_row.append(f"{comparison['relative_lift']:.1f}%")
                else:
                    z_row.append(0.5)  # Gris (neutral)
                    display_row.append("≈")
        
        z_values.append(z_row)
        hover_texts.append(hover_row)
        display_texts.append(display_row)
    
    # Crear el heatmap con plotly
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=variant_names,
        y=variant_names,
        text=display_texts,
        texttemplate="%{text}",
        textfont={"size": 14, "color": "white"},
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_texts,
        colorscale=[
            [0.0, '#C62828'],
            [0.25, '#757575'],
            [0.5, '#6A7BAA'],
            [0.75, '#757575'],
            [1.0, '#2E7D32']
        ],
        showscale=False,
        xgap=2,
        ygap=2
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="",
        yaxis_title="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=12),
        height=max(400, n_variants * 60),
        margin=dict(l=50, r=50, t=30, b=30),
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(n_variants)),
            ticktext=variant_names,
            side='top'
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(n_variants)),
            ticktext=variant_names,
            autorange='reversed'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Leyenda
    st.markdown("""
    <div style="background: #4A6489; border-radius: 8px; padding: 15px; margin-top: 10px;">
        <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;">
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #2E7D32; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Mejor rendimiento</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #C62828; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Peor rendimiento</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #757575; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Sin diferencia significativa</span>
            </div>
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="width: 20px; height: 20px; background: #6A7BAA; border-radius: 3px;"></div>
                <span style="color: white; font-size: 0.9em;">Misma variante</span>
            </div>
        </div>
        <div style="margin-top: 10px; text-align: center; font-style: italic; color: #E0E0E0; font-size: 0.8em;">
            💡 Pasa el cursor sobre cualquier celda para ver detalles completos de la comparación
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_comparison_cards(comparisons, is_control_section=True):
    """
    Crea tarjetas de comparación con estilo mejorado.
    
    Args:
        comparisons: Lista de diccionarios con resultados de comparación
        is_control_section: Si es True, usa colores para comparaciones vs control
    """
    st.markdown("""
        <style>
        .multivariant-card {
            width: 100%;
            background: #4A6489;
            box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
            border-radius: 12px;
            margin: 20px auto;
            color: white;
            position: relative;
            overflow: hidden;
            padding: 20px;
        }
        .metric-box {
            background: #FFFFFF;
            color: #1B365D;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: bold;
            min-width: 80px;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    for comparison in comparisons:
        # Determinar colores y títulos según el tipo de comparación
        if is_control_section:
            card_color = "#4A6489"
            icon = "📈"
        else:
            card_color = "#5A7099"
            icon = "⚖️"
        
        st.markdown(f"""
            <div class="multivariant-card" style="background: {card_color}; padding: 15px; margin: 10px 0;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <span style="font-size: 1.2em; margin-right: 10px;">{icon}</span>
                    <h4 style="margin: 0;">{comparison['variant_a_name']} vs {comparison['variant_b_name']}</h4>
                </div>
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px;">
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">{comparison['variant_a_name']}</div>
                        <div class="metric-box">{comparison['variant_a_p']*100:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">{comparison['variant_b_name']}</div>
                        <div class="metric-box">{comparison['variant_b_p']*100:.2f}%</div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">Lift Relativo</div>
                        <div class="metric-box" style="background: {'#E8F5E8' if comparison['relative_lift'] > 0 else '#FFE8E8'}; color: {'#2E7D32' if comparison['relative_lift'] > 0 else '#C62828'};">
                            {'+' if comparison['relative_lift'] > 0 else ''}{comparison['relative_lift']:.2f}%
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">P-value</div>
                        <div class="metric-box" style="background: {'#E8F5E8' if comparison['significant'] else '#FFE8E8'}; color: {'#2E7D32' if comparison['significant'] else '#C62828'};">
                            {comparison['p_value']:.4f}
                        </div>
                    </div>
                    <div>
                        <div style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 5px;">P2BB</div>
                        <div class="metric-box" style="background: {'#E3F2FD' if comparison['p2bb'] > 0.5 else '#FFF3E0'}; color: {'#1565C0' if comparison['p2bb'] > 0.5 else '#E65100'};">
                            {comparison['p2bb']*100:.1f}%
                        </div>
                    </div>
                </div>
                <div style="margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.2);">
                    <div style="text-align: center;">
                        <div style="padding: 8px 20px; border-radius: 20px; background: {'#2E7D32' if comparison['significant'] else '#C62828'}; color: white; font-size: 0.9em; display: inline-block;">
                            {'✓ Significativo' if comparison['significant'] else '✗ No significativo'} (α = 0.05)
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)


def create_visualization(metric_name, variants):
    """
    Crea visualización para test multivariante.
    
    Args:
        metric_name: Nombre de la métrica
        variants: Lista de diccionarios con 'name', 'n', 'x'
        
    Returns:
        go.Figure: Figura de Plotly
    """
    variant_names = [v['name'] for v in variants]
    conversion_rates = [(v['x'] / v['n']) * 100 if v['n'] > 0 else 0 for v in variants]
    
    fig = go.Figure()
    
    # Colores diferentes para cada variante
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    
    fig.add_trace(go.Bar(
        x=variant_names,
        y=conversion_rates,
        marker_color=colors[:len(variants)],
        text=[f'{rate:.2f}%' for rate in conversion_rates],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=f'Tasas de Conversión - {metric_name}',
        xaxis_title='Variantes',
        yaxis_title='Tasa de Conversión (%)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

