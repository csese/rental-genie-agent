#!/usr/bin/env python3
"""
Standalone unit tests for LLM extraction Pydantic models
"""

import unittest
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, List


# Define the models locally for testing
class ExtractedField(BaseModel):
    """Individual extracted field with confidence score"""
    value: Optional[str] = Field(None, description="The extracted value")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class TenantInfo(BaseModel):
    """Complete tenant information extraction result"""
    fields: Dict[str, ExtractedField] = Field(default_factory=dict, description="Extracted fields with confidence scores")
    language_preference: Optional[str] = Field(None, description="Detected language preference: French, English, or Other")
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence score")
    updated_fields: List[str] = Field(default_factory=list, description="List of field names that were updated")
    
    class Config:
        extra = "allow"  # Allow extra fields to prevent parsing errors


class TestExtractedField(unittest.TestCase):
    """Test the ExtractedField model"""
    
    def test_valid_extracted_field(self):
        """Test creating a valid ExtractedField"""
        field = ExtractedField(value="25", confidence=0.9)
        self.assertEqual(field.value, "25")
        self.assertEqual(field.confidence, 0.9)
    
    def test_extracted_field_with_none_value(self):
        """Test ExtractedField with None value"""
        field = ExtractedField(value=None, confidence=0.5)
        self.assertIsNone(field.value)
        self.assertEqual(field.confidence, 0.5)
    
    def test_extracted_field_confidence_bounds(self):
        """Test confidence score bounds"""
        # Test minimum confidence
        field = ExtractedField(value="test", confidence=0.0)
        self.assertEqual(field.confidence, 0.0)
        
        # Test maximum confidence
        field = ExtractedField(value="test", confidence=1.0)
        self.assertEqual(field.confidence, 1.0)
    
    def test_extracted_field_invalid_confidence(self):
        """Test that invalid confidence scores raise ValidationError"""
        with self.assertRaises(ValidationError):
            ExtractedField(value="test", confidence=-0.1)
        
        with self.assertRaises(ValidationError):
            ExtractedField(value="test", confidence=1.1)


class TestTenantInfo(unittest.TestCase):
    """Test the TenantInfo model"""
    
    def test_valid_tenant_info(self):
        """Test creating a valid TenantInfo"""
        fields = {
            "age": ExtractedField(value="25", confidence=0.9),
            "occupation": ExtractedField(value="engineer", confidence=0.8)
        }
        
        tenant_info = TenantInfo(
            fields=fields,
            language_preference="English",
            overall_confidence=0.85,
            updated_fields=["age", "occupation"]
        )
        
        self.assertEqual(len(tenant_info.fields), 2)
        self.assertEqual(tenant_info.language_preference, "English")
        self.assertEqual(tenant_info.overall_confidence, 0.85)
        self.assertEqual(tenant_info.updated_fields, ["age", "occupation"])
    
    def test_tenant_info_defaults(self):
        """Test TenantInfo with default values"""
        tenant_info = TenantInfo()
        
        self.assertEqual(tenant_info.fields, {})
        self.assertIsNone(tenant_info.language_preference)
        self.assertEqual(tenant_info.overall_confidence, 0.0)
        self.assertEqual(tenant_info.updated_fields, [])
    
    def test_tenant_info_confidence_bounds(self):
        """Test overall confidence bounds"""
        # Test minimum confidence
        tenant_info = TenantInfo(overall_confidence=0.0)
        self.assertEqual(tenant_info.overall_confidence, 0.0)
        
        # Test maximum confidence
        tenant_info = TenantInfo(overall_confidence=1.0)
        self.assertEqual(tenant_info.overall_confidence, 1.0)
    
    def test_tenant_info_invalid_confidence(self):
        """Test that invalid overall confidence raises ValidationError"""
        with self.assertRaises(ValidationError):
            TenantInfo(overall_confidence=-0.1)
        
        with self.assertRaises(ValidationError):
            TenantInfo(overall_confidence=1.1)
    
    def test_tenant_info_with_french_language(self):
        """Test TenantInfo with French language preference"""
        tenant_info = TenantInfo(language_preference="French")
        self.assertEqual(tenant_info.language_preference, "French")
    
    def test_tenant_info_with_other_language(self):
        """Test TenantInfo with Other language preference"""
        tenant_info = TenantInfo(language_preference="Other")
        self.assertEqual(tenant_info.language_preference, "Other")


class TestExtractionModelsIntegration(unittest.TestCase):
    """Test integration between ExtractedField and TenantInfo"""
    
    def test_complete_extraction_scenario(self):
        """Test a complete extraction scenario"""
        # Create extracted fields
        age_field = ExtractedField(value="28", confidence=0.9)
        sex_field = ExtractedField(value="female", confidence=0.95)
        occupation_field = ExtractedField(value="médecin", confidence=0.8)
        
        fields = {
            "age": age_field,
            "sex": sex_field,
            "occupation": occupation_field
        }
        
        # Create tenant info
        tenant_info = TenantInfo(
            fields=fields,
            language_preference="French",
            overall_confidence=0.88,
            updated_fields=["age", "sex", "occupation"]
        )
        
        # Verify the structure
        self.assertEqual(len(tenant_info.fields), 3)
        self.assertEqual(tenant_info.fields["age"].value, "28")
        self.assertEqual(tenant_info.fields["sex"].value, "female")
        self.assertEqual(tenant_info.fields["occupation"].value, "médecin")
        self.assertEqual(tenant_info.language_preference, "French")
        self.assertEqual(tenant_info.overall_confidence, 0.88)
        self.assertEqual(tenant_info.updated_fields, ["age", "sex", "occupation"])
    
    def test_json_serialization(self):
        """Test that models can be serialized to JSON"""
        field = ExtractedField(value="25", confidence=0.9)
        field_json = field.model_dump()
        
        self.assertEqual(field_json["value"], "25")
        self.assertEqual(field_json["confidence"], 0.9)
        
        tenant_info = TenantInfo(
            fields={"age": field},
            language_preference="English",
            overall_confidence=0.9,
            updated_fields=["age"]
        )
        
        tenant_json = tenant_info.model_dump()
        self.assertEqual(tenant_json["language_preference"], "English")
        self.assertEqual(tenant_json["overall_confidence"], 0.9)
        self.assertEqual(tenant_json["updated_fields"], ["age"])


if __name__ == '__main__':
    unittest.main()
