"""
Módulo para cargar automáticamente métricas desde las carpetas de metrics/.

Este módulo escanea las carpetas en metrics/ y detecta automáticamente
todas las métricas definidas en archivos *_metrics.py, organizándolas
por carpeta y generando información para mostrar en el dashboard.
"""

import os
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Tuple
import inspect


def is_valid_metric(obj: Any) -> bool:
    """
    Verifica si un objeto es una métrica válida.
    
    Una métrica válida debe ser un diccionario con la estructura:
    {'events': [('evento', [filtros]), ...]}
    
    Args:
        obj: Objeto a verificar
        
    Returns:
        bool: True si es una métrica válida, False en caso contrario
    """
    if not isinstance(obj, dict):
        return False
    
    if 'events' not in obj:
        return False
    
    events = obj['events']
    if not isinstance(events, list) or len(events) < 2:
        return False
    
    # Verificar que cada evento sea una tupla ('evento', [filtros])
    for event_item in events:
        if isinstance(event_item, tuple):
            if len(event_item) < 1:
                return False
            # El primer elemento debe ser un string (nombre del evento)
            if not isinstance(event_item[0], str):
                return False
            # El segundo elemento (si existe) debe ser una lista de filtros
            if len(event_item) >= 2 and not isinstance(event_item[1], list):
                return False
        elif isinstance(event_item, str):
            # Formato antiguo: solo string, también es válido
            pass
        else:
            return False
    
    return True


def get_event_name(event_item: Any) -> str:
    """
    Extrae el nombre del evento de un item (puede ser tupla o string).
    
    Args:
        event_item: Item del evento (tupla o string)
        
    Returns:
        str: Nombre del evento
    """
    if isinstance(event_item, tuple) and len(event_item) > 0:
        return event_item[0]
    elif isinstance(event_item, str):
        return event_item
    return "-"


def get_event_filters(event_item: Any) -> List[Any]:
    """
    Extrae los filtros de un item de evento.
    
    Args:
        event_item: Item del evento (tupla o string)
        
    Returns:
        List: Lista de filtros (puede estar vacía)
    """
    if isinstance(event_item, tuple) and len(event_item) >= 2:
        filters_list = event_item[1]
        if isinstance(filters_list, list):
            return filters_list
    return []


def load_metrics_from_file(file_path: Path, category: str) -> Dict[str, Dict]:
    """
    Carga todas las métricas válidas desde un archivo de métricas.
    
    Args:
        file_path: Ruta al archivo de métricas
        category: Categoría/carpeta de la métrica (ej: 'baggage', 'seats')
        
    Returns:
        Dict: Diccionario con {nombre_metric: config_metric}
    """
    metrics = {}
    
    try:
        # Cargar el módulo dinámicamente
        spec = importlib.util.spec_from_file_location(
            f"metrics_{category}_{file_path.stem}",
            file_path
        )
        if spec is None or spec.loader is None:
            return metrics
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Buscar todas las variables que sean métricas válidas
        for name, obj in inspect.getmembers(module):
            # Ignorar imports, funciones, clases, etc.
            if name.startswith('_'):
                continue
            
            # Verificar si es una métrica válida
            if is_valid_metric(obj):
                # Generar nombre de display con emoji según categoría
                emoji_map = {
                    'baggage': '🎒',
                    'seats': '💺',
                    'payment': '💳',
                    'passengers': '👥',
                    'extras': '➕',
                    'flight': '✈️'
                }
                emoji = emoji_map.get(category.lower(), '📊')
                
                # Generar nombre de display basado en el nombre de la variable
                display_name = generate_display_name(name, emoji)
                
                metrics[display_name] = obj
        
    except Exception as e:
        print(f"Error cargando métricas desde {file_path}: {e}")
    
    return metrics


def generate_display_name(var_name: str, emoji: str) -> str:
    """
    Genera un nombre de display legible a partir del nombre de variable.
    
    Args:
        var_name: Nombre de la variable (ej: 'NSR_BAGGAGE')
        emoji: Emoji para la categoría
        
    Returns:
        str: Nombre de display (ej: '🎒 NSR Baggage (Next Step Rate)')
    """
    # Mapeo de prefijos comunes a descripciones
    prefix_map = {
        'NSR': 'Next Step Rate',
        'WCR': 'Website Conversion Rate',
        'A2C': 'Add to Cart',
        'CABIN_BAG': 'Cabin Bag',
        'CHECKED_BAG': 'Checked Bag',
        'DB': 'DB'
    }
    
    # Remover prefijos comunes y construir nombre legible
    name_parts = var_name.split('_')
    
    # Identificar prefijos conocidos
    description_parts = []
    skip_next = False
    
    for i, part in enumerate(name_parts):
        if skip_next:
            skip_next = False
            continue
        
        if part in prefix_map:
            description_parts.append(prefix_map[part])
            # Si es DB, puede venir después de otra parte
            if part == 'DB' and i > 0:
                continue
        elif part == 'VUELA_LIGERO':
            description_parts.append('Vuela Ligero')
        elif part in ['BAGGAGE', 'SEAT', 'PAYMENT', 'PASSENGER', 'EXTRA', 'FLIGHT']:
            # Convertir a título
            description_parts.append(part.capitalize())
        else:
            # Agregar como está (puede ser parte de un nombre compuesto)
            if part not in ['NEW', 'CE']:
                description_parts.append(part.capitalize())
    
    # Construir nombre final
    if description_parts:
        base_name = ' '.join(description_parts)
    else:
        # Fallback: convertir snake_case a Title Case
        base_name = ' '.join(word.capitalize() for word in name_parts)
    
    # Agregar emoji al inicio
    return f"{emoji} {base_name}"


