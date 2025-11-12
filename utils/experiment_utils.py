"""
Módulo de utilidades para análisis de experimentos AB Test en Amplitude.

Este módulo contiene todas las funciones necesarias para:
- Obtener datos de experimentos desde la API de Amplitude
- Procesar datos de funnels por variantes
- Generar pipelines completos de análisis
"""

import os
import json
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from .amplitude_filters import get_culture_digital_filter, get_device_type
import sys
from io import StringIO

# Variable global para almacenar logs
_logs = []

def get_logs():
    """Obtiene y limpia los logs capturados"""
    global _logs
    logs = _logs.copy()
    _logs = []  # Limpiar logs después de obtenerlos
    return logs


def get_credentials():
    """
    Obtiene las credenciales de Amplitude desde variables de entorno.
    Esta función debe ser llamada DESPUÉS de que load_dotenv() se haya ejecutado.
    
    Returns:
        tuple: (api_key, secret_key, management_api_key)
    """
    api_key = os.getenv('AMPLITUDE_API_KEY')
    secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
    management_api_key = os.getenv('AMPLITUDE_MANAGEMENT_KEY')
    
    # Debug: Verificar que las credenciales se cargaron
    # También verificar variaciones comunes del nombre de la variable
    if not management_api_key:
        # Intentar con variaciones del nombre
        management_api_key = (
            os.getenv('AMPLITUDE_MANAGEMENT_KEY') or
            os.getenv('AMPLITUDE_MANAGEMENT_API_KEY') or
            os.getenv('AMPLITUDE_MGMT_KEY') or
            os.getenv('AMPLITUDE_MGMT_API_KEY')
        )
    
    return api_key, secret_key, management_api_key

def get_funnel_data_experiment(api_key, secret_key, start_date, end_date, experiment_id, device, variant, culture, event_list, conversion_window=1800):
	"""
	Obtiene datos de funnel desde la API de Amplitude para un experimento específico.
	
	Args:
		api_key: API key de Amplitude
		secret_key: Secret key de Amplitude
		start_date: Fecha de inicio (formato YYYY-MM-DD)
		end_date: Fecha de fin (formato YYYY-MM-DD)
		experiment_id: ID del experimento en Amplitude
		device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
		variant: Nombre de la variante ('control' o 'treatment')
		culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
		event_list: Lista de eventos a analizar
		conversion_window: Ventana de tiempo de conversión en segundos (default: 1800 = 30 min)
		
	Returns:
		dict: Respuesta JSON de la API de Amplitude con los datos del funnel
	"""
	url = 'https://amplitude.com/api/2/funnels'

	# event_filters_grouped = [{"event_type": event, 'filters': [], "group_by": [get_culture_digital_filter(culture)]} for event in event_list]

	# event_filters_grouped = [{"event_type": event, 'filters': [get_culture_digital_filter(culture), get_device_type(device)], "group_by": []} for event in event_list]
	filters = []

	if culture != "All":
		culture_filter = get_culture_digital_filter(culture)
		if culture_filter:  # Solo agregar si no está vacío
			filters.append(culture_filter)

	if device != "All":
		device_filter = get_device_type(device)
		if device_filter:  # Solo agregar si no está vacío
			filters.append(device_filter)


	event_filters_grouped = [
		{
			"event_type": event,
			"filters": filters,  # Usar la lista de filtros construida
			"group_by": []
		}
		for event in event_list
	]


    
    
	segments = [
						{
							'group_type': 'User',
							'prop': f'gp:[Experiment] {experiment_id}',
							'prop_type': 'user',
							'op': 'is',
							'type': 'property',
							'values': [
								variant,
							],
						},
						# {
						# 	'group_type': 'User',
						# 	'prop': 'device_type',
						# 	'prop_type': 'user',
						# 	'op': 'is',
						# 	'type': 'property',
						# 	'values': get_device_type(device)
						# },
					],

	params = {
		'e': [json.dumps(event) for event in event_filters_grouped],
		'start': start_date.replace('-', ''),
		'end': end_date.replace('-', ''),
		'cs': conversion_window,
		's': [json.dumps(segment) for segment in segments],
		
	}

	headers = {
		'Authorization': f'Basic {api_key}:{secret_key}'
	}
	
	response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(api_key, secret_key))
	
	return response.json()


