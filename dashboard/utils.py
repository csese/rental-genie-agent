"""
Utility functions for the Rental Genie Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import base64
from io import BytesIO
import requests
from config import *

def format_currency(amount: float, currency: str = "€") -> str:
    """Format currency values"""
    return f"{currency}{amount:,.2f}"

def format_date(date_str: str, format_str: str = "%Y-%m-%d") -> str:
    """Format date strings"""
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime(format_str)
        return str(date_str)
    except:
        return str(date_str)

def calculate_match_score(tenant: Dict, property_data: Dict) -> float:
    """Calculate match score between tenant and property"""
    score = 0
    total_criteria = 0
    
    # Budget match
    if tenant.get('budget') and property_data.get('price'):
        tenant_budget = float(tenant.get('budget', 0))
        property_price = float(property_data.get('price', 0))
        if tenant_budget >= property_price:
            score += 20
        total_criteria += 20
    
    # Move-in date match
    if tenant.get('move_in_date') and property_data.get('available_from'):
        tenant_date = datetime.fromisoformat(tenant.get('move_in_date'))
        property_date = datetime.fromisoformat(property_data.get('available_from'))
        if tenant_date >= property_date:
            score += 20
        total_criteria += 20
    
    # Duration match
    if tenant.get('rental_duration') and property_data.get('min_stay'):
        tenant_duration = int(tenant.get('rental_duration', 0))
        property_min_stay = int(property_data.get('min_stay', 0))
        if tenant_duration >= property_min_stay:
            score += 20
        total_criteria += 20
    
    # Room type preference
    if tenant.get('property_interest') and property_data.get('type'):
        if tenant.get('property_interest').lower() in property_data.get('type', '').lower():
            score += 20
        total_criteria += 20
    
    # Guarantor status
    if tenant.get('guarantor_status') in ['Yes', 'Available', 'Visale']:
        score += 20
        total_criteria += 20
    
    return (score / total_criteria * 100) if total_criteria > 0 else 0

def get_priority_color(priority: str) -> str:
    """Get color for priority level"""
    return PRIORITY_COLORS.get(priority.lower(), THEME_COLORS['info'])

def get_status_color(status: str) -> str:
    """Get color for status"""
    return STATUS_COLORS.get(status.lower(), THEME_COLORS['info'])

def create_metric_card(title: str, value: Any, subtitle: str = "", color: str = THEME_COLORS['primary']) -> str:
    """Create HTML for metric card"""
    return f"""
    <div class="metric-card" style="border-left-color: {color};">
        <h3>{title}</h3>
        <h2>{value}</h2>
        {f'<p>{subtitle}</p>' if subtitle else ''}
    </div>
    """

def create_tenant_card(tenant: Dict) -> str:
    """Create HTML for tenant card"""
    priority = tenant.get('escalation_priority', 'low')
    priority_class = f"{priority}-priority"
    
    return f"""
    <div class="tenant-card {priority_class}">
        <h4>{tenant.get('tenant_name', 'Anonymous')}</h4>
        <p><strong>Age:</strong> {tenant.get('tenant_age', 'N/A')} | 
           <strong>Occupation:</strong> {tenant.get('tenant_occupation', 'N/A')}</p>
        <p><strong>Move-in:</strong> {format_date(tenant.get('move_in_date', 'N/A'))} | 
           <strong>Status:</strong> {tenant.get('status', 'N/A')}</p>
        <p><strong>Property Interest:</strong> {tenant.get('property_interest', 'N/A')}</p>
        <p><strong>Priority:</strong> {priority.upper()}</p>
    </div>
    """

def create_occupancy_chart(properties: List[Dict]) -> go.Figure:
    """Create occupancy chart"""
    property_data = []
    
    for prop in properties:
        rooms = prop.get('rooms', [])
        total_rooms = len(rooms)
        occupied_rooms = len([r for r in rooms if r.get('status') == 'occupied'])
        available_rooms = len([r for r in rooms if r.get('status') == 'available'])
        maintenance_rooms = len([r for r in rooms if r.get('status') == 'maintenance'])
        
        property_data.append({
            'Property': prop.get('name', 'Unknown'),
            'Occupied': occupied_rooms,
            'Available': available_rooms,
            'Maintenance': maintenance_rooms
        })
    
    if not property_data:
        return go.Figure()
    
    df = pd.DataFrame(property_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Occupied',
        x=df['Property'],
        y=df['Occupied'],
        marker_color=THEME_COLORS['success']
    ))
    
    fig.add_trace(go.Bar(
        name='Available',
        x=df['Property'],
        y=df['Available'],
        marker_color=THEME_COLORS['info']
    ))
    
    fig.add_trace(go.Bar(
        name='Maintenance',
        x=df['Property'],
        y=df['Maintenance'],
        marker_color=THEME_COLORS['warning']
    ))
    
    fig.update_layout(
        title="Room Occupancy by Property",
        barmode='stack',
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT
    )
    
    return fig

def create_status_distribution_chart(tenants: List[Dict]) -> go.Figure:
    """Create status distribution chart"""
    if not tenants:
        return go.Figure()
    
    status_counts = pd.DataFrame([t.get('status', 'unknown') for t in tenants]).value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Tenant Status Distribution",
        color_discrete_map=STATUS_COLORS
    )
    
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT
    )
    
    return fig

def create_priority_distribution_chart(tenants: List[Dict]) -> go.Figure:
    """Create priority distribution chart"""
    if not tenants:
        return go.Figure()
    
    priority_counts = pd.DataFrame([t.get('escalation_priority', 'unknown') for t in tenants]).value_counts()
    
    fig = px.bar(
        x=priority_counts.index,
        y=priority_counts.values,
        title="Inquiry Priority Distribution",
        color=priority_counts.index,
        color_discrete_map=PRIORITY_COLORS
    )
    
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT,
        showlegend=False
    )
    
    return fig

def create_timeline_chart(tenants: List[Dict]) -> go.Figure:
    """Create timeline chart of tenant inquiries"""
    if not tenants:
        return go.Figure()
    
    timeline_data = []
    for tenant in tenants:
        created_at = tenant.get('created_at')
        if created_at:
            try:
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                timeline_data.append({
                    'Date': date,
                    'Tenant': tenant.get('tenant_name', 'Anonymous'),
                    'Status': tenant.get('status', 'unknown'),
                    'Priority': tenant.get('escalation_priority', 'low')
                })
            except:
                continue
    
    if not timeline_data:
        return go.Figure()
    
    df = pd.DataFrame(timeline_data)
    df = df.sort_values('Date')
    
    fig = px.scatter(
        df,
        x='Date',
        y='Tenant',
        color='Priority',
        size='Priority',
        title="Tenant Inquiry Timeline",
        color_discrete_map=PRIORITY_COLORS
    )
    
    fig.update_layout(
        template=CHART_TEMPLATE,
        height=CHART_HEIGHT
    )
    
    return fig

def export_to_csv(data: List[Dict], filename: str) -> str:
    """Export data to CSV and return base64 encoded string"""
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return b64

def export_to_json(data: List[Dict], filename: str) -> str:
    """Export data to JSON and return base64 encoded string"""
    json_str = json.dumps(data, indent=2, default=str)
    b64 = base64.b64encode(json_str.encode()).decode()
    return b64

def validate_property_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate property data"""
    errors = []
    
    # Check required fields
    if not data.get('name'):
        errors.append("Property name is required")
    
    if not data.get('address'):
        errors.append("Property address is required")
    
    # Check field lengths
    if data.get('name') and len(data['name']) > VALIDATION_RULES['property_name']['max_length']:
        errors.append(f"Property name must be less than {VALIDATION_RULES['property_name']['max_length']} characters")
    
    return len(errors) == 0, errors

