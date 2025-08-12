"""
Enums for the Rental Genie Agent
"""

from enum import Enum
from typing import List

class TenantStatus(Enum):
    """Enumeration of possible tenant statuses"""
    PROSPECT = "prospect"  # Initial inquiry, incomplete profile
    QUALIFIED = "qualified"  # Complete profile, ready for viewing
    VIEWING_SCHEDULED = "viewing_scheduled"  # Viewing arranged
    APPLICATION_SUBMITTED = "application_submitted"  # Rental application submitted
    APPROVED = "approved"  # Application approved
    ACTIVE_TENANT = "active_tenant"  # Currently renting
    FORMER_TENANT = "former_tenant"  # Past tenant
    REJECTED = "rejected"  # Application rejected
    WITHDRAWN = "withdrawn"  # Prospect withdrew interest
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all status values as strings"""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if a status string is valid"""
        return status in cls.get_all_values()
    
    @classmethod
    def get_display_name(cls, status: str) -> str:
        """Get a human-readable display name for a status"""
        status_map = {
            cls.PROSPECT.value: "Prospect",
            cls.QUALIFIED.value: "Qualified",
            cls.VIEWING_SCHEDULED.value: "Viewing Scheduled",
            cls.APPLICATION_SUBMITTED.value: "Application Submitted",
            cls.APPROVED.value: "Approved",
            cls.ACTIVE_TENANT.value: "Active Tenant",
            cls.FORMER_TENANT.value: "Former Tenant",
            cls.REJECTED.value: "Rejected",
            cls.WITHDRAWN.value: "Withdrawn"
        }
        return status_map.get(status, status)
    
    @classmethod
    def get_description(cls, status: str) -> str:
        """Get a description for a status"""
        descriptions = {
            cls.PROSPECT.value: "Initial inquiry, incomplete profile",
            cls.QUALIFIED.value: "Complete profile, ready for viewing",
            cls.VIEWING_SCHEDULED.value: "Viewing arranged",
            cls.APPLICATION_SUBMITTED.value: "Rental application submitted",
            cls.APPROVED.value: "Application approved",
            cls.ACTIVE_TENANT.value: "Currently renting",
            cls.FORMER_TENANT.value: "Past tenant",
            cls.REJECTED.value: "Application rejected",
            cls.WITHDRAWN.value: "Prospect withdrew interest"
        }
        return descriptions.get(status, "Unknown status")