def get_variant_funnel(variant):
    """
    Procesa los datos de una variante y genera un DataFrame con datos diarios.
    
    Args:
        variant: Diccionario con datos de la variante que incluye:
            - Data: Datos de la API de Amplitude
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
            
    Returns:
        pd.DataFrame: DataFrame con columnas:
            - Date: Fecha del evento
            - ExperimentID: ID del experimento
            - Funnel Stage: Paso del funnel
            - Culture: Cultura
            - Device: Dispositivo
            - Variant: Variante
            - Event Count: Cantidad de eventos
    """
    
    df = pd.DataFrame({
        'Date': [],
        'ExperimentID': [],
        'Culture': [],
        'Device': [],
        'Variant': [],
        'Event Count': []
    })

    variant_data = variant['Data']
    
    
    # Verificar si existe la clave 'data'
    if 'data' not in variant_data:
        raise KeyError(f"No existe la clave 'data' en variant_data. Keys disponibles: {list(variant_data.keys())}")
    
    
    # Normalizar estructura: puede venir lista o dict
    if isinstance(variant_data['data'], list):
        websites = variant_data['data']
    elif isinstance(variant_data['data'], dict):
        websites = [variant_data['data']]
    else:
        return df

    for website_funnel in websites:
        funnel_website_conversion_data = website_funnel['dayFunnels']['series']
        funnel_stages = website_funnel['events']
        dates = website_funnel['dayFunnels']['xValues']

        for date, data in zip(dates, funnel_website_conversion_data):
            for funnel_stage, value in zip(funnel_stages, data):
                new_row = {
                    'Date': pd.to_datetime(date),
                    'ExperimentID': variant['ExperimentID'],
                    'Funnel Stage': funnel_stage,
                    'Culture': variant['Culture'],
                    'Device': variant['Device'],
                    'Variant': variant['Variant'],
                    'Event Count': int(value)
                }

                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    return df


