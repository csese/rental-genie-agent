"""
Notification system for Rental Genie Agent
Handles Slack notifications for handoff events and other important alerts
"""

import os
import json
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv()

@dataclass
class HandoffNotification:
    """Structured handoff notification data"""
    session_id: str
    handoff_reason: str
    confidence_level: str
    escalation_priority: str
    conversation_summary: str
    tenant_name: Optional[str] = None
    tenant_age: Optional[int] = None
    tenant_occupation: Optional[str] = None
    tenant_language: Optional[str] = None
    tenant_profile: Dict[str, Any] = None
    conversation_history: List[Dict[str, Any]] = None
    property_interest: Optional[str] = None
    move_in_date: Optional[str] = None
    rental_duration: Optional[str] = None
    guarantor_status: Optional[str] = None
    viewing_interest: Optional[bool] = None
    availability: Optional[str] = None
    created_at: str = None

@dataclass
class SessionNotification:
    """Structured session notification data"""
    session_id: str
    tenant_message: str
    tenant_age: Optional[int] = None
    tenant_occupation: Optional[str] = None
    tenant_language: Optional[str] = None
    extracted_info: Dict[str, Any] = None
    created_at: str = None

class SlackNotifier:
    """Handles Slack notifications for rental events"""
    
    def __init__(self):
        self.webhook_url = os.environ.get("SLACK_WEBHOOK_RENTAL_GENIE_URL")
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            print("Warning: Slack notifications disabled. Set SLACK_WEBHOOK_RENTAL_GENIE_URL to enable.")
    
    def send_handoff_notification(self, notification: HandoffNotification) -> bool:
        """Send a handoff notification to Slack"""
        if not self.enabled:
            print("Slack notifications disabled")
            return False
        
        try:
            # Create Slack message
            message = self._create_handoff_message(notification)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Handoff notification sent to Slack for session {notification.session_id}")
                return True
            else:
                print(f"Failed to send Slack notification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def send_session_notification(self, notification: SessionNotification) -> bool:
        """Send a new session notification to Slack"""
        if not self.enabled:
            print("Slack notifications disabled")
            return False
        
        try:
            # Create Slack message
            message = self._create_session_message(notification)
            
            # Send to Slack
            response = requests.post(
                self.webhook_url,
                json=message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"Session notification sent to Slack for session {notification.session_id}")
                return True
            else:
                print(f"Failed to send Slack notification: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error sending Slack notification: {e}")
            return False
    
    def _create_handoff_message(self, notification: HandoffNotification) -> Dict[str, Any]:
        """Create a formatted Slack message for handoff notification"""
        
        # Determine color based on priority
        color_map = {
            "low": "#36a64f",      # Green
            "medium": "#ff8c00",   # Orange
            "high": "#ff6b6b",     # Red
            "urgent": "#8b0000"    # Dark red
        }
        color = color_map.get(notification.escalation_priority.lower(), "#36a64f")
        
        # Create tenant info section
        tenant_info = []
        if notification.tenant_age:
            tenant_info.append(f"Age: {notification.tenant_age}")
        if notification.tenant_occupation:
            tenant_info.append(f"Occupation: {notification.tenant_occupation}")
        if notification.tenant_language:
            tenant_info.append(f"Language: {notification.tenant_language}")
        if notification.move_in_date:
            tenant_info.append(f"Move-in: {notification.move_in_date}")
        if notification.rental_duration:
            tenant_info.append(f"Duration: {notification.rental_duration}")
        if notification.guarantor_status:
            tenant_info.append(f"Guarantor: {notification.guarantor_status}")
        
        # Create message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 Handoff Required - {notification.escalation_priority.upper()} Priority",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Session ID:*\n{notification.session_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Priority:*\n{notification.escalation_priority.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Reason:*\n{notification.handoff_reason}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Confidence:*\n{notification.confidence_level}"
                    }
                ]
            }
        ]
        
        # Add tenant info if available
        if tenant_info:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Tenant Info:*\n{chr(10).join(tenant_info)}"
                    }
                ]
            })
        
        # Add property interest if available
        if notification.property_interest:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Property Interest:*\n{notification.property_interest}"
                    }
                ]
            })
        
        # Add viewing interest and availability
        viewing_info = []
        if notification.viewing_interest is not None:
            viewing_info.append(f"Viewing Interest: {'Yes' if notification.viewing_interest else 'No'}")
        if notification.availability:
            viewing_info.append(f"Availability: {notification.availability}")
        
        if viewing_info:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Viewing Details:*\n{chr(10).join(viewing_info)}"
                    }
                ]
            })
        
        # Add conversation summary
        if notification.conversation_summary:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Conversation Summary:*\n{notification.conversation_summary}"
                }
            })
        
        # Add recent conversation context (last 3 messages)
        if notification.conversation_history and len(notification.conversation_history) > 0:
            recent_messages = notification.conversation_history[-3:]  # Last 3 messages
            context_text = "*Recent Conversation:*\n"
            for msg in recent_messages:
                user_msg = msg.get('user_message', '')[:100] + "..." if len(msg.get('user_message', '')) > 100 else msg.get('user_message', '')
                agent_msg = msg.get('agent_response', '')[:100] + "..." if len(msg.get('agent_response', '')) > 100 else msg.get('agent_response', '')
                context_text += f"👤 *User:* {user_msg}\n🤖 *Agent:* {agent_msg}\n\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": context_text
                }
            })
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Full Profile",
                        "emoji": True
                    },
                    "style": "primary",
                    "url": f"https://your-dashboard.com/tenants/{notification.session_id}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Contact Tenant",
                        "emoji": True
                    },
                    "style": "primary",
                    "url": f"https://your-dashboard.com/contact/{notification.session_id}"
                }
            ]
        })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Handoff triggered at {notification.created_at}"
                }
            ]
        })
        
        return {
            "attachments": [
                {
                    "color": color,
                    "blocks": blocks
                }
            ]
        }
    
    def _create_session_message(self, notification: SessionNotification) -> Dict[str, Any]:
        """Create a formatted Slack message for new session notification"""
        
        # Create tenant info section
        tenant_info = []
        if notification.tenant_age:
            tenant_info.append(f"Age: {notification.tenant_age}")
        if notification.tenant_occupation:
            tenant_info.append(f"Occupation: {notification.tenant_occupation}")
        if notification.tenant_language:
            tenant_info.append(f"Language: {notification.tenant_language}")
        
        # Add extracted information
        if notification.extracted_info:
            for key, value in notification.extracted_info.items():
                if value:
                    tenant_info.append(f"{key.title()}: {value}")
        
        # Create message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🆕 New Tenant Inquiry",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Session ID:*\n{notification.session_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Status:*\nNew Prospect"
                    }
                ]
            }
        ]
        
        # Add tenant info if available
        if tenant_info:
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Initial Info:*\n{chr(10).join(tenant_info)}"
                    }
                ]
            })
        
        # Add initial message
        if notification.tenant_message:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Initial Message:*\n{notification.tenant_message[:200]}{'...' if len(notification.tenant_message) > 200 else ''}"
                }
            })
        
        # Add action buttons
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Session",
                        "emoji": True
                    },
                    "style": "primary",
                    "url": f"https://your-dashboard.com/sessions/{notification.session_id}"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Monitor Conversation",
                        "emoji": True
                    },
                    "url": f"https://your-dashboard.com/monitor/{notification.session_id}"
                }
            ]
        })
        
        # Add timestamp
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Session started at {notification.created_at}"
                }
            ]
        })
        
        return {
            "attachments": [
                {
                    "color": "#36a64f",  # Green for new sessions
                    "blocks": blocks
                }
            ]
        }
    
    def send_test_notification(self) -> bool:
        """Send a test notification to verify Slack integration"""
        test_notification = HandoffNotification(
            session_id="test_session_123",
            handoff_reason="Test notification",
            confidence_level="medium",
            escalation_priority="low",
            conversation_summary="This is a test notification to verify Slack integration.",
            created_at=datetime.now().isoformat()
        )
        
        return self.send_handoff_notification(test_notification)

