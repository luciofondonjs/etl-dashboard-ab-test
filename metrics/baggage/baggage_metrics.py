# filtros amplitude
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.amplitude_filters import (
    cabin_bag_filter,
    checked_bag_filter,
    get_DB_filter
)

# Next Step Rate Baggage - General
NSR_BAGGAGE = [
    'baggage_dom_loaded',
    'seatmap_dom_loaded'
]

# Next Step Rate Baggage - DB
NSR_BAGGAGE_DB = {'events': [
    'baggage_dom_loaded',
    'seatmap_dom_loaded'
], 'filters': [get_DB_filter()]}

# Website Conversion Rate from Baggage - General
WCR_BAGGAGE = [
    'baggage_dom_loaded',
    'revenue_amount'
]

# Website Conversion Rate from Baggage - Vuela Ligero
# Ojo los Custom Events parten con 'ce:'
WCR_BAGGAGE_VUELA_LIGERO = [
    'ce:(NEW) baggage_dom_loaded_with_vuela_ligero',
    'revenue_amount'
]

# Cabin Bag A2C
CABIN_BAG_A2C = {'events': [
    'ce:(NEW) baggage_dom_loaded_with_vuela_ligero',
    'seatmap_dom_loaded',
], 'filters': [cabin_bag_filter()]}


# Checked Bag A2C
CHECKED_BAG_A2C = {'events': [
    'ce:(NEW) baggage_dom_loaded_with_vuela_ligero',
    'seatmap_dom_loaded',
], 'filters': [checked_bag_filter()]}