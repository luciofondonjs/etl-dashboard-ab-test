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
import streamlit.components.v1 as components


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
    
    # Calcular error estándar para diferencia de proporciones
    # Usar pooled proportion para el error estándar (más robusto)
    pooled_p = (control_x + treatment_x) / (control_n + treatment_n) if (control_n + treatment_n) > 0 else 0
    se = np.sqrt(
        pooled_p * (1 - pooled_p) * (1/control_n + 1/treatment_n)
    ) if control_n > 0 and treatment_n > 0 and pooled_p > 0 and pooled_p < 1 else np.sqrt(
        (control_p * (1 - control_p) / control_n) +
        (treatment_p * (1 - treatment_p) / treatment_n)
    ) if control_n > 0 and treatment_n > 0 else 0
    
    # Calcular z-score
    z_score = (treatment_p - control_p) / se if se > 0 else 0
    
    # Calcular p-value (two-tailed test)
    # Usar sf (survival function) que es más numéricamente estable que 1 - cdf
    p_value = 2 * stats.norm.sf(abs(z_score)) if se > 0 and not np.isnan(z_score) and not np.isinf(z_score) else 1.0
    
    # Calcular lift relativo
    relative_lift = ((treatment_p - control_p) / control_p) * 100 if control_p > 0 else 0
    
    # Calcular probabilidad bayesiana (P2BB)
    # Validar parámetros para evitar errores en la distribución beta
    n_simulations = 10000
    control_alpha = max(1, control_x + 1)
    control_beta = max(1, control_n - control_x + 1)
    treatment_alpha = max(1, treatment_x + 1)
    treatment_beta = max(1, treatment_n - treatment_x + 1)
    
    baseline_posterior = np.random.beta(control_alpha, control_beta, n_simulations)
    treatment_posterior = np.random.beta(treatment_alpha, treatment_beta, n_simulations)
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
    
    # Calcular error estándar para diferencia de proporciones
    # Usar pooled proportion para el error estándar (más robusto)
    pooled_p = (variant_a['x'] + variant_b['x']) / (variant_a['n'] + variant_b['n']) if (variant_a['n'] + variant_b['n']) > 0 else 0
    se = np.sqrt(
        pooled_p * (1 - pooled_p) * (1/variant_a['n'] + 1/variant_b['n'])
    ) if variant_a['n'] > 0 and variant_b['n'] > 0 and pooled_p > 0 and pooled_p < 1 else np.sqrt(
        (a_p * (1 - a_p) / variant_a['n']) +
        (b_p * (1 - b_p) / variant_b['n'])
    ) if variant_a['n'] > 0 and variant_b['n'] > 0 else 0
    
    # Calcular z-score
    if se > 0:
        z_score = (b_p - a_p) / se
        # Calcular p-value (two-tailed test)
        # Usar sf (survival function) que es más numéricamente estable que 1 - cdf
        p_value = 2 * stats.norm.sf(abs(z_score)) if not np.isnan(z_score) and not np.isinf(z_score) else 1.0
    else:
        z_score = 0
        p_value = 1.0
    
    # Calcular lift relativo
    if a_p > 0:
        relative_lift = ((b_p - a_p) / a_p) * 100
    else:
        relative_lift = 0
    
    # Calcular probabilidad bayesiana
    # Validar parámetros para evitar errores en la distribución beta
    n_simulations = 10000
    a_alpha = max(1, variant_a['x'] + 1)
    a_beta = max(1, variant_a['n'] - variant_a['x'] + 1)
    b_alpha = max(1, variant_b['x'] + 1)
    b_beta = max(1, variant_b['n'] - variant_b['x'] + 1)
    
    a_posterior = np.random.beta(a_alpha, a_beta, n_simulations)
    b_posterior = np.random.beta(b_alpha, b_beta, n_simulations)
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
    # Validar que no haya valores negativos o inválidos
    conversions = []
    non_conversions = []
    
    for variant in variants:
        x = max(0, variant.get('x', 0))
        n = max(0, variant.get('n', 0))
        # Asegurar que x <= n
        x = min(x, n)
        conversions.append(x)
        non_conversions.append(max(0, n - x))
    
    # Validar que haya al menos un valor positivo en cada fila
    if sum(conversions) == 0 or sum(non_conversions) == 0:
        # Si no hay conversiones o todas son conversiones, retornar valores por defecto
        return {
            'chi2': 0,
            'p_value': 1.0,
            'dof': 0,
            'significant': False
        }
    
    # Tabla de contingencia: [conversiones, no_conversiones] para cada variante
    contingency_table = np.array([conversions, non_conversions])
    
    # Validar que todos los valores sean no negativos
    if np.any(contingency_table < 0):
        return {
            'chi2': 0,
            'p_value': 1.0,
            'dof': 0,
            'significant': False
        }
    
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
            
            # IMPORTANTE: Para TODAS las métricas de conversión (WCR, NSR, etc.):
            # - n (denominador) = eventos en la etapa inicial (primer evento)
            # - x (numerador) = eventos en la etapa final (último evento)
            # Conversión = x/n = eventos_finales / eventos_iniciales
            # Ejemplo WCR: revenue_amount / baggage_dom_loaded
            # Ejemplo NSR: seatmap_dom_loaded / baggage_dom_loaded
            initial_df = variant_df[variant_df['Funnel Stage'] == initial_stage]
            n = int(initial_df['Event Count'].sum()) if not initial_df.empty else 0
            
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
    Crea una tarjeta estilizada para una métrica A/B (2 variantes).
    Diseño idéntico al multivariante con tabla HTML y header turquesa.
    
    Args:
        metric_name: Nombre de la métrica
        data: Diccionario con 'baseline' y 'treatment' (cada uno con 'name', 'n', 'x')
        results: Diccionario con resultados estadísticos
        experiment_title: Título opcional del experimento
    """
    baseline = data.get('baseline', {})
    treatment = data.get('treatment', {})
    
    # Obtener nombres de variantes (usar nombres reales)
    baseline_name = baseline.get('name', 'Baseline')
    treatment_name = treatment.get('name', 'Treatment')
    
    # Extraer KPI del metric_name si está en formato [KPI]
    kpi_name = ""
    comparison_text = metric_name
    if metric_name.startswith('[') and ']' in metric_name:
        end_bracket = metric_name.find(']')
        kpi_name = metric_name[1:end_bracket]
        if len(metric_name) > end_bracket + 1:
            comparison_text = metric_name[end_bracket + 1:].strip()
        else:
            comparison_text = ""
    
    if not comparison_text:
        comparison_text = metric_name
    
    # Calcular conversiones
    baseline_conversion = (baseline.get('x', 0) / baseline.get('n', 1)) * 100 if baseline.get('n', 0) > 0 else 0
    treatment_conversion = (treatment.get('x', 0) / treatment.get('n', 1)) * 100 if treatment.get('n', 0) > 0 else 0
    
    # Determinar los porcentajes P2BB y redondearlos
    v1_percentage = round(results['p2bb'] * 100)
    og_percentage = round((1 - results['p2bb']) * 100)
    
    # Crear barras de progreso para P2BB (igual que multivariante)
    p2bb_text_color_baseline = '#FFFFFF' if og_percentage > 60 else '#1B365D'
    p2bb_text_color_treatment = '#FFFFFF' if v1_percentage > 60 else '#1B365D'
    
    p2bb_bar_baseline = f"""<div style="position: relative; width: 120px; height: 28px; background: white; border-radius: 14px; margin: 0 auto; overflow: hidden; border: 1px solid #E0E6ED;"><div style="width: {og_percentage}%; height: 100%; background: #00AEC7; border-radius: 14px; position: absolute; top: 0; left: 0;"></div><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: {p2bb_text_color_baseline}; font-weight: 600; font-size: 13px; z-index: 1;">{og_percentage}%</span></div>"""
    
    p2bb_bar_treatment = f"""<div style="position: relative; width: 120px; height: 28px; background: white; border-radius: 14px; margin: 0 auto; overflow: hidden; border: 1px solid #E0E6ED;"><div style="width: {v1_percentage}%; height: 100%; background: #00AEC7; border-radius: 14px; position: absolute; top: 0; left: 0;"></div><span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: {p2bb_text_color_treatment}; font-weight: 600; font-size: 13px; z-index: 1;">{v1_percentage}%</span></div>"""
    
    improvement_sign = "+" if results['relative_lift'] > 0 else ""
    improvement_color = '#27AE60' if results['relative_lift'] > 0 else '#E74C3C'
    
    # Crear filas de la tabla (igual estructura que multivariante)
    table_rows = f"""
    <tr>
        <td style="padding: 16px 20px; font-weight: 600; color: #1B365D; font-size: 15px; background: white; text-align: left;">
            {baseline_name}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline.get('n', 0):,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline.get('x', 0):,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline_conversion:.2f}%
        </td>
        <td style="padding: 16px 20px; text-align: center; background: white;">
            {p2bb_bar_baseline}
        </td>
        <td style="padding: 16px 20px; text-align: center; color: #6C7B7F; font-size: 15px; background: white;">
            -
        </td>
        <td style="padding: 16px 20px; text-align: center; color: #6C7B7F; font-size: 15px; background: white;">
            -
        </td>
    </tr>
    <tr>
        <td style="padding: 16px 20px; font-weight: 600; color: #1B365D; font-size: 15px; background: white; text-align: left;">
            {treatment_name}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {treatment.get('n', 0):,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {treatment.get('x', 0):,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {treatment_conversion:.2f}%
        </td>
        <td style="padding: 16px 20px; text-align: center; background: white;">
            {p2bb_bar_treatment}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: {improvement_color}; font-size: 15px; background: white;">
            {improvement_sign}{results['relative_lift']:.1f}%
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {results['p_value']:.5f}
        </td>
    </tr>
    """
    
    # HTML completo con la misma estructura que multivariante (en una sola línea)
    card_html = f"""<div id="result-card-{hash(metric_name)}" style="background: white; border-radius: 16px; margin: 20px auto; box-shadow: 0 8px 32px rgba(0,0,0,0.12); max-width: 1000px; width: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;"><style>.no-borders-table{{border:none!important;}}.no-borders-table th{{border:none!important;outline:none!important;}}.no-borders-table td{{border:none!important;outline:none!important;}}.no-borders-table tr{{border:none!important;outline:none!important;}}</style><div style="background: #00AEC7; padding: 20px 30px; display: flex; align-items: center; gap: 20px;"><div style="background: #1B365D; color: white; padding: 12px 24px; border-radius: 25px; font-weight: 700; font-size: 16px; text-transform: uppercase;">KPI</div><div style="color: white; font-weight: 600; font-size: 24px; flex: 1;">{experiment_title if experiment_title else comparison_text}</div></div><table class="no-borders-table" style="width: 100%; border-collapse: collapse; border: none;"><thead><tr style="background: #F8FAFB;"><th style="padding: 18px 20px; text-align: left; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Variante</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Sesiones</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Conversiones</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">% Conversión</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">P2BB</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">% Improvement</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">P-value</th></tr></thead><tbody>{table_rows}</tbody></table></div>"""
    
    # Usar components.html para mejor renderizado de HTML complejo
    components.html(card_html, height=400, scrolling=False)


