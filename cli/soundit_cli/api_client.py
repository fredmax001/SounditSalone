"""
API Client for Sound It CLI
"""
import requests
from typing import Optional, Dict, Any, List
from .config import ConfigManager, CLIConfig


class APIError(Exception):
    """API Error"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class SoundItAPI:
    """Sound It API Client"""
    
    def __init__(self, config: Optional[CLIConfig] = None):
        self.config = config or ConfigManager.get_config()
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        if self.config.access_token:
            self.session.headers["Authorization"] = f"Bearer {self.config.access_token}"
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make API request"""
        url = f"{self.config.api_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            if response.status_code == 401:
                raise APIError("Unauthorized - Please login first", 401)
            
            if response.status_code == 403:
                raise APIError("Forbidden - Insufficient permissions", 403)
            
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    detail = error_data.get('detail', 'Unknown error')
                except:
                    detail = response.text or 'Unknown error'
                raise APIError(f"API Error: {detail}", response.status_code)
            
            if response.status_code == 204:
                return None
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise APIError(f"Cannot connect to API at {self.config.api_base_url}")
        except requests.exceptions.Timeout:
            raise APIError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")
    
    # ============ AUTH ============
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get tokens"""
        response = self._request("POST", "/auth/login", json={
            "email": email,
            "password": password
        })
        return response
    
    def login_otp(self, phone: str, otp: str) -> Dict[str, Any]:
        """Login with OTP"""
        response = self._request("POST", "/auth/verify-otp", json={
            "phone": phone,
            "code": otp
        })
        return response
    
    def get_me(self) -> Dict[str, Any]:
        """Get current user info"""
        return self._request("GET", "/auth/me")
    
    # ============ USERS ============
    
    def list_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None, 
                   status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List users"""
        params = {"skip": skip, "limit": limit}
        if role:
            params["role"] = role
        if status:
            params["status"] = status
        return self._request("GET", "/admin/users", params=params)
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        return self._request("GET", f"/admin/users/{user_id}")
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        return self._request("PUT", f"/admin/users/{user_id}", json=data)
    
    def delete_user(self, user_id: int) -> None:
        """Delete user"""
        return self._request("DELETE", f"/admin/users/{user_id}")
    
    # ============ EVENTS ============
    
    def list_events(self, skip: int = 0, limit: int = 100, status: Optional[str] = None,
                    city: Optional[str] = None) -> List[Dict[str, Any]]:
        """List events"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        if city:
            params["city"] = city
        return self._request("GET", "/events", params=params)
    
    def get_event(self, event_id: int) -> Dict[str, Any]:
        """Get event by ID"""
        return self._request("GET", f"/events/{event_id}")
    
    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new event"""
        return self._request("POST", "/events", json=data)
    
    def update_event(self, event_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update event"""
        return self._request("PUT", f"/events/{event_id}", json=data)
    
    def delete_event(self, event_id: int) -> None:
        """Delete event"""
        return self._request("DELETE", f"/events/{event_id}")
    
    def approve_event(self, event_id: int) -> Dict[str, Any]:
        """Approve an event"""
        return self._request("POST", f"/admin/events/{event_id}/approve")
    
    def reject_event(self, event_id: int, reason: str) -> Dict[str, Any]:
        """Reject an event"""
        return self._request("POST", f"/admin/events/{event_id}/reject", json={"reason": reason})
    
    # ============ VENUES ============
    
    def list_venues(self, skip: int = 0, limit: int = 100, city: Optional[str] = None) -> List[Dict[str, Any]]:
        """List venues"""
        params = {"skip": skip, "limit": limit}
        if city:
            params["city"] = city
        return self._request("GET", "/clubs", params=params)
    
    def get_venue(self, venue_id: int) -> Dict[str, Any]:
        """Get venue by ID"""
        return self._request("GET", f"/clubs/{venue_id}")
    
    def create_venue(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new venue"""
        return self._request("POST", "/clubs", json=data)
    
    def update_venue(self, venue_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update venue"""
        return self._request("PUT", f"/clubs/{venue_id}", json=data)
    
    def delete_venue(self, venue_id: int) -> None:
        """Delete venue"""
        return self._request("DELETE", f"/clubs/{venue_id}")
    
    # ============ ADMIN STATS ============
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get admin dashboard statistics"""
        return self._request("GET", "/admin/dashboard-stats")
    
    def get_pending_actions(self) -> Dict[str, Any]:
        """Get pending admin actions"""
        return self._request("GET", "/admin/pending-actions")
    
    def get_verification_requests(self, status: str = "pending") -> List[Dict[str, Any]]:
        """Get verification requests"""
        return self._request("GET", "/admin/verifications", params={"status": status})
    
    def approve_verification(self, verification_id: int, notes: Optional[str] = None) -> Dict[str, Any]:
        """Approve verification request"""
        return self._request("POST", f"/admin/verifications/{verification_id}/approve", 
                           json={"notes": notes} if notes else {})
    
    def reject_verification(self, verification_id: int, reason: str) -> Dict[str, Any]:
        """Reject verification request"""
        return self._request("POST", f"/admin/verifications/{verification_id}/reject", 
                           json={"reason": reason})
    
    # ============ ORDERS & PAYMENTS ============
    
    def list_orders(self, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List orders"""
        params = {"skip": skip, "limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/admin/orders", params=params)
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get order by ID"""
        return self._request("GET", f"/admin/orders/{order_id}")
    
    def refund_order(self, order_id: int, reason: str) -> Dict[str, Any]:
        """Refund an order"""
        return self._request("POST", f"/admin/orders/{order_id}/refund", json={"reason": reason})
