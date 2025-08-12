#!/usr/bin/env python3
"""
Rental Genie Dashboard for Property Owners
A comprehensive dashboard to manage properties, monitor tenant interactions, and oversee AI agent performance.
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if mock data mode is enabled
ENABLE_MOCK_DATA = os.getenv("ENABLE_MOCK_DATA", "False").lower() == "true"

# Page configuration
st.set_page_config(
    page_title="Rental Genie Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .property-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .tenant-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 0.5rem;
    }
    .high-priority {
        border-left-color: #dc3545;
    }
    .medium-priority {
        border-left-color: #ffc107;
    }
    .low-priority {
        border-left-color: #28a745;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class DashboardAPI:
    """API client for communicating with the Rental Genie backend"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
    
    def get_properties(self) -> List[Dict]:
        """Get all properties"""
        if ENABLE_MOCK_DATA:
            from utils import get_mock_properties
            return get_mock_properties()
        
        try:
            response = requests.get(f"{self.base_url}/properties")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to fetch properties: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return []
    
    def get_tenants(self) -> List[Dict]:
        """Get all tenant profiles"""
        if ENABLE_MOCK_DATA:
            from utils import get_mock_tenants
            return get_mock_tenants()
        
        try:
            response = requests.get(f"{self.base_url}/tenants")
            if response.status_code == 200:
                data = response.json()
                # Extract tenants array from response
                return data.get('tenants', []) if isinstance(data, dict) else data
            else:
                st.error(f"Failed to fetch tenants: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return []
    
    def get_conversations(self) -> List[Dict]:
        """Get all conversations"""
        if ENABLE_MOCK_DATA:
            from utils import get_mock_conversations
            return get_mock_conversations()
        
        try:
            response = requests.get(f"{self.base_url}/conversation")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to fetch conversations: {response.status_code}")
                return []
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return []
    
    def update_property(self, property_id: str, data: Dict) -> bool:
        """Update property details"""
        try:
            response = requests.put(f"{self.base_url}/properties/{property_id}", json=data)
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error updating property: {e}")
            return False
    
    def approve_tenant(self, session_id: str) -> bool:
        """Approve a tenant lead"""
        try:
            response = requests.post(f"{self.base_url}/tenants/{session_id}/approve")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error approving tenant: {e}")
            return False
    
    def reject_tenant(self, session_id: str) -> bool:
        """Reject a tenant lead"""
        try:
            response = requests.post(f"{self.base_url}/tenants/{session_id}/reject")
            return response.status_code == 200
        except Exception as e:
            st.error(f"Error rejecting tenant: {e}")
            return False
    
    def bulk_update_tenants(self, session_ids: List[str], status: str, additional_data: Optional[Dict] = None) -> Dict:
        """Bulk update tenant statuses"""
        try:
            payload = {
                "session_ids": session_ids,
                "status": status,
                "additional_data": additional_data or {}
            }
            response = requests.put(f"{self.base_url}/tenants/bulk-update", json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to bulk update tenants: {response.status_code}")
                return {"updated_count": 0, "failed_count": len(session_ids)}
        except Exception as e:
            st.error(f"Error bulk updating tenants: {e}")
            return {"updated_count": 0, "failed_count": len(session_ids)}

def transform_tenant_data(api_tenants):
    """Transform API tenant data to dashboard format"""
    transformed = []
    
    for tenant in api_tenants:
        if isinstance(tenant, dict):
            tenant_info = {
                'session_id': tenant.get('session_id', ''),
                'tenant_name': f"Tenant {tenant.get('session_id', 'Unknown')}",
                'tenant_age': tenant.get('age'),
                'tenant_occupation': tenant.get('occupation'),
                'tenant_language': tenant.get('language_preference'),
                'status': tenant.get('status', 'prospect'),
                'move_in_date': tenant.get('move_in_date'),
                'rental_duration': tenant.get('rental_duration'),
                'guarantor_status': tenant.get('guarantor_status'),
                'property_interest': tenant.get('property_interest'),
                'viewing_interest': tenant.get('viewing_interest'),
                'availability': tenant.get('availability'),
                'application_date': tenant.get('application_date'),
                'lease_start_date': tenant.get('lease_start_date'),
                'lease_end_date': tenant.get('lease_end_date'),
                'notes': tenant.get('notes'),
                'created_at': tenant.get('created_at'),
                'last_updated': tenant.get('last_updated'),
                'conversation_turns': tenant.get('conversation_turns'),
                'escalation_priority': 'medium'  # Default priority
            }
            transformed.append(tenant_info)
    
    return transformed

def transform_conversation_data(api_conversations):
    """Transform API conversation data to dashboard format"""
    transformed = []
    
    for conv in api_conversations:
        if isinstance(conv, dict):
            conversation_info = {
                'session_id': conv.get('session_id', ''),
                'status': conv.get('status', 'active'),
                'profile_complete': conv.get('profile_complete', False),
                'missing_info': conv.get('missing_info', []),
                'conversation_turns': conv.get('conversation_turns', 0),
                'last_updated': conv.get('last_updated', ''),
                'history': conv.get('history', [])
            }
            transformed.append(conversation_info)
    
    return transformed

# Initialize API client
api = DashboardAPI()

# Session state initialization
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'selected_property' not in st.session_state:
    st.session_state.selected_property = None
if 'selected_tenant' not in st.session_state:
    st.session_state.selected_tenant = None

def transform_property_data(api_properties):
    """Transform API property data to dashboard format"""
    transformed = []
    
    for prop in api_properties:
        fields = prop.get('fields', {})
        
        # Extract property information
        property_info = {
            'id': prop.get('id'),
            'name': fields.get('property_name', 'Unknown Property'),
            'address': f"{fields.get('address_street', '')}, {fields.get('city', '')} {fields.get('zip_code', '')}",
            'description': fields.get('Description', ''),
            'status': fields.get('status', 'Unknown'),
            'rent_amount': fields.get('rent_amount', 0),
            'utilities_amount': fields.get('utilities_amout', 0),
            'currency': fields.get('rent_currency', 'EUR'),
            'surface_area': fields.get('surface_apartment_square_meters', 0),
            'room_count': fields.get('number_of_rooms', 1),
            'bathroom_type': fields.get('Bathroom', 'Shared'),
            'availability_date': fields.get('date_of_availability', ''),
            'deposit_amount': fields.get('deposit_amount', 0),
            'appliances': fields.get('appliances_included', []),
            'apartment_name': fields.get('apartment_name', ''),
            'room_sub_name': fields.get('room_sub_name', ''),
            'property_type': fields.get('property_type', ''),
            'created_time': prop.get('createdTime', ''),
            # Create a single room entry for this property
            'rooms': [{
                'id': prop.get('id'),
                'name': fields.get('room_sub_name', f"Room in {fields.get('apartment_name', 'Property')}"),
                'type': 'single',
                'price': fields.get('rent_amount', 0),
                'status': 'available' if fields.get('status') == 'Available' else 'occupied',
                'amenities': fields.get('appliances_included', []),
                'surface_area': fields.get('surface_room_square_meters copy', 0),
                'bathroom_type': fields.get('Bathroom', 'Shared')
            }]
        }
        
        transformed.append(property_info)
    
    return transformed

def main_dashboard():
    """Main dashboard page"""
    st.markdown('<h1 class="main-header">🏠 Rental Genie Dashboard</h1>', unsafe_allow_html=True)
    
    # Get data from API
    raw_properties = api.get_properties()
    raw_tenants = api.get_tenants()
    raw_conversations = api.get_conversations()
    
    # Transform data
    properties = transform_property_data(raw_properties.get('properties', []) if isinstance(raw_properties, dict) else raw_properties)
    tenants = transform_tenant_data(raw_tenants)
    conversations = transform_conversation_data(raw_conversations)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Properties</h3>
            <h2>{len(properties)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_rooms = sum(len(prop.get('rooms', [])) for prop in properties)
        occupied_rooms = sum(
            sum(1 for room in prop.get('rooms', []) if room.get('status') == 'occupied')
            for prop in properties
        )
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        st.markdown(f"""
        <div class="metric-card">
            <h3>Occupancy Rate</h3>
            <h2>{occupancy_rate:.1f}%</h2>
            <p>{occupied_rooms}/{total_rooms} rooms</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        recent_tenants = [t for t in tenants if t.get('status') == 'prospect']
        st.markdown(f"""
        <div class="metric-card">
            <h3>New Leads</h3>
            <h2>{len(recent_tenants)}</h2>
            <p>This week</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        active_conversations = len([c for c in conversations if c.get('status') == 'active'])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active Conversations</h3>
            <h2>{active_conversations}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.subheader("📊 Recent Activity")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Recent tenant inquiries
        st.markdown("### Recent Tenant Inquiries")
        if tenants:
            recent_tenants_df = pd.DataFrame(tenants[:5])
            if not recent_tenants_df.empty:
                # Display key information
                for _, tenant in recent_tenants_df.iterrows():
                    priority_class = "high-priority" if tenant.get('escalation_priority') == 'high' else \
                                   "medium-priority" if tenant.get('escalation_priority') == 'medium' else "low-priority"
                    
                    st.markdown(f"""
                    <div class="tenant-card {priority_class}">
                        <h4>{tenant.get('tenant_name', 'Anonymous')}</h4>
                        <p><strong>Age:</strong> {tenant.get('tenant_age', 'N/A')} | 
                           <strong>Occupation:</strong> {tenant.get('tenant_occupation', 'N/A')}</p>
                        <p><strong>Move-in:</strong> {tenant.get('move_in_date', 'N/A')} | 
                           <strong>Status:</strong> {tenant.get('status', 'N/A')}</p>
                        <p><strong>Property Interest:</strong> {tenant.get('property_interest', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No tenant inquiries yet.")
    
    with col2:
        # Available properties
        st.markdown("### 🏠 Available Properties")
        
        # Filter for available and soon-to-be-available properties
        available_properties = []
        soon_available_properties = []
        
        for prop in properties:
            status = prop.get('status', '').lower()
            availability_date = prop.get('availability_date', '')
            
            if status == 'available':
                available_properties.append(prop)
            elif availability_date:
                try:
                    # Parse availability date
                    avail_date = datetime.strptime(availability_date, '%Y-%m-%d')
                    days_until_available = (avail_date - datetime.now()).days
                    
                    if 0 <= days_until_available <= 30:  # Available within 1 month
                        soon_available_properties.append(prop)
                except:
                    pass  # Skip if date parsing fails
        
        # Show available properties
        if available_properties:
            st.markdown("**Currently Available:**")
            for prop in available_properties[:3]:  # Show first 3
                st.markdown(f"""
                <div class="property-card">
                    <h4>🏠 {prop.get('name', 'Unknown Property')}</h4>
                    <p><strong>Rent:</strong> {prop.get('rent_amount', 0)}€ | 
                       <strong>Address:</strong> {prop.get('address', 'N/A')}</p>
                    <p><strong>Status:</strong> {prop.get('status', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No properties currently available")
        
        # Show soon-to-be-available properties
        if soon_available_properties:
            st.markdown("**Available Soon (within 1 month):**")
            for prop in soon_available_properties[:3]:  # Show first 3
                avail_date = prop.get('availability_date', '')
                st.markdown(f"""
                <div class="property-card">
                    <h4>⏰ {prop.get('name', 'Unknown Property')}</h4>
                    <p><strong>Rent:</strong> {prop.get('rent_amount', 0)}€ | 
                       <strong>Available:</strong> {avail_date}</p>
                    <p><strong>Address:</strong> {prop.get('address', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("📋 View All Properties", use_container_width=True):
            st.session_state.current_page = "Properties"
            st.rerun()
        
        if st.button("👥 View All Tenants", use_container_width=True):
            st.session_state.current_page = "Tenants"
            st.rerun()
        
        if st.button("💬 View Conversations", use_container_width=True):
            st.session_state.current_page = "Conversations"
            st.rerun()
        
        if st.button("📊 View Reports", use_container_width=True):
            st.session_state.current_page = "Reports"
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "Settings"
            st.rerun()

def properties_page():
    """Properties management page"""
    st.markdown('<h1 class="main-header">🏢 Properties Management</h1>', unsafe_allow_html=True)
    
    api = DashboardAPI()
    raw_properties = api.get_properties()
    
    # Transform properties data
    properties = transform_property_data(raw_properties.get('properties', []) if isinstance(raw_properties, dict) else raw_properties)
    
    if not properties:
        st.warning("No properties found. Please add properties through the API.")
        return
    
    # Property selection
    property_names = [prop.get('name', f"Property {i+1}") for i, prop in enumerate(properties)]
    selected_property_idx = st.selectbox("Select Property", range(len(properties)), 
                                       format_func=lambda x: property_names[x])
    
    selected_property = properties[selected_property_idx]
    
    # Property details
    st.subheader(f"📋 {selected_property.get('name', 'Property Details')}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Property information
        st.markdown("### Property Information")
        
        # Editable property details form
        with st.form("property_details_form"):
            st.markdown("#### Edit Property Details")
            
            # Get current values
            current_name = selected_property.get('name', '')
            current_address = selected_property.get('address', '')
            current_description = selected_property.get('description', '')
            current_status = selected_property.get('status', 'Unknown')
            current_rent = selected_property.get('rent_amount', 0)
            current_utilities = selected_property.get('utilities_amount', 0)
            current_availability = selected_property.get('availability_date', '')
            current_deposit = selected_property.get('deposit_amount', 0)
            
            # Form fields
            new_name = st.text_input("Property Name", value=current_name)
            new_address = st.text_input("Address", value=current_address)
            new_description = st.text_area("Description", value=current_description, height=100)
            
            # Status options
            status_options = ['Available', 'Not available', 'Under maintenance', 'Reserved']
            current_status_index = status_options.index(current_status) if current_status in status_options else 0
            new_status = st.selectbox("Status", status_options, index=current_status_index)
            
            # Financial fields
            col1_financial, col2_financial = st.columns(2)
            with col1_financial:
                new_rent = st.number_input("Monthly Rent (€)", value=float(current_rent), min_value=0.0, step=10.0)
                new_availability = st.text_input("Availability Date", value=current_availability, 
                                               help="Format: YYYY-MM-DD")
            with col2_financial:
                new_utilities = st.number_input("Utilities (€)", value=float(current_utilities), min_value=0.0, step=5.0)
                new_deposit = st.number_input("Deposit Amount (€)", value=float(current_deposit), min_value=0.0, step=50.0)
            
            # Submit button
            if st.form_submit_button("💾 Update Property"):
                # Prepare update data
                update_data = {
                    'property_name': new_name,
                    'address_street': new_address.split(',')[0] if new_address else '',
                    'city': new_address.split(',')[1].strip() if new_address and ',' in new_address else '',
                    'description': new_description,
                    'status': new_status,
                    'rent_amount': new_rent,
                    'utilities_amount': new_utilities,
                    'date_of_availability': new_availability,
                    'deposit_amount': new_deposit
                }
                
                # Call API to update property
                if api.update_property(selected_property.get('id'), update_data):
                    st.success("✅ Property updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update property. Please try again.")
        
        # Display current values (read-only view)
        st.markdown("#### Current Property Details")
        st.markdown(f"""
        **Property Name:** {selected_property.get('name')}  
        **Address:** {selected_property.get('address')}  
        **Description:** {selected_property.get('description')}  
        **Status:** {selected_property.get('status')}  
        **Rent:** {selected_property.get('rent_amount')} {selected_property.get('currency')}  
        **Utilities:** {selected_property.get('utilities_amount')} {selected_property.get('currency')}  
        **Surface Area:** {selected_property.get('surface_area')} m²  
        **Bathroom Type:** {selected_property.get('bathroom_type')}  
        **Availability Date:** {selected_property.get('availability_date')}  
        **Deposit:** {selected_property.get('deposit_amount')} {selected_property.get('currency')}
        """)
    
    with col2:
        # Property stats
        st.markdown("### Property Statistics")
        
        rooms = selected_property.get('rooms', [])
        total_rooms = len(rooms)
        available_rooms = len([r for r in rooms if r.get('status') == 'available'])
        occupied_rooms = len([r for r in rooms if r.get('status') == 'occupied'])
        
        st.metric("Total Rooms", total_rooms)
        st.metric("Available", available_rooms)
        st.metric("Occupied", occupied_rooms)
        
        if total_rooms > 0:
            occupancy_rate = (occupied_rooms / total_rooms) * 100
            st.metric("Occupancy Rate", f"{occupancy_rate:.1f}%")
    
    # Rooms management
    st.subheader("🏠 Rooms Management")
    
    rooms = selected_property.get('rooms', [])
    
    if rooms:
        # Create tabs for each room
        room_tabs = st.tabs([f"Room {i+1}" for i in range(len(rooms))])
        
        for i, (tab, room) in enumerate(zip(room_tabs, rooms)):
            with tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Room Details")
                    
                    st.markdown(f"""
                    **Room Name:** {room.get('name')}  
                    **Type:** {room.get('type')}  
                    **Price:** {room.get('price')} {selected_property.get('currency')}  
                    **Status:** {room.get('status')}  
                    **Surface Area:** {room.get('surface_area')} m²  
                    **Bathroom Type:** {room.get('bathroom_type')}
                    """)
                
                with col2:
                    st.markdown("### Amenities")
                    
                    amenities = room.get('amenities', [])
                    if amenities:
                        for amenity in amenities:
                            st.markdown(f"✅ {amenity}")
                    else:
                        st.info("No amenities listed")
    
    # Property amenities
    st.subheader("🏠 Property Amenities")
    
    appliances = selected_property.get('appliances', [])
    if appliances:
        cols = st.columns(3)
        for i, appliance in enumerate(appliances):
            with cols[i % 3]:
                st.markdown(f"✅ {appliance}")
    else:
        st.info("No appliances listed")
    
    # Bulk operations
    st.subheader("🔄 Bulk Operations")
    
    with st.expander("Bulk Update Properties"):
        st.markdown("Update multiple properties at once")
        
        # Select properties to update
        property_options = [f"{prop.get('name', 'Unknown')} ({prop.get('id', 'No ID')})" for prop in properties]
        selected_properties = st.multiselect("Select properties to update", property_options)
        
        if selected_properties:
            with st.form("bulk_update_form"):
                st.markdown("#### Bulk Update Settings")
                
                # Common fields for bulk update
                bulk_status = st.selectbox("Set Status for All Selected", 
                                         ['Keep current', 'Available', 'Not available', 'Under maintenance', 'Reserved'])
                
                col1_bulk, col2_bulk = st.columns(2)
                with col1_bulk:
                    bulk_rent_adjustment = st.number_input("Rent Adjustment (%)", value=0, min_value=-50, max_value=50, 
                                                         help="Percentage to adjust rent by")
                    bulk_utilities_adjustment = st.number_input("Utilities Adjustment (%)", value=0, min_value=-50, max_value=50)
                
                with col2_bulk:
                    bulk_availability = st.text_input("Set Availability Date for All", 
                                                    help="Leave empty to keep current dates")
                    bulk_deposit_adjustment = st.number_input("Deposit Adjustment (%)", value=0, min_value=-50, max_value=50)
                
                if st.form_submit_button("🔄 Apply Bulk Update"):
                    updated_count = 0
                    for prop_option in selected_properties:
                        # Extract property ID from the option string
                        prop_id = prop_option.split('(')[-1].rstrip(')')
                        
                        # Find the property
                        for prop in properties:
                            if prop.get('id') == prop_id:
                                # Prepare update data
                                update_data = {}
                                
                                if bulk_status != 'Keep current':
                                    update_data['status'] = bulk_status
                                
                                if bulk_rent_adjustment != 0:
                                    current_rent = prop.get('rent_amount', 0)
                                    new_rent = current_rent * (1 + bulk_rent_adjustment / 100)
                                    update_data['rent_amount'] = new_rent
                                
                                if bulk_utilities_adjustment != 0:
                                    current_utilities = prop.get('utilities_amount', 0)
                                    new_utilities = current_utilities * (1 + bulk_utilities_adjustment / 100)
                                    update_data['utilities_amount'] = new_utilities
                                
                                if bulk_deposit_adjustment != 0:
                                    current_deposit = prop.get('deposit_amount', 0)
                                    new_deposit = current_deposit * (1 + bulk_deposit_adjustment / 100)
                                    update_data['deposit_amount'] = new_deposit
                                
                                if bulk_availability:
                                    update_data['date_of_availability'] = bulk_availability
                                
                                # Update the property
                                if update_data and api.update_property(prop_id, update_data):
                                    updated_count += 1
                                
                                break
                    
                    if updated_count > 0:
                        st.success(f"✅ Successfully updated {updated_count} properties!")
                        st.rerun()
                    else:
                        st.error("❌ No properties were updated. Please check your selections.")

def tenants_page():
    """Tenants management page"""
    st.markdown('<h1 class="main-header">👥 Tenants Management</h1>', unsafe_allow_html=True)
    
    raw_tenants = api.get_tenants()
    raw_conversations = api.get_conversations()
    
    # Transform data
    tenants = transform_tenant_data(raw_tenants)
    conversations = transform_conversation_data(raw_conversations)
    
    if not tenants:
        st.info("No tenant inquiries yet.")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Filter by Status", 
                                   ['All'] + list(set(t.get('status') for t in tenants if t.get('status'))))
    
    with col2:
        priority_filter = st.selectbox("Filter by Priority", 
                                     ['All', 'low', 'medium', 'high', 'urgent'])
    
    with col3:
        search_term = st.text_input("Search by name or occupation")
    
    # Filter tenants
    filtered_tenants = tenants
    if status_filter != 'All':
        filtered_tenants = [t for t in filtered_tenants if t.get('status') == status_filter]
    if priority_filter != 'All':
        filtered_tenants = [t for t in filtered_tenants if t.get('escalation_priority') == priority_filter]
    if search_term:
        filtered_tenants = [t for t in filtered_tenants 
                          if search_term.lower() in t.get('tenant_name', '').lower() 
                          or search_term.lower() in t.get('tenant_occupation', '').lower()]
    
    # Bulk operations
    st.subheader("🔄 Bulk Operations")
    
    with st.expander("Bulk Update Tenant Statuses"):
        st.markdown("Update multiple tenants' status at once")
        
        # Select tenants to update
        tenant_options = [f"{t.get('tenant_name', 'Unknown')} ({t.get('session_id', 'No ID')})" for t in tenants]
        selected_tenants = st.multiselect("Select tenants to update", tenant_options)
        
        if selected_tenants:
            with st.form("bulk_tenant_update_form"):
                st.markdown("#### Bulk Status Update")
                
                # Status options
                status_options = [
                    'prospect', 'qualified', 'viewing_scheduled', 
                    'application_submitted', 'approved', 'active_tenant', 
                    'former_tenant', 'rejected', 'withdrawn'
                ]
                
                new_status = st.selectbox("Set Status for All Selected", status_options)
                
                # Additional notes
                additional_notes = st.text_area("Additional Notes (optional)", 
                                              help="Add notes to the status update")
                
                if st.form_submit_button("🔄 Apply Bulk Status Update"):
                    # Extract session IDs
                    session_ids = []
                    for tenant_option in selected_tenants:
                        session_id = tenant_option.split('(')[-1].rstrip(')')
                        session_ids.append(session_id)
                    
                    # Prepare additional data
                    additional_data = {}
                    if additional_notes:
                        additional_data['notes'] = additional_notes
                        additional_data['bulk_update_date'] = datetime.now().isoformat()
                    
                    # Call bulk update
                    result = api.bulk_update_tenants(session_ids, new_status, additional_data)
                    
                    if result.get('updated_count', 0) > 0:
                        st.success(f"✅ Successfully updated {result['updated_count']} tenants to '{new_status}' status!")
                        if result.get('failed_count', 0) > 0:
                            st.warning(f"⚠️ {result['failed_count']} tenants failed to update")
                        st.rerun()
                    else:
                        st.error("❌ No tenants were updated. Please check your selections.")
    
    # Display tenants
    st.subheader(f"📋 Tenant Inquiries ({len(filtered_tenants)} found)")
    
    for tenant in filtered_tenants:
        priority_class = "high-priority" if tenant.get('escalation_priority') == 'high' else \
                       "medium-priority" if tenant.get('escalation_priority') == 'medium' else "low-priority"
        
        with st.expander(f"{tenant.get('tenant_name', 'Anonymous')} - {tenant.get('status', 'N/A')} ({tenant.get('escalation_priority', 'N/A')} priority)"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                <div class="tenant-card {priority_class}">
                    <h4>Tenant Profile</h4>
                    <p><strong>Age:</strong> {tenant.get('tenant_age', 'N/A')}</p>
                    <p><strong>Occupation:</strong> {tenant.get('tenant_occupation', 'N/A')}</p>
                    <p><strong>Language:</strong> {tenant.get('tenant_language', 'N/A')}</p>
                    <p><strong>Move-in Date:</strong> {tenant.get('move_in_date', 'N/A')}</p>
                    <p><strong>Rental Duration:</strong> {tenant.get('rental_duration', 'N/A')}</p>
                    <p><strong>Guarantor Status:</strong> {tenant.get('guarantor_status', 'N/A')}</p>
                    <p><strong>Property Interest:</strong> {tenant.get('property_interest', 'N/A')}</p>
                    <p><strong>Viewing Interest:</strong> {'Yes' if tenant.get('viewing_interest') else 'No'}</p>
                    <p><strong>Availability:</strong> {tenant.get('availability', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### Actions")
                
                if tenant.get('status') == 'prospect':
                    if st.button("✅ Approve", key=f"approve_{tenant.get('session_id')}"):
                        if api.approve_tenant(tenant.get('session_id')):
                            st.success("Tenant approved!")
                            st.rerun()
                        else:
                            st.error("Failed to approve tenant.")
                    
                    if st.button("❌ Reject", key=f"reject_{tenant.get('session_id')}"):
                        if api.reject_tenant(tenant.get('session_id')):
                            st.success("Tenant rejected!")
                            st.rerun()
                        else:
                            st.error("Failed to reject tenant.")
                
                if st.button("📞 Contact", key=f"contact_{tenant.get('session_id')}"):
                    st.info("Contact functionality would be implemented here.")
                
                if st.button("📅 Schedule Viewing", key=f"viewing_{tenant.get('session_id')}"):
                    st.info("Viewing scheduling would be implemented here.")
            
            # Conversation history
            st.markdown("### Conversation History")
            session_id = tenant.get('session_id')
            if session_id:
                conversation = next((c for c in conversations if c.get('session_id') == session_id), None)
                if conversation and conversation.get('history'):
                    for msg in conversation['history'][-5:]:  # Show last 5 messages
                        st.markdown(f"**{msg.get('role', 'Unknown')}:** {msg.get('content', '')}")
                else:
                    st.info("No conversation history available.")

def conversations_page():
    """Conversations management page"""
    st.markdown('<h1 class="main-header">💬 Agent Conversations</h1>', unsafe_allow_html=True)
    
    raw_tenants = api.get_tenants()
    raw_conversations = api.get_conversations()
    
    # Transform data
    tenants = transform_tenant_data(raw_tenants)
    conversations = transform_conversation_data(raw_conversations)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tenant_filter = st.selectbox("Filter by Tenant", 
                                   ['All'] + [t.get('tenant_name', 'Unknown') for t in tenants])
    
    with col2:
        status_filter = st.selectbox("Filter by Status", 
                                   ['All'] + list(set(t.get('status') for t in tenants if t.get('status'))))
    
    with col3:
        search_term = st.text_input("Search conversations")
    
    # Filter conversations
    filtered_conversations = conversations
    filtered_tenants = tenants
    
    if tenant_filter != 'All':
        filtered_tenants = [t for t in tenants if t.get('tenant_name') == tenant_filter]
        tenant_session_ids = [t.get('session_id') for t in filtered_tenants]
        filtered_conversations = [c for c in conversations if c.get('session_id') in tenant_session_ids]
    
    if status_filter != 'All':
        filtered_tenants = [t for t in filtered_tenants if t.get('status') == status_filter]
        tenant_session_ids = [t.get('session_id') for t in filtered_tenants]
        filtered_conversations = [c for c in filtered_conversations if c.get('session_id') in tenant_session_ids]
    
    if search_term:
        # Search in conversation history
        search_conversations = []
        for conv in filtered_conversations:
            history = conv.get('history', [])
            for msg in history:
                if search_term.lower() in msg.get('content', '').lower():
                    search_conversations.append(conv)
                    break
        filtered_conversations = search_conversations
    
    # Display conversations
    st.subheader(f"💬 Agent Conversations ({len(filtered_conversations)} found)")
    
    if not filtered_conversations:
        st.info("No conversations found matching your filters.")
        return
    
    # Group conversations by tenant
    tenant_conversations = {}
    for conv in filtered_conversations:
        session_id = conv.get('session_id')
        tenant = next((t for t in tenants if t.get('session_id') == session_id), None)
        if tenant:
            tenant_name = tenant.get('tenant_name', 'Unknown')
            if tenant_name not in tenant_conversations:
                tenant_conversations[tenant_name] = []
            tenant_conversations[tenant_name].append(conv)
    
    # Display conversations grouped by tenant
    for tenant_name, tenant_convs in tenant_conversations.items():
        tenant = next((t for t in tenants if t.get('tenant_name') == tenant_name), None)
        
        with st.expander(f"👤 {tenant_name} - {len(tenant_convs)} conversation(s)", expanded=True):
            # Tenant info
            if tenant:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Status:** {tenant.get('status', 'N/A')}")
                    st.markdown(f"**Age:** {tenant.get('tenant_age', 'N/A')}")
                with col2:
                    st.markdown(f"**Occupation:** {tenant.get('tenant_occupation', 'N/A')}")
                    st.markdown(f"**Move-in Date:** {tenant.get('move_in_date', 'N/A')}")
                with col3:
                    st.markdown(f"**Property Interest:** {tenant.get('property_interest', 'N/A')}")
                    st.markdown(f"**Conversation Turns:** {tenant.get('conversation_turns', 0)}")
            
            # Conversation history
            for i, conv in enumerate(tenant_convs):
                st.markdown(f"### Conversation {i+1}")
                
                # Conversation metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**Session ID:** {conv.get('session_id', 'N/A')}")
                with col2:
                    st.markdown(f"**Profile Complete:** {'✅' if conv.get('profile_complete') else '❌'}")
                with col3:
                    st.markdown(f"**Last Updated:** {conv.get('last_updated', 'N/A')}")
                
                # Missing information
                missing_info = conv.get('missing_info', [])
                if missing_info:
                    st.markdown("**Missing Information:**")
                    for info in missing_info:
                        st.markdown(f"- {info}")
                
                # Message history
                history = conv.get('history', [])
                if history:
                    st.markdown("#### Message History")
                    
                    # Create a container for messages
                    message_container = st.container()
                    
                    with message_container:
                        for j, msg in enumerate(history):
                            role = msg.get('role', 'Unknown')
                            content = msg.get('content', '')
                            timestamp = msg.get('timestamp', '')
                            
                            # Style based on role
                            if role.lower() == 'user':
                                st.markdown(f"""
                                <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                    <strong>👤 User ({timestamp}):</strong><br>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                            elif role.lower() == 'assistant':
                                st.markdown(f"""
                                <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                    <strong>🤖 Agent ({timestamp}):</strong><br>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                    <strong>{role} ({timestamp}):</strong><br>
                                    {content}
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.info("No message history available for this conversation.")
                
                st.markdown("---")
    
    # Conversation analytics
    st.subheader("📊 Conversation Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_conversations = len(conversations)
        st.metric("Total Conversations", total_conversations)
    
    with col2:
        active_conversations = len([c for c in conversations if c.get('status') == 'active'])
        st.metric("Active Conversations", active_conversations)
    
    with col3:
        complete_profiles = len([c for c in conversations if c.get('profile_complete')])
        st.metric("Complete Profiles", complete_profiles)
    
    with col4:
        avg_turns = sum(c.get('conversation_turns', 0) for c in conversations) / len(conversations) if conversations else 0
        st.metric("Avg Conversation Turns", f"{avg_turns:.1f}")

def reports_page():
    """Reports and analytics page"""
    st.markdown('<h1 class="main-header">📊 Reports & Analytics</h1>', unsafe_allow_html=True)
    
    raw_tenants = api.get_tenants()
    raw_properties = api.get_properties()
    raw_conversations = api.get_conversations()
    
    # Transform data
    tenants = transform_tenant_data(raw_tenants)
    properties = transform_property_data(raw_properties.get('properties', []) if isinstance(raw_properties, dict) else raw_properties)
    conversations = transform_conversation_data(raw_conversations)
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())
    
    # Key metrics
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_inquiries = len(tenants)
        st.metric("Total Inquiries", total_inquiries)
    
    with col2:
        qualified_leads = len([t for t in tenants if t.get('status') == 'qualified'])
        st.metric("Qualified Leads", qualified_leads)
    
    with col3:
        viewings_scheduled = len([t for t in tenants if t.get('status') == 'viewing_scheduled'])
        st.metric("Viewings Scheduled", viewings_scheduled)
    
    with col4:
        applications_submitted = len([t for t in tenants if t.get('status') == 'application_submitted'])
        st.metric("Applications Submitted", applications_submitted)
    
    # Charts
    st.subheader("📊 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        if tenants:
            status_counts = pd.DataFrame([t.get('status', 'unknown') for t in tenants]).value_counts()
            fig_status = px.pie(values=status_counts.values, names=status_counts.index, 
                              title="Tenant Status Distribution")
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority distribution
        if tenants:
            priority_counts = pd.DataFrame([t.get('escalation_priority', 'unknown') for t in tenants]).value_counts()
            fig_priority = px.bar(x=priority_counts.index, y=priority_counts.values,
                                title="Inquiry Priority Distribution")
            st.plotly_chart(fig_priority, use_container_width=True)
    
    # Occupancy by property
    st.subheader("🏢 Property Occupancy")
    
    if properties:
        property_data = []
        for prop in properties:
            rooms = prop.get('rooms', [])
            total_rooms = len(rooms)
            occupied_rooms = len([r for r in rooms if r.get('status') == 'occupied'])
            occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
            
            property_data.append({
                'Property': prop.get('name', 'Unknown'),
                'Total Rooms': total_rooms,
                'Occupied': occupied_rooms,
                'Available': total_rooms - occupied_rooms,
                'Occupancy Rate': occupancy_rate
            })
        
        if property_data:
            df_properties = pd.DataFrame(property_data)
            fig_occupancy = px.bar(df_properties, x='Property', y=['Occupied', 'Available'],
                                 title="Room Occupancy by Property",
                                 barmode='stack')
            st.plotly_chart(fig_occupancy, use_container_width=True)
    
    # Recent activity timeline
    st.subheader("📅 Recent Activity")
    
    if tenants:
        recent_activity = []
        for tenant in tenants[:10]:  # Last 10 tenants
            recent_activity.append({
                'Date': tenant.get('created_at', 'Unknown'),
                'Tenant': tenant.get('tenant_name', 'Anonymous'),
                'Action': f"New inquiry - {tenant.get('status', 'N/A')}",
                'Priority': tenant.get('escalation_priority', 'N/A')
            })
        
        if recent_activity:
            df_activity = pd.DataFrame(recent_activity)
            st.dataframe(df_activity, use_container_width=True)

def settings_page():
    """Settings and configuration page"""
    st.markdown('<h1 class="main-header">⚙️ Settings</h1>', unsafe_allow_html=True)
    
    st.subheader("🔧 Dashboard Configuration")
    
    # API Configuration
    st.markdown("### API Configuration")
    current_api_url = st.text_input("API Base URL", value=API_BASE_URL)
    
    if st.button("Test API Connection"):
        try:
            response = requests.get(f"{current_api_url}/health")
            if response.status_code == 200:
                st.success("✅ API connection successful!")
            else:
                st.error("❌ API connection failed!")
        except Exception as e:
            st.error(f"❌ API connection error: {e}")
    
    # Notification Settings
    st.markdown("### Notification Settings")
    
    email_notifications = st.checkbox("Enable Email Notifications", value=True)
    slack_notifications = st.checkbox("Enable Slack Notifications", value=True)
    push_notifications = st.checkbox("Enable Push Notifications", value=False)
    
    if st.button("Save Notification Settings"):
        st.success("Notification settings saved!")
    
    # Agent Configuration
    st.markdown("### Agent Configuration")
    
    handoff_threshold = st.slider("Handoff Confidence Threshold", 0, 100, 70)
    auto_approve_score = st.slider("Auto-approve Match Score", 0, 100, 90)
    
    if st.button("Save Agent Settings"):
        st.success("Agent settings saved!")
    
    # Data Export
    st.markdown("### Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Tenant Data (CSV)"):
            st.info("Export functionality would be implemented here.")
    
    with col2:
        if st.button("📊 Export Property Data (CSV)"):
            st.info("Export functionality would be implemented here.")
    
    # System Information
    st.markdown("### System Information")
    
    st.info(f"""
    **Dashboard Version:** 1.0.0
    **API Base URL:** {API_BASE_URL}
    **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)

# Sidebar navigation
with st.sidebar:
    st.markdown("## 🏠 Rental Genie")
    
    # Show mock data indicator
    if ENABLE_MOCK_DATA:
        st.warning("🧪 Mock Data Mode")
    
    st.markdown("---")
    
    # Navigation menu
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()
    
    if st.button("🏢 Properties", use_container_width=True):
        st.session_state.current_page = "Properties"
        st.rerun()
    
    if st.button("👥 Tenants", use_container_width=True):
        st.session_state.current_page = "Tenants"
        st.rerun()
    
    if st.button("💬 Conversations", use_container_width=True):
        st.session_state.current_page = "Conversations"
        st.rerun()
    
    if st.button("📈 Reports", use_container_width=True):
        st.session_state.current_page = "Reports"
        st.rerun()
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.current_page = "Settings"
        st.rerun()
    
    st.markdown("---")
    
    # Quick stats in sidebar
    st.markdown("### Quick Stats")
    
    raw_properties = api.get_properties()
    raw_tenants = api.get_tenants()
    
    properties = transform_property_data(raw_properties.get('properties', []) if isinstance(raw_properties, dict) else raw_properties)
    tenants = transform_tenant_data(raw_tenants)
    
    st.metric("Properties", len(properties))
    st.metric("Total Leads", len(tenants))
    
    if tenants:
        recent_leads = len([t for t in tenants if t.get('status') == 'prospect'])
        st.metric("New Leads", recent_leads)
    
    st.markdown("---")
    
    # User info
    st.markdown("### User")
    st.markdown("👤 Property Owner")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.info("Logout functionality would be implemented here.")

# Main content area
if st.session_state.current_page == "Dashboard":
    main_dashboard()
elif st.session_state.current_page == "Properties":
    properties_page()
elif st.session_state.current_page == "Tenants":
    tenants_page()
elif st.session_state.current_page == "Conversations":
    conversations_page()
elif st.session_state.current_page == "Reports":
    reports_page()
elif st.session_state.current_page == "Settings":
    settings_page()