def create_multivariant_card(metric_name, variants, experiment_title=None, chi_square_result=None):
    """
    Crea una tarjeta estilizada para múltiples variantes (A/B/N).
    Diseño adaptado del archivo Gradio con tabla blanca y header turquesa.
    
    Args:
        metric_name: Nombre de la métrica
        variants: Lista de diccionarios con 'name', 'n', 'x'
        experiment_title: Título opcional del experimento
        chi_square_result: Resultado del test Chi-cuadrado global (dict con 'significant', 'p_value', etc.)
    """
    baseline = variants[0]
    
    # Extraer KPI del metric_name si está en formato [KPI]
    kpi_name = ""
    comparison_text = metric_name
    if metric_name.startswith('[') and ']' in metric_name:
        end_bracket = metric_name.find(']')
        kpi_name = metric_name[1:end_bracket]
        if len(metric_name) > end_bracket + 1:
            comparison_text = metric_name[end_bracket + 1:].strip()
        else:
            comparison_text = ""
    
    if not comparison_text:
        comparison_text = metric_name

    # Crear filas de la tabla
    table_rows = ""
    
    # Baseline
    baseline_conversion = (baseline['x'] / baseline['n']) * 100 if baseline['n'] > 0 else 0
    table_rows += f"""
    <tr>
        <td style="padding: 16px 20px; font-weight: 600; color: #1B365D; font-size: 15px; background: white; text-align: left;">
            {baseline['name']}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline['n']:,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline['x']:,}
        </td>
        <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
            {baseline_conversion:.2f}%
        </td>
        <td style="padding: 16px 20px; text-align: center; color: #6C7B7F; font-size: 15px; background: white;">
            -
        </td>
        <td style="padding: 16px 20px; text-align: center; color: #6C7B7F; font-size: 15px; background: white;">
            -
        </td>
        <td style="padding: 16px 20px; text-align: center; color: #6C7B7F; font-size: 15px; background: white;">
            -
        </td>
    </tr>
    """
    
    # Variantes
    for variant in variants[1:]:
        comparison = calculate_single_comparison(baseline, variant)
        variant_conversion = (variant['x'] / variant['n']) * 100 if variant['n'] > 0 else 0
        
        improvement_sign = "+" if comparison['relative_lift'] > 0 else ""
        p2bb_percentage = comparison['p2bb'] * 100
        
        # Crear barra de progreso para P2BB con borde visible y texto azul JetSMART
        # Color blanco solo si es mayor a 60%, de lo contrario azul
        p2bb_text_color = '#FFFFFF' if p2bb_percentage > 60 else '#1B365D'
        p2bb_bar = f"""
        <div style="position: relative; width: 120px; height: 28px; background: white; border-radius: 14px; margin: 0 auto; overflow: hidden; border: 1px solid #E0E6ED;">
            <div style="width: {p2bb_percentage:.0f}%; height: 100%; background: #00AEC7; border-radius: 14px; position: absolute; top: 0; left: 0;"></div>
            <span style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: {p2bb_text_color}; font-weight: 600; font-size: 13px; z-index: 1;">
                {p2bb_percentage:.0f}%
            </span>
        </div>
        """
        
        table_rows += f"""
        <tr>
            <td style="padding: 16px 20px; font-weight: 600; color: #1B365D; font-size: 15px; background: white; text-align: left;">
                {variant['name']}
            </td>
            <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
                {variant['n']:,}
            </td>
            <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
                {variant['x']:,}
            </td>
            <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
                {variant_conversion:.2f}%
            </td>
            <td style="padding: 16px 20px; text-align: center; background: white;">
                {p2bb_bar}
            </td>
            <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: {'#27AE60' if comparison['relative_lift'] > 0 else '#E74C3C'}; font-size: 15px; background: white;">
                {improvement_sign}{comparison['relative_lift']:.1f}%
            </td>
            <td style="padding: 16px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: white;">
                {comparison['p_value']:.5f}
            </td>
        </tr>
        """
    
    # HTML completo de la tarjeta con el diseño exacto de la imagen (en una sola línea para evitar problemas de renderizado)
    # Siempre mostrar "KPI" en el label, independientemente del kpi_name extraído
    card_html = f"""<div id="result-card-{hash(metric_name)}" style="background: white; border-radius: 16px; margin: 20px auto; box-shadow: 0 8px 32px rgba(0,0,0,0.12); max-width: 1000px; width: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;"><style>.no-borders-table{{border:none!important;}}.no-borders-table th{{border:none!important;outline:none!important;}}.no-borders-table td{{border:none!important;outline:none!important;}}.no-borders-table tr{{border:none!important;outline:none!important;}}</style><div style="background: #00AEC7; padding: 20px 30px; display: flex; align-items: center; gap: 20px;"><div style="background: #1B365D; color: white; padding: 12px 24px; border-radius: 25px; font-weight: 700; font-size: 16px; text-transform: uppercase;">KPI</div><div style="color: white; font-weight: 600; font-size: 24px; flex: 1;">{experiment_title if experiment_title else comparison_text}</div></div><table class="no-borders-table" style="width: 100%; border-collapse: collapse; border: none;"><thead><tr style="background: #F8FAFB;"><th style="padding: 18px 20px; text-align: left; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Variante</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Sesiones</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">Conversiones</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">% Conversión</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">P2BB</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">% Improvement</th><th style="padding: 18px 20px; text-align: center; font-weight: 600; color: #1B365D; font-size: 15px; background: #F8FAFB;">P-value</th></tr></thead><tbody>{table_rows}</tbody></table></div>"""
    
    # Resumen de significancia basado en el test Chi-cuadrado global
    # Solo mostrar mensaje cuando hay test global (chi_square_result)
    # Para comparaciones individuales, la significancia ya se muestra en la tabla (columna P-value)
    if chi_square_result is not None:
        is_globally_significant = chi_square_result.get('significant', False)
        if is_globally_significant:
            # Hay diferencias significativas globalmente
            significant_variants = [v['name'] for v in variants[1:] 
                                   if calculate_single_comparison(baseline, v)['significant']]
            if significant_variants:
                summary_html = f'<div style="background: #E8F5E8; color: #2E7D32; padding: 16px 24px; border-radius: 12px; margin: 20px auto; max-width: 1000px; text-align: center; font-weight: 700; font-size: 15px; border: 2px solid #27AE60; box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">✅ Diferencias significativas detectadas - Variantes: {", ".join(significant_variants)}</div>'
            else:
                summary_html = '<div style="background: #E8F5E8; color: #2E7D32; padding: 16px 24px; border-radius: 12px; margin: 20px auto; max-width: 1000px; text-align: center; font-weight: 700; font-size: 15px; border: 2px solid #27AE60; box-shadow: 0 4px 12px rgba(46, 125, 50, 0.15); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">✅ Diferencias significativas detectadas globalmente</div>'
        else:
            # No hay diferencias significativas globalmente - usar diseño similar a la cajita
            summary_html = '<div style="background: white; color: #1B365D; padding: 16px 24px; border-radius: 12px; margin: 20px auto; max-width: 1000px; text-align: center; font-weight: 700; font-size: 15px; border: 2px solid #00AEC7; box-shadow: 0 4px 12px rgba(0, 174, 199, 0.15); font-family: -apple-system, BlinkMacSystemFont, \'Segoe UI\', Roboto, sans-serif;">⚠️ Sin diferencias significativas (p-value: {:.4f})</div>'.format(chi_square_result.get('p_value', 1.0))
    else:
        # No hay test global - no mostrar mensaje de resumen
        # Las comparaciones individuales ya muestran su significancia en la tabla
        summary_html = ''
    
    # Usar components.html para mejor renderizado de HTML complejo
    components.html(card_html + summary_html, height=400, scrolling=False)


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