def get_variant_funnel_cum(variant):
    """
    Procesa los datos de una variante y genera un DataFrame con datos acumulados.
    
    Args:
        variant: Diccionario con datos de la variante que incluye:
            - Data: Datos de la API de Amplitude
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
            
    Returns:
        pd.DataFrame: DataFrame con columnas:
            - Start Date: Fecha de inicio del período
            - End Date: Fecha de fin del período
            - ExperimentID: ID del experimento
            - Culture: Cultura
            - Device: Dispositivo
            - Variant: Variante
            - Funnel Stage: Paso del funnel
            - Event Count: Cantidad acumulada de eventos
    """
    
    df = pd.DataFrame({
        'Start Date': [],
        'End Date': [],
        'ExperimentID': [],
        'Culture': [],
        'Device': [],
        'Variant': [],
        'Funnel Stage': [],
        'Event Count': []
    })

    variant_data = variant['Data']
    
    
    # Verificar si existe la clave 'data'
    if 'data' not in variant_data:
        raise KeyError(f"No existe la clave 'data' en variant_data. Keys disponibles: {list(variant_data.keys())}")
    
    
    # Normalizar estructura: puede venir lista o dict
    if isinstance(variant_data['data'], list):
        websites = variant_data['data']
    elif isinstance(variant_data['data'], dict):
        websites = [variant_data['data']]
    else:
        return df

    for website_funnel in websites:
        # Fechas desde dayFunnels
        day_funnels = website_funnel.get('dayFunnels', {})
        x_values = day_funnels.get('xValues', [])
        start_date_filter = pd.to_datetime(x_values[0]) if x_values else None
        end_date_filter = pd.to_datetime(x_values[-1]) if x_values else None

        # Pasos del funnel y acumulados
        funnel_stages = website_funnel.get('events', [])
        cumulative_raw = website_funnel.get('cumulativeRaw', [])

        # Validaciones mínimas
        if not cumulative_raw or not funnel_stages:
            continue

        # Alinear cada paso con su acumulado
        for funnel_stage, value in zip(funnel_stages, cumulative_raw):
            # Si el paso viene como dict de Amplitude, tomar el nombre
            if isinstance(funnel_stage, dict):
                stage_name = funnel_stage.get('event_type', str(funnel_stage))
            else:
                stage_name = funnel_stage

            new_row = {
                'Start Date': start_date_filter,
                'End Date': end_date_filter,
                'ExperimentID': variant['ExperimentID'],
                'Culture': variant['Culture'],
                'Device': variant['Device'],
                'Variant': variant['Variant'],
                'Funnel Stage': stage_name,
                'Event Count': int(value)
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    return df


def get_control_treatment_raw_data(
    start_date, 
    end_date, 
    experiment_id, 
    device, 
    culture, 
    event_list,
    conversion_window=1800
):
    """
    Obtiene los datos raw de control y treatment para un experimento.
    
    Args:
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de tiempo de conversión en segundos (default: 1800 = 30 min)
        
    Returns:
        tuple: (control_data, treatment_data) donde cada uno es un diccionario con:
            - Data: Respuesta de la API
            - ExperimentID: ID del experimento
            - Culture: Cultura filtrada
            - Device: Dispositivo filtrado
            - Variant: Nombre de la variante
    """
    # Obtener credenciales
    api_key, secret_key, _ = get_credentials()
    
    
    control_response = get_funnel_data_experiment(
        api_key,
        secret_key,
        start_date,
        end_date,
        experiment_id,
        device,
        "control",
        culture,
        event_list,
        conversion_window
    )
    
    
    treatment_response = get_funnel_data_experiment(
        api_key,
        secret_key,
        start_date,
        end_date,
        experiment_id,
        device,
        "treatment",
        culture,
        event_list,
        conversion_window
    )
    
    
    control = {
        'Data': control_response,
        'ExperimentID': experiment_id,
        'Culture': culture,
        'Device': device,
        'Variant': 'control'
    }
    
    treatment = {
        'Data': treatment_response,
        'ExperimentID': experiment_id,
        'Culture': culture,
        'Device': device,
        'Variant': 'treatment'
    }
    
    
    return control, treatment


def final_pipeline(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800):
    """
    Pipeline completo para análisis de experimentos AB Test.
    
    Args:
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        
    Returns:
        pd.DataFrame: DataFrame combinado con datos de todas las variantes
    """
    # Obtener datos de todas las variantes
    all_variants_data = get_all_variants_raw_data(
        start_date,
        end_date,
        experiment_id,
        device,
        culture,
        event_list,
        conversion_window
    )

    # Procesar cada variante
    all_dataframes = []
    for variant_data in all_variants_data:
        df_variant = get_variant_funnel(variant_data)
        all_dataframes.append(df_variant)

    # Combinar todos los DataFrames
    if all_dataframes:
        df_final = pd.concat(all_dataframes, axis=0, ignore_index=True)
    else:
        df_final = pd.DataFrame()

    return df_final


def get_experiments_list():
    """
    Obtiene la lista de todos los experimentos disponibles en Amplitude.
    
    Returns:
        pd.DataFrame: DataFrame con la información de todos los experimentos
        
    Raises:
        ValueError: Si las credenciales no están disponibles o la respuesta es inválida
        requests.RequestException: Si hay un error en la petición HTTP
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    # Verificar que la management API key esté disponible
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        # Verificar el status code
        response.raise_for_status()
        
        # Verificar que la respuesta no esté vacía
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        # Intentar parsear el JSON
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        # Verificar que la respuesta tenga la estructura esperada
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        return pd.DataFrame(data['experiments'])
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}\n"
            f"URL: https://experiment.amplitude.com/api/1/experiments"
        )


def get_experiment_variants(experiment_id):
    """
    Obtiene las variantes de un experimento específico.
    
    Args:
        experiment_id (str): ID del experimento
        
    Returns:
        list: Lista de nombres de variantes del experimento CON GUIONES
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}"
            )
        
        experiments = data['experiments']
        
        # Buscar el experimento específico
        for exp in experiments:
            if exp.get('key') == experiment_id:
                variants = exp.get('variants', [])
                variant_names = []
                
                
                for variant in variants:
                    if isinstance(variant, dict):
                        name = variant.get('name', variant.get('key', str(variant)))
                    else:
                        name = str(variant)
                    
                    # SIMPLE: Reemplazar espacios por guiones
                    processed_name = name.replace(' ', '-')
                    variant_names.append(processed_name)
                
                return variant_names
        
        # Si no se encuentra el experimento, retornar variantes por defecto
        return ['control', 'treatment']
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}"
        )


