import httpx
import logging
from typing import Optional, Dict, Any, List
from config import settings
from uuid import UUID

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.baileys_url = settings.baileys_api_url
        
    async def create_session(self, session_id: str, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Create a new WhatsApp session"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.baileys_url}/create-session",
                    json={
                        "sessionId": session_id,
                        "webhookUrl": webhook_url
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            raise Exception(f"Failed to create WhatsApp session: {str(e)}")
    
    async def get_qr_code(self, session_id: str) -> Optional[str]:
        """Get QR code for session"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baileys_url}/qr-code/{session_id}",
                    timeout=10.0
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                data = response.json()
                return data.get("qrCode")
        except httpx.HTTPError as e:
            logger.error(f"Failed to get QR code for {session_id}: {e}")
            return None
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baileys_url}/status/{session_id}",
                    timeout=10.0
                )
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get status for {session_id}: {e}")
            return None
    
    async def send_message(
        self, 
        session_id: str, 
        to: str, 
        message: str, 
        message_type: str = "text"
    ) -> Optional[Dict[str, Any]]:
        """Send a message through WhatsApp"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.baileys_url}/send-message",
                    json={
                        "sessionId": session_id,
                        "to": to,
                        "message": message,
                        "messageType": message_type
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to send message via {session_id}: {e}")
            raise Exception(f"Failed to send message: {str(e)}")
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a WhatsApp session"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.baileys_url}/session/{session_id}",
                    timeout=30.0
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.baileys_url}/sessions",
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("sessions", [])
        except httpx.HTTPError as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

# Global instance
whatsapp_service = WhatsAppService()