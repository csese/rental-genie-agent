-- Rental Genie Database Schema for Supabase
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE tenant_status AS ENUM (
  'prospect',
  'qualified', 
  'viewing_scheduled',
  'application_submitted',
  'approved',
  'active_tenant',
  'former_tenant',
  'rejected',
  'withdrawn'
);

CREATE TYPE platform_type AS ENUM (
  'facebook',
  'web',
  'whatsapp',
  'telegram',
  'email'
);

CREATE TYPE message_type AS ENUM (
  'user',
  'agent',
  'system'
);

-- Properties table
CREATE TABLE properties (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL,
  address_street TEXT,
  city TEXT,
  zip_code TEXT,
  country TEXT DEFAULT 'France',
  description TEXT,
  status TEXT DEFAULT 'available',
  rent_amount DECIMAL(10,2),
  rent_currency TEXT DEFAULT 'EUR',
  utilities_amount DECIMAL(10,2),
  surface_area DECIMAL(8,2), -- square meters
  room_count INTEGER,
  bathroom_type TEXT DEFAULT 'shared',
  availability_date DATE,
  deposit_amount DECIMAL(10,2),
  appliances_included TEXT[], -- array of appliances
  apartment_name TEXT,
  room_sub_name TEXT,
  property_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tenants table (flexible JSON structure)
CREATE TABLE tenants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT UNIQUE,
  status tenant_status DEFAULT 'prospect',
  
  -- Core profile data (structured)
  age INTEGER,
  sex TEXT CHECK (sex IN ('Male', 'Female', 'Other')),
  occupation TEXT,
  move_in_date DATE,
  rental_duration TEXT,
  guarantor_status TEXT CHECK (guarantor_status IN ('Yes', 'No', 'Need', 'Visale')),
  guarantor_details TEXT,
  viewing_interest BOOLEAN DEFAULT FALSE,
  availability TEXT,
  language_preference TEXT CHECK (language_preference IN ('English', 'French')),
  property_interest TEXT,
  
  -- Dates
  application_date DATE,
  lease_start_date DATE,
  lease_end_date DATE,
  
  -- Flexible data storage
  profile_data JSONB DEFAULT '{}', -- Store any additional fields
  notes TEXT,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  conversation_turns INTEGER DEFAULT 0
);

-- Chat sessions table
CREATE TABLE chat_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT UNIQUE NOT NULL,
  platform platform_type NOT NULL,
  user_id TEXT, -- Facebook user ID, etc.
  tenant_id UUID REFERENCES tenants(id),
  status TEXT DEFAULT 'active',
  handoff_completed BOOLEAN DEFAULT FALSE,
  handoff_reason TEXT,
  confidence_level DECIMAL(3,2), -- 0.00 to 1.00
  escalation_priority TEXT CHECK (escalation_priority IN ('low', 'medium', 'high', 'urgent')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversation messages table
CREATE TABLE conversation_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  session_id TEXT NOT NULL,
  message_type message_type NOT NULL,
  content TEXT NOT NULL,
  extracted_info JSONB, -- Store structured data extracted from message
  confidence DECIMAL(3,2),
  metadata JSONB DEFAULT '{}', -- Additional message metadata
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Property applications table
CREATE TABLE property_applications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id),
  property_id UUID REFERENCES properties(id),
  status TEXT DEFAULT 'pending',
  application_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_tenants_session_id ON tenants(session_id);
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_chat_sessions_session_id ON chat_sessions(session_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX idx_conversation_messages_created_at ON conversation_messages(created_at);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_city ON properties(city);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_property_applications_updated_at BEFORE UPDATE ON property_applications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) policies
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE property_applications ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (you can restrict later)
CREATE POLICY "Allow all operations on tenants" ON tenants FOR ALL USING (true);
CREATE POLICY "Allow all operations on chat_sessions" ON chat_sessions FOR ALL USING (true);
CREATE POLICY "Allow all operations on conversation_messages" ON conversation_messages FOR ALL USING (true);
CREATE POLICY "Allow all operations on properties" ON properties FOR ALL USING (true);
CREATE POLICY "Allow all operations on property_applications" ON property_applications FOR ALL USING (true);

-- Insert sample property data
INSERT INTO properties (
  name, address_street, city, zip_code, description, status, 
  rent_amount, surface_area, room_count, availability_date
) VALUES 
(
  'Modern 2-Bedroom Apartment', 
  '123 Rue de la Paix', 
  'Paris', 
  '75001', 
  'Beautiful modern apartment in the heart of Paris', 
  'available',
  1500.00,
  65.5,
  2,
  '2024-02-01'
),
(
  'Cozy Studio Near Metro', 
  '456 Avenue des Champs', 
  'Paris', 
  '75008', 
  'Cozy studio apartment with great metro access', 
  'available',
  1200.00,
  35.0,
  1,
  '2024-01-15'
);

-- Create views for easier querying
CREATE VIEW tenant_summary AS
SELECT 
  t.id,
  t.session_id,
  t.status,
  t.age,
  t.sex,
  t.occupation,
  t.move_in_date,
  t.conversation_turns,
  cs.platform,
  cs.user_id,
  cs.handoff_completed,
  t.created_at,
  t.updated_at
FROM tenants t
LEFT JOIN chat_sessions cs ON t.session_id = cs.session_id;

-- Create function to get tenant with conversation history
CREATE OR REPLACE FUNCTION get_tenant_with_history(p_session_id TEXT)
RETURNS TABLE (
  tenant_data JSONB,
  conversation_history JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    to_jsonb(t.*) as tenant_data,
    COALESCE(
      jsonb_agg(
        jsonb_build_object(
          'id', cm.id,
          'message_type', cm.message_type,
          'content', cm.content,
          'extracted_info', cm.extracted_info,
          'created_at', cm.created_at
        ) ORDER BY cm.created_at
      ) FILTER (WHERE cm.id IS NOT NULL),
      '[]'::jsonb
    ) as conversation_history
  FROM tenants t
  LEFT JOIN conversation_messages cm ON t.session_id = cm.session_id
  WHERE t.session_id = p_session_id
  GROUP BY t.id, t.session_id, t.status, t.age, t.sex, t.occupation, 
           t.move_in_date, t.rental_duration, t.guarantor_status, 
           t.guarantor_details, t.viewing_interest, t.availability, 
           t.language_preference, t.property_interest, t.application_date, 
           t.lease_start_date, t.lease_end_date, t.profile_data, t.notes, 
           t.created_at, t.updated_at, t.conversation_turns;
END;
$$ LANGUAGE plpgsql;
