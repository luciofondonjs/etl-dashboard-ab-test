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
NSR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('seatmap_dom_loaded', [])
]}


# Next Step Rate Baggage - General (Vuela Ligero)
NSR_BAGGAGE_VUELA_LIGERO = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [])
]}


# Next Step Rate Baggage - DB (Vuela Ligero)
NSR_BAGGAGE_VUELA_LIGERO_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}


# Next Step Rate Baggage - DB
NSR_BAGGAGE_DB = {'events': [
    ('baggage_dom_loaded', [get_DB_filter()]),
    ('seatmap_dom_loaded', [get_DB_filter()])
]}

# Website Conversion Rate from Baggage - General
WCR_BAGGAGE = {'events': [
    ('baggage_dom_loaded', []),
    ('revenue_amount', [])
]}

# Website Conversion Rate from Baggage - Vuela Ligero
# Ojo los Custom Events parten con 'ce:'
WCR_BAGGAGE_VUELA_LIGERO = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('revenue_amount', [])
]}

# Cabin Bag A2C - General
CABIN_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter()])  # Con filtro
]}

# Cabin Bag A2C - DB
CABIN_BAG_A2C_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),  # Sin filtros
    ('seatmap_dom_loaded', [cabin_bag_filter(), get_DB_filter()])  # Con filtro
]}

# Checked Bag A2C - General (Vuela Ligero)
CHECKED_BAG_A2C = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', []),
    ('seatmap_dom_loaded', [checked_bag_filter()])
]}

# Checked Bag A2C - DB (Vuela Ligero)
CHECKED_BAG_A2C_DB = {'events': [
    ('ce:(NEW) baggage_dom_loaded_with_vuela_ligero', [get_DB_filter()]),
    ('seatmap_dom_loaded', [checked_bag_filter(), get_DB_filter()])
]}