def load_all_metrics(metrics_root: Path = None) -> Dict[str, Dict[str, Dict]]:
    """
    Carga todas las métricas desde todas las carpetas de metrics/.
    
    Args:
        metrics_root: Ruta raíz de la carpeta metrics/ (por defecto: relativa a este archivo)
        
    Returns:
        Dict: Diccionario organizado por categoría:
        {
            'baggage': {
                '🎒 NSR Baggage': {'events': [...]},
                ...
            },
            'seats': {...},
            ...
        }
    """
    if metrics_root is None:
        # Obtener la ruta del directorio actual (utils/)
        current_dir = Path(__file__).resolve().parent
        # Subir un nivel y entrar a metrics/
        metrics_root = current_dir.parent / 'metrics'
    else:
        metrics_root = Path(metrics_root)
    
    if not metrics_root.exists():
        return {}
    
    all_metrics = {}
    
    # Escanear cada subcarpeta en metrics/
    for category_dir in metrics_root.iterdir():
        if not category_dir.is_dir():
            continue
        
        category = category_dir.name
        
        # Buscar archivos *_metrics.py en esta carpeta
        metrics_files = list(category_dir.glob('*_metrics.py'))
        
        if not metrics_files:
            continue
        
        category_metrics = {}
        
        # Cargar métricas de cada archivo
        for metrics_file in metrics_files:
            file_metrics = load_metrics_from_file(metrics_file, category)
            category_metrics.update(file_metrics)
        
        if category_metrics:
            all_metrics[category] = category_metrics
    
    return all_metrics


def get_metrics_info(metrics_dict: Dict[str, Dict]) -> List[Dict[str, str]]:
    """
    Genera información de display para las métricas.
    
    Args:
        metrics_dict: Diccionario de métricas {display_name: config}
        
    Returns:
        List[Dict]: Lista de diccionarios con información para mostrar
    """
    info_list = []
    
    for display_name, metric_config in metrics_dict.items():
        events = metric_config.get('events', [])
        
        if not events:
            continue
        
        # Extraer información de eventos
        initial_event = get_event_name(events[0]) if events else "-"
        final_event = get_event_name(events[-1]) if len(events) > 1 else "-"
        
        # Extraer información de filtros
        filters_info = []
        for event_item in events:
            event_filters = get_event_filters(event_item)
            if event_filters:
                # Intentar obtener descripción del filtro
                filter_descriptions = []
                for filt in event_filters:
                    if callable(filt):
                        # Si es una función, intentar obtener su nombre
                        filter_descriptions.append(filt.__name__ if hasattr(filt, '__name__') else 'custom')
                    else:
                        filter_descriptions.append(str(filt))
                
                if filter_descriptions:
                    filters_info.append(', '.join(filter_descriptions))
        
        # Construir descripción de filtros
        if filters_info:
            # Si todos los eventos tienen los mismos filtros, simplificar
            if len(set(filters_info)) == 1:
                filters_desc = filters_info[0]
            else:
                unique_filters = ', '.join(set(filters_info))
                filters_desc = f"Variados ({unique_filters})"
        else:
            filters_desc = "Ninguno"
        
        info_list.append({
            'Métrica': display_name,
            'Evento Inicial': initial_event,
            'Evento Final': final_event,
            'Filtros': filters_desc
        })
    
    return info_list


def get_all_metrics_flat(metrics_by_category: Dict[str, Dict[str, Dict]] = None) -> Dict[str, Dict]:
    """
    Obtiene todas las métricas en un diccionario plano (sin categorías).
    
    Args:
        metrics_by_category: Diccionario organizado por categoría (si None, carga automáticamente)
        
    Returns:
        Dict: Diccionario plano {display_name: config}
    """
    if metrics_by_category is None:
        metrics_by_category = load_all_metrics()
    
    flat_metrics = {}
    for category_metrics in metrics_by_category.values():
        flat_metrics.update(category_metrics)
    
    return flat_metrics