def get_experiment_variants_original(experiment_id):
    """
    Obtiene las variantes originales (sin procesar) de un experimento específico.
    
    Args:
        experiment_id (str): ID del experimento
        
    Returns:
        list: Lista de nombres originales de variantes del experimento
    """
    # Obtener credenciales
    _, _, management_api_key = get_credentials()
    
    if not management_api_key:
        raise ValueError(
            "AMPLITUDE_MANAGEMENT_KEY no está configurada. "
            "Por favor, verifica tus variables de entorno."
        )
    
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {management_api_key}',
    }

    params = {
        'limit': '1000',
    }

    try:
        response = requests.get(
            'https://experiment.amplitude.com/api/1/experiments', 
            params=params, 
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        
        if not response.text or not response.text.strip():
            raise ValueError(
                f"La respuesta de la API está vacía. "
                f"Status code: {response.status_code}"
            )
        
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Error al parsear la respuesta JSON: {str(e)}\n"
                f"Status code: {response.status_code}\n"
                f"Response text (primeros 500 caracteres): {response.text[:500]}"
            )
        
        if 'experiments' not in data:
            raise ValueError(
                f"La respuesta no contiene la clave 'experiments'. "
                f"Claves disponibles: {list(data.keys())}"
            )
        
        experiments = data['experiments']
        
        # Buscar el experimento específico
        for exp in experiments:
            if exp.get('key') == experiment_id:
                variants = exp.get('variants', [])
                variant_names = []
                
                
                for variant in variants:
                    if isinstance(variant, dict):
                        # Extraer el nombre original de la variante (sin procesar)
                        name = variant.get('name', variant.get('key', str(variant)))
                        variant_names.append(name)
                    else:
                        # Usar el nombre original (sin procesar)
                        variant_names.append(str(variant))
                
                return variant_names
        
        # Si no se encuentra el experimento, retornar variantes por defecto
        return ['control', 'treatment']
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Error al realizar la petición a la API de Amplitude: {str(e)}"
        )


def get_all_variants_raw_data(
    start_date, 
    end_date, 
    experiment_id, 
    device, 
    culture, 
    event_list,
    conversion_window=1800
):
    """
    Obtiene los datos raw de todas las variantes de un experimento.
    
    Args:
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        
    Returns:
        list: Lista de diccionarios con datos de cada variante
    """
    # Obtener las variantes del experimento
    variants = get_experiment_variants(experiment_id)
    
    
    # Obtener credenciales
    api_key, secret_key, _ = get_credentials()
    
    all_variants_data = []
    
    # Obtener datos para cada variante
    for variant in variants:
        
        variant_response = get_funnel_data_experiment(
            api_key,
            secret_key,
            start_date,
            end_date,
            experiment_id,
            device,
            variant,
            culture,
            event_list
        )
        
        variant_data = {
            'Data': variant_response,
            'ExperimentID': experiment_id,
            'Culture': culture,
            'Device': device,
            'Variant': variant
        }
        
        all_variants_data.append(variant_data)
    
    
    return all_variants_data


def final_pipeline_cumulative(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800):
    """
    Pipeline completo para análisis de experimentos AB Test con datos acumulados.
    
    Args:
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        
    Returns:
        pd.DataFrame: DataFrame combinado con datos acumulados de todas las variantes
    """
    # Obtener datos de todas las variantes
    all_variants_data = get_all_variants_raw_data(
        start_date,
        end_date,
        experiment_id,
        device,
        culture,
        event_list,
        conversion_window
    )

    # Procesar cada variante con datos acumulados
    all_dataframes = []
    for variant_data in all_variants_data:
        df_variant = get_variant_funnel_cum(variant_data)
        all_dataframes.append(df_variant)

    # Combinar todos los DataFrames
    if all_dataframes:
        df_final = pd.concat(all_dataframes, axis=0, ignore_index=True)
    else:
        df_final = pd.DataFrame()

    return df_final


def final_pipeline_cumulative(start_date, end_date, experiment_id, device, culture, event_list, conversion_window=1800):
    """
    Pipeline completo para análisis de experimentos AB Test con datos acumulados.
    
    Args:
        start_date: Fecha de inicio (formato YYYY-MM-DD)
        end_date: Fecha de fin (formato YYYY-MM-DD)
        experiment_id: ID del experimento en Amplitude
        device: Tipo de dispositivo ('mobile', 'desktop', 'tablet', o 'All')
        culture: Código de cultura ('CL', 'AR', 'PE', etc., o 'All')
        event_list: Lista de eventos a analizar
        conversion_window: Ventana de conversión en segundos (default: 1800)
        
    Returns:
        pd.DataFrame: DataFrame combinado con datos acumulados de todas las variantes
    """
    # Obtener datos de todas las variantes
    all_variants_data = get_all_variants_raw_data(
        start_date,
        end_date,
        experiment_id,
        device,
        culture,
        event_list,
        conversion_window
    )

    # Procesar cada variante con datos acumulados
    all_dataframes = []
    for variant_data in all_variants_data:
        df_variant = get_variant_funnel_cum(variant_data)
        all_dataframes.append(df_variant)

    # Combinar todos los DataFrames
    if all_dataframes:
        df_final = pd.concat(all_dataframes, axis=0, ignore_index=True)
    else:
        df_final = pd.DataFrame()

    return df_final