# Global Slack notifier instance
slack_notifier = SlackNotifier()

def send_handoff_notification(
    session_id: str,
    handoff_reason: str,
    confidence_level: str,
    escalation_priority: str,
    conversation_summary: str,
    tenant_profile: Optional[Dict[str, Any]] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> bool:
    """Send a handoff notification to Slack"""
    
    notification = HandoffNotification(
        session_id=session_id,
        handoff_reason=handoff_reason,
        confidence_level=confidence_level,
        escalation_priority=escalation_priority,
        conversation_summary=conversation_summary,
        tenant_profile=tenant_profile,
        conversation_history=conversation_history,
        created_at=datetime.now().isoformat(),
        **kwargs
    )
    
    return slack_notifier.send_handoff_notification(notification)

def send_session_notification(
    session_id: str,
    tenant_message: str,
    extracted_info: Optional[Dict[str, Any]] = None,
    **kwargs
) -> bool:
    """Send a new session notification to Slack"""
    
    notification = SessionNotification(
        session_id=session_id,
        tenant_message=tenant_message,
        extracted_info=extracted_info,
        created_at=datetime.now().isoformat(),
        **kwargs
    )
    
    return slack_notifier.send_session_notification(notification)

def test_slack_integration() -> bool:
    """Test Slack integration"""
    return slack_notifier.send_test_notification()
