"""
Configuration settings for the Rental Genie Dashboard
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Dashboard Configuration
DASHBOARD_TITLE = "Rental Genie Dashboard"
DASHBOARD_ICON = "🏠"
DASHBOARD_LAYOUT = "wide"

# Property Management
DEFAULT_ROOM_TYPES = ['single', 'double', 'studio']
DEFAULT_ROOM_STATUSES = ['available', 'occupied', 'maintenance']
DEFAULT_AMENITIES = [
    'WiFi', 'Parking', 'Kitchen', 'Bathroom', 'Balcony', 
    'Air Conditioning', 'Heating', 'Washing Machine', 'Dishwasher'
]

# Tenant Management
TENANT_STATUSES = [
    'prospect', 'qualified', 'viewing_scheduled', 'application_submitted',
    'approved', 'active_tenant', 'former_tenant', 'rejected', 'withdrawn'
]

PRIORITY_LEVELS = ['low', 'medium', 'high', 'urgent']

# Notification Settings
DEFAULT_NOTIFICATION_SETTINGS = {
    'email_notifications': True,
    'slack_notifications': True,
    'push_notifications': False,
    'daily_digest': True,
    'high_priority_alerts': True
}

# Agent Configuration
DEFAULT_AGENT_SETTINGS = {
    'handoff_threshold': 70,
    'auto_approve_score': 90,
    'max_conversation_turns': 20,
    'response_timeout': 30
}

# Dashboard Theme Colors
THEME_COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Priority Color Mapping
PRIORITY_COLORS = {
    'low': THEME_COLORS['success'],
    'medium': THEME_COLORS['warning'],
    'high': THEME_COLORS['danger'],
    'urgent': '#8b0000'  # Dark red
}

# Status Color Mapping
STATUS_COLORS = {
    'prospect': THEME_COLORS['info'],
    'qualified': THEME_COLORS['warning'],
    'viewing_scheduled': THEME_COLORS['secondary'],
    'application_submitted': THEME_COLORS['primary'],
    'approved': THEME_COLORS['success'],
    'active_tenant': THEME_COLORS['success'],
    'former_tenant': THEME_COLORS['light'],
    'rejected': THEME_COLORS['danger'],
    'withdrawn': THEME_COLORS['light']
}

# Export Settings
EXPORT_FORMATS = ['CSV', 'JSON', 'PDF']
EXPORT_DATE_FORMAT = '%Y-%m-%d_%H-%M-%S'

# Pagination Settings
ITEMS_PER_PAGE = 10
MAX_ITEMS_PER_PAGE = 50

# Cache Settings
CACHE_TTL = 300  # 5 minutes
CACHE_MAX_ENTRIES = 100

# Security Settings
SESSION_TIMEOUT = 3600  # 1 hour
MAX_LOGIN_ATTEMPTS = 3
PASSWORD_MIN_LENGTH = 8

# Localization
SUPPORTED_LANGUAGES = ['en', 'fr']
DEFAULT_LANGUAGE = 'en'

# File Upload Settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['.csv', '.json', '.xlsx', '.pdf']

# Dashboard Layout Settings
SIDEBAR_WIDTH = 300
MAIN_CONTENT_PADDING = 20

# Chart Settings
CHART_HEIGHT = 400
CHART_TEMPLATE = "plotly_white"

# Notification Templates
NOTIFICATION_TEMPLATES = {
    'new_tenant': {
        'title': 'New Tenant Inquiry',
        'message': 'A new tenant inquiry has been received for {property_name}.'
    },
    'handoff_required': {
        'title': 'Handoff Required',
        'message': 'A conversation requires human intervention. Priority: {priority}'
    },
    'viewing_scheduled': {
        'title': 'Viewing Scheduled',
        'message': 'A viewing has been scheduled for {property_name} with {tenant_name}.'
    }
}

# Validation Rules
VALIDATION_RULES = {
    'property_name': {
        'min_length': 2,
        'max_length': 100,
        'required': True
    },
    'room_price': {
        'min_value': 0,
        'max_value': 10000,
        'required': True
    },
    'tenant_age': {
        'min_value': 18,
        'max_value': 100,
        'required': False
    },
    'email': {
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'required': False
    }
}

# Performance Settings
ENABLE_CACHING = True
ENABLE_LOGGING = True
LOG_LEVEL = 'INFO'

# Development Settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
ENABLE_MOCK_DATA = os.getenv("ENABLE_MOCK_DATA", "False").lower() == "true"