def validate_room_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate room data"""
    errors = []
    
    # Check price
    if data.get('price') is not None:
        price = float(data['price'])
        if price < VALIDATION_RULES['room_price']['min_value']:
            errors.append(f"Price must be at least {VALIDATION_RULES['room_price']['min_value']}")
        if price > VALIDATION_RULES['room_price']['max_value']:
            errors.append(f"Price must be less than {VALIDATION_RULES['room_price']['max_value']}")
    
    # Check room type
    if data.get('type') and data['type'] not in DEFAULT_ROOM_TYPES:
        errors.append(f"Room type must be one of: {', '.join(DEFAULT_ROOM_TYPES)}")
    
    return len(errors) == 0, errors

def get_mock_properties() -> List[Dict]:
    """Get mock property data for testing"""
    return [
        {
            'id': 'prop_1',
            'name': 'Downtown Apartment',
            'address': '123 Main St, City Center',
            'description': 'Modern apartment in the heart of the city',
            'rooms': [
                {
                    'id': 'room_1',
                    'name': 'Room 1',
                    'type': 'single',
                    'price': 800,
                    'status': 'available',
                    'amenities': ['WiFi', 'Kitchen', 'Bathroom'],
                    'min_stay': 6,
                    'max_stay': 12
                },
                {
                    'id': 'room_2',
                    'name': 'Room 2',
                    'type': 'double',
                    'price': 1200,
                    'status': 'occupied',
                    'amenities': ['WiFi', 'Kitchen', 'Bathroom', 'Balcony'],
                    'min_stay': 6,
                    'max_stay': 12
                }
            ]
        },
        {
            'id': 'prop_2',
            'name': 'Suburban House',
            'address': '456 Oak Ave, Suburbs',
            'description': 'Spacious house with garden',
            'rooms': [
                {
                    'id': 'room_3',
                    'name': 'Master Bedroom',
                    'type': 'double',
                    'price': 1500,
                    'status': 'available',
                    'amenities': ['WiFi', 'Kitchen', 'Bathroom', 'Garden'],
                    'min_stay': 12,
                    'max_stay': 24
                }
            ]
        }
    ]

def get_mock_tenants() -> List[Dict]:
    """Get mock tenant data for testing"""
    return [
        {
            'session_id': 'session_1',
            'tenant_name': 'John Doe',
            'tenant_age': 25,
            'tenant_occupation': 'Software Engineer',
            'tenant_language': 'English',
            'status': 'prospect',
            'escalation_priority': 'medium',
            'move_in_date': '2024-03-01',
            'rental_duration': '12 months',
            'guarantor_status': 'Yes',
            'property_interest': 'Downtown Apartment',
            'viewing_interest': True,
            'availability': 'Weekends',
            'created_at': '2024-01-15T10:30:00Z'
        },
        {
            'session_id': 'session_2',
            'tenant_name': 'Jane Smith',
            'tenant_age': 28,
            'tenant_occupation': 'Marketing Manager',
            'tenant_language': 'English',
            'status': 'qualified',
            'escalation_priority': 'high',
            'move_in_date': '2024-02-15',
            'rental_duration': '24 months',
            'guarantor_status': 'Available',
            'property_interest': 'Suburban House',
            'viewing_interest': True,
            'availability': 'Any time',
            'created_at': '2024-01-10T14:20:00Z'
        }
    ]

def get_mock_conversations() -> List[Dict]:
    """Get mock conversation data for testing"""
    return [
        {
            'session_id': 'session_1',
            'status': 'active',
            'history': [
                {'role': 'user', 'content': 'Hi, I\'m looking for an apartment in the city center.'},
                {'role': 'assistant', 'content': 'Hello! I can help you find the perfect place. What\'s your budget?'},
                {'role': 'user', 'content': 'Around 800-1000 euros per month.'}
            ]
        }
    ]

@st.cache_data(ttl=CACHE_TTL)
def cached_api_call(func, *args, **kwargs):
    """Cache API calls for better performance"""
    return func(*args, **kwargs)
